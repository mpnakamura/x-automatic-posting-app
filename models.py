from app import db
from datetime import datetime

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Tweet %r>' % self.content
