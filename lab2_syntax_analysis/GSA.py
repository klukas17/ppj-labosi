from syn_utils import lr_item_utils

# enumeracija za tip znaka
class Symbol_type():
    NONTERMINAL = 1
    TERMINAL = 2

# enumeracija za tip akcije
class Action_type():
    REDUCE = 1
    SHIFT = 2

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

# klasa za modeliranje akcije parsera
class Action():
    def __init__(self):
        pass

class Reduce(Action):
    def __init__(self, left_side: str, right_side: tuple):
        Action.__init__(self)
        self.left_side = left_side
        self.right_side = right_side

class Shift(Action):
    def __init__(self, new_state: int):
        Action.__init__(self)
        self.new_state = new_state

# funkcija za dohvaćanje pojedine LR stavke (objekti LR stavke su jedinstveni objekti -> obrazac singleton)
def fetch_lr_item(left_side: str, right_side: tuple, index: int, follow_set: tuple) -> lr_item_utils.LR_item:
    if (left_side, right_side, index, follow_set) not in lr_items:
        lr_items[(left_side, right_side, index, follow_set)] = lr_item_utils.LR_item(left_side, right_side, index, follow_set)
    return lr_items[(left_side, right_side, index, follow_set)] 

# liste nezavršnih i završnih znakova gramatike, onim redom kojim se pojavljuju u ulaznoj .san datoteci
nonterminal_symbols = []
terminal_symbols = []

# skup svih sinkronizacijskih znakova
synchronisation_symbols = set()

# riječnik u kojem se pod ključevima koji su završni znakovi gramatike nalaze liste svih desnih strana produkcija za dane ključeve
productions = {}

# riječnik u kojem se pod ključevima koji su hash sažeci LR stavki nalaze reference na jedinstvene objekte LR stavki
lr_items = {}

# riječnik u kojem se pod ključevima koju su simboli gramatike (završni ili nezavršni) nalazi informacija o tome je li dani simbol završni ili nezavršni znak gramatike
symbol_type = {}

# skup svih nezavršnih znakova gramatike koji mogu generirati prazni niz, tzv. prazni znakovi
empty_nonterminal_symbols = None

# riječnik u kojem se pod ključevima simbola nalazi informacija koji simboli gramatike se nalaze u skupu ZAPOČINJE danog ključa
starts_with = None

# riječnici u kojima se preko objetka LR stavke može doći do njenog pripadnog indeksa, i preko indeksa može doći do pripadnog objetka LR stavke
lr_dict_item = {}
lr_dict_index = {}

# riječnik koji pod ključem tuple koji označava stanje DKA čuva redni broj tog stanja za gradnju parsera
parser_states = {}

# lista u kojoj se čuvaju sve nejednoznačnosti u gramatici
conflicts = []

# jedinstvena varijabla pod kojom se čuva oznaka kraja niza
end_symbol = End_symbol()

# funkcija kojom se dohvaća jedinstven objekt koji označava kraj niza -> obrazac singleton
def fetch_end_symbol() -> End_symbol:
    return end_symbol

# funkcija koja gradi e-NKA čija stanja su LR stavke
def build_enfa() -> Automata:
    global lr_dict_item
    global lr_dict_index

    e_nfa = Automata()

    # početno stanje e-NKA
    e_nfa.start_state = fetch_lr_item(new_start_symbol, tuple([start_symbol]), 0, (fetch_end_symbol(),))
    
    # varijabla za spremanje pronađenih LR stavki (bit će korisno za konstrukciju DKA)
    lr_items_list = []
    lr_items_list.append(e_nfa.start_state)

    # red za obradu svih LR stavki koje čine stanja e-NKA
    lr_queue = [e_nfa.start_state]

    # skup u kojem se čuvaju sve otkrivene LR stavke radi izbjegavanja cirkularnih ovisnosti i beskonačne petlje kao rezultat
    found_lr_items = set()
    found_lr_items.add(e_nfa.start_state)

    # obrada svih LR stavki
    while len(lr_queue) > 0:
        curr_lr_state = lr_queue.pop(0)

        # pomicanje točke udesno u produkciji
        if curr_lr_state.index < len(curr_lr_state.right_side) and curr_lr_state.right_side != ("$",):
            new_lr_state = fetch_lr_item(curr_lr_state.left_side, curr_lr_state.right_side, curr_lr_state.index + 1, curr_lr_state.follow_set)
            if new_lr_state not in found_lr_items:
                found_lr_items.add(new_lr_state)
                lr_queue.append(new_lr_state)
                lr_items_list.append(new_lr_state)
            if (curr_lr_state, curr_lr_state.right_side[curr_lr_state.index]) not in e_nfa.transition_function:
                e_nfa.transition_function[(curr_lr_state, curr_lr_state.right_side[curr_lr_state.index])] = []
            e_nfa.transition_function[(curr_lr_state, curr_lr_state.right_side[curr_lr_state.index])].append(new_lr_state)

        # ako se točka nalazi ispred nezavršnog znaka, potrebno je obraditi taj nezavršni znak i dodati nove prijelaze
        if curr_lr_state.index < len(curr_lr_state.right_side) and curr_lr_state.right_side != ("$",) and symbol_type[curr_lr_state.right_side[curr_lr_state.index]] == Symbol_type.NONTERMINAL:
            
            # varijabla pomoću koje pamtimo jesmo li došli do kraja niza (i moramo li u novoj LR stavci nasljediti simbole koji slijede staru LR stavku)
            end_reached = False

            # skup svih simbola koji slijede novu LR stavku
            symbol_set = set()

            # prvi indeks pod kojim tražimo znakove koji slijede novu LR stavku
            index = curr_lr_state.index + 1

            # računanje skupa znakova pridruženih LR stavci
            while index < len(curr_lr_state.right_side) and not end_reached:
                follow_set = set()
                curr_symbol = curr_lr_state.right_side[index]
                for s in starts_with[curr_symbol]:
                    if starts_with[curr_symbol][s]:
                        follow_set.add(s) 
                symbol_set = symbol_set.union(follow_set)
                if curr_symbol not in empty_nonterminal_symbols:
                    end_reached = True
                index += 1
            if not end_reached:
                symbol_set = symbol_set.union(set(curr_lr_state.follow_set))

            # u skupu znakova se nalaze samo završni znakovi gramatike, pa uklanjamo nezavršne
            symbol_set = symbol_set.difference(set(nonterminal_symbols))

            # dodavanje epsilon prijelaza u izračunatu LR stavku
            for production in productions[curr_lr_state.right_side[curr_lr_state.index]]:

                # production je prethdno bio tuple, gdje je na nultom mjestu sama produkcija, a na prvom redni broj pojavljivanja produkcije u .san datoteci
                production = production[0]

                # sortiranje novog skupa znakova leksikografski
                symbol_set = list(symbol_set)
                end_symbol_in_set = False
                if fetch_end_symbol() in symbol_set:
                    end_symbol_in_set = True
                    symbol_set.remove(fetch_end_symbol())
                else:
                    end_symbol_in_set = False
                symbol_set.sort()
                if end_symbol_in_set:
                    symbol_set.append(fetch_end_symbol())

                new_lr_state = fetch_lr_item(curr_lr_state.right_side[curr_lr_state.index], production, 0, tuple(symbol_set))
                if new_lr_state not in found_lr_items:
                    found_lr_items.add(new_lr_state)
                    lr_queue.append(new_lr_state)
                    lr_items_list.append(new_lr_state)
                if (curr_lr_state, "$") not in e_nfa.transition_function:
                    e_nfa.transition_function[(curr_lr_state), "$"] = []
                e_nfa.transition_function[(curr_lr_state, "$")].append(new_lr_state)

    # izgradnja riječnika potrebnih za konstrukciju DKA
    for i in range(len(lr_items_list)):
        lr_dict_index[i] = lr_items_list[i]
        lr_dict_item[lr_items_list[i]] = i

    return e_nfa

# funkcija koja gradi DKA na temelju danog e-NKA
def build_dfa(e_nfa: Automata) -> Automata:
    dfa = Automata()

    # skup svih stanja DKA
    dfa_states = set()

    # LR stavke koje čine početno stanje DKA
    dfa_start_state_lr_items = []

    # red kojim obrađujemo LR stavke koje pripadaju početnom stanju DKA
    dfa_start_state_queue = [e_nfa.start_state]

    # skup u kojem se čuvaju sve otkrivene LR stavke radi izbjegavanja cirkularnih ovisnosti i beskonačne petlje kao rezultat
    found_lr_items = set()
    found_lr_items.add(e_nfa.start_state)

    # trenutni indeks za stanja parsera
    parser_index = 0

    # računanje epsilon okruženja početnog stanja e-NKA
    while len(dfa_start_state_queue) > 0:
        curr_lr_item = dfa_start_state_queue.pop(0)
        dfa_start_state_lr_items.append(curr_lr_item)

        # provjera ima li trenutno stanje epsilon produkcije
        if (curr_lr_item, "$") in e_nfa.transition_function:

            # dodavanje svih desnih strana epsilon produkcija u red za obradu LR stavki
            for lr_item in e_nfa.transition_function[(curr_lr_item, "$")]:
                if lr_item not in found_lr_items:
                    found_lr_items.add(lr_item)
                    dfa_start_state_queue.append(lr_item)

    # izgradnja početnog stanja DKA, stanja DKA čine indeksi LR stavki koje se nalaze unutar stanja DKA
    dfa.start_state = []
    for lr_item in dfa_start_state_lr_items:
        dfa.start_state.append(lr_dict_item[lr_item])
    dfa.start_state.sort()
    dfa.start_state = tuple(dfa.start_state)
    
    # dodavanje početnog stanja DKA u skup svih stanja DKA
    dfa_states.add(dfa.start_state)

    # dodavanje početnog stanja DKA u skup stanja parsera
    parser_states[dfa.start_state] = parser_index
    parser_index += 1

    # obrada svih stanja DKA kojeg trenutno gradimo
    dfa_state_queue = [dfa.start_state]
    while len(dfa_state_queue) > 0:
        curr_dfa_state = dfa_state_queue.pop(0)

        # računanje skupa simbola za koje trenutno stanje DKA ima definiran prijelaz
        transition_symbols = set()
        for component in curr_dfa_state:

            # dekodiranje pojedine LR stavke unutar stanja DKA preko njenog jednistvenog indeksa
            lr_item = lr_dict_index[component]
            if lr_item.right_side != ("$",) and lr_item.index < len(lr_item.right_side):
                transition_symbols.add(lr_item.right_side[lr_item.index])
        
        # pretvorba skupa simbola za koje je definiran prijelaz u listu, i potom sortiranje liste radi uniformnosti
        transition_symbols = list(transition_symbols)
        transition_symbols.sort()

        # obrada prijelaza za svako stanje DKA
        for symbol in transition_symbols:

            # lista svih komponenti novog stanja DKA
            new_dfa_state_lr_items = []

            # red za obradu LR stavki
            lr_queue = []

            # skup svih otkrivenih LR stavi
            discovered_lr_items = set()

            for component in curr_dfa_state:
                
                # dekodiranje pojedine LR stavke unutar stanja DKA preko njenog jednistvenog indeksa
                lr_item = lr_dict_index[component]
                if (lr_item, symbol) in e_nfa.transition_function:
                    lr_queue.append(e_nfa.transition_function[(lr_item, symbol)][0])
                    discovered_lr_items.add(e_nfa.transition_function[(lr_item, symbol)][0])

            # obrada svih LR stavki koje su dijelom novog stanja DKA
            while len(lr_queue) > 0:
                curr_lr_item = lr_queue.pop(0)
                new_dfa_state_lr_items.append(curr_lr_item)
                
                # računanje epsilon okruženja trenutne LR stavke
                if (curr_lr_item, "$") in e_nfa.transition_function:
                    for lr_item in e_nfa.transition_function[(curr_lr_item, "$")]:
                        if lr_item not in discovered_lr_items:
                            lr_queue.append(lr_item)

            # gradnja novog stanja DKA
            new_dfa_state = []
            for lr_item in new_dfa_state_lr_items:
                new_dfa_state.append(lr_dict_item[lr_item])
            new_dfa_state.sort()
            new_dfa_state = tuple(new_dfa_state)

            # dodavanje odgovarajućeg prijelaza u funkciju prijelaza DKA
            dfa.transition_function[curr_dfa_state, symbol] = new_dfa_state

            # ako smo prvi put naišli na ovo stanje DKA, moramo ga registrirati
            if new_dfa_state not in dfa_states:
                dfa_states.add(new_dfa_state)
                dfa_state_queue.append(new_dfa_state)
                parser_states[new_dfa_state] = parser_index
                parser_index += 1

    return dfa

# funkcija koja gradi tablicu parsiranja na temelju danog DKA
def build_parser_table(dfa: Automata) -> dict:
    parser_table = {}

    # inicijalno popunjavanje tablice LR parsera
    for i in range(len(parser_states)):
        parser_table[i] = {}
        for terminal in terminal_symbols:
            parser_table[i][terminal] = None
        parser_table[i][fetch_end_symbol()] = None
        for nonterminal in nonterminal_symbols:
            
            # u tablici parsera se ne nalazi stupac za početni nezavršni znak gramatike
            if nonterminal == nonterminal_symbols[0]:
                continue
            parser_table[i][nonterminal] = None

    # popunjavanje tablice LR parsera
    for parser_state in parser_states:

        # dohvaćanje indeksa koji odgovara trenutnom stanju DKA
        table_index = parser_states[parser_state]
        
        # dohvaćanje LR stavki koje odgovaraju trenutnom stanju DKA
        lr_items = []
        for index in parser_state:
            lr_items.append(lr_dict_index[index])

        # računanje potpunih LR stavki
        complete_lr_items = []
        for lr_item in lr_items:
            if lr_item.index == len(lr_item.right_side) or lr_item.right_side == ("$",):
                complete_lr_items.append(lr_item)

        # stvaranje riječnika u koji se pohranjuju akcije za svaki ulazni znak za trenutno stanje
        actions = {}

        # iniciranje riječnika akcija
        for terminal in terminal_symbols:
            actions[terminal] = []
        actions[fetch_end_symbol()] = []
        for nonterminal in nonterminal_symbols:
            if nonterminal == nonterminal_symbols[0]:
                continue
            actions[nonterminal] = []

        # dodavanje akcije redukcije za svaku potpunu LR stavku
        for lr_item in complete_lr_items:
            for symbol in lr_item.follow_set:
                actions[symbol].append(Reduce(lr_item.left_side, lr_item.right_side))

        # dodavanje akcija pomaka
        

    return parser_table

# generiranje SA.py datoteke
if __name__ == "__main__":

    # oznaka trenutnog nezavršnog znaka
    curr_nonterminal = None

    # indeks pod kojim se dana produkcija pojavljuje u ulaznoj .san datoteci (bitno za razrješavanje Reduciraj/Reduciraj proturječja)
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

    # klasificiranje završnih i nezavršnih znakova u jedan riječnik
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
    empty_nonterminal_symbols, starts_with = lr_item_utils.calculate_relation_starts(nonterminal_symbols, terminal_symbols, productions)

    # stvaranje e-NKA čija stanja su LR stavke
    e_nfa = build_enfa()

    # stvaranje DKA na temelju e-NKA
    dfa = build_dfa(e_nfa)

    # stvaranje tablice parsiranja na temelju DKA
    parser_table = build_parser_table(dfa)

    # TODO: serijalizacija objekta parser_table u neku datoteku