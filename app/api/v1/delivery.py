from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.database import get_db
from app.services import DeliveryService
from app.schemas.order import DeliveryTrackingCreateSchema
from app.core.exceptions import MealiFastException
from app.api.dependencies import get_current_user, get_current_group_admin
from app.utils.response import success_response, created_response
from app.models import User
from app.core.constants import DeliveryStatus

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.post("/", response_model=dict)
async def create_delivery(
    delivery_data: DeliveryTrackingCreateSchema,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Create delivery tracking record"""
    try:
        delivery_service = DeliveryService()
        delivery = delivery_service.create_delivery(
            db,
            group_id=delivery_data.group_id,
            delivery_date=delivery_data.delivery_date,
            meal_summary=delivery_data.meal_summary,
        )
        
        return created_response(
            data={
                "delivery_id": delivery.id,
                "status": delivery.status.value,
            },
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{delivery_id}", response_model=dict)
async def get_delivery(
    delivery_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get delivery details"""
    try:
        delivery_service = DeliveryService()
        delivery = delivery_service.get_by_id(db, delivery_id)
        
        if not delivery:
            raise HTTPException(status_code=404, detail="Delivery not found")
        
        return success_response(
            data={
                "delivery_id": delivery.id,
                "group_id": delivery.group_id,
                "delivery_date": delivery.delivery_date.isoformat(),
                "status": delivery.status.value,
                "meal_summary": delivery.meal_summary or {},
                "missed_meals": delivery.missed_meals or {},
                "notes": delivery.notes,
                "created_at": delivery.created_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{delivery_id}/status", response_model=dict)
async def update_delivery_status(
    delivery_id: str,
    status: str,
    notes: str = None,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Update delivery status"""
    try:
        delivery_service = DeliveryService()
        
        # Validate status enum
        valid_statuses = [s.value for s in DeliveryStatus]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        update_data = {"status": DeliveryStatus[status.upper()]}
        if notes:
            update_data["notes"] = notes
        
        delivery = delivery_service.update(db, delivery_id, **update_data)
        
        return success_response(
            data={
                "delivery_id": delivery.id,
                "status": delivery.status.value,
            },
            message="Delivery status updated",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{delivery_id}/record-missed", response_model=dict)
async def record_missed_meals(
    delivery_id: str,
    missed_meals: dict,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Record missed meals for delivery"""
    try:
        delivery_service = DeliveryService()
        delivery = delivery_service.record_missed_meals(db, delivery_id, missed_meals)
        
        return success_response(
            data={
                "delivery_id": delivery.id,
                "status": delivery.status.value,
                "missed_meals": delivery.missed_meals,
            },
            message="Missed meals recorded",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group/{group_id}", response_model=dict)
async def get_group_deliveries(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get group deliveries"""
    try:
        delivery_service = DeliveryService()
        
        # Build query
        query = db.query(DeliveryService.model)
        query = query.filter_by(group_id=group_id)
        
        if status_filter:
            query = query.filter_by(status=DeliveryStatus[status_filter.upper()])
        
        total = query.count()
        deliveries = query.offset(skip).limit(limit).all()
        
        return success_response(
            data={
                "items": [
                    {
                        "delivery_id": d.id,
                        "delivery_date": d.delivery_date.isoformat(),
                        "status": d.status.value,
                        "created_at": d.created_at.isoformat(),
                    }
                    for d in deliveries
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group/{group_id}/upcoming", response_model=dict)
async def get_upcoming_deliveries(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get upcoming deliveries for group"""
    try:
        delivery_service = DeliveryService()
        
        # Get deliveries from today onwards
        from app.models import DeliveryTracking
        
        today = date.today()
        query = db.query(DeliveryTracking)
        query = query.filter(DeliveryTracking.group_id == group_id)
        query = query.filter(DeliveryTracking.delivery_date >= today)
        query = query.order_by(DeliveryTracking.delivery_date.asc())
        
        deliveries = query.all()
        
        return success_response(
            data={
                "items": [
                    {
                        "delivery_id": d.id,
                        "delivery_date": d.delivery_date.isoformat(),
                        "status": d.status.value,
                    }
                    for d in deliveries
                ],
                "total": len(deliveries),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
