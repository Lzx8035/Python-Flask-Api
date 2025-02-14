# from marshmallow import Schema, fields

# # http://localhost:5005/swagger-ui

# class PlainItemSchema(Schema):
#     id = fields.UUID(dump_only=True)
#     name = fields.Str(required=True)
#     price = fields.Float(required=True)

# class PlainStoreSchema(Schema):
#     id = fields.UUID(dump_only=True)
#     name = fields.Str(required=True)

# class ItemUpdateSchema(Schema):
#     name = fields.Str()
#     price = fields.Float()

# class ItemSchema(PlainItemSchema):
#     store_id = fields.UUID(required=True)
#     store = fields.Nested(PlainStoreSchema(), dump_only=True)

# class StoreSchema(PlainStoreSchema):
#     items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

import re
from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from models.user import UserModel

class PlainItemSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(
        required=True, 
        validate=lambda x: len(x) >= 1,  # 名称不能为空
        error_messages={"validate": "Name cannot be empty"}
    )
    price = fields.Float(
        required=True,
        validate=lambda x: x >= 0.01,    # 价格必须大于0.01
        error_messages={"validate": "Price must be greater than 0.01"}
    )

    @validates("name")
    def validate_name(self, value):
        if len(value.strip()) == 0:
            raise ValidationError("Name cannot be only whitespace")

class PlainTagSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(
        required=True,
        validate=lambda x: 1 <= len(x) <= 30,  # 标签长度限制
        error_messages={"validate": "Tag name must be between 1 and 30 characters"}
    )

    @validates("name")
    def validate_tag_name(self, value):
        if len(value.strip()) == 0:
            raise ValidationError("Tag name cannot be only whitespace")
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValidationError("Tag name can only contain letters, numbers, hyphens and underscores")

class PlainStoreSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(
        required=True,
        validate=lambda x: 3 <= len(x) <= 80,  # 名称长度限制
        error_messages={"validate": "Store name must be between 3 and 80 characters"}
    )

class ItemUpdateSchema(Schema):
    name = fields.Str(validate=lambda x: len(x) >= 1 if x else True)
    price = fields.Float(validate=lambda x: x >= 0.01 if x else True)
    # store_id 不应该在这里，因为：
    # - 商品和商店的关系一旦建立不应该修改
    # - 如果要转移商品到其他商店，应该用专门的 API 端点

    @validates_schema
    def validate_at_least_one(self, data, **kwargs):
        if not data:
            raise ValidationError("At least one field must be provided for update")

class ItemSchema(PlainItemSchema):
    store_id = fields.UUID(required=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.UUID(required=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

# Response Schema
class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

###### USER
class UserSchema(Schema):
    id = fields.UUID(dump_only=True) # 只能输出，不能输入
    username = fields.Str(required=True) # 既能输入也能输出
    password = fields.Str(required=True, load_only=True) # 只用于输入，不会输出
    # password_hash = fields.Str(dump_only=True)  # 添加这行来输出哈希密码，不推荐暴露给前端

    @validates('username')
    def validate_username(self, value):
        if not 3 <= len(value) <= 80:
            raise ValidationError('Username must be 3-80 characters and can only contain letters, numbers, and underscore')
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError('Username can only contain letters, numbers, and underscore')

    @validates('password')
    def validate_password(self, value):
        if not (len(value) >= 8 and
                any(c.isupper() for c in value) and
                any(c.islower() for c in value) and
                any(c.isdigit() for c in value)):
            raise ValidationError('Password must be at least 8 characters and contain upper/lowercase letters and numbers')