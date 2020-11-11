from flask import render_template, request, redirect, url_for, session, flash
from tombola import app, db, bcrypt, mail
from tombola.models import User,tombola_db, db_gagnant
from tombola.form import SignUpForm, LoginForm, adminForm, ticketForm, lydiaForm, RequestPasswordForm,ResetPasswordForm, ClearCartForm, OrderTickets, AcceptChartForm
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, timedelta
import random
import string
from tombola.tirage import gagnant, tirage_au_sort


@app.route("/")
def home():
	return redirect(url_for('tombola'))

@app.route("/admin", methods=["GET","POST"])
def admin():
	if current_user.is_authenticated and current_user.username == "adminne":
		if 'Validate' in request.form :
			for k in range(int(request.form.get('Nombre'))):
				new_ticket = tombola_db()
				db.session.add(new_ticket)
				db.session.commit()
		elif 'Clear' in request.form:
			User.query.filter_by(id=current_user.id).update({User.tickets:None})
			db.session.commit()
		elif 'Change' in request.form :
			hashed_pass = bcrypt.generate_password_hash(request.form.get('New_MDP')).decode('utf-8')
			User.query.filter_by(email=request.form.get('Mail')).update({User.passw:hashed_pass})
			db.session.commit()
		elif 'Change1' in request.form :
			user = User.query.filter_by(email=request.form.get('Mail1')).first()
			new_ticket = user.tickets + [request.form.get('Num_ticket')]
			seen = []
			for ticket in new_ticket:
				if ticket not in seen:
					seen.append(ticket)
			new_ticket = seen
			User.query.filter_by(id=user.id).update({User.tickets:new_ticket})
			
			for ticket in new_ticket: 
				tombola_db.query.filter_by(id=ticket).update({tombola_db.ticket_owner:user.email})
			db.session.commit()
			for ticket in user.cart:
				reset = datetime.utcnow()
				tombola_db.query.filter_by(id=int(ticket)).update({tombola_db.expiry:reset})
			User.query.filter_by(id=user.id).update({User.cart:[]})
			db.session.commit()
		data2=tombola_db.query.all()
		data3=User.query.all()
		compteur = 0
		compteur2 = 0
		for k in data2:
			if not (k.ticket_owner == None):
				compteur+=1
		for k in data3:
			if len(k.tickets) > 0:
				compteur2+=1

		return render_template("admin.html", data=User.query.all(), nb_ticket_vendu=compteur, nb_participants = compteur2)
	else:
		return redirect(url_for('home'))



@app.route("/tombola",methods=["POST","GET"])
def tombola():
	form=ticketForm()
	form_option = OrderTickets()
	taille=0
	data=tombola_db.query.all()
	if current_user.is_authenticated:
		user = User.query.filter_by(id=current_user.id).first()
		taille = len(user.tickets)

	if form_option.validate_on_submit():
		if(form_option.option1.data):
			random.shuffle(data)
		elif(form_option.option2.data):
			date=datetime.utcnow()
			data_new,data_booked,data_no=[],[],[]
			for k in data:
				if k.ticket_owner == None and k.expiry < date:
					data_new.append(k)
				elif  k.ticket_owner == None and k.expiry > date:
					data_booked.append(k)
				else:
					data_no.append(k)
			data=data_new+data_booked+data_no

	if form.validate_on_submit() and current_user.is_authenticated and not (form_option.option1.data) and not (form_option.option2.data) and current_user.confirmed :
		if not current_user.confirmed:
			flash('Attention vous devez accepter la charte pour acheter des tickets.', 'danger')
			return redirect(url_for('tombola'))
		L = request.form.getlist('tickets')
		actual_cart = current_user.cart
		for k in L:
			check = tombola_db.query.filter_by(id=int(k)).first()
			if check.ticket_owner is None:
				actual_cart.append(k)
		User.query.filter_by(id=current_user.id).update({User.cart:actual_cart})
		db.session.commit()
		for ticket in L:
			new_exp = datetime.utcnow() + timedelta(minutes=15)
			tombola_db.query.filter_by(id=int(ticket)).update({tombola_db.expiry:new_exp})
		db.session.commit()
		return redirect(url_for('panier'))

	return render_template("tombola.html", data=data, form=form, form_option=form_option, date=datetime.utcnow(), taille = taille)

def random_string(N):
	return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))

"""
@app.route("/panier",methods=["GET","POST"])
@login_required
def panier():
	if current_user.is_authenticated:
		form = ClearCartForm()
		if form.validate_on_submit():
			return redirect(url_for('clear_cart'))
		L = current_user.cart
		user = User.query.filter_by(id=current_user.id).first()
		liste_achetes = user.tickets
		if(len(L)+len(liste_achetes)>10):
			return redirect(url_for('clear_cart'))
		L2 = []
		date = datetime.utcnow()
		if len(current_user.cart) != 0:
			for k in range(len(L)):
				ticket = tombola_db.query.filter_by(id=L[k]).first()
				exp = ticket.expiry
				if ticket.expiry > date:
					L2.append(L[k])
		User.query.filter_by(id=current_user.id).update({User.cart:L2})
		db.session.commit()
		email = current_user.email
		ref = random_string(12)
		User.query.filter_by(id=current_user.id).update({User.request_id:ref})
		db.session.commit()
		phone="+"+user.phone
		return render_template('confirm_checkout.html', data=current_user.cart, taille=len(current_user.cart), form=form, ref=ref, who=user, phone=phone)
	return redirect(url_for('tombola'))
"""


@app.route("/login/",methods=["POST","GET"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		found_user = User.query.filter_by(email = form.email.data).first()
		if found_user and bcrypt.check_password_hash(found_user.passw, form.password.data):
			login_user(found_user, remember=True)
			flash(f'Bienvenue { form.email.data } !', 'success')
			return redirect(url_for('home'))
		else :
			flash('Login unsuccessful please check credentials', 'danger')
	return render_template("login.html", title='Hello World', form=form)


"""
@app.route("/signup/",methods=["POST","GET"])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = SignUpForm()
	if form.validate_on_submit():
		hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		temp_user = User(username = form.username.data, passw = hashed_pass, email = form.email.data, phone = form.phone.data, tickets=[], cart=[], confirmed=False)
		db.session.add(temp_user)
		db.session.commit()
		flash(f'Compte créé ! Vous pouvez maintenant vous connecter.', 'success')
		return redirect(url_for('home'))
	return render_template("signup.html", form=form)
"""


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
	user = User.query.filter_by(id=current_user.id).first()
	taille = len(user.tickets)
	taille2 = len(user.cart)
	return render_template("dashboard.html", data=user, taille = taille, taille2 = taille2)


"""
@app.route('/clear_cart')
def clear_cart():
	if current_user.is_authenticated:
		for ticket in current_user.cart:
			reset = datetime.utcnow()
			tombola_db.query.filter_by(id=int(ticket)).update({tombola_db.expiry:reset})
		User.query.filter_by(id=current_user.id).update({User.cart:[]})
		db.session.commit()
	return redirect(url_for('tombola'))

def checkout_confirmed():
	if current_user.is_authenticated():
		new_ticket = current_user.tickets + current_user.cart
		User.query.filter_by(id=current_user.id).update({User.tickets:new_ticket})
		db.session.commit()
		clear_cart()


@app.route("/lydia", methods=["POST"])
def lydia():
	form  = lydiaForm()
	if request.method == 'POST':
		user = User.query.filter_by(request_id=form.order_ref.data).first()
		new_ticket = user.tickets + user.cart
		User.query.filter_by(id=user.id).update({User.tickets:new_ticket})
		for ticket in new_ticket:
			tombola_db.query.filter_by(id=ticket).update({tombola_db.ticket_owner:user.email})
		db.session.commit()
		for ticket in user.cart:
			reset = datetime.utcnow()
			tombola_db.query.filter_by(id=int(ticket)).update({tombola_db.expiry:reset})
		User.query.filter_by(id=user.id).update({User.cart:[]})
		db.session.commit()
	return render_template("lydia.html", form=form)

@app.route('/success')
def success():
	token = request.args.get('transaction', 0)
	if token != 0:
		user = User.query.filter_by(request_id=token).first()
		if status:
			new_ticket = current_user.tickets + current_user.cart
			User.query.filter_by(id=current_user.id).update({User.tickets:new_ticket})
			for ticket in new_ticket:
				tombola_db.query.filter_by(id=ticket).update({tombola_db.ticket_owner:current_user.email})
			db.session.commit()
			clear_cart()
	return redirect(url_for('dashboard'))



@app.route("/confirm_checkout", methods=['GET', 'POST'])
def confirm_checkout():
	if current_user.is_authenticated():
		new_ticket = current_user.tickets + current_user.cart
		User.query.filter_by(id=current_user.id).update({User.tickets:new_ticket})
		db.session.commit()
		clear_cart()
		return redirect(url_for('dashboard'))
	return redirect(url_for('home'))
"""
@app.route("/reset_password", methods=["POST","GET"])
def request_reset():
	if current_user.is_authenticated:
		return redirect(url_for('tombola'))
	form = RequestPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		flash('Envoyez un mail à tombola.bds.phelma@gmail.com.')
		return redirect(url_for('login'))
	return render_template('request_reset_password.html',form=form)



@app.route('/charte', methods=["POST","GET"])
def charte():

	if request.method == 'POST':
		if current_user.is_authenticated:
			try:
				a = 'on' in request.form.get('charte')
				User.query.filter_by(id=current_user.id).update({User.confirmed:True})
				db.session.commit()
				flash('Vous pouvez maintenant acheter vos premiers tickets !','success')
				return redirect(url_for('tombola'))
			except:
				flash('Veuillez cocher la case "J\'accpete la charte" et puis envoyer.','danger')
		else:
			return redirect(url_for('login'))
	return render_template('charte.html')


@app.route('/tirage',methods=["POST","GET"])
def tirage():
		"""data=tombola_db.query.all()
		L_owners = []
		for ticket in data:
			if ticket.ticket_owner != None:
				L_owners.append(ticket.ticket_owner)
		Lots = ['switch', '2 forfait paintball', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '1 mois gratuit dans la salle fifty nine', '2 places jump park', '2 places jump park', 'un coffret vignerons + goodies', 'un coffret vignerons + goodies', 'un coffret vignerons + goodies', 'jeu PS4', '1 casquette FCG', '1 casquette US', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', ' 1 calendrier spring', 'casquette raid + goodies', 'masque raid + goodies', '1 assiette fro + 1 assiette sauc (+ goodies à répartir selon nombre)', '1 assiette fro + 1 assiette sauc (+ goodies à répartir selon nombre)', '1 assiette fro + 1 assiette sauc (+ goodies à répartir selon nombre)', '1 assiette fro + 1 assiette sauc (+ goodies à répartir selon nombre)', '1 assiette fro + 1 assiette sauc (+ goodies à répartir selon nombre)', '1 carte noire', '1 carte noire', '1 carte noire', '1 carte noire', '1 carte noire', '1 carte blanche', '1 carte blanche', '1 carte blanche', '1 carte blanche', '1 carte blanche', 'réveil fcg', 'réveil fcg', '2 places phelma zic', 'jeu loup garou', 'colo violette + masque violet', 'colo violette + masque violet', '1 éventail + 1 sac à dos', '1 éventail + 1 sac à dos', '1 éventail + 1 sac à dos', '1 éventail + 1 sac à dos', '1 éventail + 1 sac à dos', '1 éventail + 1 sac à dos', 'une paire de raquette ', 'une paire de raquette ', 'une paire de raquette ', 'une paire de raquette ', 'une paire de raquette ', 'une paire de raquette ', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 frisbee', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 gourde', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', ' 1 tasse vype', 'polo phelma', 'polo phelma', 'polo phelma', 'polo phelma', 'polo phelma', 'livre occitanie ', 'livre occitanie ', 'livre occitanie ', 'livre occitanie ', 'livre occitanie ', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' 1 carnet', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena', ' bonnets de bains arena']
		if 'Tirer' in request.form :
			data = tirage_au_sort(L_owners, Lots)
			for winner in data:
				temp_user = db_gagnant(username=winner.nom,lot=winner.lot)
				db.session.add(temp_user)
				db.session.commit()
				user = User.query.filter_by(email=winner.nom).first()
				liste = user.cart + [winner.lot]
				User.query.filter_by(email=winner.nom).update({User.cart:liste})
				db.session.commit()"""
		db_gagnant.query.filter_by(username = "paulmaxime.martin@phelma.grenoble-inp.fr").update({db_gagnant.username:"clementguezennec@phelma.grenoble-inp.fr"})
		liste = []
		User.query.filter_by(email =  "paulmaxime.martin@phelma.grenoble-inp.fr").update({User.cart:liste})
		db.session.commit()
		data2=db_gagnant.query.all()
		return render_template("tirage.html", data2 = data2)
