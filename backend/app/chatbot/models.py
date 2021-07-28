from app import db

class UnfulfilledMessage(db.Model):
    __tablename__ = 'unfulfilled_messages'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255))
    line_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True))