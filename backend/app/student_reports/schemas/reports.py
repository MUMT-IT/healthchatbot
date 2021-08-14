from extensions import ma
from marshmallow import post_load
from ..models.reports import *


class ReportTopicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TopicReport
    topic = ma.auto_field()
    id = ma.auto_field()

    @post_load
    def make_topic(self, data, **kwargs):
        return TopicReport(**data)


class ReportSubTopicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = SubTopicReport
    topic = ma.auto_field()
    id = ma.auto_field()

    @post_load
    def make_topic(self, data, **kwargs):
        return SubTopicReport(**data)


class ReportSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ComplaintReport
