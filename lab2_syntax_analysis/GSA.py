# enumeracija za tip znaka
class Symbol_type():
    NONTERMINAL = 1
    TERMINAL = 2

# oznaka kraja niza
class End_symbol():
    def __init__(self):
        self.name = "end_symbol"
    def __repr__(self) -> str:
        return "END SYMBOL"

# klasa za modeliranje konačnog automata
class Automata():
    def __init__(self):
        self.start_state = None
        self.transition_function = {}

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

# funkcija za dohvaćanje pojedine LR stavke (objekti LR stavke su jedinstveni objekti -> obrazac singleton)
def fetch_lr_item(left_side: str, right_side: tuple, index: int, follow_set: tuple) -> LR_item:
    if (left_side, right_side, index, follow_set) not in lr_items:
        lr_items[(left_side, right_side, index, follow_set)] = LR_item(left_side, right_side, index, follow_set)
    return lr_items[(left_side, right_side, index, follow_set)] 

# deklaracija globalnih varijabli
nonterminal_symbols = []
terminal_symbols = []
synchronisation_symbols = set()
productions = {}
symbol_type = {}
lr_items = {}
end_symbol = End_symbol()

# funkcija kojom se dohvaća jedinstven objekt koji označava kraj niza -> obrazac singleton
def fetch_end_symbol() -> End_symbol:
    return end_symbol

# generiranje SA.py datoteke
if __name__ == "__main__":

    # varijable za čitanje 
    curr_nonterminal = None
    production_index = 0
    
    # parsiranje ulaza sa stdin
    try:

        while True:
            line = input()
            if line == "":
                break

            # čitanje nezavršnih znakova gramatike
            if len(line) >= 2 and line[:2] == "%V":
                nonterminal_symbols = line[3:].split(" ") if len(line) >= 3 else []

            # čitanje završnih znakova gramatike
            elif len(line) >= 2 and line[:2] == "%T":
                terminal_symbols = line[3:].split(" ") if len(line) >= 3 else []

            # čitanje sinkronizacijskih znakova
            elif len(line) >= 4 and line[:4] == "%Syn":
                synchronisation_symbols = set(line[5:].split(" ")) if len(line) >= 5 else set()

            # čitanje produkcija gramatike
            else:
                
                # čitamo lijevu stranu produkcije
                if line[0] != " ":
                    curr_nonterminal = line
                    if curr_nonterminal not in productions:
                        productions[curr_nonterminal] = []

                # čitamo desnu stranu produkcije
                else:
                    production_index += 1
                    productions[curr_nonterminal].append((tuple(line[1:].split(" ")), production_index))

    except EOFError:
        pass

    for symbol in nonterminal_symbols:
        symbol_type[symbol] = Symbol_type.NONTERMINAL

    for symbol in terminal_symbols:
        symbol_type[symbol] = Symbol_type.TERMINAL

    # ubacivanje početnog nezavršnog znaka u gramatiku
    start_symbol = nonterminal_symbols[0]
    new_start_symbol = start_symbol + '\''
    nonterminal_symbols.insert(0, new_start_symbol)
    productions[new_start_symbol] = [(start_symbol, 0)]
    symbol_type[new_start_symbol] = Symbol_type.NONTERMINAL

    # stvaranje epsilon NKA
    e_nfa = Automata()

    # dodavanje početnog stanja e-NKA u automat
    e_nfa.start_state = fetch_lr_item(new_start_symbol, tuple([start_symbol]), 0, (fetch_end_symbol(),))
    lr_queue = [e_nfa.start_state]
    visited = set()
    visited.add(e_nfa.start_state)

    # gradnja epsilon NKA automata
    while len(lr_queue) > 0:
        curr_lr_state = lr_queue[0]
        lr_queue = lr_queue[1:]

        # pomicanje točke udesno u produkciji
        if curr_lr_state.index < len(curr_lr_state.right_side) and curr_lr_state.right_side != ("$",):
            new_lr_state = fetch_lr_item(curr_lr_state.left_side, curr_lr_state.right_side, curr_lr_state.index + 1, curr_lr_state.follow_set)
            if new_lr_state not in visited:
                visited.add(new_lr_state)
                lr_queue.append(new_lr_state)
            if ((curr_lr_state), curr_lr_state.right_side[curr_lr_state.index]) not in e_nfa.transition_function:
                e_nfa.transition_function[(curr_lr_state), curr_lr_state.right_side[curr_lr_state.index]] = []
            e_nfa.transition_function[(curr_lr_state), curr_lr_state.right_side[curr_lr_state.index]].append(new_lr_state)