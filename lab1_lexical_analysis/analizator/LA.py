from sys import stdin, path, stderr
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
errors = []

# deklaracija globalnih varijabli
starting_state = None
curr_state = None
input_program = None
curr_line = 1

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

# funkcija koja pokušava naći prefiks preostalog dijela ulaznog niza za dano pravilo
def find_prefix(rule: rule.Rule) -> int:
    
    global curr_state
    global input_program

    # dohvaćanje i spremanje reference radi lakšeg korištenja
    enfa = rule.enfa

    # analizator je u odgovarajućem stanju za ovo pravilo pa može tražiti valjan prefiks
    if rule.state == curr_state:
        
        # inicijalizacija varijabli
        visit_queue = [enfa.start_state]

        prefix_length = 0
        matched_prefix_length = 0

        # automat se nalazi u nekim stanjima
        while len(visit_queue) > 0:

            current_states = set()

            # računanje epsilon okoline trenutnog skupa stanja
            while len(visit_queue) > 0:

                s = visit_queue[0]
                visit_queue = visit_queue[1:]
                current_states.add(s)
                if (s, "$") in enfa.transition_function:
                    for e in enfa.transition_function[(s, "$")]:
                        if e not in current_states and e not in visit_queue:
                            visit_queue.append(e)

            if enfa.end_state in current_states:
                matched_prefix_length = prefix_length
            
            # provjera je li pročitan cijeli niz
            if prefix_length < len(input_program):
                c = input_program[prefix_length]

                # računanje prijelaza trenutnih stanja automata za pročitani znak
                for s in current_states:
                    if (s, c) in enfa.transition_function:
                        for e in enfa.transition_function[(s,c)]:
                            visit_queue.append(e)

                # uvećanje duljinu pronađenog prefiksa za 1
                if len(visit_queue) > 0:
                    prefix_length += 1
                    
        return matched_prefix_length

    # analizator nije u odgovarajućem stanju za ovo pravilo pa odustati od traženja valjanog prefiksa
    else:
        return 0

# funkcija koja primjenjuje pravilo s obzirom na pronađeni prefiks
def apply_rule(rule: rule.Rule, prefix_length: int) -> None:
    global input_program
    global curr_line
    global curr_state

    prefix_list = input_program[:prefix_length]
    
    # micanje escape znakova
    prefix_list = [c if c not in ['\\(', '\\)', '\\{', '\\}', '\\|', '\\*', '\\$', '\\\\'] else c[1] for c in prefix_list]
    prefix_list = [c if c != "\\_" else " " for c in prefix_list]

    found_prefix = ''.join(prefix_list)

    if rule.lexem is not None:
        print(f'{rule.lexem} {curr_line} {found_prefix if not rule.VRATI_SE else found_prefix[:rule.VRATI_SE_arg]}')
    
    found_prefix_unescaped = list(found_prefix)
    found_prefix = []

    i = 0
    while i < len(found_prefix_unescaped):
        if found_prefix_unescaped[i] != '\\':
            found_prefix.append(found_prefix_unescaped[i])
            i += 1
        else:
            found_prefix.append(found_prefix_unescaped[i] + found_prefix_unescaped[i+1])
            i += 2

    
    input_program = input_program[prefix_length:]

    if rule.NOVI_REDAK:
        curr_line += 1

    if rule.UDJI_U_STANJE:
        curr_state = rule.UDJI_U_STANJE_arg

    if rule.VRATI_SE:
        input_program = found_prefix[rule.VRATI_SE_arg:] + input_program

# čitanje ulazne datoteke i ispisivanje niza leksičkih jedinki na standardni izlaz
if __name__ == "__main__":
    
    # deserijalizacija izračunatih pravila
    read_rules()

    # čitanje ulaznog programa
    input_program = list(stdin.read())

    # prefiksiranje specijalnih znakova
    input_program = [c if c not in ['(', ')', '{', '}', '|', '*', '$', '\\'] else f'\\{c}' for c in input_program]
    input_program = [c if c != '\n' else '\\n' for c in input_program]
    input_program = [c if c != '\t' else '\\t' for c in input_program]

    # obrada razmaka
    input_program = [c if c != " " else "\\_" for c in input_program]

    # iniciranje stanja analizatora
    curr_state = starting_state

    # čitanje ulaznog niza i generiranje uniformnog niza leksičkih jedinki
    while check_symbol():
        
        rule_index = None
        prefix_found_length = 0

        if curr_line == 12:
            o = 0

        # za svako pravilo pokušaj pronaći najdulji prefiks
        for i in range(len(rules)):
            ret_val = find_prefix(rules[i])
            if ret_val > prefix_found_length:
                rule_index = i
                prefix_found_length = ret_val

        # pronađen je valjan prefiks niza
        if prefix_found_length > 0:
            apply_rule(rules[rule_index], prefix_found_length)

        # nije pronađen valjan prefiks niza, oporavak od greške
        else:
            errors.append((input_program[0], curr_line))
            input_program = input_program[1:]

    # ispis pogrešaka na stderr
    if len(errors) > 0:
        stderr.write("ERRORS:\n")
        for error in errors:
            stderr.write(f' symbol {error[0]} at line {error[1]}\n')