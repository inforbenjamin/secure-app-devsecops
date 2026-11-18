from flask import Flask, request

app = Flask(__name__)


@app.route('/hello')
def hello():
    name = request.args.get('name')
    return f"Hello, {name}!"


if __name__ == '__main__':
    # host 0.0.0.0 es necesario para que Docker/ZAP puedan llegar a la app
    app.run(host='0.0.0.0', port=5000, debug=True)
