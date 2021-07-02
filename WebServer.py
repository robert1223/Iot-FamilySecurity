from flask import Flask, request, abort, send_file, render_template


# Create Flask
app = Flask(__name__, static_folder='./static', static_url_path='/static')


# Picture folder
@app.route("/picture", methods=['GET'])
def picture():
    file_path = './static/{}.jpg'.format(request.args.get('FileName'))
    return send_file(file_path, mimetype='image/jpg')
    
    
    
    
# Flask run
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 