import os
import uuid
import requests
from flask import request, current_app
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema, UserRegisterSchema
from tasks import send_user_registration_email

blp = Blueprint("Users", "users", description="Operations on users", url_prefix="/users") 

@blp.route("/")
class AllUserTEST(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema(many=True))
    def get(self):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        return UserModel.query.all()

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"],
            )
        ).first():
            abort(409, message="A user with that username or email already exists.")
        user = UserModel(
            username=user_data["username"],
            email=user_data["email"]
        )
        user.set_password(user_data["password"])
        db.session.add(user)
        db.session.commit()
        current_app.queue.enqueue(send_user_registration_email, user.email, user.username)
        return {"message": "User created successfully.", "user": str(user.id)}, 201
    

# For Test: DELETE ALL CUSTOMER
# docker exec -it day3-flask-app-1 sh
# flask shell
# from models import UserModel
# from db import db

# db.session.query(UserModel).delete()
# db.session.commit()
    
@blp.route("/user/<uuid:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @jwt_required()
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
    

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()
        if user and user.check_password(user_data["password"]):
            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(identity = user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"] 
        BLOCKLIST.add(jti)  
        return {"message": "Successfully logged out"}
    
@blp.route("/refresh")
class RefreshToken(MethodView):
    @jwt_required(refresh = True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}