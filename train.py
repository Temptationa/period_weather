import pandas as pd
import glob
import tensorflow as tf
import json
from tensorflow import keras
import numpy as np

pd.set_option('display.max_columns', 1000000)

train_json = pd.read_json('train.json')
train_json['filename'] = train_json['annotations'].apply(lambda x: x['filename'].replace('\\', '/'))
train_json['period'] = train_json['annotations'].apply(lambda x: x['period'])
train_json['weather'] = train_json['annotations'].apply(lambda x: x['weather'])


train_json.head()
train_json['period'], period_dict = pd.factorize(train_json['period'])
train_json['weather'], weather_dict = pd.factorize(train_json['weather'])


period_labels = list(train_json['period'])
weather_labels = list(train_json['weather'])
images_ds = list(train_json['filename'])


image_dataset = tf.data.Dataset.from_tensor_slices(images_ds)
AUTOTUNE = tf.data.experimental.AUTOTUNE
image_label = tf.data.Dataset.from_tensor_slices((period_labels,weather_labels))


def load_image(path):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [224, 224])
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_flip_up_down(image)
    image = tf.cast(image, tf.float32)
    image = image/255.0
    image = 2 * image - 1
    return image

image_dataset = image_dataset.map(load_image, num_parallel_calls=AUTOTUNE)
image_label_dataset = tf.data.Dataset.zip((image_dataset ,image_label))


val_count = int(2600*0.2)
train_count = 2600-val_count
train_dataset = image_label_dataset.skip(val_count)
val_dataset = image_label_dataset.take(val_count)

batchsz=32
train_dataset = train_dataset.shuffle(buffer_size=train_count).batch(batchsz)
train_dataset = train_dataset.prefetch(buffer_size=AUTOTUNE)#电脑根据内存预先读取数据等待训练
val_dataset = val_dataset.batch(batchsz)


net=keras.applications.VGG19(include_top=False,pooling='max',input_shape=(224,224,3))
net.trainable=True
inputs = tf.keras.Input(shape=(224,224,3))
x = net(inputs)
period = tf.keras.layers.Dense(512,activation='relu')(x)
period_bn = tf.keras.layers.BatchNormalization()(period)
period_Dropout = tf.keras.layers.Dropout(rate=0.5)(period_bn)
output_period = tf.keras.layers.Dense(4,activation='softmax',name='period')(period_Dropout)
weather = tf.keras.layers.Dense(512,activation='relu')(x)
weather_bn = tf.keras.layers.BatchNormalization()(weather)
weather_Dropout = tf.keras.layers.Dropout(rate=0.5)(weather_bn)
output_weather = tf.keras.layers.Dense(3,activation='softmax',name='weather')(weather_Dropout)
model = tf.keras.Model(inputs=inputs,outputs=[output_period,output_weather])
model.summary()


train_steps = train_count//batchsz
val_steps = val_count//batchsz

model.compile(optimizer = tf.keras.optimizers.SGD(0.0001),
              loss='sparse_categorical_crossentropy',
               # loss={'period':'sparse_categorical_crossentropy',
               #       'weather':'sparse_categorical_crossentropy'},
              metrics=['accuracy'])
history  = model.fit(train_dataset, validation_data=val_dataset, validation_freq=1, epochs=50,steps_per_epoch=train_steps,validation_steps=val_steps)
save_model_path = 'F:/DL/period_weather/results/Demo.pb'
model.save(save_model_path)


test_df = pd.DataFrame({'filename': glob.glob('./test_images/*.jpg')})
test_images_ds=list(test_df['filename'])


new_period_dict ={0:'Morning', 1:'Afternoon', 2:'Dawn', 3:'Dusk'}
new_weather_dict ={0:'Cloudy', 1:'Sunny', 2:'Rainy'}
period_pred_list=[]
weather_pred_list=[]


submit_json = {
    'annotations':[],
}

# 生成测试集结果
for i in range(len(test_images_ds)):
    my_image = load_image(test_images_ds[i])
    my_image = tf.expand_dims(my_image, 0)
    pred = model.predict(my_image)
    period_pred = np.argmax(pred[0])
    weather_pred = np.argmax(pred[1])
    submit_json['annotations'].append({
        'filename': test_images_ds[i].split('/')[-1],
        'period': new_period_dict.get(period_pred),
        'weather': new_weather_dict.get(weather_pred),
    })

with open('submit.json', 'w') as up:
    json.dump(submit_json, up)