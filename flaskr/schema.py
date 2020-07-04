from marshmallow import Schema, fields, validates, ValidationError
from bson import ObjectId


class SongRatingPayload(Schema):
    _id = fields.String(required=True)
    rating = fields.Integer(required=True)

    @validates("_id")
    def validate_objectid(self, _id: str) -> None:
        if not ObjectId.is_valid(_id):
            raise ValidationError("{} is not valid ObjectId".format(_id))

    @validates("rating")
    def validate_rating(self, rating: int) -> None:
        if rating < 1 or rating > 5:
            raise ValidationError("Rating must be in between 1 and 5")
