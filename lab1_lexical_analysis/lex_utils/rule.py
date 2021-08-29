from sys import path
path[0] = path[0][:path[0].rfind("/")]
from lex_utils import regex_utils, e_nfa_utils

# klasa za pravilo leksičkog analizatora
class Rule():
	def __init__(self, state: str, regex: str):
		self.state = state
		self.regex = regex
		self.lexem = None
		self.NOVI_REDAK = False
		self.UDJI_U_STANJE = False
		self.UDJI_U_STANJE_arg = None
		self.VRATI_SE = False
		self.VRATI_SE_arg = None
		self.enfa = None

	# funkcija koja na temelju regularnog izraza stvara konačni automat 
	def create_enka(self) -> None:
		regex_tree = regex_utils.Symbol()
		regex_tree.elements = self.regex
		regex_tree = regex_tree.build_regex_tree()
		self.enfa = e_nfa_utils.E_NFA(regex_tree)