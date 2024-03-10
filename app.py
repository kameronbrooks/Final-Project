
from math import prod
import os
from venv import create
from flask import Flask, request, jsonify, abort, render_template
from models import setup_db, Brand, ProductCategory, Product, Customer, Order, ProductReview
from flask_cors import CORS
from auth import requires_auth


def create_app(test_config=None):

    app = Flask(__name__, static_folder='./static')
    setup_db(app)
    CORS(app)

    @app.route('/')
    def index():
        categories = [x.format() for x in ProductCategory.get_all(1, 10)]
        # append a category for all products
        categories.insert(0, {
            'id': -1,
            'name': 'All Products',
            'description': 'All products in the store'
        })

        return render_template('index.html', categories=categories)
    

    @app.route('/products')
    #@requires_auth('get:products')
    def get_products():
        # get all products using pagination
        page = request.args.get('page', 1, type=int)
        items_per_page = 10

        products = Product.get_all(page, items_per_page)

        # get count of all products
        total_products = Product.count_total()

        return jsonify({
            'success': True,
            'products': [product.format() for product in products],
            'total_products': total_products
        })
    
    @app.route('/products', methods=['POST'])
    #@requires_auth('post:products')
    def create_product():
        body = request.get_json()

        name = body.get('name', None)
        price = body.get('price', None)
        brand = body.get('brand', None)
        description = body.get('description', None)
        product_category_id = body.get('product_category_id', None)

        if not name or not price or not brand:
            abort(400)

        product = Product(name=name, price=price, brand=brand, description=description, product_category=product_category_id)
        Product.insert(product)

        return jsonify({
            'success': True,
            'product': product.format()
        })
    


    @app.route('/products/<int:product_id>', methods=['PATCH'])
    #@requires_auth('patch:products')
    def update_product(product_id):
        product = Product.get_one_or_none(product_id)

        if product is None:
            abort(404)

        body = request.get_json()

        name = body.get('name', product.name)
        price = body.get('price', product.price)
        brand = body.get('brand', product.brand)

        product.name = name
        product.price = price
        product.brand = brand

        product.update()

        return jsonify({
            'success': True,
            'product': product.format()
        })
    
    @app.route('/products/<int:product_id>', methods=['DELETE'])
    #@requires_auth('delete:products')
    def delete_product(product_id):
        product = Product.get_one_or_none(product_id)

        if product is None:
            abort(404)

        Product.delete(product)

        return jsonify({
            'success': True,
            'product_id': product_id
        })
    
    @app.route('/products/<int:product_id>/product-reviews', methods=['GET'])
    #@requires_auth('get:product-reviews')
    def get_product_reviews():
        product_id = request.args.get('product_id', None)
        product = Product.get_one_or_none(product_id)

        if product is None:
            abort(404)

        reviews = product.reviews

        return jsonify({
            'success': True,
            'reviews': [review.format() for review in reviews]
        })
    
    @app.route('/products/<int:product_id>/product-reviews', methods=['POST'])
    #@requires_auth('post:product-reviews')
    def create_product_review():
        customer_id = request.args.get('customer_id', None)
        product_id = request.args.get('product_id', None)

        product = Product.get_one_or_none(product_id)

        if product is None:
            abort(404)

        body = request.get_json()

        rating = body.get('rating', None)
        review = body.get('review', None)

        if not rating or not review:
            abort(400)

        product_review = ProductReview(rating=rating, review=review, product_id=product_id, customer_id=customer_id)
        ProductReview.insert(product_review)

        return jsonify({
            'success': True,
            'product_review': product_review.format()
        })
    
    

    @app.route('/brands')
    #@requires_auth('get:brands')
    def get_brands():
        page = request.args.get('page', 1, type=int)
        items_per_page = 10
        brands = Brand.get_all(page, items_per_page)
        total_count = Brand.count_total()
        return jsonify({
            'success': True,
            'brands': [brand.format() for brand in brands],
            'total_brands': total_count
        })
    
    @app.route('/brands', methods=['POST'])
    #@requires_auth('post:brands')
    def create_brand():
        body = request.get_json()

        name = body.get('name', None)
        catchphrase = body.get('catchphrase', None)

        if not name:
            abort(400)

        brand = Brand(name=name, catchphrase=catchphrase)
        Brand.insert(brand)

        return jsonify({
            'success': True,
            'brand': brand.format()
        })
    
    @app.route('/brands/<int:brand_id>', methods=['PATCH'])
    #@requires_auth('patch:brands')
    def update_brand(brand_id):
        brand = Brand.get_one_or_none(brand_id)

        if brand is None:
            abort(404)

        body = request.get_json()

        name = body.get('name', brand.name)
        catchphrase = body.get('catchphrase', brand.catchphrase)

        brand.name = name
        brand.catchphrase = catchphrase

        brand.update()

        return jsonify({
            'success': True,
            'brand': brand.format()
        })
    
    @app.route('/brands/<int:brand_id>', methods=['DELETE'])
    #@requires_auth('delete:brands')
    def delete_brand(brand_id):
        brand = Brand.get_one_or_none(brand_id)

        if brand is None:
            abort(404)

        Brand.delete(brand)

        return jsonify({
            'success': True,
            'brand_id': brand_id
        })
    
    @app.route('/product-categories')
    #@requires_auth('get:product-categories')
    def get_product_categories():
        page = request.args.get('page', 1, type=int)
        items_per_page = 10
        categories = ProductCategory.get_all(page, items_per_page)
        total_count = ProductCategory.count_total()
        return jsonify({
            'success': True,
            'product_categories': [category.format() for category in categories],
            'total_product_categories': total_count
        })
    
    @app.route('/product-categories', methods=['POST'])
    #@requires_auth('post:product-categories')
    def create_product_category():
        body = request.get_json()

        name = body.get('name', None)
        description = body.get('description', None)

        if not name:
            abort(400)

        category = ProductCategory(name=name, description=description)
        ProductCategory.insert(category)

        return jsonify({
            'success': True,
            'product_category': category.format()
        })
    
    @app.route('/product-categories/<int:category_id>', methods=['PATCH'])
    #@requires_auth('patch:product-categories')
    def update_product_category(category_id):
        #category_id = request.args.get('category_id', None)
        category = ProductCategory.get_one_or_none(category_id)

        if category is None:
            abort(404)

        body = request.get_json()

        name = body.get('name', category.name)
        description = body.get('description', category.description)

        category.name = name
        category.description = description

        ProductCategory.update(category)

        return jsonify({
            'success': True,
            'product_category': category.format()
        })
    
    @app.route('/product-categories/<int:category_id>', methods=['DELETE'])
    #@requires_auth('delete:product-categories')
    def delete_product_category(category_id):
        category = ProductCategory.get_one_or_none(category_id)

        if category is None:
            abort(404)

        ProductCategory.delete(category)

        return jsonify({
            'success': True,
            'category_id': category_id
        })
    
    @app.route('/customers')
    #@requires_auth('get:customers')
    def get_customers():
        page = request.args.get('page', 1, type=int)
        items_per_page = 10
        customers = Customer.get_all(page, items_per_page)
        total_count = Customer.count_total()
        return jsonify({
            'success': True,
            'customers': [customer.format() for customer in customers],
            'total_customers': total_count
        })
    
    @app.route('/customers', methods=['POST'])
    #@requires_auth('post:customers')
    def create_customer():
        body = request.get_json()

        name = body.get('name', None)
        email = body.get('email', None)
        address = body.get('address', None)

        if not name or not email:
            abort(400)

        customer = Customer(name=name, email=email, address=address)
        Customer.insert(customer)

        return jsonify({
            'success': True,
            'customer': customer.format()
        })
    
    @app.route('/customers/<int:customer_id>', methods=['PATCH'])
    #@requires_auth('patch:customers')
    def update_customer(customer_id):
        customer = Customer.get_one_or_none(customer_id)

        if customer is None:
            abort(404)

        body = request.get_json()

        name = body.get('name', customer.name)
        email = body.get('email', customer.email)
        address = body.get('address', customer.address)

        customer.name = name
        customer.email = email
        customer.address = address

        Customer.update(customer)

        return jsonify({
            'success': True,
            'customer': customer.format()
        })
    
    @app.route('/customers/<int:customer_id>', methods=['DELETE'])
    #@requires_auth('delete:customers')
    def delete_customer(customer_id):
        customer = Customer.get_one_or_none(customer_id)

        if customer is None:
            abort(404)

        Customer.delete(customer)

        return jsonify({
            'success': True,
            'customer_id': customer_id
        })
    
    @app.route('/orders')
    #@requires_auth('get:orders')
    def get_orders():
        page = request.args.get('page', 1, type=int)
        items_per_page = 10
        orders = Order.get_all(page, items_per_page)
        total_count = Order.count_total()
        return jsonify({
            'success': True,
            'orders': [order.format() for order in orders],
            'total_orders': total_count
        })
    
    @app.route('/orders/', methods=['POST'])
    #@requires_auth('post:orders')
    def create_order():
        body = request.get_json()

        customer_id = body.get('customer_id', None)
        items_json = body.get('items', None)
        cost = body.get('cost', None)

        if not customer_id or not items_json or not cost:
            abort(400)

        order = Order(customer_id=customer_id, items_json=items_json, cost=cost)
        Order.insert(order)

        return jsonify({
            'success': True,
            'order': order.format()
        })
    
    @app.route('/orders/<int:order_id>', methods=['PATCH'])
    #@requires_auth('patch:orders')
    def update_order(order_id):
        order = Order.get_one_or_none(order_id)

        if order is None:
            abort(404)

        body = request.get_json()

        customer_id = body.get('customer_id', order.customer_id)
        items_json = body.get('items', order.items_json)
        cost = body.get('cost', order.cost)

        order.customer_id = customer_id
        order.items_json = items_json
        order.cost = cost

        order.update()

        return jsonify({
            'success': True,
            'order': order.format()
        })
    
    @app.route('/orders/<int:order_id>', methods=['DELETE'])
    #@requires_auth('delete:orders')
    def delete_order(order_id):
        order = Order.get_one_or_none(order_id)

        if order is None:
            abort(404)

        Order.delete(order)

        return jsonify({
            'success': True,
            'order_id': order_id
        })
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable entity"
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
        }), 500
    




    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)