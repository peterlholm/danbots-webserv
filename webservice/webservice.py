#import os
from flask import Flask #, request, session, redirect
from picture import pic
from pic_2d import pic2d
from pic_3d import pic3d

app = Flask(__name__)
app.debug = True
app.register_blueprint(pic)
app.register_blueprint(pic2d)
app.register_blueprint(pic3d)
app.secret_key = b'_5#y2xyzQ8z\n\xec]/'

@app.route('/')
def home():
    #searchword = request.args.get('pic', '')
    #print("pic parameter", searchword)
    return """
    <h1>Home</h1>
    <br><ul>
    <li><a href=\"/pic/picture\">/pic/picture</a> - show picture in full resolution</li>
    <li><a href=\"/pic/cam\">/pic/cam?size=xx&maxframerate=xx</a> - stream picture</li>
    <li><a href=\"/pic/info\">/pic/info</a> - camera picture information</li>
    <li><a href=\"/2d/2d\">/2d/2d?size=nn</a> - take pictures and send to stiching</li>

    </ul>
    <br>

    """


# @app.route('/log')
# def u_log():
#     # app.logger.debug('A value for debugging')
#     # app.logger.warning('A warning occurred (%d apples)', 42)
#     # app.logger.error('An error occurred')
#     if 'username' in session:
#         return 'Logged in as %s' + session['username']
#         #return 'Logged in as %s' % escape(session['username'])
#     return 'You are not logged in'

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect('/')
#     return '''
#         <form method="post">
#             <p><input type=text name=username>
#             <p><input type=submit value=Login>
#         </form>
#     '''

# @app.route("/json")
# def me_api():

#     return {
#         "username": "peter",
#         "theme": "user.theme",
#         "image": "url_for",
#     }

if __name__ == '__main__':
    print("script server running")
    #app = Flask(__name__)
    app.debug = False
    app.run(host='0.0.0.0', port=8080)
