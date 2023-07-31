#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.form['payload']
    print(json.loads(payload))
    return '', 200