from itertools import count, product
from math import prod
import os
from flask import Flask, request, jsonify, abort
from models import setup_db, Brand, ProductCategory, Product, Customer, Order
from flask_cors import CORS
from auth import requires_auth

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def index():
        return "Hello, world!"
    

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

        if not name or not price or not brand:
            abort(400)

        product = Product(name=name, price=price, brand=brand)
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



    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)