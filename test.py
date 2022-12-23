#!/usr/bin/env python
import time
from flask import Flask, Response

app = Flask(__name__)


def stream_template(template_name, **context):
    # http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    # uncomment if you don't need immediate reaction
    ##rv.enable_buffering(5)
    return rv


@app.route('/')
def index():
    def g():
        for i, c in enumerate("hello"*10):
            time.sleep(.1)  # an artificial delay
            yield i, c
    return Response(stream_template('index.html', data=g()))


if __name__ == "__main__":
    app.run(host='localhost', port=23423)