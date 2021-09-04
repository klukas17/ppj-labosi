from sys import path, stderr
from typing import Union
old_path = path[0]
path[0] = path[0][:path[0].rfind("/")]

# oznaka kraja niza - implementacija i reprezentacija potpuno nezavisna od one u GSA, već je lokalna
class End_symbol():
    def __init__(self):
        self.name = "end_symbol"
    def __repr__(self) -> str:
        return "END_SYMBOL"

# dekorator koji omotava oznaku kraja niza i čini ju leksičkom jedinkom
class End_symbol_decorator():
    def __init__(self):
        self.symbol = fetch_end_symbol()
        self.line = None
        self.lexical_unit = "EOF"
    def __repr__(self) -> str:
        return "END_SYMBOL"

# oznaka kraja stoga
class Stack_end():
    def __init__(self):
        self.symbol = "stack_end"
        #self.line = "EOF"
        self.lexical_unit = "EOF"
    def __repr__(self) -> str:
        return "STACK_END"

# enumeracija za tip znaka
class Symbol_type():
    NONTERMINAL = 1
    TERMINAL = 2

# klasa za modeliranje akcija parsera
class Action():
    def __init__(self):
        pass

class Reduce(Action):
    def __init__(self, left_side: str, right_side: list):
        Action.__init__(self)
        self.left_side = left_side
        self.right_side = right_side
        self.right_side_length = len(right_side) if self.right_side != ["$"] else 0
    def __repr__(self) -> str:
        ret_val =  f"REDUCE {self.left_side} ->"
        for el in self.right_side:
            ret_val += f" {el}"
        ret_val += " {len=" + str(self.right_side_length) + "}"
        return ret_val

class Shift(Action):
    def __init__(self, new_state: int):
        Action.__init__(self)
        self.new_state = new_state
    def __repr__(self) -> str:
        return f"SHIFT {self.new_state}"

class Put(Action):
    def __init__(self, new_state: int):
        Action.__init__(self)
        self.new_state = new_state
    def __repr__(self) -> str:
        return f"PUT {self.new_state}"

# apstraktna klasa za modeliranje čvora generativnog stabla
class Abs_Node():
    def __init__(self):
        pass

# klasa za modeliranje unutarnjeg čvora generativnog stabla
class Node(Abs_Node):
    def __init__(self, symbol: str):
        Abs_Node.__init__(self)
        self.symbol = symbol
        self.children = []
    def __repr__(self) -> str:
        return self.symbol

# klasa za modeliranje lista stabla
class Leaf(Abs_Node):
    def __init__(self, symbol: str, line: int, lexical_unit: str):
        Abs_Node.__init__(self)
        self.symbol = symbol
        self.line = line
        self.lexical_unit = lexical_unit
    def __repr__(self) -> str:
        return self.symbol

# klasa za modeliranje praznog lista stabla (epsilon produkcija)
class Empty_Leaf(Abs_Node):
    def __init__(self):
        Abs_Node.__init__(self)
    def __repr__(self) -> str:
        return "$"

# klasa za modeliranje sintaksne greške
class Error():
    def __init__(self):
        self.line = None
        self.uniform = None
        self.lexical_unit = None
        self.expected = None

# globalne varijable
terminal_symbols = []
nonterminal_symbols = []
synchronisation_symbols = []
acceptance_state = []
symbol_type = {}
parser_table = {}
stack = []
uniform_units = None
errors = []
last_line = None                # za dodjelu broja retka oznaci kraja niza
end_symbol = End_symbol()
stack_end = Stack_end()

# funkcija kojom se dohvaća jedinstven objekt koji označava kraj niza -> obrazac singleton
def fetch_end_symbol() -> End_symbol:
    return end_symbol

# funkcija kojom se dohvaća jedinstven objekt koji označava kraj stoga
def fetch_stack_end() -> Stack_end:
    return stack_end

# funkcija za uklanjanje oznaka kraja reda s pročitaneog linije u datoteci
def remove_end_of_line_character(line: str) -> str:
    return line[:len(line)-1] if line[len(line)-1] == '\n' else line

# funkcija za deserijalizaciju tablice parsiranja
def read_parsing_table() -> None:
    
    global terminal_symbols
    global nonterminal_symbols
    global synchronisation_symbols
    global acceptance_state
    global parser_table

    with open(old_path + '/parser_table.txt', "r") as data:
        
        # čitanje nezavršnih znakova
        line = remove_end_of_line_character(data.readline())
        nonterminal_symbols = line.split(" ")[1:] 

        # čitanje završnih znakova
        line = remove_end_of_line_character(data.readline())
        terminal_symbols = line.split(" ")[1:] 

        # čitanje sinkronizacijskih znakova
        line = remove_end_of_line_character(data.readline())
        synchronisation_symbols = line.split(" ")[1:] 

        # čitanje stanja u kojem se za čitanje kraja niza niz prihvaća
        line = remove_end_of_line_character(data.readline())
        acceptance_state = line

        # čitanje oznake kojom je kodirana oznaka kraja niza
        line = remove_end_of_line_character(data.readline())
        end_of_input = line

        for terminal in terminal_symbols:
            symbol_type[terminal] = Symbol_type.TERMINAL
        for nonterminal in nonterminal_symbols:
            symbol_type[nonterminal] = Symbol_type.NONTERMINAL

        parser_state = None

        while (line := data.readline()):
            line = remove_end_of_line_character(line)

            # čitanje ćelije u tablici prijelaza
            if line[0] == " ":

                # uklanjanje oznake kraja niza
                line = line[1:].split(sep=" ", maxsplit=1)
                symbol = line[0]
                action = line[1]
                action_code = action[0]
                action = action[1:]

                # kraj niza
                if symbol == end_of_input:
                    symbol = fetch_end_symbol()

                # pomak
                if action_code == "s":
                    parser_table[parser_state][symbol] = Shift(int(action))

                # stavljanje stanja na stog
                elif action_code == "p":
                    parser_table[parser_state][symbol] = Put(int(action))

                # redukcija
                elif action_code == "r":
                    action = action[1:len(action)-1]
                    action = action.split(sep=" -> ", maxsplit=1)
                    parser_table[parser_state][symbol] = Reduce(action[0], action[1].split(" "))

            # čitanje pravila za novo stanje parsera
            else:
                parser_state = int(line)
                parser_table[parser_state] = {}

# funkcija dohvaća sljedeću leksičku jedinku
def fetch_next_uniform_unit() -> Union[Leaf, End_symbol]:
    global uniform_units
    global last_line

    if len(uniform_units) > 0:
        ret_val = uniform_units.pop(0)
        last_line = ret_val.line
        return ret_val

    else:
        ret_val = End_symbol_decorator()
        ret_val.line = last_line + 1
        return ret_val

# funkcija koja čita niz uniformnih jedinki i na temelju njih gradi generativno stablo
def build_generative_tree() -> Abs_Node:
    
    global parser_table
    global stack
    global errors
    
    uniform_unit = None

    while True:
        
        # potrebno dohvatiti sljedeću uniformnu jedinku
        if uniform_unit is None:
            uniform_unit = fetch_next_uniform_unit()

        # za trenutnu leksičku jedinku i za trenutno stanje parsera definirana akcija
        if uniform_unit.symbol in parser_table[stack[-1]]:
            action = parser_table[stack[-1]][uniform_unit.symbol]

            if isinstance(action, Shift):
                stack.append(uniform_unit)
                uniform_unit = None
                stack.append(action.new_state)

            elif isinstance(action, Reduce):

                # završetak parsiranja
                if action.left_side == nonterminal_symbols[0]:
                    return stack[-2]

                # stvaranje novog unutarnjeg čvora
                new_symbol = Node(action.left_side)

                # elementi desne strane produkcije čine djecu novog unutarnjeg čvora
                for i in range(len(stack) - 2, len(stack) - 2 - 2 * action.right_side_length, -2):
                    new_symbol.children.append(stack[i])

                # ako novi unutarnji čvor nema djecu, tj. riječ je o epsilon produkciji
                if len(new_symbol.children) == 0:
                    new_symbol.children =  [Empty_Leaf()]

                # inače treba obrnuti poredak djece jer se na čitaju zdesna nalijevo
                else:
                    new_symbol.children = new_symbol.children[::-1]

                # micanje znakova sa stoga
                stack = stack[:len(stack) - 2 * action.right_side_length]
                stack.append(new_symbol)
                    
                # obavljanje akcije stavljanja
                stack.append(parser_table[stack[-2]][action.left_side].new_state)

        # oporavak od pogreške
        else:

            # zapis podatak o pogrešci u poseban objekt
            err = Error()
            err.line = stack[-2].line
            err.uniform = stack[-2].symbol
            err.lexical_unit = stack[-2].lexical_unit
            expected = []
            for symbol in parser_table[stack[-1]]:
                if not isinstance(parser_table[stack[-1]][symbol], Put):
                    if symbol == fetch_end_symbol():
                        expected.append("END_SYMBOL")
                    else:
                        expected.append(symbol)
            err.expected = ' | '.join(expected)
            errors.append(err)

            # pronalazak sinkronizacijskog znaka
            while uniform_unit.symbol not in synchronisation_symbols:
                uniform_unit = fetch_next_uniform_unit()

            # odbacivanje znakova sa stoga
            while len(stack) > 2 and uniform_unit.symbol not in parser_table[stack[-1]]:
                stack = stack[:len(stack)-2]

# funkcija rekurzivno printa generativno stablo
def print_tree(curr_root: Node, indent: int):

    print(indent*' ', end='')
    
    if isinstance(curr_root, Node):
        print(curr_root.symbol)
        for el in curr_root.children:
            print_tree(el, indent + 1)

    elif isinstance(curr_root, Leaf):
        print(f"{curr_root.symbol} {curr_root.line} {curr_root.lexical_unit}")

    elif isinstance(curr_root, Empty_Leaf):
        print("$")

# čitanje niza leksičkih jedinki i gradnja sintaksnog stabla
if __name__ == "__main__":
    
    # deserijalizacija tablice parsiranja
    read_parsing_table()

    # inicijalizacija stoga
    stack.append(fetch_stack_end())
    stack.append(0)

    uniform_units = []
    # čitanje ulaznog niza
    try:
        while True:
            line = input()
            if line == "":
                break

            line = line.split(sep=" ", maxsplit=1)
            lexical_unit = line[0]
            line = line[1]
            line = line.split(sep=" ", maxsplit=1)
            ind = int(line[0])
            line = line[1]

            uniform_units.append(Leaf(lexical_unit, ind, line))

    except EOFError:
        pass

    generative_tree_root = build_generative_tree()
    print_tree(generative_tree_root, 0)

    # ispis grešaka
    if len(errors) > 0:
        stderr.write("\nSYNTACTIC ERRORS:\n")
        for err in errors:
            stderr.write(f" at line {err.line} expected uniform symbol from {err.expected} but read uniform symbol {err.uniform} as a lexical unit {err.lexical_unit}\n\n")