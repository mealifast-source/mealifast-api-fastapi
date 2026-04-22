from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import requests
import json
from datetime import datetime

from app.models import Invoice, DeliveryTracking, MealRating
from app.core.constants import InvoiceStatus, DeliveryStatus
from app.core.exceptions import NotFoundException, BadRequestException, PaymentFailedException
from app.config import settings
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class InvoiceService(BaseService[Invoice]):
    """Service for invoice operations"""
    
    def __init__(self):
        super().__init__(Invoice)
    
    def generate_invoice(
        self,
        db: Session,
        group_id: str,
        billing_start_date: datetime,
        billing_end_date: datetime,
        total_meals: int,
        total_amount: float,
    ) -> Invoice:
        """Generate invoice"""
        try:
            invoice = self.create(
                db,
                group_id=group_id,
                billing_start_date=billing_start_date,
                billing_end_date=billing_end_date,
                total_meals_delivered=total_meals,
                total_amount=total_amount,
                amount_due=total_amount,
                status=InvoiceStatus.DRAFT,
            )
            logger.info(f"Invoice generated: {invoice.id}")
            return invoice
        except Exception as e:
            logger.error(f"Failed to generate invoice: {e}")
            raise
    
    def mark_as_sent(self, db: Session, invoice_id: str) -> Invoice:
        """Mark invoice as sent"""
        invoice = self.get_by_id(db, invoice_id)
        
        if not invoice:
            raise NotFoundException("Invoice", invoice_id)
        
        invoice = self.update(db, invoice_id, status=InvoiceStatus.SENT)
        logger.info(f"Invoice marked as sent: {invoice_id}")
        return invoice
    
    def mark_as_paid(self, db: Session, invoice_id: str, payment_details: dict) -> Invoice:
        """Mark invoice as paid"""
        invoice = self.get_by_id(db, invoice_id)
        
        if not invoice:
            raise NotFoundException("Invoice", invoice_id)
        
        invoice = self.update(
            db,
            invoice_id,
            status=InvoiceStatus.PAID,
            amount_due=0,
            payment_record=payment_details,
        )
        logger.info(f"Invoice marked as paid: {invoice_id}")
        return invoice
    
    def get_group_invoices(
        self,
        db: Session,
        group_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Invoice], int]:
        """Get invoices for a group"""
        try:
            total = db.query(Invoice).filter(Invoice.group_id == group_id).count()
            invoices = db.query(Invoice).filter(
                Invoice.group_id == group_id
            ).offset(skip).limit(limit).all()
            return invoices, total
        except Exception as e:
            logger.error(f"Failed to get group invoices: {e}")
            raise


class PaymentService:
    """Service for payment processing via Paystack"""
    
    @staticmethod
    def initialize_payment(
        invoice_id: str,
        email: str,
        amount: float,
    ) -> tuple[str, str]:
        """Initialize Paystack payment"""
        try:
            # Amount in kobo (cents)
            amount_kobo = int(amount * 100)
            
            payload = {
                "email": email,
                "amount": amount_kobo,
                "reference": f"inv_{invoice_id}",
            }
            
            headers = {
                "Authorization": f"Bearer {settings.paystack_secret_key}",
                "Content-Type": "application/json",
            }
            
            response = requests.post(
                f"{settings.paystack_api_url}/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=30,
            )
            
            if response.status_code != 200:
                raise PaymentFailedException(f"Paystack returned {response.status_code}")
            
            data = response.json()
            
            if not data.get("status"):
                raise PaymentFailedException(data.get("message", "Unknown error"))
            
            checkout_url = data["data"]["authorization_url"]
            reference = data["data"]["reference"]
            
            logger.info(f"Payment initialized: {invoice_id} -> {reference}")
            return checkout_url, reference
        except requests.RequestException as e:
            logger.error(f"Payment initialization failed: {e}")
            raise PaymentFailedException(str(e))
    
    @staticmethod
    def verify_payment(reference: str) -> dict:
        """Verify Paystack payment"""
        try:
            headers = {
                "Authorization": f"Bearer {settings.paystack_secret_key}",
            }
            
            response = requests.get(
                f"{settings.paystack_api_url}/transaction/verify/{reference}",
                headers=headers,
                timeout=30,
            )
            
            if response.status_code != 200:
                raise PaymentFailedException(f"Paystack returned {response.status_code}")
            
            data = response.json()
            
            if not data.get("status"):
                raise PaymentFailedException(data.get("message", "Unknown error"))
            
            transaction_data = data["data"]
            
            if transaction_data["status"] != "success":
                raise PaymentFailedException(f"Payment status: {transaction_data['status']}")
            
            logger.info(f"Payment verified: {reference}")
            return transaction_data
        except requests.RequestException as e:
            logger.error(f"Payment verification failed: {e}")
            raise PaymentFailedException(str(e))


class DeliveryService(BaseService[DeliveryTracking]):
    """Service for delivery tracking"""
    
    def __init__(self):
        super().__init__(DeliveryTracking)
    
    def create_delivery(
        self,
        db: Session,
        group_id: str,
        delivery_date: datetime,
        meal_summary: dict,
    ) -> DeliveryTracking:
        """Create delivery record"""
        try:
            delivery = self.create(
                db,
                group_id=group_id,
                delivery_date=delivery_date,
                meal_summary=meal_summary,
                status=DeliveryStatus.PENDING,
            )
            logger.info(f"Delivery created: {delivery.id}")
            return delivery
        except Exception as e:
            logger.error(f"Failed to create delivery: {e}")
            raise
    
    def update_delivery_status(
        self,
        db: Session,
        delivery_id: str,
        status: DeliveryStatus,
    ) -> DeliveryTracking:
        """Update delivery status"""
        delivery = self.get_by_id(db, delivery_id)
        
        if not delivery:
            raise NotFoundException("DeliveryTracking", delivery_id)
        
        delivery = self.update(db, delivery_id, status=status)
        logger.info(f"Delivery status updated: {delivery_id} -> {status}")
        return delivery
    
    def record_missed_meals(
        self,
        db: Session,
        delivery_id: str,
        missed_meals: dict,
    ) -> DeliveryTracking:
        """Record missed meals for delivery"""
        delivery = self.get_by_id(db, delivery_id)
        
        if not delivery:
            raise NotFoundException("DeliveryTracking", delivery_id)
        
        delivery = self.update(
            db,
            delivery_id,
            missed_meals=missed_meals,
            status=DeliveryStatus.PARTIAL_DELIVERY,
        )
        logger.info(f"Missed meals recorded: {delivery_id}")
        return delivery


class MealRatingService(BaseService[MealRating]):
    """Service for meal ratings"""
    
    def __init__(self):
        super().__init__(MealRating)
    
    def create_rating(
        self,
        db: Session,
        meal_id: str,
        member_id: str,
        rating: int,
        review: Optional[str] = None,
    ) -> MealRating:
        """Create meal rating"""
        if not 1 <= rating <= 5:
            raise BadRequestException("Rating must be between 1 and 5")
        
        # Check if already rated
        existing_rating = db.query(MealRating).filter(
            MealRating.meal_id == meal_id,
            MealRating.member_id == member_id,
        ).first()
        
        if existing_rating:
            # Update existing rating
            return self.update(
                db,
                existing_rating.id,
                rating=rating,
                review=review,
            )
        
        try:
            rating_obj = self.create(
                db,
                meal_id=meal_id,
                member_id=member_id,
                rating=rating,
                review=review,
            )
            logger.info(f"Rating created: {rating_obj.id}")
            return rating_obj
        except Exception as e:
            logger.error(f"Failed to create rating: {e}")
            raise
