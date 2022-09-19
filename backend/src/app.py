from http.client import HTTPException
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink, db
# from .auth.auth import AuthError, requires_auth
from auth.auth import *

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
@requires_auth('GET:drinks')
def get_drinks(payload):
    print(payload)
    query = Drink.query.order_by(Drink.id).all()

    if len(query) == 0:
        abort(404)

    drinks = [drink.short() for drink in query]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('GET:drinks-detail')
def get_drinks_detail(payload):
    print(payload)
    query = Drink.query.order_by(Drink.id).all()

    if len(query) == 0:
        abort(404)

    drinks = [drink.long() for drink in query]

    return jsonify({
        "success": True,
        "drinks": drinks
    })


'''
@implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where 
    drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('POST:drinks')
def create_drinks(payload):
    try:
        print(payload)
        body = request.get_json()
        req_title = body.get("title", None)
        print(req_title)
        req_recipe = json.dumps(body.get("recipe", None))
        print(req_recipe)
        drink = Drink(title=req_title, recipe=req_recipe)

        if not drink:
            abort(400)

        drink.insert()

        return jsonify({
            "success": True,
            "drinks": drink.long()
        })

    except Exception as e:
        if isinstance(e, HTTPException):
            abort(e.code)
        db.session.rollback()
        abort(422)
 
    finally:
        db.session.close()



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where 
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int: id>', methods=['PATCH'])
@requires_auth('PATCH:drinks')
def update_drinks(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    body = request.get_json()
    drink.title = body.get("title", None)
    drink.recipe = json.dumps(body.get("recipe", None))

    if drink is None:
        abort(404)

    drink.update()

    return jsonify({
        "success": True,
        "drinks": drink.long()
    })

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id 
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5050')
