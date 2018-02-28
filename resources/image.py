from flask_restful import Resource,reqparse
from flask_jwt import jwt_required
from flask import request
from models.image import ImageModel
import datetime
import os


class Image(Resource):

    @jwt_required()
    def post(self,user_id,image_id):
        #request_data = Image.parser.parse_args()
        target_dir = 'E:\MartinMa\Intel Cup\server\section6\images'
        print(target_dir)

        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        for uploaded_file in request.files.getlist('file'):
            print(uploaded_file)
            filename = user_id + '_' + image_id + '.jpg'
            new_image = ImageModel(str(datetime.datetime.now()),user_id)
            new_image.save_to_db()
            destination = '\\'.join([target_dir, filename])
            print(destination)
            uploaded_file.save(destination)
            return {'url':destination}




