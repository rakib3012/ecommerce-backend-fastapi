from fastapi import APIRouter

from api.v1.endpoints import (
    categories,
    product_attributes,
    product_images,
    products,
    users,
)

router = APIRouter()

router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(categories.router, prefix="/categories", tags=["Categories"])
router.include_router(products.router, prefix="/products", tags=["Products"])
router.include_router(
    product_images.router,
    prefix="/product-images",
    tags=["Product Images"],
)
router.include_router(
    product_attributes.router,
    prefix="/product-attributes",
    tags=["Product Attributes"],
)
