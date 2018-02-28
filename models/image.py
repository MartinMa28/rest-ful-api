from db import db

class ImageModel(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.Integer, primary_key = True)
    image_time = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self,time,user_id):
        self.image_time = time
        self.user_id = user_id

    @classmethod
    def find_by_image_id(cls,i_id):
        return cls.query.filter_by(image_id = i_id).first()

    @classmethod
    def find_by_user_id(cls,u_id):
        return cls.query.filter_by(user_id = u_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_image(self):
        db.session.delete(self)
        db.session.commit()
