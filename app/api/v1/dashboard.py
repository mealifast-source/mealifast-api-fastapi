from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.services import (
    DashboardService,
    MealRatingService,
)
from app.schemas.dashboard import (
    MealRatingCreateSchema,
    PlatformDashboardSchema,
    GroupDashboardSchema,
)
from app.core.exceptions import MealiFastException
from app.api.dependencies import (
    get_current_user,
    get_current_admin_user,
    get_current_group_admin,
)
from app.utils.response import success_response, created_response
from app.models import User
from app.core.constants import UserRole

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/platform", response_model=dict)
async def get_platform_dashboard(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get platform dashboard (admin only)"""
    try:
        dashboard_service = DashboardService()
        
        dashboard_data = dashboard_service.get_platform_dashboard(db)
        
        return success_response(
            data={
                "total_users": dashboard_data.get("total_users", 0),
                "total_groups": dashboard_data.get("total_groups", 0),
                "active_subscriptions": dashboard_data.get("active_subscriptions", 0),
                "total_orders": dashboard_data.get("total_orders", 0),
                "total_revenue": dashboard_data.get("total_revenue", 0.0),
                "recent_transactions": dashboard_data.get("recent_transactions", []),
            },
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group/{group_id}", response_model=dict)
async def get_group_dashboard(
    group_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Get group dashboard"""
    try:
        dashboard_service = DashboardService()
        
        dashboard_data = dashboard_service.get_group_dashboard(db, group_id)
        
        return success_response(
            data={
                "group_name": dashboard_data.get("group_name"),
                "active_members": dashboard_data.get("active_members", 0),
                "total_members": dashboard_data.get("total_members", 0),
                "orders_this_week": dashboard_data.get("orders_this_week", 0),
                "pending_orders": dashboard_data.get("pending_orders", 0),
                "upcoming_deliveries": dashboard_data.get("upcoming_deliveries", 0),
                "invoice_summary": dashboard_data.get("invoice_summary", {}),
            },
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/member/{member_id}", response_model=dict)
async def get_member_dashboard(
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get member dashboard"""
    try:
        dashboard_service = DashboardService()
        
        dashboard_data = dashboard_service.get_member_dashboard(db, member_id)
        
        return success_response(
            data={
                "member_name": dashboard_data.get("member_name"),
                "groups": dashboard_data.get("groups", []),
                "active_orders": dashboard_data.get("active_orders", 0),
                "recent_orders": dashboard_data.get("recent_orders", []),
                "invoices_due": dashboard_data.get("invoices_due", []),
                "dietary_preferences": dashboard_data.get("dietary_preferences", []),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=dict)
async def get_current_user_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user summary dashboard"""
    try:
        if current_user.role == UserRole.PLATFORM_ADMIN:
            dashboard_service = DashboardService()
            dashboard_data = dashboard_service.get_platform_dashboard(db)
            
            return success_response(
                data={
                    "role": "admin",
                    "total_users": dashboard_data.get("total_users", 0),
                    "total_groups": dashboard_data.get("total_groups", 0),
                    "total_revenue": dashboard_data.get("total_revenue", 0.0),
                },
            )
        else:
            # Get user's groups and summary
            from app.models import GroupMember
            
            memberships = db.query(GroupMember).filter(
                GroupMember.user_id == current_user.id
            ).all()
            
            groups = [m.group_id for m in memberships]
            
            return success_response(
                data={
                    "role": current_user.role.value,
                    "user_id": current_user.id,
                    "full_name": current_user.full_name,
                    "groups_count": len(groups),
                    "groups": groups,
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ratings Endpoints
@router.post("/ratings/", response_model=dict)
async def create_meal_rating(
    rating_data: MealRatingCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create meal rating"""
    try:
        rating_service = MealRatingService()
        
        # Validate rating is between 1-5
        if rating_data.rating < 1 or rating_data.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        rating = rating_service.create_rating(
            db,
            meal_id=rating_data.meal_id,
            member_id=current_user.id,
            rating=rating_data.rating,
            review=rating_data.review,
        )
        
        return created_response(
            data={
                "rating_id": rating.id,
                "meal_id": rating.meal_id,
                "rating": rating.rating,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ratings/meal/{meal_id}", response_model=dict)
async def get_meal_ratings(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ratings for meal"""
    try:
        from app.models import MealRating
        
        ratings = db.query(MealRating).filter(
            MealRating.meal_id == meal_id
        ).order_by(MealRating.created_at.desc()).all()
        
        if not ratings:
            return success_response(
                data={
                    "meal_id": meal_id,
                    "ratings": [],
                    "average_rating": 0.0,
                    "total_ratings": 0,
                },
            )
        
        total_rating = sum(r.rating for r in ratings)
        average_rating = total_rating / len(ratings) if ratings else 0
        
        return success_response(
            data={
                "meal_id": meal_id,
                "ratings": [
                    {
                        "rating_id": r.id,
                        "rating": r.rating,
                        "review": r.review,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in ratings
                ],
                "average_rating": round(average_rating, 2),
                "total_ratings": len(ratings),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ratings/member/{member_id}", response_model=dict)
async def get_member_ratings(
    member_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get ratings created by member"""
    try:
        from app.models import MealRating
        
        ratings = db.query(MealRating).filter(
            MealRating.member_id == member_id
        ).order_by(MealRating.created_at.desc()).all()
        
        return success_response(
            data={
                "member_id": member_id,
                "total_ratings": len(ratings),
                "ratings": [
                    {
                        "rating_id": r.id,
                        "meal_id": r.meal_id,
                        "rating": r.rating,
                        "review": r.review,
                        "created_at": r.created_at.isoformat(),
                    }
                    for r in ratings
                ],
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
