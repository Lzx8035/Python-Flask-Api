from db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
    # 一对多关系
    items = db.relationship(
        "ItemModel",                  # 关联的模型
        back_populates="store",       # ItemModel 中对应的属性名
        lazy="dynamic",               # 查询策略：动态加载
        cascade="all, delete-orphan"  # 建议添加：删除商店时自动删除商品
    )
    # 一对多关系
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic", cascade="all, delete-orphan")

# cascade="all, delete": 删除商店时删除关联的商品
# cascade="all, delete-orphan": 不仅在删除商店时删除商品，而且当商品与商店解除关联时也会删除商品