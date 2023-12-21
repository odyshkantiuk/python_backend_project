from flask import request, jsonify
from marshmallow import ValidationError
from .. import app, db, schemas, models
from ..utils import add, delete


@app.get('/users')
def get_users():
    users = [{"id": user.id, "name": user.name} for user in db.session.query(models.User).all()]
    return jsonify(users)


@app.get('/user')
def get_user():
    user_id = request.args.get('userID')
    try:
        user = db.session.query(models.User).filter(models.User.id == user_id).first()
        return jsonify({"id": user.id, "name": user.name})
    except AttributeError:
        return "AttributeError, 404"


@app.post('/user')
def add_user():
    user_data = request.get_json()
    try:
        schemas.UserSchema().load({"name": user_data["name"]})
        if db.session.query(models.User).filter(models.User.name == user_data["name"]).first() is None:
            user = models.User(user_data["name"])
            add(user)
            schemas.AccountSchema().load({"user_id": user.id, "money": user_data["money"]})
            account = models.Account(user.id, user_data["money"])
            add(account)
            return jsonify({"id": user.id, "name": user.name, "money": account.money})
        else:
            return "UserExist, 404"
    except ValidationError as error:
        return error.messages


@app.delete('/user')
def delete_user():
    user_id = request.args.get('userID')
    deleted_user = delete(models.User, user_id)
    if deleted_user:
        return jsonify(deleted_user)
    else:
        return "AttributeError, 404"