from sys import path, stderr
old_path = path[0]
path[0] = path[0][:path[0].rfind("/")]

# oznaka kraja niza - implementacija i reprezentacija potpuno nezavisna od one u GSA, već je lokalna
class End_symbol():
    def __init__(self):
        self.name = "end_symbol"
    def __repr__(self) -> str:
        return "END_SYMBOL"

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

# globalne varijable
terminal_symbols = []
nonterminal_symbols = []
synchronisation_symbols = []
acceptance_state = []
parser_table = {}
symbol_type = {}
end_symbol = End_symbol()

# funkcija kojom se dohvaća jedinstven objekt koji označava kraj niza -> obrazac singleton
def fetch_end_symbol() -> End_symbol:
    return end_symbol

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

# čitanje niza leksičkih jedinki i gradnja sintaksnog stabla
if __name__ == "__main__":
    
    # deserijalizacija tablice parsiranja
    read_parsing_table()

    pass