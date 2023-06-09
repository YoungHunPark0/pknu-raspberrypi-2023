# Flask 웹서버
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/hello') # http://localhost:5000/hello 경로변경하는게 app.route
def  index():
    return render_template('index.html') # 웹서버부름

if __name__ == '__main__':
    app.run(host='localhost', port='8000', debug=True)