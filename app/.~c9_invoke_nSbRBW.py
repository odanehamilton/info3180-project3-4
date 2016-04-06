import requests, BeautifulSoup, urlparse
from flask import render_template, request, redirect, url_for, jsonify, session
from flask.ext.wtf import Form 
from wtforms.validators import Required, Email
from wtforms.fields import TextField, PasswordField, IntegerField
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from app.models import Myprofile



class ProfileForm(Form):
     id_num = IntegerField('ID')
     first_name = TextField('First Name', validators=[Required()])
     last_name = TextField('Last Name', validators=[Required()])
     email = TextField('Username', validators=[Required(), Email(message="Invalid email address")])
     password = PasswordField('Password', validators=[Required()])



###
# Routing for your application.
###


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/api/thumbnail/process', methods=['POST', 'GET'])
def thumb():
    id_num = session['i']
    data = Myprofile.query.all()
    url1 = request.args.get('url')
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
                print img["src"]
                listing.append(img["src"])
        return listing
    
    response = {}
    if request.method == 'GET':
        url = request.args.get('url')
        if url != "":
            response['error'] = 'null'
            response['data'] = {}
            response['data']['thumbnails'] = [image_dem()]
            response['message'] = "Success"
        else:
            response = {}
            response['error'] = "1"
            response['data'] = {}
            response['message'] = "Unable to extract thumbnails"
        image = image_dem()
        return render_template('filelisting.html', image=image, title=title, description=description, id_num=id_num)

@app.route('/api/user/login', methods = ['POST', 'GET'])
def user_login():
    """Processes an user login"""
    error = None
    data = Myprofile.query.all()
    if request.method == 'POST':
        for each in data:
            if request.form['email'] == each.email and request.form['password'] == each.password:
                session['logged_in'] = True
                session['id_num'] = each.id_num
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
        

    form = ProfileForm()
    return render_template('profile_add.html',
                           form=form)
    
    

@app.route('/api/user/<int:id_num>/wishlist', methods=['GET', 'POST'])
def profile_view(id_num):
    profile = Myprofile.query.get(id_num)
    return render_template('profile_view.html',profile=profile)


@app.route('/api/user/<int:id_num>/wishlist', methods=['GET', 'POST'])
def item_add(id_num):
    if request.method == 'POST':
        id_num = Myprofile.query.get(id_num)
    #send data to database here
        return render_template('home.html')
        #return redirect(url_for('profile_view', id_num=profile.id_num))
    

###
# The functions below should be applicable to all Flask apps.
###

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
