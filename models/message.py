from db import db

class MessageModel(db.Model):
    __talbename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.String(100))
    session_id = db.Column(db.Integer)
    emotion_type = db.Column(db.String)
    emotion_score = db.Column(db.Float(precision = 1))

    # session_id = db.Column(db.Integer, db.ForeignKey('sessions.s_id'))
    # session = db.relationship('SessionModel')

    def __init__(self,value,session_id,e_type,e_score):
        self.value = value
        self.session_id = session_id
        self.emotion_type = e_type
        self.emotion_score = e_score

    def json(self):
        return {'value': self.value, 'session_id': self.session_id}

    @classmethod
    def get_messages_by_session_id(cls,s_id):
        return cls.query.filter_by(session_id = s_id).all()

    @classmethod
    def get_message_by_massage_id(cls,m_id):
        return cls.query.filter_by(massage_id = m_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_message(self):
        db.session.delete(self)
        db.session.commit()

