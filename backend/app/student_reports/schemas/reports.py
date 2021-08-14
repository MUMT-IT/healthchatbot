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


class ComplaintReportSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ComplaintReport
    topic_id = ma.auto_field()
    subtopic_id = ma.auto_field()
    description = ma.auto_field()
    subject = ma.auto_field()
    comment = ma.auto_field()
    creator = ma.auto_field()

    @post_load
    def make_complaint(self, data, **kwargs):
        return ComplaintReport(**data)

    def save(self):
        db.session.add(self)
        db.session.commit()