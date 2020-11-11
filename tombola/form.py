from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from tombola.models import User,tombola_db


class SignUpForm(FlaskForm):

	username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=3, max=12)])

	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6, max=24)])

	confirm_password = PasswordField('Confirmation mot de passe', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('S\'inscrire')

	phone = StringField('Numéro de téléphone', validators=[DataRequired(),Length(min=10, max=10)])

	def validate_username(self, username):
		user = User.query.filter_by(username = username.data).first()
		if user:
			raise ValidationError('Ce nom d\'utilisateur est déjà pris.')


	def validate_email(self, email):
		user = User.query.filter_by(email = email.data).first()
		if '@phelma.grenoble-inp.fr' not in email.data:
			raise ValidationError('Vous devez posséder une adresse @phelma.grenoble-inp.fr pour participer.')
		if user:
			raise ValidationError('Cette adresse email est déjà prise.')



class LoginForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(),Length(min=1, max=50)])

	password = PasswordField('Mot de passe', validators=[DataRequired(),Length(min=1, max=54)])

	submit = SubmitField('Se connecter')

class adminForm(FlaskForm):

	nb_tickets = IntegerField('Add_tickets')

	submit = SubmitField('Vadiate')

	clear = SubmitField('clear')


class ticketForm(FlaskForm):

	 submit = SubmitField('Ajouter au panier')


class lydiaForm(FlaskForm):
	amount = StringField('amount')
	transaction_identifier = StringField('transaction_identifier')
	currency = StringField('currency')
	request_id = StringField('request_id')
	sig  = StringField('sig')
	vendor_token = StringField('vendor_token')
	order_ref = StringField('order_ref')
	send = SubmitField('send')


class RequestPasswordForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Recevoir un mail de réinitialisation de mon mot de passe.')

	def validate_email(self,email):
		user =  User.query.filter_by(email=email.data).first()
		if user is None :
			raise ValidationError('Adresse email non reconnue.')

class ResetPasswordForm(FlaskForm):
	password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=6, max=24)])
	confirm_password =  PasswordField('Confirmation mot de passe', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Changer mon mot de passe')

class ClearCartForm(FlaskForm):
	submit = SubmitField('Supprimer Panier')

class OrderTickets(FlaskForm):
	option1 = SubmitField('Au Hasard')
	option2 = SubmitField('Disponible en premier')

class AcceptChartForm(FlaskForm):
	cocher = SelectField('Accepter la charte')
	valider = SubmitField('Envoyer')