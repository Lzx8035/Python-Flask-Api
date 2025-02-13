from db import db
from sqlalchemy.dialects.postgresql import UUID # type: ignore
import uuid

class ItemsTags(db.Model):
    __tablename__ = "items_tags"
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_id = db.Column(UUID(as_uuid=True), db.ForeignKey("items.id"))
    tag_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tags.id"))