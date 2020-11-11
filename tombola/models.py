from tombola import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))



class User(db.Model, UserMixin):

	id = db.Column("id", db.Integer, primary_key = True)

	username = db.Column("username", db.String(14), unique=True, nullable=False)

	passw = db.Column("passw", db.String(128), nullable=False)

	email = db.Column("prenom", db.String(50), nullable=False, unique=True)

	tickets = db.Column("tickets",db.PickleType())

	cart = db.Column("cart",db.PickleType())

	request_id = db.Column("request_id",db.String(24))

	phone = db.Column("phone", db.String(10), nullable=False, unique=True)

	confirmed = db.Column(db.Boolean, nullable=False, default=False)


	def __repr__(self):
		return f"User('{self.username}', '{self.passw}', '{self.email}', '{self.phone}')"




class tombola_db(db.Model):

	id = db.Column("id", db.Integer, primary_key = True)

	ticket_owner = db.Column("ticker_owner", db.String(50), nullable=True)

	expiry =  db.Column(db.DateTime(), default=datetime.utcnow())

	def __repr__(self):
		return f"tombola('{self.ticket_owner}')"



class db_gagnant(db.Model):

	id = db.Column("id", db.Integer, primary_key = True)

	username = db.Column("username", db.String(14), nullable=False)

	lot = db.Column("lot", db.String(50), nullable=False)
