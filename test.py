from flask import Flask, request, abort, send_file, render_template
from datetime import datetime
import configparser
import cv2

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *



CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

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
    

# Take Picutre
cap = cv2.VideoCapture(0)
ret_flag , Vshow = cap.read()
FileName = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
cv2.imwrite('./static/'+ FileName + '.jpg', Vshow)

cap.release()

    
# Linebot Push message

#test
#UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
#ImgURL =  'https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/vvv-1577264388.jpg'
#line_bot_api.push_message(UserID, ImageSendMessage(original_content_url=ImgURL, preview_image_url=ImgURL))


ImgURL =  'https://445b30d99d45.ngrok.io' + '/picture?FileName=2021-06-20_08-32-34'
UserID = 'U1d8a810fac51c901fbb7ea3e820cf1f8'
line_bot_api.push_message(UserID, ImageSendMessage(original_content_url=ImgURL, preview_image_url=ImgURL))
