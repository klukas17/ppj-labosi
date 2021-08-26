# enumeracija za parsiranje ulazne .lan datoteke
class Lan_parsing_step():
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

	# iniciranje koraka čitanja na čitanje regularnih definicija
	current_step = Lan_parsing_step.REGULAR_DEFINITIONS

	# parsiranje ulaza sa stdin
	try:
		while True:
			line = input()

				# čitanje regularnih definicija
			if current_step == Lan_parsing_step.REGULAR_DEFINITIONS and line[0] != "%":
				definition = ""
				line = line[1:]
				while line[0] != "}":
					definition += line[0]
					line = line[1:]
				regular_definitions[definition] = line[2:]

			# čitanje stanja
			elif current_step <= Lan_parsing_step.STATES and line[0] == "%" and line[1] == "X":
				current_step = Lan_parsing_step.STATES
				states = line[3:].split(" ")

			# čitanje leksičkih jedinki
			elif current_step <= Lan_parsing_step.LEXEMES and line[0] == "%" and line[1] == "L":
				current_step = Lan_parsing_step.LEXEMES
				lexemes = line[3:].split(" ")

			# čitanje pravila
			elif current_step <= Lan_parsing_step.RULES and line[0] != "%":
				current_step = Lan_parsing_step.RULES

				#TODO : parsiranje pravila (4. dio .lan datoteke)

	except EOFError:
		pass