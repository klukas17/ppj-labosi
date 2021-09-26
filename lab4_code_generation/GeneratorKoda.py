'''
REGISTRI POSEBNE NAMJENE
    R6 - povratna vrijednost funkcije
    R5 - početak okvira stoga trenutnog djelokruga
'''

import SemantickiAnalizator as s

# klasa za modeliranje varijable u nekom djelokrugu
class Variable():
    def __init__(self, node: s.Node, dist: int):
        self.node = node
        self.dist = dist

# varijabla za tabulatore u a.frisc datoteci
spaces = 12

# tablica funkcija
functions = {}

# tablica globalnih varijabli
globals = {}

# tablica konstanti
constants = {}

# globalni djelokrug
global_scope = None

# brojači
function_counter = 0
global_counter = 0
constant_counter = 0

# globalna varijabla za a.frisc datoteku
machine_code = open("a.frisc", "w")

# funkcija generira strojni kod za danu funkciju
def generate_function(f):
    machine_code.write(f'{functions[f]}\n')

    function_body = s.function_definitions[f]
    dist = 0

    # stvaranje mjesta na stogu za parametre funkcije
    if not isinstance(function_body.params, s.Void):
        parameters = function_body.node.children[3]
        for parameter in parameters.attributes["imena"]:
            parameters.symbol_table.table[parameter].dist = dist
            dist += 4
    
    # ostavljanje mjesta za povratnu adresu na stogu
    dist += 4

    # čuvanje konteksta
    dist += 24
    for i in [0,1,2,3,4,5]:
        machine_code.write(f'{spaces * " "}PUSH R{i}\n')

    # praćenje veličine lokalnih podataka
    old_dist = dist

    # stvaranje lokalnih varijabli na stogu
    for l in function_body.node.symbol_table.table:
        if function_body.node.symbol_table.table[l].dist is None:
            dist = generate_local_variable(l, function_body.node.symbol_table, dist)

    function_body.node.symbol_table.dist = dist

    for variable in function_body.node.symbol_table.table:
        function_body.node.symbol_table.table[variable].dist = dist - 4 - function_body.node.symbol_table.table[variable].dist

    instructions = []
    body = function_body.node.children[5].children[-2]
    while len(body.children) > 1:
        instructions.insert(0, body.children[1])
        body = body.children[0]
    instructions.insert(0, body.children[0])

    for instruction in instructions:
        generiraj_instrukcija(instruction)

    if old_dist != dist:
        machine_code.write(f'{spaces * " "}ADD R7, %D {dist-old_dist}, R7\n')

    # obnova konteksta
    for i in [5,4,3,2,1,0]:
        machine_code.write(f'{spaces * " "}POP R{i}\n')

    machine_code.write(f'{spaces * " "}RET\n\n')

# funkcija generira strojni kod za danu globalnu varijablu
def generate_global(g):
    machine_code.write(f'{globals[g]}{(spaces-len(globals[g])) * " "}')

    # dohvaćanje varijable
    item = s.generative_tree_root.symbol_table.table[g].node

    # polje
    if isinstance(item.attributes["tip"], s.Array):
        
        tip = item.attributes["tip"].primitive

        if isinstance(tip, s.Const):
            tip = tip.primitive

        elem_count = item.attributes["br-elem"]
        written_count = 0

        if isinstance(tip, s.Int):
            machine_code.write("DW ")

            brothers = item.parent.children
            if len(brothers) == 3:
                expressions = brothers[2].children[1].children
                l = []
                while len(expressions) > 1:
                    last_child = expressions[2]
                    expressions = expressions[0].children
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]
                    l.insert(0, last_child.lexical_unit)
                
                last_child = expressions[0]
                while isinstance(last_child, s.Node):
                    last_child = last_child.children[0]
                l.insert(0, last_child.lexical_unit)

                for item in l:
                    machine_code.write(f'%D {item}')
                    written_count += 1
                    if written_count < elem_count:
                        machine_code.write(", ")

            while written_count < elem_count:
                machine_code.write("%D 0")
                if written_count + 1 < elem_count:
                    machine_code.write(", ")
                written_count += 1

            machine_code.write("\n\n")

        elif isinstance(tip, s.Char):
            machine_code.write("DW ")

            brothers = item.parent.children
            if len(brothers) == 3:
                expressions = brothers[2].children

                if len(expressions) == 3:
                    expressions = expressions[1].children
                    l = []
                    while len(expressions) > 1:
                        last_child = expressions[2]
                        expressions = expressions[0].children
                        while isinstance(last_child, s.Node):
                            last_child = last_child.children[0]
                        l.insert(0, last_child.lexical_unit)
                    
                    last_child = expressions[0]
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]
                    l.insert(0, last_child.lexical_unit)

                    for item in l:
                        machine_code.write(f'%D {ord(item[1])}')
                        written_count += 1
                        if written_count < elem_count:
                            machine_code.write(", ")

                elif len(expressions) == 1:
                    child = expressions[0]
                    while isinstance(child, s.Node):
                        child = child.children[0]

                    arr = child.lexical_unit[1:len(child.lexical_unit)-1]
                    for el in arr:
                        machine_code.write(f'%D {ord(el)}, ')
                        written_count += 1

            while written_count < elem_count:
                machine_code.write("%D 0")
                if written_count + 1 < elem_count:
                    machine_code.write(", ")
                written_count += 1

            machine_code.write("\n\n")

    # varijabla
    else:
        
        tip = item.attributes["tip"]

        if isinstance(tip, s.Const):
            tip = tip.primitive

        if isinstance(tip, s.Int):
            machine_code.write("DW %D ")

            if len(item.parent.children) == 1:
                machine_code.write('0\n\n')

            elif len(item.parent.children) == 3:

                node = item.parent.children[2]
                while isinstance(node, s.Node):
                    node = node.children[0]

                machine_code.write(f'{node.lexical_unit}\n\n')

        elif isinstance(tip, s.Char):
            machine_code.write("DW %D ")

            if len(item.parent.children) == 1:
                machine_code.write('0\n\n')

            elif len(item.parent.children) == 3:
                node = item.parent.children[2]
                while isinstance(node, s.Node):
                    node = node.children[0]

                machine_code.write(f'{ord(node.lexical_unit[1])}\n\n')

# funkcija generira strojni kod za dane lokalne deklaracije
def generate_local_variable(l, scope, dist) -> int:
    global constant_counter
    
    item = scope.table[l].node

    # polje
    if isinstance(item.attributes["tip"], s.Array):
        
        tip = item.attributes["tip"].primitive

        if isinstance(tip, s.Const):
            tip = tip.primitive

        elem_count = item.attributes["br-elem"]
        items = []

        if isinstance(tip, s.Int):
            brothers = item.parent.children

            if len(brothers) == 3:
                expressions = brothers[2].children[1].children
                while len(expressions) > 1:
                    last_child = expressions[2]
                    expressions = expressions[0].children
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]
                    items.insert(0, int(last_child.lexical_unit))

                last_child = expressions[0]
                while isinstance(last_child, s.Node):
                    last_child = last_child.children[0]
                items.insert(0, int(last_child.lexical_unit))

            while len(items) < elem_count:
                items.append(0)

            items = items[::-1]

            scope.table[l].dist = dist + (len(items)-1)*4
            dist += len(items) * 4

            for item in items:
                
                if item not in constants:
                    constant_counter += 1
                    constants[item] = f'C_{constant_counter}'

                label = constants[item]

                machine_code.write(f'{spaces * " "}LOAD R0, ({label})\n')
                machine_code.write(f'{spaces * " "}PUSH R0\n')

        elif isinstance(tip, s.Char):
            brothers = item.parent.children

            if len(brothers) == 3:
                expressions = brothers[2].children

                if len(expressions) == 3:
                    expressions = expressions[1].children
                    while len(expressions) > 1:
                        last_child = expressions[2]
                        expressions = expressions[0].children
                        while isinstance(last_child, s.Node):
                            last_child = last_child.children[0]
                        items.insert(0, ord(last_child.lexical_unit[1]))
                    
                    last_child = expressions[0]
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]
                    items.insert(0, ord(last_child.lexical_unit[1]))

                    while len(items) < elem_count:
                        items.append(0)

                    items = items[::-1]

                    scope.table[l].dist = dist + (len(items)-1)*4
                    dist += len(items) * 4

                    for item in items:
                        
                        if item not in constants:
                            constant_counter += 1
                            constants[item] = f'C_{constant_counter}'

                        label = constants[item]

                        machine_code.write(f'{spaces * " "}LOAD R0, ({label})\n')
                        machine_code.write(f'{spaces * " "}PUSH R0\n')

                elif len(expressions) == 1:
                    child = expressions[0]
                    while isinstance(child, s.Node):
                        child = child.children[0]

                    items = child.lexical_unit[1:len(child.lexical_unit)-1]
                    items = list(items)
                    items = [ord(x) for x in items]
                    
                    while len(items) < elem_count:
                        items.append(0)

                    items = items[::-1]

                    scope.table[l].dist = dist + (len(items)-1)*4
                    dist += len(items) * 4

                    for item in items:
                        
                        if item not in constants:
                            constant_counter += 1
                            constants[item] = f'C_{constant_counter}'

                        label = constants[item]

                        machine_code.write(f'{spaces * " "}LOAD R0, ({label})\n')
                        machine_code.write(f'{spaces * " "}PUSH R0\n')

    # varijabla
    else:
        
        tip = item.attributes["tip"]
        
        if isinstance(tip, s.Const):
            tip = tip.primitive
    
        if len(item.parent.children) == 1:
            value = 0

        elif len(item.parent.children) == 3:

            node = item.parent.children[2]

            while isinstance(node, s.Node):
                if len(node.children) > 1:
                    raise NotImplementedError
                node = node.children[0]

            if isinstance(tip, s.Int):
                value = int(node.lexical_unit)

            elif isinstance(tip, s.Char):
                value = ord(node.lexical_unit[1])

        if value not in constants:
            constant_counter += 1
            constants[value] = f'C_{constant_counter}'

        label = constants[value]

        scope.table[l].dist = dist
        dist += 4

        machine_code.write(f'{spaces * " "}LOAD R0, ({label})\n')
        machine_code.write(f'{spaces * " "}PUSH R0\n')

    return dist

def generiraj_instrukcija(instruction):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<slozena_naredba>"]:
        generiraj_slozena_naredba(instruction.children[0])

    elif children == ["<izraz_naredba>"]:
        generiraj_izraz_naredba(instruction.children[0])
    
    elif children == ["<naredba_grananja>"]:
        pass

    elif children == ["<naredba_petlje>"]:
        pass

    elif children == ["<naredba_skoka>"]:
        pass

def generiraj_slozena_naredba(instruction):

    instructions = []
    scope = instruction.symbol_table
    dist = 0

    # čuvanje konteksta
    dist += 24
    for i in [0,1,2,3,4,5]:
        machine_code.write(f'{spaces * " "}PUSH R{i}\n')

    body = instruction.children[-2]
    while len(body.children) > 1:
        instructions.insert(0, body.children[1])
        body = body.children[0]
    instructions.insert(0, body.children[0])

    # deklaracije
    if len(scope.table) > 0:
        for item in scope.table:
            dist = generate_local_variable(item, scope, dist)

    for variable in scope.table:
        scope.table[variable].dist = dist - 4 - scope.table[variable].dist

    scope.dist = dist

    for instruction in instructions:
        generiraj_instrukcija(instruction)

    # micanje lokalnih varijabli sa stoga
    if len(scope.table) > 0:
        machine_code.write(f'{spaces * " "}ADD R7, %D {scope.dist-24}, R7\n')

    # obnova konteksta
    for i in [5,4,3,2,1,0]:
        machine_code.write(f'{spaces * " "}POP R{i}\n')

def generiraj_izraz_naredba(instruction):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<izraz>", "TOCKAZAREZ"]:
        generiraj_izraz(instruction.children[0])

def generiraj_izraz(instruction):
    
    children = list(map(lambda n: n.symbol, instruction.children))
            
    if children == ["<izraz_pridruzivanja>"]:
        generiraj_izraz_pridruzivanja(instruction.children[0])

    elif children == ["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]:
        generiraj_izraz(instruction.children[0])
        generiraj_izraz_pridruzivanja(instruction.children[2])

def generiraj_izraz_pridruzivanja(instruction):
    
    children = list(map(lambda n: n.symbol, instruction.children))
            
    if children == ["<log_ili_izraz>"]:
        pass

    elif children == ["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]:
        pass

def generiraj_log_ili_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<log_i_izraz>"]:
        pass

    elif children == ["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]:
        pass

def generiraj_log_i_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_ili_izraz>"]:
        pass

    elif children == ["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]:
        pass

def generiraj_bin_ili_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_xili_izraz>"]:
        pass

    elif children == ["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]:
        pass

def generiraj_bin_xili_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_i_izraz>"]:
        pass

    elif children == ["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]:
        pass

def generiraj_bin_i_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<jednakosni_izraz>"]:
        pass

    elif children == ["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]:
        pass

def generiraj_jednakosni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<odnosni_izraz>"]:
        pass

    elif children == ["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]:
        pass

    elif children == ["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]:
        pass

def generiraj_odnosni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<aditivni_izraz>"]:
        pass

    elif children == ["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"]:
        pass

    elif children == ["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"]:
        pass

    elif children == ["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"]:
        pass

    elif children == ["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]:
        pass

def generiraj_aditivni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<multiplikativni_izraz>"]:
        pass

    elif children == ["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]:
        pass

    elif children == ["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]:
        pass

def generiraj_multiplikativni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<cast_izraz>"]:
        pass

    elif children == ["<multiplikativni izraz>", "OP_PUTA", "<cast_izraz>"]:
        pass

    elif children == ["<multiplikativni izraz>", "OP_DIJELI", "<cast_izraz>"]:
        pass

    elif children == ["<multiplikativni izraz>", "OP_MOD", "<cast_izraz>"]:
        pass

def generiraj_cast_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<unarni_izraz>"]:
        pass

    elif children == ["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]:
        pass 

def generiraj_unarni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<postfiks_izraz>"]:
        pass

    elif children == ["OP_INC", "<unarni_izraz>"]:
        pass

    elif children == ["OP_DEC", "<unarni_izraz>"]:
        pass

    elif children == ["<unarni_operator>", "<cast_izraz>"]:
        pass

def generiraj_postfiks_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<primarni_izraz>"]:
        pass

    elif children == ["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]:
        pass

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]:
        pass

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]:
        pass

    elif children == ["<postfiks_izraz>", "OP_INC"]:
        pass

    elif children == ["<postfiks_izraz>", "OP_DEC"]:
        pass

def generiraj_primarni_izraz(instruction):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["IDN"]:
        pass

    elif children == ["BROJ"]:
        pass

    elif children == ["ZNAK"]:
        pass

    elif children == ["NIZ_ZNAKOVA"]:
        pass

    elif children == ["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]:
        pass

if __name__ == "__main__":
    
    # semantička analiza nad generativnim stablom na standardnom ulazu
    s.semantic_analysis()

    # inicijalizacija i završetak izvođenja programa
    machine_code.write(f'{spaces * " "}MOVE 40000, R7\n')
    machine_code.write(f'{spaces * " "}CALL F_MAIN\n')
    machine_code.write(f'{spaces * " "}HALT\n\n')

    # dodavanje main funkcije u riječnik funkcija
    functions["main"] = "F_MAIN"

    # spremanje globalnog djelokruga u posebnu varijablu
    global_scope = s.generative_tree_root.symbol_table.table

    # obrada globalnih varijabli i funkcija
    for item in s.generative_tree_root.symbol_table.table:

        val = s.generative_tree_root.symbol_table.table[item]
        
        # funkcija
        if isinstance(val, s.Function):
            if item != "main":
                function_counter += 1
                functions[item] = f'F_{function_counter}'

        # globalna varijabla
        else:
            global_counter += 1
            globals[item] = f'G_{global_counter}'

    # dodavanje mjesta za podatak o odmaku od referentne točke okvira stoga pojedine varijable
    for scope in s.scopes:
        for unit in scope.table:
            if not isinstance(unit, s.Function):
                scope.table[unit] = Variable(scope.table[unit], None)

    # obrada funkcija
    for f in functions:
        generate_function(f)

    # obrada globalnih varijabli
    for g in globals:
        generate_global(g)

    # zapis konstanti
    for c in constants:
        machine_code.write(f'{constants[c]}{(spaces-len(constants[c])) * " "}DW %D {c}\n')

    # zatvaranje datoteke
    machine_code.close()