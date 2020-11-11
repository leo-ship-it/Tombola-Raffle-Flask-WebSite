from tombola import app, db

if __name__ == "__main__":
	app.run(debug=False)
	db.create_all()
