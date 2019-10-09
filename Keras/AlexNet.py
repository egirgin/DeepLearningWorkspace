import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.callbacks import TensorBoard
import numpy as np
import time

batch_size = 50
num_classes = 10
epochs = 10
learning_rate = 0.01

"""
Set Tensorboard
Timestamp is used to create uniqueness
"""

model_name = "AlexNet-E{}-LR{}-BS{}-{}".format(epochs, learning_rate, batch_size, int(time.time()))
tensorboard = TensorBoard(log_dir="logs/{}".format(model_name))

(x_train, y_train), (x_test, y_test) = cifar10.load_data()
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255 #NORMALIZING
x_test /= 255

"""
Architecture

```
padding="same"
```
in order to adjust architecture to CIFAR-10 dataset

AlexNet: https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf

"""

model = Sequential()
#-----------LAYER-1--------------
model.add( Conv2D(filters=96, kernel_size=(11,11), strides=(4,4), padding="same", input_shape=x_train.shape[1:], activation="relu") )
model.add( BatchNormalization() )
model.add( MaxPooling2D(pool_size=(2,2), strides=(3,3), padding="same") )
#-----------LAYER-2--------------
model.add( Conv2D(filters=256, kernel_size=(5,5), activation="relu", padding="same") )
model.add( BatchNormalization() )
model.add( MaxPooling2D(pool_size=(2,2), strides=(3,3), padding="same") )
#-----------LAYER-3--------------
model.add( Conv2D(filters=384, kernel_size=(3,3), activation="relu", padding="same") )
#-----------LAYER-4--------------
model.add( Conv2D(filters=384, kernel_size=(3,3), activation="relu", padding="same") )
#-----------LAYER-5--------------
model.add( Conv2D(filters=256, kernel_size=(3,3), activation="relu", padding="same") )
model.add( MaxPooling2D(pool_size=(2,2), strides=(3,3), padding="same") )
#-----------LAYER-6--------------
model.add( Flatten() )
model.add( Dense(units=4096, activation="relu") )
#-----------LAYER-7--------------
model.add( Dense(units=4096, activation="relu") )
#-----------LAYER-8--------------OUTPUT
model.add( Dense(units=10, activation="softmax") )

opt = tf.keras.optimizers.Adam(lr=learning_rate)

model.compile(loss="sparse_categorical_crossentropy",
              optimizer=opt,
              metrics=["accuracy"])

history = model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.33, verbose=1, callbacks=[tensorboard])

"""
Plotting
"""
import matplotlib.pyplot as plt
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
#------------------------------------------------
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

#!tensorboard --logdir logs

"""
Evaluation
"""

scores = model.evaluate(x_test, y_test, verbose=0)
print("%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

"""
Save and Load
"""

# serialize model to JSON
model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights("model.h5")
print("Saved model to disk")

from tensorflow.keras.models import model_from_json

# load json and create model
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded model from disk")

# evaluate loaded model on test data
loaded_model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
score = loaded_model.evaluate(x_test, y_test, verbose=0)
print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))

#save and load architecture and weights together
model.save("full_model.h5")
from tensorflow.keras.models import load_model
full_model = load_model('full_model.h5')
full_model.summary()

# evaluate loaded model on test data
full_model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
score = full_model.evaluate(x_test, y_test, verbose=0)
print("%s: %.2f%%" % (full_model.metrics_names[1], score[1]*100))