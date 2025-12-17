from marshmallow import Schema,fields

class PlainUserSchema(Schema):
    id=fields.Integer(dump_only=True)
    username=fields.Str(required=True)
    password=fields.Str(load_only=True,required=True)

class PlainCashSchema(Schema):
    id=fields.Integer(dump_only=True)
    name=fields.Str(required=True)
    value=fields.Float(required=True)

class PlainSecuritySchema(Schema):
    id=fields.Integer(dump_only=True)
    ticker=fields.String(required=True)
    units=fields.Float(required=True)
    unit_price=fields.Float(required=True)

class PlainTagSchema(Schema):
    id=fields.Integer(dump_only=True)
    name=fields.String(required=True)

class UserSchema(Schema):
    cash=fields.List(fields.Nested(PlainCashSchema),dump_only=True)
    securities=fields.List(fields.Nested(PlainSecuritySchema),dump_only=True)

class CashSchema(PlainCashSchema):
    user_id=fields.Integer(load_only=True,required=True)
    user=fields.Nested(PlainUserSchema(),dump_only=True)

class SecuritySchema(PlainSecuritySchema):
    user_id=fields.Integer(load_only=True,required=True)
    user=fields.Nested(PlainUserSchema(),dump_only=True)