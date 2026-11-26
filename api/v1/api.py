from fastapi import APIRouter

from api.v1.endpoints import categories, products, users

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(products.router, prefix="/products", tags=["Products"])
