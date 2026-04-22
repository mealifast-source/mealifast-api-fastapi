from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import MenuService
from app.schemas.catalog import MenuCreateSchema
from app.core.exceptions import MealiFastException
from app.api.dependencies import get_current_user, get_current_group_admin
from app.utils.response import success_response, created_response
from app.models import User
from app.core.constants import MenuStatus

router = APIRouter(prefix="/menus", tags=["menus"])


@router.post("/", response_model=dict)
async def create_menu(
    menu_data: MenuCreateSchema,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Create new menu"""
    try:
        menu_service = MenuService()
        menu = menu_service.create(
            db,
            name=menu_data.name,
            start_date=menu_data.start_date,
            end_date=menu_data.end_date,
            menu_items=menu_data.menu_items or {},
            status=MenuStatus.DRAFT,
        )
        
        return created_response(
            data={
                "menu_id": menu.id,
                "name": menu.name,
                "status": menu.status.value,
            },
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=dict)
async def list_menus(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List menus"""
    try:
        menu_service = MenuService()
        
        if status_filter and status_filter.upper() == MenuStatus.PUBLISHED.value:
            menus, total = menu_service.get_published_menus(db, skip, limit)
        elif status_filter and status_filter.upper() == MenuStatus.DRAFT.value:
            menus, total = menu_service.get_draft_menus(db, skip, limit)
        else:
            menus, total = menu_service.get_all(db, skip, limit)
        
        return success_response(
            data={
                "items": [
                    {
                        "menu_id": m.id,
                        "name": m.name,
                        "start_date": m.start_date.isoformat(),
                        "end_date": m.end_date.isoformat(),
                        "status": m.status.value,
                    }
                    for m in menus
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{menu_id}", response_model=dict)
async def get_menu(
    menu_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get menu details"""
    try:
        menu_service = MenuService()
        menu = menu_service.get_by_id(db, menu_id)
        
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")
        
        return success_response(
            data={
                "menu_id": menu.id,
                "name": menu.name,
                "start_date": menu.start_date.isoformat(),
                "end_date": menu.end_date.isoformat(),
                "status": menu.status.value,
                "menu_items": menu.menu_items or {},
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{menu_id}/publish", response_model=dict)
async def publish_menu(
    menu_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Publish menu"""
    try:
        menu_service = MenuService()
        menu = menu_service.publish_menu(db, menu_id)
        
        return success_response(
            data={"menu_id": menu.id, "status": menu.status.value},
            message="Menu published",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{menu_id}/archive", response_model=dict)
async def archive_menu(
    menu_id: str,
    current_user: User = Depends(get_current_group_admin),
    db: Session = Depends(get_db),
):
    """Archive menu"""
    try:
        menu_service = MenuService()
        menu = menu_service.archive_menu(db, menu_id)
        
        return success_response(
            data={"menu_id": menu.id, "status": menu.status.value},
            message="Menu archived",
        )
    except MealiFastException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
