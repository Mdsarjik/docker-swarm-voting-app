from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import socket
import random
import json
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Options displayed on the vote page
option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")
hostname = socket.gethostname()


def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(
            host="redis",
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    return g.redis


@app.route("/", methods=['POST', 'GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form.get('vote')
        if vote:
            data = json.dumps({'voter_id': voter_id, 'vote': vote})
            redis.rpush('votes', data)
            app.logger.info('Registered vote: %s by voter %s', vote, voter_id)

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
