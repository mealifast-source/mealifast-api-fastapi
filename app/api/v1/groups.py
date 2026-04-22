from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import GroupService, GroupMemberService
from app.schemas.group import (
    GroupCreateSchema,
    GroupResponseSchema,
    MemberCreateSchema,
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

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=dict)
async def create_group(
    group_data: GroupCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new group"""
    try:
        if current_user.role not in (UserRole.GROUP_ADMIN, UserRole.PLATFORM_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Group admin access required",
            )
        
        group_service = GroupService()
        group = group_service.create_group(
            db,
            group_name=group_data.group_name,
            company_name=group_data.company_name,
            admin_id=current_user.id,
            subscription_plan_id=group_data.subscription_plan_id,
        )
        
        return created_response(
            data={
                "group_id": group.id,
                "group_name": group.group_name,
                "status": group.status.value,
            },
            message="Group created successfully",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}", response_model=dict)
async def get_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get group details"""
    try:
        group_service = GroupService()
        group = group_service.get_by_id(db, group_id)
        
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        return success_response(
            data={
                "group_id": group.id,
                "group_name": group.group_name,
                "company_name": group.company_name,
                "status": group.status.value,
                "created_at": group.created_at.isoformat(),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{group_id}/members/invite", response_model=dict)
async def invite_member(
    group_id: str,
    member_data: MemberCreateSchema,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Invite member to group"""
    try:
        member_service = GroupMemberService()
        
        # Create invitation
        member = member_service.invite_member(
            db,
            group_id=group_id,
            email=member_data.email,
        )
        
        return created_response(
            data={
                "member_id": member.id,
                "status": member.status.value,
            },
            message="Member invitation sent",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{group_id}/members", response_model=dict)
async def list_group_members(
    group_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List group members"""
    try:
        member_service = GroupMemberService()
        members, total = member_service.get_group_members(db, group_id, skip, limit)
        
        return success_response(
            data={
                "items": [
                    {
                        "member_id": m.id,
                        "user_email": m.user.email,
                        "status": m.status.value,
                        "role": m.member_role.value,
                    }
                    for m in members
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{group_id}/approve", response_model=dict)
async def approve_group(
    group_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Approve pending group"""
    try:
        group_service = GroupService()
        group = group_service.approve_group(db, group_id)
        
        return success_response(
            data={"group_id": group.id, "status": group.status.value},
            message="Group approved",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
