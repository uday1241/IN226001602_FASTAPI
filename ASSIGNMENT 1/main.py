from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Models
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True

# Initial products list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Helper function
def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

# GET all products
@app.get('/products')
def get_products():
    return {'products': products, 'total': len(products)}

# GET single product
@app.get('/products/{product_id}')
def get_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    return product

# POST - Add new product (Q1)
@app.post('/products', status_code=status.HTTP_201_CREATED)
def add_product(new_product: NewProduct, response: Response):
    # Check for duplicate name
    for p in products:
        if p['name'].lower() == new_product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': f"Product '{new_product.name}' already exists"}
    
    # Auto-generate ID
    next_id = max(p['id'] for p in products) + 1
    product_dict = new_product.dict()
    product_dict['id'] = next_id
    products.append(product_dict)
    
    return {'message': 'Product added', 'product': product_dict}

# PUT - Update product (Q2)
@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    price: Optional[int] = None,
    in_stock: Optional[bool] = None,
    response: Response = None
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    
    if price is not None:
        product['price'] = price
    if in_stock is not None:
        product['in_stock'] = in_stock
    
    return {'message': 'Product updated', 'product': product}

# DELETE - Remove product (Q3)
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}
