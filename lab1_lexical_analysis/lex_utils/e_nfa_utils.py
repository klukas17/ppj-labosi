from sys import path
path[0] = path[0][:path[0].rfind("/")]
from lex_utils import regex_utils
from typing import Tuple

# klasa za definiranje automata koji odgovara jednom definiranom pravilu
class E_NFA():
    def __init__(self, regex_tree: regex_utils.RegularSubexpression):
        self.index = 0
        self.start_state = "s_" + str(self.index)
        self.end_state = "s_" + str(self.index + 1)
        self.transition_function = {}

        self.index += 2
        (starting, ending) = self.create_automata(regex_tree)
        self.transition_function[(self.start_state, "$")] = starting
        self.transition_function[(ending, "$")] = self.end_state

    # funkcija koja na temelju izgrađenog stabla regularnog izraza gradi konačni automat
    def create_automata(self, regex_tree: regex_utils.RegularSubexpression) -> Tuple[str, str]:

        starting = "s_" + str(self.index)
        ending = "s_" + str(self.index + 1)
        self.index += 2
        
        if isinstance(regex_tree, regex_utils.Symbol):
            self.transition_function[(starting, regex_tree.elements)] = ending
    
        elif isinstance(regex_tree, regex_utils.Alternation):
            self.transition_function[(starting, "$")] = []
            for sub_ex in regex_tree.elements:
                (s, e) = self.create_automata(sub_ex)
                self.transition_function[(starting, "$")].append(s)
                self.transition_function[(e, "$")] = ending

        elif isinstance(regex_tree, regex_utils.Concatenation):
            curr = starting
            for sub_ex in regex_tree.elements:
                (s, e) = self.create_automata(sub_ex)
                self.transition_function[(curr), "$"] = s
                curr = e
            self.transition_function[(curr, "$")] = ending

        elif isinstance(regex_tree, regex_utils.Kleene):
            (s, e) = self.create_automata(regex_tree.elements[0])
            self.transition_function[(starting, "$")] = [s, ending]
            self.transition_function[(e, "$")] = [s, ending]

        return (starting, ending)