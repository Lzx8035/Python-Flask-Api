from db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)

    description = db.Column(db.String(255))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    
    # 多对一关系
    store_id = db.Column(UUID(as_uuid=True), db.ForeignKey("stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="items")  # 反向引用
    
    # 多对多关系
    tags = db.relationship("TagModel", secondary="items_tags", back_populates="items")