from sys import path
path[0] = path[0][:path[0].rfind("/")]
from lex_utils import regex_utils

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
		self.enka = None

	# funkcija koja na temelju regularnog izraza stvara konačni automat 
	def create_enka(self) -> None:
		self.enka = ENKA(0, "s_fin", True, None)
		alternation_list = regex_utils.find_alternations(self.regex)

# klasa za definiranje automata koji odgovara jednom definiranom pravilu
class ENKA():
    def __init__(self, start: int, acceptable: str, is_root: bool, root_enka_dict: dict):
        self.startState = "s_" + str(start)
        self.acceptableState = acceptable if is_root else None
        self.transitionFunction = {} if is_root else root_enka_dict