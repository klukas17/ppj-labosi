# klasa za modeliranje LR stavke
class LR_item():
    def __init__(self, left_side: str, right_side: tuple, index: int, follow_set: tuple):
        self.left_side = left_side
        self.right_side = right_side
        self.index = index
        self.follow_set = follow_set
    def __repr__(self) -> str:
        ret_val = self.left_side + " ->"
        for el in self.right_side:
            ret_val += " " + el
        ret_val += ", " + str(self.index) + ", {"
        for el in self.follow_set:
            ret_val += str(el) + ", "
        ret_val = ret_val[:len(ret_val) - 2]
        ret_val += "}"
        return ret_val

# funkcija računa relaciju ZAPOČINJE za dane produkcije gramatike
def calculate_relation_starts(nonterminal_symbols: list, terminal_symbols: list, productions: dict):
    pass