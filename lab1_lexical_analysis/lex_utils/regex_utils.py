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

# klasa za modeliranje elementare jedinke regularnog izraza
class Elementary(RegularSubexpression):
	def __init__(self):
		RegularSubexpression.__init__(self)
	def print(self, indents: int) -> None:
		for _ in range(indents):
			print("  ", end="")
		print("Elementary -> " + str(self.elements))

# funkcija koja u regularnom izrazu odvaja dijelove izraza povezane operatorom izbora |
def find_alternations(regex: str) -> list:
	alternations = []
	parentheses = 0
	curr_ex = ""
	end = False

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

# funkcija koja gradi stablo razrješavajući operator izbora |
def list_alternations(regex: str) -> Union[str, list]:
	result = find_alternations(trim_enclosing_parentheses(regex))

	if len(result) == 1:
		ret_val = Elementary()
		ret_val.elements = result[0]

	else:
		ret_list = []
		for r in result:
			ret_list.append(list_alternations(r))
		ret_val = Alternation()
		ret_val.elements = ret_list

	return ret_val

# funkcija koja u regularnom izrazu odvaja dijelove izraza koji su međusobno konkatenirani
def find_concatenations(regex: str) -> list:
	concatenations = []
	curr_ex = ""
	parentheses = 0
	end = False

	i = 0
	while i < len(regex):

		while regex[i] == "\\":
			curr_ex += regex[i:i+2]
			i += 2
			if parentheses == 0:
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

# funkcija koja gradi stablo razrješavajući operator konkatenacije
def list_concatenations(regex: str) -> Union[str, list]:
	result = find_concatenations(trim_enclosing_parentheses(regex))

	if len(result) == 1:
		ret_val = Elementary()
		ret_val.elements = result[0]

	else :
		ret_list = []
		for r in result:
			ret_list.append(list_alternations(r))
		ret_val = Concatenation()
		ret_val.elements = ret_list

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

# funkcija koja na temelju regularnog izraza gradi stablo elementarnih jedinki
def create_regex_tree(regex: str) -> Union[str, list]:
	tree = list_alternations(regex)
	if isinstance(tree, Elementary):
		tree = list_concatenations(tree.elements)
	else:
		for i in range(len(tree.elements)):
			tree.elements[i] = list_concatenations(tree.elements[i].elements)
			
	return tree