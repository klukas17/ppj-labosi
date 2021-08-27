# klasa za pravilo leksičkog analizatora
class Rule():
	def __init__(self, state, regex):
		self.state = state
		self.regex = regex
		self.lexem = None
		self.NOVI_REDAK = False
		self.UDJI_U_STANJE = False
		self.UDJI_U_STANJE_arg = None
		self.VRATI_SE = False
		self.VRATI_SE_arg = None
		self.enka = None

# klasa za definiranje automata koji odgovara jednom definiranom pravilu
class ENKA():
    def __init__(self):
        self.states = []
        self.symbols = []
        self.acceptableStates = []
        self.startState = None
        self.transitionFunction = {}