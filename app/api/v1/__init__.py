from app.api.v1.auth import router as auth_router
from app.api.v1.groups import router as groups_router
from app.api.v1.meals import router as meals_router
from app.api.v1.menus import router as menus_router
from app.api.v1.orders import router as orders_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.delivery import router as delivery_router
from app.api.v1.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "groups_router",
    "meals_router",
    "menus_router",
    "orders_router",
    "invoices_router",
    "delivery_router",
    "dashboard_router",
]
