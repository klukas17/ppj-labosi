'''
    NAPOMENA: pri pisanju datoteke LA.py, iskoristio sam dijelove svog 
    vlastitog rješenja 1. laboratorijske vježbe (SimEnka.py) na kolegiju 
    "Uvod u teoriju računarstva" koje sam predao ak. god. 2020/2021
'''

from sys import stdin, path
old_path = path[0]
path[0] = path[0][:path[0].rfind("/")]
from lex_utils import rule, e_nfa_utils

# enumeracija za deserijalizaciju izračunatih pravila
class Deserialization_step():
    STARTING_STATE = 0
    ARGS = 1
    TRANSITION_FUNCTION = 2
    START_END_STATES = 3

# lista svih pravila, posloženih po prioritetu
rules = []

# deklaracija globalnih varijabli
starting_state = None
input_program = None

# funkcija za deserijalizaciju izračunatih pravila
def read_rules() -> None:

    global rules
    global starting_state

    new_rule = rule.Rule(None, None)
    new_rule.enfa = e_nfa_utils.E_NFA(None, False)
    step = Deserialization_step.STARTING_STATE

    with open(old_path + "/rules.txt", "r") as data:

        while (curr_line := data.readline()):

            # micanje znaka za prelazak u novi red \n
            curr_line = curr_line[:len(curr_line)-1] if curr_line[len(curr_line)-1] == '\n' else curr_line
                
            # ulazak u novo stanje čitanja datoteke
            if curr_line in ["{", "}"]:
                            
                if curr_line == "{":
                    step += 1

                elif curr_line == "}":
                    step -= 1

                if step == 0:
                    rules.append(new_rule)
                    new_rule = rule.Rule(None, None)
                    new_rule.enfa = e_nfa_utils.E_NFA(None, False)

            # čitanje podataka
            else:

                if step == Deserialization_step.STARTING_STATE:
                    starting_state = curr_line

                elif step == Deserialization_step.ARGS:
                    args = curr_line.split()
                    new_rule.state = args[0]
                    new_rule.lexem = args[1] if args[1] != "-" else None
                    new_rule.NOVI_REDAK = True if args[2] == "1" else False
                    new_rule.UDJI_U_STANJE = True if args[3] == "1" else False
                    new_rule.UDJI_U_STANJE_arg = args[4] if args[3] == "1" else None
                    new_rule.VRATI_SE = True if args[5] == "1" else False
                    new_rule.VRATI_SE_arg = int(args[6]) if args[5] == "1" else None
                    pass

                elif step == Deserialization_step.TRANSITION_FUNCTION:
                    args = curr_line.split()
                    new_rule.enfa.transition_function[(args[0], args[1])] = args[2:]

                elif step == Deserialization_step.START_END_STATES:
                    args = curr_line.split()
                    new_rule.enfa.start_state = args[0]
                    new_rule.enfa.end_state = args[1]

# funkcija dohvaća sljedeći simbol iz ulaznog niza
def fetch_symbol() -> str:
    global input_program

    if len(input_program) > 0:
        c = input_program[0]
        input_program = input_program[1:]
        return c

    else:
        return None

# funkcija vraća pročitani simbol u ulazni niz
def return_symbol(c: str) -> None:
    global input_program

    input_program.insert(0, c)

# funkcija provjerava postoje li znakovi u ulaznom nizu
def check_symbol() -> bool:
    return True if len(input_program) > 0 else False

# čitanje ulazne datoteke i ispisivanje niza leksičkih jedinki na standardni izlaz
if __name__ == "__main__":
    
    # deserijalizacija izračunatih pravila
    read_rules()

    # čitanje ulaznog programa
    input_program = list(stdin.read())

    # prefiksiranje specijalnih znakova
    input_program = [c if c not in ['(', ')', '{', '}', '|', '*', '$'] else f'\{c}' for c in input_program]

    # obrada razmaka
    input_program = [c if c != " " else "\\_" for c in input_program]

    while check_symbol():
        pass