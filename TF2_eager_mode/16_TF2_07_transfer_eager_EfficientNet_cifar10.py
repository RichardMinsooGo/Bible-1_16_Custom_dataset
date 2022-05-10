!pip install --upgrade --no-cache-dir gdown

from IPython.display import clear_output 
clear_output()

# Step 1 : Git clone Feature map

'''
# Clone from Github Repository
! git init .
! git remote add origin https://github.com/RichardMinsooGo/5_TF2_UCF101_video_classification.git
! git pull origin master
# ! git pull origin main
'''

# Mini-COCO dataset download from Auther's Github repository
import gdown
google_path = 'https://drive.google.com/uc?id='
file_id = '18I06ymkUqKwEon4Dsb8GqkJORwPZZxLd'
output_name = 'Cifar_10.zip'
gdown.download(google_path+file_id,output_name,quiet=False)
# https://drive.google.com/file/d/18I06ymkUqKwEon4Dsb8GqkJORwPZZxLd/view?usp=sharing

% rm -rf sample_data
!unzip /content/Cifar_10.zip -d /content/data
clear_output()
! rm /content/Cifar_10.zip

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPool2D, Dropout
from tensorflow.keras import Model, Sequential

batch_size = 128
n_epoch = 3

# path joining version for other paths

# Datasets = "cifar_10_32_pixels"
# Datasets = "cifar_100_32_pixels"
Datasets = "cifar_10_224_pixels"
# Datasets = "cifar_100_224_pixels"
# Datasets = "mini_imagenet"

if Datasets == "cifar_10_32_pixels":
    n_classes = 10
    img_size = 32

    dst_dir_train = './01_CIFAR10_32pixels/train/'
    dst_dir_test  = './01_CIFAR10_32pixels/test/'
    
elif Datasets == "cifar_100_32_pixels":
    n_classes = 100
    img_size = 32
    
    dst_dir_train = './02_CIFAR100_32pixels/train/'
    dst_dir_test  = './02_CIFAR100_32pixels/test/'
    
elif Datasets == "cifar_10_224_pixels":
    n_classes = 10
    img_size = 224       # 224

    dst_dir_train = '/content/data/train/'
    dst_dir_test  = '/content/data/train/'
    
elif Datasets == "cifar_100_224_pixels":
    n_classes = 100
    img_size = 224
    
    dst_dir_train = './04_CIFAR100_224pixels/train/'
    dst_dir_test  = './04_CIFAR100_224pixels/test/'
    
elif Datasets == "mini_imagenet":
    n_classes = 200
    img_size = 160
    
    dst_dir_train = './07_mini_imagenet/train/'
    dst_dir_test  = './07_mini_imagenet/test/'
    
    
# DIR = '/tmp'
num_train = sum([len(files) for r, d, files in os.walk(dst_dir_train)])
num_test  = sum([len(files) for r, d, files in os.walk(dst_dir_test)])



# Part 2 - Fitting the CNN to the images
from keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale = 1./255,
                                   shear_range = 0.2,
                                   zoom_range = 0.2,
                                   horizontal_flip = True)

test_datagen = ImageDataGenerator(rescale = 1./255)

train_ds = train_datagen.flow_from_directory(dst_dir_train,
                                                 target_size = (img_size, img_size),
                                                 batch_size = batch_size,
                                                 class_mode = 'sparse')
                                                 # class_mode = 'categorical')

test_ds = test_datagen.flow_from_directory(dst_dir_test,
                                            target_size = (img_size, img_size),
                                            batch_size = batch_size,
                                            class_mode = 'sparse')
                                            # class_mode = 'categorical')

steps_per_epoch  = int(num_train/batch_size)
validation_steps = int(num_test/batch_size)


# returns batch_size random samples from either training set or validation set
# resizes each image to (224, 244, 3), the native input size for VGG19
#Define network
IMG_SIZE = 224                      # VGG19
IMG_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
num_classes = 10                    # cifar10

def build_model(num_classes, img_size=224):
    input = tf.keras.layers.Input(shape=(img_size, img_size, 3))
    model = tf.keras.applications.EfficientNetB3(include_top=False, input_tensor=input, weights="imagenet")

    # Freeze the pretrained weights
    model.trainable = False

    # Rebuild top
    x = tf.keras.layers.GlobalAveragePooling2D(name="avg_pool")(model.output)
    x = tf.keras.layers.BatchNormalization()(x)

    top_dropout_rate = 0.2
    x = tf.keras.layers.Dropout(top_dropout_rate, name="top_dropout")(x)
    output = tf.keras.layers.Dense(num_classes, activation="softmax", name="pred")(x)

    # Compile
    model = tf.keras.Model(input, output, name="EfficientNet")
    return model

model = build_model(num_classes)
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
model_name = 'cifar10_EfficientNetB3'

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])


"""
from keras.callbacks import EarlyStopping, ModelCheckpoint

early_stop = EarlyStopping(monitor='loss', min_delta=0.001, patience=3, mode='min', verbose=1)
checkpoint = ModelCheckpoint('model_best_weights.h5', monitor='loss', verbose=1, save_best_only=True, mode='min', period=1
checkpoint = ModelCheckpoint("best_model.hdf5", monitor='loss', verbose=1, save_best_only=True, mode='auto', period=1)
model.fit_generator(X_train, Y_train, validation_data=(X_val, Y_val), 
      callbacks = [early_stop,checkpoint])
"""

import time

start_time = time.time()

model.fit_generator(train_ds,steps_per_epoch = steps_per_epoch, epochs = n_epoch, 
                    validation_data = test_ds, validation_steps = validation_steps)

# model.evaluate_generator(test_set, validation_steps)

finish_time = time.time()

print(int(finish_time - start_time), "Sec")





