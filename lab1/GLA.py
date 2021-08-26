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

# enumeracija za parsiranje ulazne .lan datoteke
class Lan_parsing_step():
	REGULAR_DEFINITIONS = 1
	STATES = 2
	LEXEMES = 3
	RULES = 4
	RULES_LEXEM = 5
	RULES_ARGS = 6

regular_definitions = {}
states = []
lexemes = []
rules = []

# generiranje LA.py datoteke
if __name__ == "__main__":

	# iniciranje koraka čitanja na čitanje regularnih definicija
	curr_step = Lan_parsing_step.REGULAR_DEFINITIONS
	curr_rule = None
	line = None

	# parsiranje ulaza sa stdin
	try:

		# čitanje regularnih definicija, stanja i leksičkih jedinki
		while True:
			line = input()

			# čitanje regularnih definicija
			if curr_step == Lan_parsing_step.REGULAR_DEFINITIONS and line[0] != "%":
				definition = ""
				line = line[1:]
				while line[0] != "}":
					definition += line[0]
					line = line[1:]
				regular_definitions[definition] = line[2:]

			# čitanje stanja
			elif curr_step <= Lan_parsing_step.STATES and line[0] == "%" and line[1] == "X":
				curr_step = Lan_parsing_step.STATES
				states = line[3:].split(" ")

			# čitanje leksičkih jedinki
			elif curr_step <= Lan_parsing_step.LEXEMES and line[0] == "%" and line[1] == "L":
				curr_step = Lan_parsing_step.LEXEMES
				lexemes = line[3:].split(" ")

			# čitanje pravila
			elif curr_step <= Lan_parsing_step.RULES and line[0] != "%":
				curr_step = Lan_parsing_step.RULES
				break

		# čitanje pravila
		while True:

			if line[0] == "<" and curr_step == Lan_parsing_step.RULES:
				state = ""
				line = line[1:]
				while line[0] != ">":
					state += line[0]
					line = line[1:]
				curr_rule = Rule(state, line[1:])

			elif line[0] == "{":
				curr_step = Lan_parsing_step.RULES_LEXEM

			elif line[0] == "}":
				rules.append(curr_rule)
				curr_rule = None
				curr_step = Lan_parsing_step.RULES

			elif curr_step == Lan_parsing_step.RULES_LEXEM:
				if line == "-":
					curr_rule.lexem = None
				else:
					curr_rule.lexem = line
				curr_step = Lan_parsing_step.RULES_ARGS

			elif curr_step == Lan_parsing_step.RULES_ARGS:
				arg_components = line.split(" ")
				if arg_components[0] == "NOVI_REDAK":
					curr_rule.NOVI_REDAK = True
				elif arg_components[0] == "UDJI_U_STANJE":
					curr_rule.UDJI_U_STANJE = True
					curr_rule.UDJI_U_STANJE_arg = arg_components[1]
				elif arg_components[0] == "VRATI_SE":
					curr_rule.VRATI_SE = True
					curr_rule.VRATI_SE_arg = int(arg_components[1])

			line = input()

	except EOFError:
		pass