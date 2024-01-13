#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(  bakeries,   200  )

@app.route('/bakeries/<int:id>')
def bakery_by_id(id):

    bakery = Bakery.query.filter_by(id=id).first()
    bakery_serialized = bakery.to_dict()
    return make_response ( bakery_serialized, 200  )

@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    return make_response( baked_goods_by_price_serialized, 200  )
   

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()
    return make_response( most_expensive_serialized,   200  )



@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form

    name = data.get('name')
    price = data.get('price')
    bakery_id = data.get('bakery_id')

    # Validate the required fields
    if not (name and price and bakery_id):
        return make_response(jsonify({"error": "Incomplete data. Please provide name, price, and bakery_id."}), 400)

    # Create a new BakedGood instance
    new_baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)

    # Add to the database
    db.session.add(new_baked_good)
    db.session.commit()

    # Return the created baked good's data as JSON
    return make_response(jsonify(new_baked_good.to_dict()), 201)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    # Retrieve the bakery from the database
    bakery = Bakery.query.get(id)

    if not bakery:
        return make_response(jsonify({"error": f"Bakery with ID {id} not found."}), 404)

    # Extract relevant data from the form
    data = request.form
    new_name = data.get('name')

    # Update the bakery's name if provided
    if new_name:
        bakery.name = new_name

    # Commit changes to the database
    db.session.commit()

    # Return the updated bakery's data as JSON
    return make_response(jsonify(bakery.to_dict()), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    # Retrieve the baked good from the database
    baked_good = BakedGood.query.get(id)

    if not baked_good:
        return make_response(jsonify({"error": f"Baked Good with ID {id} not found."}), 404)

    # Delete the baked good from the database
    db.session.delete(baked_good)
    db.session.commit()

    # Return a JSON message confirming the deletion
    return make_response(jsonify({"message": f"Baked Good with ID {id} deleted successfully."}), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)