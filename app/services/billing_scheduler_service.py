import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.services import InvoiceService, GroupService, EmailService
from app.models import MealiFastGroup
from app.core.constants import GroupStatus
import json

logger = logging.getLogger(__name__)


class BillingSchedulerService:
    """Service for scheduling background billing tasks"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.configure(timezone="UTC")

    def start(self):
        """Start the scheduler"""
        try:
            # Schedule daily billing at 2 AM UTC
            self.scheduler.add_job(
                self.run_daily_billing,
                CronTrigger(hour=2, minute=0),
                id="daily_billing",
                name="Daily Billing Task",
                replace_existing=True,
            )
            self.scheduler.start()
            logger.info("Billing scheduler started")
        except Exception as e:
            logger.error(f"Failed to start billing scheduler: {e}")
            raise

    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Billing scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping billing scheduler: {e}")

    @staticmethod
    def run_daily_billing():
        """Run daily billing tasks"""
        db = SessionLocal()
        try:
            logger.info("Starting daily billing task...")

            # Get groups whose billing period ends today
            today = datetime.utcnow().date()
            groups = db.query(MealiFastGroup).filter(
                MealiFastGroup.plan_end_date == today,
                MealiFastGroup.status == GroupStatus.ACTIVE,
            ).all()

            invoice_service = InvoiceService()
            email_service = EmailService()

            for group in groups:
                try:
                    # Generate invoice for this group
                    billing_start = group.plan_start_date
                    billing_end = group.plan_end_date

                    # Calculate total meals and amount from orders
                    from app.models import MemberOrder
                    from app.core.constants import OrderStatus

                    orders = db.query(MemberOrder).filter(
                        MemberOrder.group_id == group.id,
                        MemberOrder.week_start_date >= billing_start,
                        MemberOrder.week_start_date <= billing_end,
                        MemberOrder.status == OrderStatus.LOCKED,
                    ).all()

                    # Calculate totals
                    total_meals = 0
                    for order in orders:
                        if order.daily_meals:
                            for day_meals in order.daily_meals.values():
                                if isinstance(day_meals, dict):
                                    total_meals += sum(
                                        count
                                        for meal_counts in day_meals.values()
                                        if isinstance(meal_counts, dict)
                                        for count in meal_counts.values()
                                    )

                    # Get subscription plan price
                    plan_price = (
                        group.subscription_plan.price_per_meal
                        if group.subscription_plan
                        else 0.0
                    )
                    total_amount = total_meals * plan_price

                    # Generate invoice
                    invoice = invoice_service.generate_invoice(
                        db,
                        group_id=group.id,
                        billing_start_date=billing_start,
                        billing_end_date=billing_end,
                        total_meals=total_meals,
                        total_amount=total_amount,
                    )

                    logger.info(
                        f"Invoice generated for group {group.id}: {invoice.id} (${total_amount})"
                    )

                    # Send email notification
                    try:
                        admin = group.admin
                        email_service.send_invoice_email(
                            email=admin.email,
                            invoice_id=invoice.id,
                            total_amount=total_amount,
                            group_name=group.group_name,
                            payment_url=f"{settings.app_url}/invoices/{invoice.id}/pay",
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send invoice email: {e}")

                except Exception as e:
                    logger.error(f"Failed to process billing for group {group.id}: {e}")
                    continue

            logger.info("Daily billing task completed")

        except Exception as e:
            logger.error(f"Daily billing task failed: {e}")
        finally:
            db.close()

    @staticmethod
    def run_weekly_reminder():
        """Send weekly order reminders"""
        db = SessionLocal()
        try:
            logger.info("Starting weekly reminder task...")

            from app.models import OrderWindow
            from app.core.constants import OrderWindowStatus
            from datetime import timedelta

            # Get open order windows ending in next 24 hours
            now = datetime.utcnow()
            tomorrow = now + timedelta(days=1)

            windows = db.query(OrderWindow).filter(
                OrderWindow.close_date_time > now,
                OrderWindow.close_date_time <= tomorrow,
                OrderWindow.status == OrderWindowStatus.OPEN,
            ).all()

            email_service = EmailService()

            for window in windows:
                try:
                    group = window.group
                    members = group.members

                    for member in members:
                        try:
                            email_service.send_email(
                                to_email=member.user.email,
                                subject=f"Reminder: Order window closing for {group.group_name}",
                                html_content=f"""
                                <h2>Order Reminder</h2>
                                <p>The order window for <strong>{group.group_name}</strong> is closing in 24 hours.</p>
                                <p>Please submit your meal preferences before {window.close_date_time.strftime('%Y-%m-%d %H:%M UTC')}.</p>
                                """,
                            )
                        except Exception as e:
                            logger.warning(f"Failed to send reminder to {member.user.email}: {e}")

                except Exception as e:
                    logger.error(f"Failed to process reminders for window {window.id}: {e}")

            logger.info("Weekly reminder task completed")

        except Exception as e:
            logger.error(f"Weekly reminder task failed: {e}")
        finally:
            db.close()


# Global scheduler instance
billing_scheduler = BillingSchedulerService()


def start_billing_scheduler():
    """Start the billing scheduler"""
    billing_scheduler.start()


def stop_billing_scheduler():
    """Stop the billing scheduler"""
    billing_scheduler.stop()
