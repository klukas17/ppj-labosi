from enum import Enum

# enumeracija za parsiranje ulazne .lan datoteke
class Lan_parsing_step(Enum):
	REGULAR_DEFINITIONS = 1
	STATES = 2
	LEXEMES = 3
	RULES = 4

regular_definitions = {}
states = []
lexemes = []
rules = []

# generiranje LA.py datoteke
if __name__ == "__main__":

	# parsiranje cijelog ulaza sa stdin
	lan_file = []
	try:
		while True:
			lan_file.append(input())
	except EOFError:
		pass

	# iniciranje koraka čitanja na čitanje regularnih definicija
	current_step = Lan_parsing_step.REGULAR_DEFINITIONS

	# obrada svake linije .lan datoteke
	rules_start = None
	for i in range(len(lan_file)):
		line = lan_file[i]

		# čitanje regularnih definicija
		if current_step == Lan_parsing_step.REGULAR_DEFINITIONS and line[0] != "%":
			definition = ""
			line = line[1:]
			while line[0] != "}":
				definition += line[0]
				line = line[1:]
			regular_definitions[definition] = line[2:]

		# čitanje stanja
		elif current_step == Lan_parsing_step.REGULAR_DEFINITIONS and line[0] == "%":
			current_step = Lan_parsing_step.STATES
			states = line[3:].split(" ")

		# čitanje leksičkih jedinki
		elif current_step == Lan_parsing_step.STATES:
			current_step = Lan_parsing_step.LEXEMES
			lexemes = line[3:].split(" ")

		# čitanje pravila
		elif current_step == Lan_parsing_step.LEXEMES:
			current_step = Lan_parsing_step.RULES
			rules_start = i
			break

	#TODO : parsiranje pravila (4. dio .lan datoteke)