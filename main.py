from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI(
    title="QuickBite Food Delivery",
    description="Complete FastAPI Food Delivery System with 20 Endpoints",
    version="1.0.0"
)

# Data
menu = [
    {"id": 1, "name": "Margherita Pizza", "price": 299, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Chicken Burger", "price": 199, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Coke", "price": 50, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Chocolate Cake", "price": 150, "category": "Dessert", "is_available": True},
    {"id": 5, "name": "Pepperoni Pizza", "price": 399, "category": "Pizza", "is_available": False},
    {"id": 6, "name": "Veggie Burger", "price": 179, "category": "Burger", "is_available": True}
]
orders = []
order_counter = [1]
cart = []

# Pydantic Models
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type: str = "delivery"

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# Helper Functions
def find_menu_item(item_id: int):
    return next((item for item in menu if item["id"] == item_id), None)

def calculate_bill(price: int, quantity: int, order_type: str = "delivery") -> int:
    total = price * quantity
    if order_type == "delivery":
        total += 30
    return total

def filter_menu_logic(category: Optional[str], max_price: Optional[int], is_available: Optional[bool]):
    filtered = menu.copy()
    if category is not None:
        filtered = [item for item in filtered if item["category"] == category]
    if max_price is not None:
        filtered = [item for item in filtered if item["price"] <= max_price]
    if is_available is not None:
        filtered = [item for item in filtered if item["is_available"] == is_available]
    return filtered

# Q1: Welcome Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to QuickBite Food Delivery", "status": "running"}

# Q5: Menu Summary
@app.get("/menu/summary")
async def menu_summary():
    available = sum(1 for item in menu if item["is_available"])
    return {
        "total_items": len(menu),
        "available": available,
        "unavailable": len(menu) - available,
        "categories": list(set(item["category"] for item in menu))
    }

# Q10: Filter Menu
@app.get("/menu/filter")
async def filter_menu(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    filtered = filter_menu_logic(category, max_price, is_available)
    return {"items": filtered, "count": len(filtered)}

# Q16: Search Menu
@app.get("/menu/search")
async def search_menu(keyword: str = Query(..., min_length=1)):
    keyword_lower = keyword.lower()
    results = [item for item in menu if keyword_lower in item["name"].lower() or keyword_lower in item["category"].lower()]
    return {"items": results, "total_found": len(results)}

# Q17: Sort Menu
@app.get("/menu/sort")
async def sort_menu(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order")
    sorted_menu = sorted(menu, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"sorted_by": sort_by, "order": order, "items": sorted_menu}

# Q18: Paginate Menu
@app.get("/menu/page")
async def paginate_menu(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    paginated = menu[start:start + limit]
    total_pages = math.ceil(len(menu) / limit)
    return {"page": page, "limit": limit, "total": len(menu), "total_pages": total_pages, "items": paginated}

# Q20: Browse Menu (Combined)
@app.get("/menu/browse")
async def browse_menu(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=10)
):
    filtered = menu.copy()
    if keyword:
        filtered = [item for item in filtered if keyword.lower() in item["name"].lower()]
    sorted_items = sorted(filtered, key=lambda x: x[sort_by], reverse=(order == "desc"))
    start = (page - 1) * limit
    paginated = sorted_items[start:start + limit]
    total_pages = math.ceil(len(sorted_items) / limit)
    return {"page": page, "limit": limit, "total": len(sorted_items), "total_pages": total_pages, "items": paginated}

# Q2: Get All Menu Items
@app.get("/menu")
async def get_menu():
    return {"items": menu, "total": len(menu)}

# Q3: Get Menu Item by ID
@app.get("/menu/{item_id}")
async def get_menu_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Q4: Get All Orders
@app.get("/orders")
async def get_orders():
    return {"orders": orders, "total_orders": len(orders)}

# Q19: Search Orders
@app.get("/orders/search")
async def search_orders(customer_name: str = Query(..., min_length=1)):
    results = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"orders": results, "total_found": len(results)}

# Q8: Create Order
@app.post("/orders")
async def create_order(order_req: OrderRequest):
    item = find_menu_item(order_req.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item unavailable")
    total_price = calculate_bill(item["price"], order_req.quantity, order_req.order_type)
    new_order = {
        "order_id": order_counter[0],
        "customer_name": order_req.customer_name,
        "item_id": order_req.item_id,
        "item_name": item["name"],
        "quantity": order_req.quantity,
        "delivery_address": order_req.delivery_address,
        "order_type": order_req.order_type,
        "total_price": total_price
    }
    orders.append(new_order)
    order_counter[0] += 1
    return new_order

# Q14: Add to Cart
@app.post("/cart/add")
async def add_to_cart(item_id: int = Query(..., gt=0), quantity: int = Query(1, gt=0)):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item unavailable")
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart_item["quantity"] += quantity
            cart_item["subtotal"] = item["price"] * cart_item["quantity"]
            return cart_item
    cart.append({"item_id": item_id, "name": item["name"], "price": item["price"], "quantity": quantity, "subtotal": item["price"] * quantity})
    return cart[-1]

# Q14: Get Cart
@app.get("/cart")
async def get_cart():
    grand_total = sum(item["subtotal"] for item in cart)
    return {"cart_items": cart, "grand_total": grand_total}

# Q15: Remove from Cart
@app.delete("/cart/{item_id}")
async def remove_from_cart(item_id: int):
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart.remove(cart_item)
            return {"message": "Item removed", "removed_item": cart_item}
    raise HTTPException(status_code=404, detail="Item not in cart")

# Q15: Checkout
@app.post("/cart/checkout")
async def checkout_cart(checkout_req: CheckoutRequest):
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    placed_orders = []
    grand_total = 0
    for cart_item in cart:
        total_price = cart_item["subtotal"] + 30
        new_order = {
            "order_id": order_counter[0],
            "customer_name": checkout_req.customer_name,
            "item_name": cart_item["name"],
            "quantity": cart_item["quantity"],
            "delivery_address": checkout_req.delivery_address,
            "total_price": total_price
        }
        orders.append(new_order)
        placed_orders.append(new_order)
        grand_total += total_price
        order_counter[0] += 1
    cart.clear()
    return {"message": "Checkout successful", "orders": placed_orders, "grand_total": grand_total}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)