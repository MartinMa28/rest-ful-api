from flask_restful import Resource
from flask_jwt import jwt_required
from flask import request
from models.image import ImageModel
import datetime
import os
import numpy as np
import caffe

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class Image(Resource):

    @jwt_required()
    def post(self,user_id,image_id):
        #request_data = Image.parser.parse_args()
        #target_dir = 'E:\\MartinMa\\Intel Cup\\server\\section6\\images'
        target_dir = os.path.join(APP_ROOT,'images')
        print(target_dir)

        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        print(request.files.getlist('file'))
        for uploaded_file in request.files.getlist('file'):
            print(uploaded_file)
            filename = user_id + '_' + image_id + '.jpg'
            new_image = ImageModel(str(datetime.datetime.now()),user_id)
            new_image.save_to_db()
            destination = '/'.join([target_dir, filename])
            print(destination)
            uploaded_file.save(destination)
            face = Image.faceRecognition(destination)
            print('face:'+face)
            return {'url':destination}

    @classmethod
    def faceRecognition(imagepath):
        root = 'intel_cup/faceR/'  # 根目录
        deploy = root + 'model/deploy.prototxt'  # deploy文件
        caffe_model = root + 'predict/myfacialnet_iter_200000.caffemodel'  # 训练好的 caffemodel
        # img=root + 'examples/fer2013/test_net/00014.jpg'    #随机找的一张待测图片
        img = imagepath
        labels_filename = root + 'data/labels.txt'  # 类别名称文件，将数字标签转换回类别名称
        net = caffe.Net(deploy, caffe_model, caffe.TEST)  # 加载model和network

        # 图片预处理设置
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})  # 设定图片的shape格式(1,1,42,42)
        transformer.set_transpose('data', (2, 0, 1))  # 改变维度的顺序，由原始图片(42,42,1)变为(1,42,42)
        # transformer.set_mean('data', np.load(mean_file).mean(1).mean(1))    #减去均值，前面训练模型时没有减均值，这儿就不用
        transformer.set_raw_scale('data', 255)  # 缩放到【0，255】之间
        net.blobs['data'].reshape(1, 1, 42, 42)
        im = caffe.io.load_image(img, False)  # 加载图片
        net.blobs['data'].data[...] = transformer.preprocess('data', im)  # 执行上面设置的图片预处理操作，并将图片载入到blob中

        # 执行测试
        out = net.forward()
        labels = np.loadtxt(labels_filename, str, delimiter='\t')  # 读取类别名称文件
        prob = net.blobs['prob'].data[0].flatten()  # 取出最后一层（Softmax）属于某个类别的概率值，并打印
        order = prob.argsort()[-1]  # 将概率值排序，取出最大值所在的序号
        face = labels[order]
        return face  # face是最终识别的表情




