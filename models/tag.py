from db import db
from sqlalchemy.dialects.postgresql import UUID # type: ignore
import uuid

class TagModel(db.Model):
    __tablename__ = "tags"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True, nullable=False)
    store_id = db.Column(UUID(as_uuid=True), db.ForeignKey("stores.id"), nullable=False)
    
    store = db.relationship("StoreModel", back_populates="tags")
    items = db.relationship("ItemModel", secondary="items_tags", back_populates="tags")