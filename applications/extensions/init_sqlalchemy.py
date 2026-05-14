import datetime

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)

URL.default_message = 'Invalid URL'
Email.default_message = 'Invalid email'
Range.message_min = 'Must not be less than {min}'
Range.message_max = 'Must not be greater than {max}'
Range.message_all = 'Must be between {min} and {max}'
Length.message_min = 'Must be at least {min} characters'
Length.message_max = 'Must be at most {max} characters'
Length.message_all = 'Must be between {min} and {max} characters'
Length.message_equal = 'Must be exactly {equal} characters'
Equal.default_message = 'Must be equal to {other}'
Regexp.default_message = 'Invalid input'
Predicate.default_message = 'Invalid input'
NoneOf.default_message = 'Invalid input'
OneOf.default_message = 'Invalid choice'
ContainsOnly.default_message = 'One or more invalid choices'

fields.Field.default_error_messages = {
    "required": "Missing required data",
    "null": "Data cannot be null",
    "validator_failed": "Invalid data",
}

fields.Str.default_error_messages = {
    'invalid': "Not a valid string"
}

fields.Int.default_error_messages = {
    "invalid": "Not a valid integer"
}

fields.Number.default_error_messages = {
    "invalid": "Not a valid number"
}

fields.Boolean.default_error_messages = {
    "invalid": "Not a valid boolean"
}


db = SQLAlchemy()
ma = Marshmallow()


def layui_paginate(query):
    """Layui table pagination helper."""
    return query.paginate(
        page=request.args.get('page', type=int),
        per_page=request.args.get('limit', type=int),
        error_out=False
    )


try:
    from sqlalchemy.orm import Query

    Query.layui_paginate = layui_paginate
except Exception:
    pass


def init_databases(app: Flask):
    db.init_app(app)
    ma.init_app(app)
