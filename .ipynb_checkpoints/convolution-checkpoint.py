import cv2
import numpy as np
import os
from random import shuffle
from tqdm import tqdm
#import tflearn
#from tflearn.layers.conv import conv_2d, max_pool_2d
#from tflearn.layers.core import input_data, dropout, fully_connected
#from tflearn.layers.estimator import regression
import tensorflow as tf
import matplotlib.pyplot as plt

TRAIN_DIR = '/Users/paulmathai/python-virtual-enviorments/DBSystel/ICE/Dataset'
TEST_DIR = '/Users/paulmathai/python-virtual-enviorments/DBSystel/test'
IMG_WIDTH = 72
IMG_HEIGHT = 128
LR = 1e-3

MODEL_NAME = 'dbsdoor-{}-{}.model'.format(LR, '2conv-basic')


def label_img(img):
    word_label = img.split('.')[-3]
    if word_label == 'Door':
        return [1, 0]  # [door, nodoor]
    elif word_label == 'NoDoor':
        return [0, 1]


def create_train_data():
    training_data = []
    for img in tqdm(os.listdir(TRAIN_DIR)):
        label = label_img(img)
        path = os.path.join(TRAIN_DIR, img)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        training_data.append([np.array(img), np.array(label)])
    shuffle(training_data)
    np.save('train_data.npy', training_data)
    return training_data


"""def process_test_data():
    testing_data = []
    for img in tqdm(os.listdir(TEST_DIR)):
        path = os.path.join(TEST_DIR,img)
        img_num = img.split('.')[0]
        img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img,(IMG_WIDTH,IMG_HEIGHT))
        testing_data.append([np.array(img), img_num])
        
    shuffle(testing_data)
    np.save('test_data.npy', testing_data)
    return testing_data"""

train_data = create_train_data()
# train_data = np.load('train_data.npy')

tf.reset_default_graph()

convnet = input_data(shape=[None, IMG_WIDTH, IMG_HEIGHT, 3], name='input')

convnet = conv_2d(convnet, 32, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 64, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 128, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 64, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = conv_2d(convnet, 32, 5, activation='relu')
convnet = max_pool_2d(convnet, 5)

convnet = fully_connected(convnet, 1024, activation='relu')
convnet = dropout(convnet, 0.3)

convnet = fully_connected(convnet, 2, activation='softmax')
convnet = regression(convnet, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(convnet, tensorboard_dir='log')

if os.path.exists('{}.meta'.format(MODEL_NAME)):
    model.load(MODEL_NAME)
    print('model loaded!')

train = train_data[:-50]
test = train_data[-50:]

X = np.array([i[0] for i in train]).reshape(-1, IMG_WIDTH, IMG_HEIGHT, 3)
Y = [i[1] for i in train]

test_x = np.array([i[0] for i in test]).reshape(-1, IMG_WIDTH, IMG_HEIGHT, 3)
test_y = [i[1] for i in test]

model.fit({'input': X}, {'targets': Y}, n_epoch=10, validation_set=({'input': test_x}, {'targets': test_y}),
          snapshot_step=500, show_metric=True, run_id=MODEL_NAME)

model.save(MODEL_NAME)

# test_data = process_test_data()
# test_data = np.load('test_data.npy')

fig = plt.figure()

for num, data in enumerate(train_data[:20]):
    # door: [1,0]
    # nodoor: [0,1]

    img_num = data[1]
    img_data = data[0]

    y = fig.add_subplot(5, 4, num + 1)
    orig = img_data
    data = img_data.reshape(IMG_WIDTH, IMG_HEIGHT, 3)
    model_out = model.predict([data])[0]

    if np.argmax(model_out) == 1:
        str_label = 'No Door'
    else:
        str_label = 'Door'

    y.imshow(orig)
    plt.title(str_label)
    y.axes.get_xaxis().set_visible(False)
    y.axes.get_yaxis().set_visible(False)
plt.show()
