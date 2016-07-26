import requests, BeautifulSoup, urlparse, smtplib, jwt, base64
#from PIL import Image
from flask import render_template, request, redirect, url_for, jsonify, session, _request_ctx_stack
from flask_wtf import Form 
from wtforms import TextField, PasswordField, IntegerField
from wtforms.validators import Required, Email
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import Myprofile, Mylist
from functools import wraps
from flask_cors import cross_origin


SECRET = "This is my secret key"

def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['Authorization'] = response
    return response


def authenticate(error):
  resp = jsonify(error)

  resp.status_code = 401

  return resp

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
    elif len(parts) == 1:
      return {'code': 'invalid_header', 'description': 'Token not found'}
    elif len(parts) > 2:
      return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

    token = parts[1]
    try:
         payload = jwt.decode(token, 'secret')
  
    except jwt.ExpiredSignature:
        return authenticate({'code': 'token_expired', 'description': 'token is expired'})
    except jwt.DecodeError:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
    
    _request_ctx_stack.top.current_user = user = payload
    return f(*args, **kwargs)

  return decorated




def send_email():
    fromaddr = 'odane.hamilton@gmail.com'
    fromname = 'Odane P. Hamilton'
    subject = "Sharing my wishlist with you"
    msg = "This is the link to my wishlist"
    toaddr  = request.form['email']
    message = """From: {} <{}>
To: <{}>
Subject: {}

{}
"""


    messagetosend  = message.format(fromname, fromaddr, toaddr, subject, msg)
    username = 'odane.hamilton@gmail.com'
    password = 'xcncejeiwtjbbqzg'

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddr, messagetosend)
    server.quit()


###
# Routing for your application.
###


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')
    
    
    
@app.route('/emailshare', methods=['GET', 'POST'])
def contact():
    """Render website's contact page."""
    if request.method == 'POST':
        send_email()
    return ""


@app.route('/api/thumbnail/process', methods=['POST', 'GET'])
def thumb():
    current_id = session['id_num']
    url1 = request.form['url']
    result = requests.get(url1)
    soup = BeautifulSoup.BeautifulSoup(result.text)
    og_image = (soup.find('meta', property='og:image') or
                soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        print og_image['content']
    title = soup.find("meta", {"name":"title"})['content']
    description = soup.find("meta", {"name":"description"})['content']
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        print thumbnail_spec['href']
    listing = []
    def image_dem():
        for img in soup.findAll("img", src=True):
            if "sprite" not in img["src"]:
                listing.append(img["src"])
        return listing
    
    
    if request.method == 'POST':
        url = request.form['url']
        if url != "":
            response = {
            "error": 'null',
            "data": {
            "thumbnails": image_dem() },
            "message": "Success" }
        else:
            response = {
            "error": "1",
            "data" : {},
            "message": "Unable to extract thumbnails"
            }
        image = image_dem()
        return render_template('filelisting.html', image=image, title=title, description=description, id_num=current_id, response=response)

@app.route('/api/user/login', methods = ['POST', 'GET'])
def user_login():
    """Processes a user login"""
    error = None
    data = Myprofile.query.all()
    if request.method == 'POST':
        for each in data:
            if request.form['email'] == each.email and request.form['password'] == each.password:
                session['logged_in'] = True
                session['id_num'] = each.id_num
              #  payload = {"email": request.form['email'], "password": request.form['password']}
                
                #add_header('Bearer')
                return redirect(url_for('profile_view', id_num=each.id_num))
        else:
            error = "Invalid login data"
    return render_template('profile_login.html', error=error)
    
    
@app.route('/logout')
def logout():
    """Render website's logout page."""
    session.pop('logged_in', None)
    return redirect(url_for('home'))
    
    
@app.route('/api/user/register', methods=['POST', 'GET'])
def user_registration():
    """Processes a user registration"""

    db.create_all()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        # write the information to the database
        newprofile = Myprofile(first_name=first_name,
                               last_name=last_name, email=email, password=password)
        db.session.add(newprofile)
        db.session.commit()

        return "{} {} was added to the database".format(request.form['first_name'],
                                             request.form['last_name']) + render_template('home.html')
        

    return render_template('profile_add.html')
    
    

@app.route('/api/user/<int:id_num>/wishlist', methods=['GET', 'POST'])
#@requires_auth
#@cross_origin(headers=['Content-Type', 'Authorization'])
def profile_view(id_num):
    encoded = jwt.encode({'some': 'payload'}, 'secret', algorithm='HS256')
    current_id = session['id_num']
    profile = Myprofile.query.get(id_num)
    data = Mylist.query.filter_by(id_num=current_id).all()
    if request.method == 'GET':
        for each in data:
            if each.id_num == current_id:
                return render_template('profile_view.html', profile=profile, data=data)
        return render_template('profile_view.html', profile=profile)
    else:
        db.create_all()
        url = request.form['image']
        description = request.form['description']
        title = request.form['title']
        id_num = session['id_num']
        new_list = Mylist(id_num=id_num,
                               description=description, url=url, title=title)
        db.session.add(new_list)
        db.session.commit()
        payload = {'some': 'data'}
        jwt_token = jwt.encode({'some': 'payload'}, 'secret', algorithm='HS256')
        
        #send data to database here
        return redirect(url_for('profile_view', profile=profile, id_num=current_id, encoded=encoded))
    
    
###
# The functions below should be applicable to all Flask apps.
###

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
