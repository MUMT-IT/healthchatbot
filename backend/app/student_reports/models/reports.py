from extensions import db


class TopicReport(db.Model):
    __tablename__ = 'report_topics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_by_id(cls, topic_id):
        return cls.query.get(topic_id)

    def save(self):
        db.session.add(self)
        db.session.commit()


class SubTopicReport(db.Model):
    __tablename__ = 'report_subtopics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_by_id(cls, topic_id):
        return cls.query.get(topic_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

class ComplaintReport(db.Model):
    __tablename__ = 'report_complaints'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.ForeignKey('report_topics.id'))
    subtopic_id = db.Column(db.ForeignKey('report_subtopics.id'))
    description = db.Column(db.Text())
    subject = db.Column(db.String(255), nullable=True)
    comment = db.Column(db.String(255), nullable=True)
    creator = db.Column(db.String(255), nullable=True, default='Anonymous')
    created_at = db.Column(db.DateTime(timezone=True))
    topic = db.relationship(TopicReport, backref=db.backref('reports', lazy='dynamic'))
    subtopic = db.relationship(SubTopicReport, backref=db.backref('reports', lazy='dynamic'))

    def save(self):
        db.session.add(self)
        db.session.commit()