import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from schemas import ItemSchema, ItemUpdateSchema
from models import ItemModel

blp = Blueprint("Items", __name__, description="Operations on items")

@blp.route("/item/<uuid:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data.get("price", item.price)
            item.name = item_data.get("name", item.name)
        else:
            item = ItemModel(id=item_id, **item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the item.") 
        return item
    
    @jwt_required()
    @blp.response(204) 
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted"}
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the item.")


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @jwt_required(fresh = True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError: # 处理唯一性冲突/Handle uniqueness conflicts
            abort(400, message="A item with that name already exists.")
        except SQLAlchemyError: # 处理一般数据库错误/Handle general DB errors
            abort(500, message="An error occurred while inserting the item.")
        return item