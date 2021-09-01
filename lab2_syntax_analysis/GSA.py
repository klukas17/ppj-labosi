# deklaracija globalnih varijabli
nonterminal_symbols = []
terminal_symbols = []
synchronisation_symbols = []
productions = {}

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
                synchronisation_symbols = line[5:].split(" ") if len(line) >= 5 else []

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
                    productions[curr_nonterminal].append((line[1:].split(" "), production_index))

    except EOFError:
        pass