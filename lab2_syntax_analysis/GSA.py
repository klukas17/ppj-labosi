from syn_utils import lr_item_utils

# enumeracija za tip znaka
class Symbol_type():
    NONTERMINAL = 1
    TERMINAL = 2

# oznaka kraja niza
class End_symbol():
    def __init__(self):
        self.name = "end_symbol"
    def __repr__(self) -> str:
        return "END_SYMBOL"

# klasa za modeliranje konačnog automata
class Automata():
    def __init__(self):
        self.start_state = None
        self.transition_function = {}

# funkcija za dohvaćanje pojedine LR stavke (objekti LR stavke su jedinstveni objekti -> obrazac singleton)
def fetch_lr_item(left_side: str, right_side: tuple, index: int, follow_set: tuple) -> lr_item_utils.LR_item:
    if (left_side, right_side, index, follow_set) not in lr_items:
        lr_items[(left_side, right_side, index, follow_set)] = lr_item_utils.LR_item(left_side, right_side, index, follow_set)
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

# funkcija koja gradi e-NKA čija stanja su LR stavke
def build_enfa() -> Automata:
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
            e_nfa.transition_function[(curr_lr_state, curr_lr_state.right_side[curr_lr_state.index])].append(new_lr_state)

        # ako se točka nalazi ispred nezavršnog znaka
    pass

    return e_nfa

# funkcija koja gradi DKA na temelju danog e-NKA
def build_dfa() -> Automata:
    pass

# funkcija koja gradi tablicu parsiranja na temelju danog DKA
def build_parser_table() -> dict:
    pass

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
    while new_start_symbol in nonterminal_symbols or new_start_symbol in terminal_symbols:
        new_start_symbol += '\''
    nonterminal_symbols.insert(0, new_start_symbol)
    productions[new_start_symbol] = [((start_symbol,), 0)]
    symbol_type[new_start_symbol] = Symbol_type.NONTERMINAL

    # računanje relacije ZAPOČINJE za produkcije gramatike
    starts_with = lr_item_utils.calculate_relation_starts(nonterminal_symbols, terminal_symbols, productions)

    # stvaranje e-NKA čija stanja su LR stavke
    e_nfa = build_enfa()

    # stvaranje DKA na temelju e-NKA
    dfa = build_dfa(e_nfa)

    # stvaranje tablice parsiranja na temelju DKA
    parser_table = build_parser_table(dfa)

    # TODO: serijalizacija objekta parser_table u neku datoteku