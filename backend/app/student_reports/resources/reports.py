import marshmallow
from pytz import timezone
from flask import request
from flask_restful import Resource
from ..schemas.reports import *
from ..models.reports import *
from http import HTTPStatus
from datetime import datetime

localtz = timezone('Asia/Bangkok')

topic_schema = ReportTopicSchema()
topic_schema_list = ReportTopicSchema(many=True)

subtopic_schema = ReportSubTopicSchema()
subtopic_schema_list = ReportSubTopicSchema(many=True)


class ReportTopicListResource(Resource):
    def get(self):
        data = TopicReport.query.all()
        return {'data': topic_schema_list.dump(data)}, HTTPStatus.OK

    def post(self):
        json_data = request.get_json()
        try:
            topic = topic_schema.load(data=json_data)
        except marshmallow.ValidationError:
            return {'message': 'Validation Error'}, HTTPStatus.BAD_REQUEST
        else:
            topic.save()

        return topic_schema.dump(topic), HTTPStatus.CREATED


class ReportTopicResource(Resource):
    def patch(self, topic_id):
        tp = TopicReport.get_by_id(topic_id)
        json_data = request.get_json()
        try:
            _tp = topic_schema.load(data=json_data)
        except marshmallow.ValidationError:
            return {'message': 'Validation Error'}, HTTPStatus.BAD_REQUEST
        else:
            tp.topic = _tp.topic
            tp.save()
        return topic_schema.dump(tp), HTTPStatus.OK


class ReportSubTopicListResource(Resource):
    def get(self):
        data = SubTopicReport.query.all()
        return {'data': subtopic_schema_list.dump(data)}, HTTPStatus.OK

    def post(self):
        json_data = request.get_json()
        try:
            subtopic = subtopic_schema.load(data=json_data)
        except marshmallow.ValidationError:
            return {'message': 'Validation Error'}, HTTPStatus.BAD_REQUEST
        else:
            subtopic.save()

        return subtopic_schema.dump(subtopic), HTTPStatus.CREATED


class ReportSubTopicResource(Resource):
    def patch(self, subtopic_id):
        tp = SubTopicReport.get_by_id(subtopic_id)
        json_data = request.get_json()
        try:
            _tp = subtopic_schema.load(data=json_data)
        except marshmallow.ValidationError:
            return {'message': 'Validation Error'}, HTTPStatus.BAD_REQUEST
        else:
            tp.topic = _tp.topic
            tp.save()
        return subtopic_schema.dump(tp), HTTPStatus.OK


complaint_schema = ComplaintReportSchema()
complaint_list_schema = ComplaintReportSchema(many=True)


class ComplaintReportListResource(Resource):
    def get(self):
        data = ComplaintReport.query.all()
        return complaint_list_schema.dump(data), HTTPStatus.OK

    def post(self):
        json_data = request.get_json()
        try:
            comp = complaint_schema.load(data=json_data, partial=('creator',
                                                                  'created_at',
                                                                  'subject',
                                                                  'comment'))
        except marshmallow.ValidationError:
            return {'message': 'Validation Error'}, HTTPStatus.BAD_REQUEST
        else:
            comp.created_at = localtz.localize(datetime.now())
            comp.save()

        return complaint_schema.dump(comp), HTTPStatus.CREATED
