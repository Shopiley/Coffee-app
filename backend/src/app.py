from http.client import HTTPException
import os
from urllib import response
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
def get_drinks():
    try:
        query = Drink.query.order_by(Drink.id).all()

        if len(query) == 0:
            abort(404)

        drinks = [drink.short() for drink in query]

        return jsonify({
            "success": True,
            "drinks": drinks
        }), 200
    except Exception as e:
        abort(405)
    finally:
        db.session.close()


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
    if payload:
        try:
            query = Drink.query.order_by(Drink.id).all()

            if len(query) == 0:
                abort(404)

            drinks = [drink.long() for drink in query]

            return jsonify({
                "success": True,
                "drinks": drinks
            }), 200
        except Exception as e:
            abort(405)
        finally:
            db.session.close()


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
    if payload:
        try:
            body = request.get_json()
            req_title = body.get("title", None)
            req_recipe = json.dumps(body.get("recipe", None))

            drink = Drink(title=req_title, recipe=req_recipe)

            if not drink:
                abort(400)

            drink.insert()

            return jsonify({
                "success": True,
                "drinks": drink.long()
            }), 200

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


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('PATCH:drinks')
def update_drinks(payload, id):
    if payload:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        body = request.get_json()
        updated_title = body.get("title", None)
        updated_recipe = body.get("recipe", None)

        if drink is None:
            abort(404)

        try:
            if updated_title and not updated_recipe:
                drink.title = updated_title
                drink.update()

            elif updated_recipe and not updated_title:
                drink.recipe = json.dumps(updated_recipe)
                drink.update()

            elif updated_title and updated_recipe:
                drink.title = updated_title
                drink.recipe = json.dumps(updated_recipe)
                drink.update()

            updated_drink = Drink.query.get(id)

            return jsonify({
                "success": True,
                "drinks": [updated_drink.long()]
            }), 200
        except Exception as e:
            abort(405)
        finally:
            db.session.close()


'''
@implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id
    is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('DELETE:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        drink.delete()

    except Exception as e:
        abort(405)

    return jsonify({
       "success": True,
       "delete": id
    }), 200


# Error Handling
# '''
# Example error handling for unprocessable entity
# '''


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


@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"}),
            422,
            )


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({
                "success": False,
                "error": 400,
                "message": "bad request"}),
            400,
            )


@app.errorhandler(405)
def not_found(error):
    return (jsonify({
                "success": False,
                "error": 405,
                "message": "method not allowed"}),
            405,
            )


'''
@implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return (jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"}),
            404,
            )


'''
@implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(error):
    response = error
    return jsonify({
        "success": False,
        "error": response.status_code,
        "message": response.error
    }), response.status_code


if __name__ == '__main__':
    app.run()
