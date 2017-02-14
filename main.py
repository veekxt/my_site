
from flask import Flask, request, render_template
from flask.ext.bootstrap import Bootstrap
import config

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config.from_object(config)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

@app.route('/')
def index():
    return render_template('index.html', text='Hello, My Site!')

@app.route('/login')
def user_login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
