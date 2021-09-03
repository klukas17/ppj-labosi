from typing import Tuple

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

# funkcija računa prazne nezavršne znakove
def calculate_empty_nonterminal_symbols(nonterminal_symbols: list, terminal_symbols: list, productions: dict) -> set:
    empty_symbols = set()

    # početno traženje epsilon produkcija
    for nonterminal in productions:
        for production in productions[nonterminal]:
            if production[0] == ("$",):
                empty_symbols.add(nonterminal)

    # potraga za ostalim praznim znakovima
    while True:
        change_done = False

        for nonterminal in productions:
            for production in productions[nonterminal]:
                all_empty = True
                for right_side_element in production[0]:
                    if right_side_element not in empty_symbols:
                        all_empty = False
                        break
                if all_empty and nonterminal not in empty_symbols:
                    empty_symbols.add(nonterminal)
                    change_done = True

        if not change_done:
            break

    return empty_symbols

# funkcija računa relaciju IzravnoZapočinjeZnakom
def calculate_directly_starts_with(nonterminal_symbols: list, terminal_symbols: list, productions: dict, empty_nonterminal_symbols: set) -> dict:
    table = {}

    # iniciranje tablice
    for nonterminal in nonterminal_symbols:
        table[nonterminal] = {}
        for symbol in nonterminal_symbols:
            table[nonterminal][symbol] = False
        for symbol in terminal_symbols:
            table[nonterminal][symbol] = False
    for terminal in terminal_symbols:
        table[terminal] = {}
        for symbol in nonterminal_symbols:
            table[terminal][symbol] = False
        for symbol in terminal_symbols:
            table[terminal][symbol] = False

    for nonterminal in productions:
        for production in productions[nonterminal]:
            if production[0] == ("$",):
                continue
            for symbol in production[0]:
                table[nonterminal][symbol] = True
                if symbol not in empty_nonterminal_symbols:
                    break

    return table

# funkcija računa relaciju ZapočinjeZnakom
def calculate_starts_with(nonterminal_symbols: list, terminal_symbols: list, productions: dict, table: dict) -> None:
     
    # određivanje refleksivnog okruženja relacije IzravnoZapočinjeZnakom
    for symbol in nonterminal_symbols:
        table[symbol][symbol] = True
    for symbol in terminal_symbols:
        table[symbol][symbol] = True

    # određivanje tranzitivnog okruženja relacije IzravnoZapočinjeZnakom
    for symbol1 in table:
        for symbol2 in table[symbol1]:
            if symbol1 == symbol2:
                continue
            if table[symbol1][symbol2]:
                for symbol3 in table[symbol2]:
                    if table[symbol2][symbol3]:
                        table[symbol1][symbol3] = True

# funkcija računa relaciju ZAPOČINJE za dane produkcije gramatike
def calculate_relation_starts(nonterminal_symbols: list, terminal_symbols: list, productions: dict) -> Tuple[set, dict]:
    empty_nonterminal_symbols = calculate_empty_nonterminal_symbols(nonterminal_symbols, terminal_symbols, productions)
    table = calculate_directly_starts_with(nonterminal_symbols, terminal_symbols, productions, empty_nonterminal_symbols)
    calculate_starts_with(nonterminal_symbols, terminal_symbols, productions, table)
    return empty_nonterminal_symbols, table