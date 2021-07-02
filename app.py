from flask import Flask, request, abort, send_file, render_template
from datetime import datetime
import configparser
import cv2
import time 

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *



CONFIG = configparser.ConfigParser()
CONFIG.read('/home/pi/Python_project/HW_3/config.ini')

# Create Flask
app = Flask(__name__, static_folder='./static', static_url_path='/static')


# Linebot verification information
line_bot_api = LineBotApi(CONFIG['LINE_BOT']['ACCESS_TOKEN'])
handler = WebhookHandler(CONFIG['LINE_BOT']['SECRET'])



# Linebot Verification
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text  
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'
    
time.sleep(25)
# Take Picutre
cap = cv2.VideoCapture(0)
ret_flag , Vshow = cap.read()
FileName = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
cv2.imwrite('/home/pi/Python_project/HW_3/static/'+ FileName + '.jpg', Vshow)
print(FileName)
cap.release()
time.sleep(0.5)

    
# Linebot Push message

#test
#UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
#ImgURL =  'https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/vvv-1577264388.jpg'
#line_bot_api.push_message(UserID, ImageSendMessage(original_content_url=ImgURL, preview_image_url=ImgURL))


ImgURL =  'https://23f0a93e41ff.ngrok.io' + '/picture?FileName={}'.format(FileName)
UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
line_bot_api.push_message(UserID, ImageSendMessage(original_content_url=ImgURL, preview_image_url=ImgURL))




    

