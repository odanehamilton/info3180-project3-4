from . import db  
class Myprofile(db.Model):     
    id_num = db.Column(db.Integer, primary_key=True, unique = True, autoincrement=True)     
    first_name = db.Column(db.String(80))     
    last_name = db.Column(db.String(80)) 
    email = db.Column(db.String(100))
    password = db.Column(db.String(150))


class Mylist (db.Model):
    id_num = db.Column(db.Integer, primary_key=True, unique = True)
    image_id = db.Column(db.Integer, primary_key=True, unique = True, autoincrement=True)
    url = db.Column(db.String(200))
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
 

   
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.username)