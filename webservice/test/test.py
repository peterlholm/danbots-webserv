from flask import Flask, Response, send_file

from webservice import app

@app.route('/test2')
def u_test2():
    return "<h1>Test 2</h1>test"
