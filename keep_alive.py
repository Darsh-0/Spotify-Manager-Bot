from flask import Flask, render_template
from threading import Thread


app = Flask('__name__')

@app.route('/')
def index():
    return 'Im in bitch!'


def run():
  app.run(
        host='0.0.0.0',
        port=8080
    )

def keep_alive():
    '''
    Creates and starts new thread that runs the function run.
    '''
    t = Thread(target=run)
    t.start()
