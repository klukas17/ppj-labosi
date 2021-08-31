from sys import stdin
from lex_utils import rule

# enumeracija za parsiranje ulazne .lan datoteke
class Lan_parsing_step():
	REGULAR_DEFINITIONS = 1
	STATES = 2
	LEXEMES = 3
	RULES = 4
	RULES_LEXEM = 5
	RULES_ARGS = 6

# enumeracija za pretvaranje regularnih definicija u regularne izraze
class Reg_def_parsing_step():
	NORMAL_MODE = 1
	REG_DEF_REFERENCE_MODE = 2

# deklaracija globalnih varijabli
regular_definitions = {}
states = []
lexemes = []
rules = []

# funkcija za pretvaranje regularne definicije u regularni izraz
def reg_def_to_reg_ex(reg_def_body: str) -> str:

	global regular_definitions

	reg_ex = ""
	reg_def_referenced = None
	prefixed = 0
	curr_state = Reg_def_parsing_step.NORMAL_MODE

	i = 0
	while i < len(reg_def_body):

		prefixed = 0

		while reg_def_body[i] == "\\":
			reg_ex += reg_def_body[i]
			i += 1
			prefixed = 1 - prefixed

		if curr_state == Reg_def_parsing_step.NORMAL_MODE and reg_def_body[i] == "{" and not prefixed:
			curr_state = Reg_def_parsing_step.REG_DEF_REFERENCE_MODE
			reg_def_referenced = ""

		elif curr_state == Reg_def_parsing_step.REG_DEF_REFERENCE_MODE and reg_def_body[i] == "}" and not prefixed:
			curr_state = Reg_def_parsing_step.NORMAL_MODE
			reg_ex += "(" + regular_definitions[reg_def_referenced] + ")"

		elif curr_state == Reg_def_parsing_step.REG_DEF_REFERENCE_MODE:
			reg_def_referenced += reg_def_body[i]

		else:
			reg_ex += reg_def_body[i]
			
		i += 1

	return reg_ex

# generiranje LA.py datoteke
if __name__ == "__main__":

	# iniciranje koraka čitanja na čitanje regularnih definicija i definiranje ostalih varijabli
	curr_step = Lan_parsing_step.REGULAR_DEFINITIONS
	curr_rule = None
	line = None
	regular_definitions_raw = []

	# parsiranje ulaza sa stdin
	try:

		# čitanje regularnih definicija, stanja i leksičkih jedinki
		while True:
			line = ""
			while (c := stdin.read(1)) != "\n":
				line += c

			# čitanje regularnih definicija
			if curr_step == Lan_parsing_step.REGULAR_DEFINITIONS and line[0] != "%":
				definition = ""
				line = line[1:]
				while line[0] != "}":
					definition += line[0]
					line = line[1:]
				regular_definitions_raw.append((definition, line[2:])) 

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
				curr_rule = rule.Rule(state, line[1:])

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

	# pretvorba regularnih definicija u regularne izraze u deklaraciji regularnih definicija
	for reg_def in regular_definitions_raw:
		reg_def_name = reg_def[0]
		reg_def_body = reg_def[1]
		regular_definitions[reg_def_name] = reg_def_to_reg_ex(reg_def_body)

	# pretvorba regularnih definicija u regularne izraze u deklaraciji pravila
	for r in rules:
		r.regex = reg_def_to_reg_ex(r.regex)

	# stvaranje automata za svako pravilo
	for r in rules:
		r.create_enka()

	# stvaranje datoteke s opisom svih pravila
	file = open("analizator/rules.txt", "w")

	# serijalizacija izračunatih pravila
	for r in rules:

		file.write("{\n")

		file.write(r.state + " ")

		if r.lexem is None:
			file.write("-" + " ")
		else:
			file.write(r.lexem + " ")

		if r.NOVI_REDAK:
			file.write("1" + " ")
		else:
			file.write("0" + " ")

		if r.UDJI_U_STANJE:
			file.write("1" + " " + r.UDJI_U_STANJE_arg + " ")
		else:
			file.write("0" + " " + "-" + " ")

		if r.VRATI_SE:
			file.write("1" + " " + str(r.VRATI_SE_arg) + " ")
		else:
			file.write("0" + " " + "-" + " ")

		file.write("\n")

		file.write("{\n")

		file.write("{\n")
		file.write(r.enfa.start_state + " " + r.enfa.end_state)
		file.write("\n")
		file.write("}\n")

		for transition in r.enfa.transition_function:
			file.write(transition[0] + " " + transition[1])
			for el in r.enfa.transition_function[transition]:
				file.write(" " + el)
			file.write("\n")

		file.write("}\n")

		file.write("}\n")

	file.write(states[0])

	file.close()