from typing import Union

# klasa za modeliranje podizraza regularnog izraza
class RegularSubexpression():

	def __init__(self):
		self.elements = []

# klasa za modeliranje alternacije
class Alternation(RegularSubexpression):

	def __init__(self):
		RegularSubexpression.__init__(self)

	def print(self, indents: int) -> None:
		for _ in range(indents):
			print("  ", end="")
		print("Alternation")
		for sub_el in self.elements:
			sub_el.print(indents + 1)

# klasa za modeliranje konkatenacije
class Concatenation(RegularSubexpression):

	def __init__(self):
		RegularSubexpression.__init__(self)

	def print(self, indents: int) -> None:
		for _ in range(indents):
			print("  ", end="")
		print("Concatenation")
		for sub_el in self.elements:
			sub_el.print(indents + 1)

# klasa za modeliranje Kleeneovog operatora
class Kleene(RegularSubexpression):

	def __init__(self):
		RegularSubexpression.__init__(self)

	def print(self, indents: int) -> None:
		for _ in range(indents):
			print("  ", end="")
		print("Kleene")
		for sub_el in self.elements:
			sub_el.print(indents + 1)

# klasa za modeliranje elementare jedinke regularnog izraza tj. jednog simbola abecede
class Symbol(RegularSubexpression):

	def __init__(self):
		RegularSubexpression.__init__(self)

	def print(self, indents: int) -> None:
		for _ in range(indents):
			print("  ", end="")
		print("Symbol -> " + str(self.elements))

	# funkcija koja od dane elementarne jedinke gradi regularno podstablo
	def build_regex_tree(self) -> RegularSubexpression:
		ret_val = self

		alternations = find_alternations(self.elements)

		if len(alternations) == 1:
			concatenations = find_concatenations(alternations[0])

			if len(concatenations) == 1:
				kleene = check_Kleene(concatenations[0])

				if kleene == False:
					pass # regularni podizraz je jedan simbol abecede

				else:
					ret_val = Kleene()

					e = Symbol()
					e.elements = kleene
					ret_val.elements.append(e)

					ret_val.elements[0] = ret_val.elements[0].build_regex_tree()

			else:
				ret_val = Concatenation()

				for r in concatenations:
					e = Symbol()
					e.elements = r
					ret_val.elements.append(e)

				for i in range(len(ret_val.elements)):
				    ret_val.elements[i] = ret_val.elements[i].build_regex_tree()

		else:
			ret_val = Alternation()

			for r in alternations:
				e = Symbol()
				e.elements = r
				ret_val.elements.append(e)

			for i in range(len(ret_val.elements)):
				ret_val.elements[i] = ret_val.elements[i].build_regex_tree()

		return ret_val

# funkcija koja u regularnom izrazu briše zagrade koje ga okružuju
def trim_enclosing_parentheses(ex: str) -> str:
	stop = False
	while ex[0] == "(" and ex[len(ex)-1] == ")" and not stop:
		parentheses = 1
		for i in range(1, len(ex) - 1):
			if ex[i] == "(":
				parentheses += 1
			elif ex[i] == ")":
				parentheses -= 1
			if parentheses == 0:
				stop = True
				break
		if not stop:
			ex = ex[1:len(ex)-1]
	return ex

# funkcija koja u regularnom izrazu odvaja dijelove izraza povezane operatorom izbora |
def find_alternations(regex: str) -> list:
	alternations = []
	parentheses = 0
	curr_ex = ""
	end = False
	regex = trim_enclosing_parentheses(regex)

	i = 0
	while i < len(regex):
		prefixed = 0

		while regex[i] == "\\":
			prefixed = 1 - prefixed
			curr_ex += regex[i]
			i += 1
			if i == len(regex):
				end = True
				break
			
		if end:
			break

		if regex[i] == "|" and prefixed == 0 and parentheses == 0:
			alternations.append(trim_enclosing_parentheses(curr_ex))
			curr_ex = ""

		else:

			curr_ex += regex[i]

			if regex[i] == "(" and prefixed == 0:
				parentheses += 1

			elif regex[i] == ")" and prefixed == 0:
				parentheses -= 1

		i += 1

	alternations.append(trim_enclosing_parentheses(curr_ex))

	return alternations

# funkcija koja u regularnom izrazu odvaja dijelove izraza koji su međusobno konkatenirani
def find_concatenations(regex: str) -> list:
	concatenations = []
	curr_ex = ""
	parentheses = 0
	end = False
	regex = trim_enclosing_parentheses(regex)

	i = 0
	while i < len(regex):

		while i < len(regex) and regex[i] == "\\":
			curr_ex += regex[i:i+2]
			i += 2
			if parentheses == 0:
				if i < len(regex) and regex[i] == "*":
					curr_ex += regex[i]
					i += 1
				concatenations.append(trim_enclosing_parentheses(curr_ex))
				curr_ex = ""
			if i == len(regex):
				end = True
				break
			if regex[i] == "*":
				curr_ex += regex[i]
				i += 1

		if end:
			break

		if regex[i] == "(":
			parentheses += 1

		elif regex[i] == ")":
			parentheses -= 1

		curr_ex += regex[i]
		i += 1
		if i < len(regex) and regex[i] == "*":
			curr_ex += regex[i]
			i += 1
		if parentheses == 0:
			concatenations.append(trim_enclosing_parentheses(curr_ex))
			curr_ex = ""
	
	return concatenations

# funkcija provjerava je li dani regularni izraz okružen Kleeneovim operatorom *
def check_Kleene(regex: str) -> Union[bool, str]:
	regex = trim_enclosing_parentheses(regex)

	if regex[len(regex) - 1] == "*":
		prefixed = 0

		i = len(regex) - 1
		while i >= 0:
			i -= 1
			if regex[i] != "\\":
				break
			else:
				prefixed = 1 - prefixed

		if prefixed == 0:
			return trim_enclosing_parentheses(regex[:len(regex)-1])
			
		else:
			return False
	
	else:
		return False