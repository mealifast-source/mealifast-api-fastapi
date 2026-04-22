from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import MealService, MenuService
from app.schemas.catalog import (
    MealCreateSchema,
    MealUpdateSchema,
    MealResponseSchema,
    MenuCreateSchema,
)
from app.core.exceptions import MealiFastException
from app.api.dependencies import get_current_user, get_current_admin_user
from app.utils.response import success_response, created_response
from app.models import User

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/", response_model=dict)
async def create_meal(
    meal_data: MealCreateSchema,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create new meal"""
    try:
        meal_service = MealService()
        meal = meal_service.create(
            db,
            name=meal_data.name,
            description=meal_data.description,
            photo_url=meal_data.photo_url,
            category=meal_data.category,
            cost_price=meal_data.cost_price,
            dietary_tags=meal_data.dietary_tags,
            active=True,
        )
        
        return created_response(
            data={
                "meal_id": meal.id,
                "name": meal.name,
                "category": meal.category.value,
                "cost_price": meal.cost_price,
            },
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_meals(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all active meals"""
    try:
        meal_service = MealService()
        
        if category:
            meals, total = meal_service.get_by_category(db, category, skip, limit)
        else:
            meals, total = meal_service.get_active_meals(db, skip, limit)
        
        return success_response(
            data={
                "items": [
                    {
                        "meal_id": m.id,
                        "name": m.name,
                        "category": m.category.value,
                        "cost_price": m.cost_price,
                        "dietary_tags": m.dietary_tags or [],
                    }
                    for m in meals
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meal_id}", response_model=dict)
async def get_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get meal details"""
    try:
        meal_service = MealService()
        meal = meal_service.get_by_id(db, meal_id)
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        return success_response(
            data={
                "meal_id": meal.id,
                "name": meal.name,
                "description": meal.description,
                "category": meal.category.value,
                "cost_price": meal.cost_price,
                "dietary_tags": meal.dietary_tags or [],
                "active": meal.active,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{meal_id}", response_model=dict)
async def update_meal(
    meal_id: str,
    meal_data: MealUpdateSchema,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update meal"""
    try:
        meal_service = MealService()
        meal = meal_service.get_by_id(db, meal_id)
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        update_data = meal_data.dict(exclude_unset=True)
        meal = meal_service.update(db, meal_id, **update_data)
        
        return success_response(
            data={"meal_id": meal.id},
            message="Meal updated",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{meal_id}", response_model=dict)
async def delete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete meal"""
    try:
        meal_service = MealService()
        meal = meal_service.get_by_id(db, meal_id)
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        meal_service.deactivate_meal(db, meal_id)
        
        return success_response(message="Meal deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
