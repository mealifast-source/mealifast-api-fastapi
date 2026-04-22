from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, date
import logging

from app.models import (
    User,
    MealiFastGroup,
    GroupMember,
    MemberOrder,
    Invoice,
    DeliveryTracking,
)
from app.core.constants import (
    UserRole,
    GroupStatus,
    MemberStatus,
    InvoiceStatus,
    OrderStatus,
    DeliveryStatus,
)

logger = logging.getLogger(__name__)


class DashboardService:
    """Dashboard and analytics service"""

    def get_platform_dashboard(self, db: Session) -> dict:
        """Get platform-wide analytics"""
        try:
            # Total users
            total_users = db.query(func.count(User.id)).scalar() or 0

            # Total groups
            total_groups = db.query(func.count(MealiFastGroup.id)).scalar() or 0

            # Active subscriptions
            active_groups = (
                db.query(func.count(MealiFastGroup.id))
                .filter(MealiFastGroup.status == GroupStatus.ACTIVE)
                .scalar()
                or 0
            )

            # Total orders this month
            month_start = datetime.now().replace(day=1)
            total_orders = (
                db.query(func.count(MemberOrder.id))
                .filter(MemberOrder.created_at >= month_start)
                .scalar()
                or 0
            )

            # Total revenue from paid invoices
            total_revenue = (
                db.query(func.sum(Invoice.total_amount))
                .filter(Invoice.status == InvoiceStatus.PAID)
                .scalar()
                or 0.0
            )

            # Recent transactions (last 10 paid invoices)
            recent_invoices = (
                db.query(Invoice)
                .filter(Invoice.status == InvoiceStatus.PAID)
                .order_by(Invoice.updated_at.desc())
                .limit(10)
                .all()
            )

            recent_transactions = [
                {
                    "invoice_id": inv.id,
                    "amount": inv.total_amount,
                    "date": inv.updated_at.isoformat(),
                }
                for inv in recent_invoices
            ]

            return {
                "total_users": int(total_users),
                "total_groups": int(total_groups),
                "active_subscriptions": int(active_groups),
                "total_orders": int(total_orders),
                "total_revenue": float(total_revenue),
                "recent_transactions": recent_transactions,
            }
        except Exception as e:
            logger.error(f"Error getting platform dashboard: {str(e)}")
            return {
                "total_users": 0,
                "total_groups": 0,
                "active_subscriptions": 0,
                "total_orders": 0,
                "total_revenue": 0.0,
                "recent_transactions": [],
            }

    def get_group_dashboard(self, db: Session, group_id: str) -> dict:
        """Get group dashboard analytics"""
        try:
            group = db.query(MealiFastGroup).filter(
                MealiFastGroup.id == group_id
            ).first()

            if not group:
                return {}

            # Member counts
            total_members = (
                db.query(func.count(GroupMember.id))
                .filter(GroupMember.group_id == group_id)
                .scalar()
                or 0
            )

            active_members = (
                db.query(func.count(GroupMember.id))
                .filter(
                    and_(
                        GroupMember.group_id == group_id,
                        GroupMember.status == MemberStatus.ACTIVE,
                    )
                )
                .scalar()
                or 0
            )

            # Orders this week
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            orders_this_week = (
                db.query(func.count(MemberOrder.id))
                .filter(
                    and_(
                        MemberOrder.group_id == group_id,
                        MemberOrder.created_at >= week_start,
                    )
                )
                .scalar()
                or 0
            )

            # Pending orders
            pending_orders = (
                db.query(func.count(MemberOrder.id))
                .filter(
                    and_(
                        MemberOrder.group_id == group_id,
                        MemberOrder.status.in_([OrderStatus.DRAFT, OrderStatus.SUBMITTED]),
                    )
                )
                .scalar()
                or 0
            )

            # Upcoming deliveries (next 7 days)
            today = date.today()
            upcoming_date = today + timedelta(days=7)
            upcoming_deliveries = (
                db.query(func.count(DeliveryTracking.id))
                .filter(
                    and_(
                        DeliveryTracking.group_id == group_id,
                        DeliveryTracking.delivery_date >= today,
                        DeliveryTracking.delivery_date <= upcoming_date,
                    )
                )
                .scalar()
                or 0
            )

            # Invoice summary
            invoices = db.query(Invoice).filter(Invoice.group_id == group_id).all()

            invoice_summary = {
                "total_invoices": len(invoices),
                "pending": sum(
                    1 for inv in invoices if inv.status == InvoiceStatus.DRAFT
                ),
                "sent": sum(1 for inv in invoices if inv.status == InvoiceStatus.SENT),
                "paid": sum(1 for inv in invoices if inv.status == InvoiceStatus.PAID),
                "outstanding": sum(
                    inv.amount_due
                    for inv in invoices
                    if inv.status in [InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID]
                ),
            }

            return {
                "group_name": group.group_name,
                "active_members": int(active_members),
                "total_members": int(total_members),
                "orders_this_week": int(orders_this_week),
                "pending_orders": int(pending_orders),
                "upcoming_deliveries": int(upcoming_deliveries),
                "invoice_summary": invoice_summary,
            }
        except Exception as e:
            logger.error(f"Error getting group dashboard: {str(e)}")
            return {}

    def get_member_dashboard(self, db: Session, member_id: str) -> dict:
        """Get member dashboard"""
        try:
            user = db.query(User).filter(User.id == member_id).first()

            if not user:
                return {}

            # Get member's groups
            memberships = db.query(GroupMember).filter(
                GroupMember.user_id == member_id
            ).all()

            groups = [
                {
                    "group_id": m.group_id,
                    "status": m.status.value,
                }
                for m in memberships
            ]

            # Active orders
            active_orders = (
                db.query(func.count(MemberOrder.id))
                .filter(
                    and_(
                        MemberOrder.member_id == member_id,
                        MemberOrder.status.in_(
                            [OrderStatus.DRAFT, OrderStatus.SUBMITTED, OrderStatus.APPROVED]
                        ),
                    )
                )
                .scalar()
                or 0
            )

            # Recent orders
            recent_orders = (
                db.query(MemberOrder)
                .filter(MemberOrder.member_id == member_id)
                .order_by(MemberOrder.created_at.desc())
                .limit(5)
                .all()
            )

            # Invoices due
            today = date.today()
            due_invoices = (
                db.query(Invoice)
                .filter(
                    and_(
                        Invoice.group_id.in_([m.group_id for m in memberships]),
                        Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.PARTIAL_PAID]),
                        Invoice.billing_end_date <= today,
                    )
                )
                .all()
            )

            # Dietary preferences
            dietary_prefs = set()
            for membership in memberships:
                if membership.dietary_preferences:
                    dietary_prefs.update(membership.dietary_preferences)

            return {
                "member_name": user.full_name,
                "groups": groups,
                "active_orders": int(active_orders),
                "recent_orders": [
                    {
                        "order_id": o.id,
                        "status": o.status.value,
                        "created_at": o.created_at.isoformat(),
                    }
                    for o in recent_orders
                ],
                "invoices_due": [
                    {
                        "invoice_id": inv.id,
                        "amount_due": inv.amount_due,
                        "billing_end_date": inv.billing_end_date.isoformat(),
                    }
                    for inv in due_invoices
                ],
                "dietary_preferences": list(dietary_prefs),
            }
        except Exception as e:
            logger.error(f"Error getting member dashboard: {str(e)}")
            return {}
