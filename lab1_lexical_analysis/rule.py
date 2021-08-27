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
		alternation_list = Rule.find_alternations(self.regex)

	# funkcija koja u regularnom izrazu odvaja dijelove izraza povezane operatorom izbora |
	def find_alternations(regex: str) -> list:
		alternations = []
		prefixed = 0
		parentheses = 0
		curr_ex = ""

		for i in range(len(regex)):
			if regex[i] == "|" and prefixed == 0 and parentheses == 0:
				alternations.append(curr_ex)
				curr_ex = ""
				prefixed = 0

			else:
				curr_ex += regex[i]

				if regex[i] == "\\":
					prefixed = 1 - prefixed

				else:
					prefixed = 0

					if regex[i] == "(" and prefixed == 0:
						parentheses += 1

					elif regex[i] == ")" and prefixed == 0:
						parentheses -= 1

		alternations.append(curr_ex)

		return alternations

	# funkcija koja iz regularnog izraza briše eventualne zagrade koje ga okružuju
	def trim_enclosing_parentheses(ex: str) -> str:
		while ex[0] == "(" and ex[len(ex)-1] == ")":
			ex = ex[1:len(ex)-1]
		return ex

	# TODO: concatenation, Kleene

# klasa za definiranje automata koji odgovara jednom definiranom pravilu
class ENKA():
    def __init__(self, start: int, acceptable: str, is_root: bool, root_enka_dict: dict):
        self.startState = "s_" + str(start)
        self.acceptableState = acceptable if is_root else None
        self.transitionFunction = {} if is_root else root_enka_dict