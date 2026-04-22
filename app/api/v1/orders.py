from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import OrderWindowService, MemberOrderService
from app.schemas.order import (
    OrderWindowCreateSchema,
    MemberOrderCreateSchema,
    MemberOrderUpdateSchema,
)
from app.core.exceptions import MealiFastException
from app.api.dependencies import get_current_user, get_current_group_admin
from app.utils.response import success_response, created_response
from app.models import User
from app.core.constants import OrderWindowStatus

router = APIRouter(prefix="/orders", tags=["orders"])


# Order Window Endpoints
@router.post("/windows/", response_model=dict)
async def create_order_window(
    window_data: OrderWindowCreateSchema,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Open order window"""
    try:
        window_service = OrderWindowService()
        window = window_service.open_order_window(
            db,
            group_id=window_data.group_id,
            week_start_date=window_data.week_start_date,
            open_date_time=window_data.open_date_time,
            close_date_time=window_data.close_date_time,
        )
        
        return created_response(
            data={
                "window_id": window.id,
                "status": window.status.value,
            },
            message="Order window opened",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/windows/{window_id}", response_model=dict)
async def get_order_window(
    window_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get order window details"""
    try:
        window_service = OrderWindowService()
        window = window_service.get_by_id(db, window_id)
        
        if not window:
            raise HTTPException(status_code=404, detail="Order window not found")
        
        return success_response(
            data={
                "window_id": window.id,
                "group_id": window.group_id,
                "week_start_date": window.week_start_date.isoformat(),
                "open_date_time": window.open_date_time.isoformat(),
                "close_date_time": window.close_date_time.isoformat(),
                "status": window.status.value,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/windows/{window_id}/close", response_model=dict)
async def close_order_window(
    window_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Close order window"""
    try:
        window_service = OrderWindowService()
        window = window_service.close_order_window(db, window_id)
        
        return success_response(
            data={"window_id": window.id, "status": window.status.value},
            message="Order window closed",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Member Order Endpoints
@router.post("/", response_model=dict)
async def create_order(
    order_data: MemberOrderCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new order"""
    try:
        order_service = MemberOrderService()
        order = order_service.create_order(
            db,
            member_id=current_user.id,  # In real app, use member_id from request
            group_id=order_data.group_id,
            daily_meals=order_data.daily_meals,
            special_notes=order_data.special_notes,
        )
        
        return created_response(
            data={"order_id": order.id, "status": order.status.value},
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get order details"""
    try:
        order_service = MemberOrderService()
        order = order_service.get_by_id(db, order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return success_response(
            data={
                "order_id": order.id,
                "status": order.status.value,
                "daily_meals": order.daily_meals or {},
                "special_notes": order.special_notes,
                "submit_date": order.submit_date.isoformat() if order.submit_date else None,
                "created_at": order.created_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}", response_model=dict)
async def update_order(
    order_id: str,
    order_data: MemberOrderUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update order"""
    try:
        order_service = MemberOrderService()
        order = order_service.get_by_id(db, order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        update_data = order_data.dict(exclude_unset=True)
        order = order_service.update(db, order_id, **update_data)
        
        return success_response(
            data={"order_id": order.id},
            message="Order updated",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/submit", response_model=dict)
async def submit_order(
    order_id: str,
    window_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit order"""
    try:
        order_service = MemberOrderService()
        order = order_service.submit_order(db, order_id, window_id)
        
        return success_response(
            data={"order_id": order.id, "status": order.status.value},
            message="Order submitted",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/approve", response_model=dict)
async def approve_order(
    order_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Approve order"""
    try:
        order_service = MemberOrderService()
        order = order_service.approve_order(db, order_id)
        
        return success_response(
            data={"order_id": order.id, "status": order.status.value},
            message="Order approved",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/reject", response_model=dict)
async def reject_order(
    order_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Reject order"""
    try:
        order_service = MemberOrderService()
        order = order_service.reject_order(db, order_id)
        
        return success_response(
            data={"order_id": order.id, "status": order.status.value},
            message="Order rejected",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/lock", response_model=dict)
async def lock_order(
    order_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Lock order for delivery"""
    try:
        order_service = MemberOrderService()
        order = order_service.lock_order(db, order_id)
        
        return success_response(
            data={"order_id": order.id, "status": order.status.value},
            message="Order locked",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group/{group_id}", response_model=dict)
async def get_group_orders(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get group orders"""
    try:
        order_service = MemberOrderService()
        orders, total = order_service.get_group_orders(db, group_id, skip=skip, limit=limit)
        
        return success_response(
            data={
                "items": [
                    {
                        "order_id": o.id,
                        "member_id": o.member_id,
                        "status": o.status.value,
                        "week_start_date": o.week_start_date.isoformat(),
                        "submit_date": o.submit_date.isoformat() if o.submit_date else None,
                    }
                    for o in orders
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
