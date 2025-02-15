import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
import models
from blocklist import BLOCKLIST
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = (
    db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    # app.config['SECRET_KEY'] = secrets.SystemRandom().getrandbits(128)
    app.config['SECRET_KEY'] = '79132973107910942272314248226039329829'
    app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'your-jwt-secret')  # 可以从环境变量获取
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
        
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            {"message": "Token revoked", "error": "token_revoked"},
            401,
        )
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            {"message": "The token has expired.", "error": "token_expired"},
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == "74fbb6e1-9394-4ea8-9172-1652585e5944":
            return {"is_admin": True}
        return {"is_admin": False}
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "message": "token expired",
            "error": "token_expired"
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "message": "invalid token",
            "error": "invalid_token"
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            "message": "authorization required",
            "error": "authorization_required"
        }), 401

    with app.app_context():
        db.create_all()

    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)