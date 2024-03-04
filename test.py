import tensorflow as tf
import numpy as np


def image_load_image(path):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [224, 224])
    image = tf.cast(image, tf.float32)
    image = image/255.0
    image = 2 * image - 1
    return image


def camera_load_image(path):
    image = tf.image.resize(path, [224, 224])
    image = image/255.0
    image = 2 * image - 1
    return image


model = tf.keras.models.load_model('./results/91.68')
period_dict ={0:'Morning', 1:'Afternoon', 2:'Dawn', 3:'Dusk'}
vedio_weather_dict ={0:'Rainy', 1:'Sunny', 2:'Cloudy'}
weather_dict ={0:'Cloudy', 1:'Sunny', 2:'Rainy'}


def camera_predict(image):
    my_image = camera_load_image(image)
    my_image = tf.expand_dims(my_image, 0)
    pred = model.predict(my_image)
    period_pred = np.argmax(pred[0])
    weather_pred = np.argmax(pred[1])
    return period_dict.get(period_pred),weather_dict.get(weather_pred)


def vedio_predict(image):
    my_image = camera_load_image(image)
    my_image = tf.expand_dims(my_image, 0)
    pred = model.predict(my_image)
    period_pred = np.argmax(pred[0])
    weather_pred = np.argmax(pred[1])
    return period_dict.get(period_pred),vedio_weather_dict.get(weather_pred)


def image_predict(image):
    my_image = image_load_image(image)
    my_image = tf.expand_dims(my_image, 0)
    pred = model.predict(my_image)
    period_pred = np.argmax(pred[0])
    weather_pred = np.argmax(pred[1])
    return period_dict.get(period_pred), weather_dict.get(weather_pred)