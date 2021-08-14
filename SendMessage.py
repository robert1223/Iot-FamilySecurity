from flask import Flask, request, abort, send_file, render_template
from datetime import datetime
import configparser
import cv2
import time 
import os 
import importlib.util
import sys
import glob
import numpy as np


from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *



CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')


# Linebot verification information
line_bot_api = LineBotApi(CONFIG['LINE_BOT']['ACCESS_TOKEN'])
#handler = WebhookHandler(CONFIG['LINE_BOT']['SECRET'])


# Take Picutre
cap = cv2.VideoCapture(0)  # open camera
ret_flag , Vshow = cap.read()
FileName = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
cv2.imwrite('/home/pi/Python_project/HW_3/'+ FileName + '.jpg', Vshow)
cap.release()
time.sleep(0.5)


MODEL_NAME = 'Sample_TFLite_model'
IM_NAME = FileName + '.jpg' 
GRAPH_NAME = 'detect.tflite'
LABELMAP_NAME = 'labelmap.txt'


# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    #if use_TPU:
        #from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    #if use_TPU:
        #from tensorflow.lite.python.interpreter import load_delegate
        
# Get path to current working directory
CWD_PATH = os.getcwd()

# Define path to images and grab all image filenames
PATH_TO_IMAGES = os.path.join(CWD_PATH, IM_NAME)
images = glob.glob(PATH_TO_IMAGES)

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_NAME, LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
    
# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])
    
# Load the Tensorflow Lite model.
# If using Edge TPU, use special load_delegate argument
#if use_TPU:
    #interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              #experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    #print(PATH_TO_CKPT)
#else:
interpreter = Interpreter(model_path=PATH_TO_CKPT)
    
interpreter.allocate_tensors()


# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Loop over every image and perform detection
for image_path in images:

    # Load image and resize to expected shape [1xHxWx3]
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    imH, imW, _ = image.shape 
    image_resized = cv2.resize(image_rgb, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

    # Retrieve detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
    scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
    #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)


    # set a tmplist for object name
    tmplist = []
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        if ((scores[i] > 0.5) and (scores[i] <= 1.0)):

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            
            cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%' 
            # Get font size
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) 
            # Make sure not to draw label too close to top of window
            label_ymin = max(ymin, labelSize[1] + 10) 
            # Draw white box to put label text in
            cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED)
            # Draw label text
            cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) 
            # join object_name to tmplist
            tmplist.append(object_name)
          
    if 'person' in tmplist:
        
        # Linebot Push message
        text = "有人靠近家門口囉!!"
        UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
        line_bot_api.push_message(UserID, TextSendMessage(text=text))
        
        cv2.imwrite('/home/pi/Python_project/HW_3/static/'+ FileName + '_Detection.jpg', image)
              
        ## Linebot Push message(image)
        ## 需架設Web server
        # ImgURL =  'your domain name' + '/picture?FileName={}'.format(FileName + '_Detection')
        # UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
        # line_bot_api.push_message(UserID, ImageSendMessage(original_content_url=ImgURL, preview_image_url=ImgURL)) 
        
    else:        
        os.remove(FileName+'.jpg')
    
    
    


















    

