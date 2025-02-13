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

from marshmallow import Schema, fields, validates, validates_schema, ValidationError

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
