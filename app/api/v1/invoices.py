from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import InvoiceService, PaymentService
from app.schemas.order import (
    InvoiceGenerateSchema,
    InvoicePaymentSchema,
)
from app.core.exceptions import MealiFastException
from app.api.dependencies import (
    get_current_user,
    get_current_admin_user,
    get_current_group_admin,
)
from app.utils.response import success_response, created_response
from app.models import User

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/{group_id}/generate", response_model=dict)
async def generate_invoice(
    group_id: str,
    invoice_data: InvoiceGenerateSchema,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Generate invoice for group"""
    try:
        invoice_service = InvoiceService()
        
        # In production, calculate actual meals from orders
        invoice = invoice_service.generate_invoice(
            db,
            group_id=group_id,
            billing_start_date=invoice_data.billing_start_date,
            billing_end_date=invoice_data.billing_end_date,
            total_meals=0,
            total_amount=0.0,
        )
        
        return created_response(
            data={"invoice_id": invoice.id, "status": invoice.status.value},
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{invoice_id}", response_model=dict)
async def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get invoice details"""
    try:
        invoice_service = InvoiceService()
        invoice = invoice_service.get_by_id(db, invoice_id)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return success_response(
            data={
                "invoice_id": invoice.id,
                "group_id": invoice.group_id,
                "billing_start_date": invoice.billing_start_date.isoformat(),
                "billing_end_date": invoice.billing_end_date.isoformat(),
                "total_amount": invoice.total_amount,
                "amount_due": invoice.amount_due,
                "status": invoice.status.value,
                "created_at": invoice.created_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{invoice_id}/send", response_model=dict)
async def send_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Send invoice"""
    try:
        invoice_service = InvoiceService()
        invoice = invoice_service.mark_as_sent(db, invoice_id)
        
        return success_response(
            data={"invoice_id": invoice.id, "status": invoice.status.value},
            message="Invoice sent",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{invoice_id}/pay", response_model=dict)
async def initialize_payment(
    invoice_id: str,
    payment_data: InvoicePaymentSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initialize Paystack payment"""
    try:
        invoice_service = InvoiceService()
        invoice = invoice_service.get_by_id(db, invoice_id)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Initialize Paystack payment
        checkout_url, reference = PaymentService.initialize_payment(
            invoice_id,
            payment_data.email,
            invoice.total_amount,
        )
        
        # Store reference in invoice
        invoice_service.update(
            db,
            invoice_id,
            payment_record={"paystack_reference": reference},
        )
        
        return created_response(
            data={
                "invoice_id": invoice_id,
                "payment_url": checkout_url,
                "paystack_reference": reference,
            },
            message="Payment initialized",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/list", response_model=dict)
async def list_group_invoices(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List group invoices"""
    try:
        invoice_service = InvoiceService()
        invoices, total = invoice_service.get_group_invoices(db, group_id, skip, limit)
        
        return success_response(
            data={
                "items": [
                    {
                        "invoice_id": inv.id,
                        "billing_end_date": inv.billing_end_date.isoformat(),
                        "total_amount": inv.total_amount,
                        "amount_due": inv.amount_due,
                        "status": inv.status.value,
                    }
                    for inv in invoices
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/paystack", response_model=dict)
async def paystack_webhook(
    request_body: dict,
    db: Session = Depends(get_db),
):
    """Paystack webhook for payment confirmation"""
    try:
        # Verify webhook signature (implement in production)
        event = request_body.get("event")
        
        if event == "charge.success":
            data = request_body.get("data", {})
            reference = data.get("reference", "")
            
            # Verify payment with Paystack
            payment_details = PaymentService.verify_payment(reference)
            
            # Extract invoice ID from reference
            invoice_id = reference.replace("inv_", "")
            
            # Mark invoice as paid
            invoice_service = InvoiceService()
            invoice_service.mark_as_paid(db, invoice_id, payment_details)
            
            return success_response(message="Payment processed")
        
        return success_response(message="Event processed")
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
