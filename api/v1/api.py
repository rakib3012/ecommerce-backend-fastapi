from fastapi import APIRouter

from api.v1.endpoints import (
    cart_items,
    carts,
    categories,
    orders,
    product_attributes,
    product_images,
    products,
    users,
    wishlists,
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
router.include_router(carts.router, prefix="/carts", tags=["Carts"])
router.include_router(cart_items.router, prefix="/cart-items", tags=["Cart Items"])
router.include_router(wishlists.router, prefix="/wishlists", tags=["Wishlists"])
router.include_router(orders.router, prefix="/orders", tags=["Orders"])
