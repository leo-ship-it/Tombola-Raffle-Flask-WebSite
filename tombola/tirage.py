import random

class gagnant :
	nom=""
	lot=""
	def __init__(self, nom, lot):
		self.nom = nom 
		self.lot = lot
	def __repr__(self):
		return f"gagnant('{self.nom}', '{self.lot}')"


def tirage_au_sort(L_users, L_lots): #L_users est une liste des noms d'utilisateurs, 
							 #chaque utilisateur est représenté une fois pour chaque tickets achetés
	L_gagnants = []
	for lot in L_lots:
		rang_gagnant = random.randint(0,len(L_users)-1)
		L_gagnants.append(gagnant(L_users[rang_gagnant], lot))
		L_users.pop(rang_gagnant)
	return L_gagnants
