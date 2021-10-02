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

# global constants
global_constants = {}

# brojači
function_counter = 0
global_counter = 0
constant_counter = 0
label_counter = 0

# globalna varijabla za a.frisc datoteku
machine_code = open("a.frisc", "w")

# temp funkcija za debugging
def p(s):
    machine_code.write(s)
    print(s,end='')

# funkcija generira strojni kod za danu funkciju
def generate_function(f):
    p(f'{functions[f]}\n')

    function_body = s.function_definitions[f]
    dist = 0

    if not isinstance(function_body.params, s.Void):
        parameters = function_body.node.children[3]
        for parameter in parameters.attributes["imena"]:
            parameters.symbol_table.table[parameter].dist = 0
            dist += 4
            for param in function_body.node.symbol_table.table:
                if function_body.node.symbol_table.table[param].dist is not None and param != parameter:
                    function_body.node.symbol_table.table[param].dist += 4

    # ostavljanje mjesta za povratnu adresu na stogu
    dist += 4

    # čuvanje konteksta
    dist += 24
    for i in [0,1,2,3,4,5]:
        p(f'{spaces * " "}PUSH R{i}\n')

    for param in function_body.node.symbol_table.table:
        if function_body.node.symbol_table.table[param].dist is not None:
            function_body.node.symbol_table.table[param].dist += 28

    # ažuriranje okvira stoga
    p(f'{spaces * " "}MOVE R7, R5\n')

    function_body.node.symbol_table.dist = dist

    # praćenje veličine lokalnih podataka
    old_dist = dist

    # stvaranje lokalnih varijabli na stogu
    for l in function_body.node.symbol_table.table:
        if function_body.node.symbol_table.table[l].dist is None:
            dist_before = dist
            dist = generate_local_variable(l, function_body.node.symbol_table, dist)
            diff = dist - dist_before
            if diff > 0:
                for param in function_body.node.symbol_table.table:
                    if function_body.node.symbol_table.table[param].dist is not None and param != l:
                        function_body.node.symbol_table.table[param].dist += diff

            # ažuriranje okvira stoga
            p(f'{spaces * " "}MOVE R7, R5\n')

            # ažuriranje veličine okvira stoga
            function_body.node.symbol_table.dist = dist

    instructions = []
    body = function_body.node.children[5].children[-2]
    while len(body.children) > 1:
        instructions.insert(0, body.children[1])
        body = body.children[0]
    instructions.insert(0, body.children[0])

    for instruction in instructions:
        generiraj_naredba(instruction, function_body.node.symbol_table)

    if old_dist != dist:
        p(f'{spaces * " "}ADD R7, %D {dist-old_dist}, R7\n')

    # obnova konteksta
    for i in [5,4,3,2,1,0]:
        p(f'{spaces * " "}POP R{i}\n')

    # povratak iz funkcije
    p(f'{spaces * " "}RET\n\n')

# funkcija generira strojni kod za danu globalnu varijablu
def generate_global(g):
    global global_constants

    p(f'{globals[g]}{(spaces-len(globals[g])) * " "}')

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
            p("DW ")

            brothers = item.parent.children
            if len(brothers) == 3:
                expressions = brothers[2].children[1].children
                l = []
                while len(expressions) > 1:
                    last_child = expressions[2]
                    expressions = expressions[0].children
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]

                    if last_child.symbol == "BROJ":
                        l.insert(0, int(last_child.lexical_unit))

                    elif last_child.symbol == "IDN":
                        l.insert(0, last_child.lexical_unit)
                
                last_child = expressions[0]
                while isinstance(last_child, s.Node):
                    last_child = last_child.children[0]
                if last_child.symbol == "BROJ":
                    l.insert(0, int(last_child.lexical_unit))
                elif last_child.symbol == "IDN":
                    l.insert(0, last_child.lexical_unit)

                for item in l:
                    if isinstance(item, int):
                        p(f'%D {item}')
                    elif isinstance(item, str):
                        p(f'%D {global_constants[item]}')
                    written_count += 1
                    if written_count < elem_count:
                        p(", ")

            while written_count < elem_count:
                p("%D 0")
                if written_count + 1 < elem_count:
                    p(", ")
                written_count += 1

            p("\n\n")

        elif isinstance(tip, s.Char):
            p("DW ")

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
                        l.insert(0, last_child)
                    
                    last_child = expressions[0]
                    while isinstance(last_child, s.Node):
                        last_child = last_child.children[0]
                    l.insert(0, last_child)

                    for item in l:
                        if item.symbol == "ZNAK":
                            p(f'%D {ord(item.lexical_unit[1])}')
                        elif item.symbol == "IDN":
                            p(f'%D {global_constants[item.lexical_unit]}')
                        written_count += 1
                        if written_count < elem_count:
                            p(", ")

                elif len(expressions) == 1:
                    child = expressions[0]
                    while isinstance(child, s.Node):
                        child = child.children[0]

                    arr = child.lexical_unit[1:len(child.lexical_unit)-1]
                    for el in arr:
                        p(f'%D {ord(el)}, ')
                        written_count += 1

            while written_count < elem_count:
                p("%D 0")
                if written_count + 1 < elem_count:
                    p(", ")
                written_count += 1

            p("\n\n")

    # varijabla
    else:
        
        tip = item.attributes["tip"]

        old_tip = tip

        if isinstance(tip, s.Const):
            tip = tip.primitive

        if isinstance(tip, s.Int):
            p("DW %D ")

            if len(item.parent.children) == 1:
                p('0\n\n')

            elif len(item.parent.children) == 3:

                node = item.parent.children[2]
                while isinstance(node, s.Node):
                    node = node.children[0]

                if node.symbol == "BROJ":
                    p(f'{node.lexical_unit}\n\n')

                elif node.symbol == "IDN":
                    p(f'{global_constants[node.lexical_unit]}\n\n')

                if isinstance(old_tip, s.Const):
                    global_constants[g] = int(node.lexical_unit)

        elif isinstance(tip, s.Char):
            p("DW %D ")

            if len(item.parent.children) == 1:
                p('0\n\n')

            elif len(item.parent.children) == 3:
                node = item.parent.children[2]
                while isinstance(node, s.Node):
                    node = node.children[0]

                if node.symbol == "ZNAK":
                    p(f'{ord(node.lexical_unit[1])}\n\n')

                elif node.symbol == "IDN":
                    p(f'{global_constants[node.lexical_unit]}\n\n')

                if isinstance(old_tip, s.Const):
                    global_constants[g] = ord(node.lexical_unit[1])

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

                while len(expressions) == 3:
                    items.append(expressions[2])
                    expressions = expressions[0].children
                items.append(expressions[0])

            while len(items) < elem_count:
                items.insert(0, None)

            scope.table[l].dist = 0
            dist += len(items) * 4

            for item in items:

                if item is None:
                    val = 0
                    if val not in constants:
                        constant_counter += 1
                        constants[val] = f'C_{constant_counter}'

                    label = constants[val]

                    p(f'{spaces * " "}LOAD R0, ({label})\n')
                    p(f'{spaces * " "}PUSH R0\n')

                else:
                    generiraj_izraz_pridruzivanja(item, scope)

        elif isinstance(tip, s.Char):
            brothers = item.parent.children

            if len(brothers) == 3:
                expressions = brothers[2].children

                if len(expressions) == 3:
                    expressions = expressions[1].children

                    while len(expressions) == 3:
                        items.append(expressions[2])
                        expressions = expressions[0].children
                    items.append(expressions[0])

                    while len(items) < elem_count:
                        items.insert(0, None)

                    for item in items:

                        if item is None:
                            val = 0
                            if val not in constants:
                                constant_counter += 1
                                constants[val] = f'C_{constant_counter}'

                            label = constants[val]

                            p(f'{spaces * " "}LOAD R0, ({label})\n')
                            p(f'{spaces * " "}PUSH R0\n')

                        else:
                            generiraj_izraz_pridruzivanja(item, scope)

                    scope.table[l].dist = 0
                    dist += len(items) * 4

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

                    scope.table[l].dist = 0
                    dist += len(items) * 4

                    for item in items:
                        
                        if item not in constants:
                            constant_counter += 1
                            constants[item] = f'C_{constant_counter}'

                        label = constants[item]

                        p(f'{spaces * " "}LOAD R0, ({label})\n')
                        p(f'{spaces * " "}PUSH R0\n')

            elif len(brothers) == 1:
                
                for _ in range(elem_count):
                    items.append(0)

                for item in items:

                    if item not in constants:
                        constant_counter += 1
                        constants[item] = f'C_{constant_counter}'

                    label = constants[item]

                    p(f'{spaces * " "}LOAD R0, ({label})\n')
                    p(f'{spaces * " "}PUSH R0\n')

                scope.table[l].dist = 0
                dist += 4 * elem_count

    # varijabla
    else:
        
        tip = item.attributes["tip"]
        
        if isinstance(tip, s.Const):
            tip = tip.primitive
    
        if len(item.parent.children) == 1:
            value = 0

            if value not in constants:
                constant_counter += 1
                constants[value] = f'C_{constant_counter}'

            label = constants[value]

            p(f'{spaces * " "}LOAD R0, ({label})\n')
            p(f'{spaces * " "}PUSH R0\n')

        elif len(item.parent.children) == 3:

            generiraj_izraz_pridruzivanja(item.parent.children[2].children[0], scope)

            # na stogu se sada nalazi ta varijabla s vrijednošću i nije ju potrebno mijenjati

        scope.table[l].dist = 0
        dist += 4

    return dist

def generiraj_naredba(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<slozena_naredba>"]:
        generiraj_slozena_naredba(instruction.children[0], scope)

    elif children == ["<izraz_naredba>"]:
        generiraj_izraz_naredba(instruction.children[0], scope)
        p(f'{spaces * " "}ADD R7, %D 4, R7\n')
    
    elif children == ["<naredba_grananja>"]:
        generiraj_naredba_grananja(instruction.children[0], scope)

    elif children == ["<naredba_petlje>"]:
        generiraj_naredba_petlje(instruction.children[0], scope)

    elif children == ["<naredba_skoka>"]:
        generiraj_naredba_skoka(instruction.children[0], scope)

def generiraj_slozena_naredba(instruction, scope):

    instructions = []
    scope = instruction.symbol_table
    dist = 0

    # čuvanje konteksta
    dist += 24
    for i in [0,1,2,3,4,5]:
        p(f'{spaces * " "}PUSH R{i}\n')

    scope.dist = dist

    body = instruction.children[-2]
    while len(body.children) > 1:
        instructions.insert(0, body.children[1])
        body = body.children[0]
    instructions.insert(0, body.children[0])

    # deklaracije
    if len(scope.table) > 0:
        for item in scope.table:
            old_dist = dist
            dist = generate_local_variable(item, scope, dist)
            diff = dist - old_dist
            if diff > 0:
                for var in scope.table:
                    if scope.table[var].dist is not None and var != item:
                        scope.table[var].dist += diff

            p(f'{spaces * " "}MOVE R7, R5\n')
            scope.dist = dist

    for instruction in instructions:
        generiraj_naredba(instruction, scope)

    # micanje lokalnih varijabli sa stoga
    if len(scope.table) > 0:
        p(f'{spaces * " "}ADD R7, %D {scope.dist-24}, R7\n')

    # obnova konteksta
    for i in [5,4,3,2,1,0]:
        p(f'{spaces * " "}POP R{i}\n')

def generiraj_naredba_grananja(instruction, scope):
    global label_counter
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        generiraj_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label1}\n')
        
        generiraj_naredba(instruction.children[4], scope)

        p(f'{label1}{(spaces - len(label1))  * " "}ADD R0, %D 0, R0\n')

    elif children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]:
        generiraj_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label1}\n')

        generiraj_naredba(instruction.children[4], scope)

        p(f'{spaces * " "}JP {label2}\n')

        p(f'{label1}{(spaces - len(label1))  * " "}ADD R0, %D 0, R0\n')
        
        generiraj_naredba(instruction.children[6], scope)
        
        p(f'{label2}{(spaces - len(label2))  * " "}ADD R0, %D 0, R0\n')

def generiraj_izraz_naredba(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<izraz>", "TOCKAZAREZ"]:
        generiraj_izraz(instruction.children[0], scope)

def generiraj_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))
            
    if children == ["<izraz_pridruzivanja>"]:
        generiraj_izraz_pridruzivanja(instruction.children[0], scope)

    elif children == ["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]:
        generiraj_izraz(instruction.children[0], scope)
        p(f'{spaces * " "}ADD R7, %D 4, R7\n')
        generiraj_izraz_pridruzivanja(instruction.children[2], scope)

def generiraj_izraz_pridruzivanja(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))
            
    if children == ["<log_ili_izraz>"]:
        generiraj_log_ili_izraz(instruction.children[0], scope)

    elif children == ["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]:
        generiraj_izraz_pridruzivanja(instruction.children[2], scope)
        is_local = dohvati_postfiks_izraz(instruction.children[0], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}STORE R0, (R1)\n')
        p(f'{spaces * " "}PUSH R0\n')
        
def generiraj_log_ili_izraz(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<log_i_izraz>"]:
        generiraj_log_i_izraz(instruction.children[0], scope)

    elif children == ["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]:
        instructions = []
        curr = instruction
        while len(curr.children) > 1:
            instructions.insert(0, curr.children[2])
            curr = curr.children[0]
        instructions.insert(0, curr.children[0])

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        for instr in instructions:
            generiraj_log_i_izraz(instr, scope)
            p(f'{spaces * " "}POP R0\n')
            p(f'{spaces * " "}CMP R0, %D 0\n')
            p(f'{spaces * " "}JP_NE {label1}\n')
        
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2))* " "}PUSH R0\n')

def generiraj_log_i_izraz(instruction, scope):
    global label_counter

    # TODO short-circuiting

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_ili_izraz>"]:
        generiraj_bin_ili_izraz(instruction.children[0], scope)

    elif children == ["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]:
        instructions = []
        curr = instruction
        while len(curr.children) > 1:
            instructions.insert(0, curr.children[2])
            curr = curr.children[0]
        instructions.insert(0, curr.children[0])

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        for instr in instructions:
            generiraj_bin_ili_izraz(instr, scope)
            p(f'{spaces * " "}POP R0\n')
            p(f'{spaces * " "}CMP R0, %D 0\n')
            p(f'{spaces * " "}JP_EQ {label1}\n')
        
        p(f'{spaces * " "}MOVE %D 1, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 0, R0\n')
        p(f'{label2}{(spaces - len(label2))* " "}PUSH R0\n')

def generiraj_bin_ili_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_xili_izraz>"]:
        generiraj_bin_xili_izraz(instruction.children[0], scope)

    elif children == ["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]:
        generiraj_bin_ili_izraz(instruction.children[0], scope)
        generiraj_bin_xili_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}OR R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

def generiraj_bin_xili_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_i_izraz>"]:
        generiraj_bin_i_izraz(instruction.children[0], scope)

    elif children == ["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]:
        generiraj_bin_xili_izraz(instruction.children[0], scope)
        generiraj_bin_i_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}XOR R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

def generiraj_bin_i_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<jednakosni_izraz>"]:
        generiraj_jednakosni_izraz(instruction.children[0], scope)

    elif children == ["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]:
        generiraj_bin_i_izraz(instruction.children[0], scope)
        generiraj_jednakosni_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}AND R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

def generiraj_jednakosni_izraz(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<odnosni_izraz>"]:
        generiraj_odnosni_izraz(instruction.children[0], scope)

    elif children == ["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"]:
        generiraj_jednakosni_izraz(instruction.children[0], scope)
        generiraj_odnosni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_EQ {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

    elif children == ["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]:
        generiraj_jednakosni_izraz(instruction.children[0], scope)
        generiraj_odnosni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_NE {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

def generiraj_odnosni_izraz(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<aditivni_izraz>"]:
        generiraj_aditivni_izraz(instruction.children[0], scope)

    elif children == ["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"]:
        generiraj_odnosni_izraz(instruction.children[0], scope)
        generiraj_aditivni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_SLT {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

    elif children == ["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"]:
        generiraj_odnosni_izraz(instruction.children[0], scope)
        generiraj_aditivni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_SGT {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

    elif children == ["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"]:
        generiraj_odnosni_izraz(instruction.children[0], scope)
        generiraj_aditivni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_SLE {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

    elif children == ["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]:
        generiraj_odnosni_izraz(instruction.children[0], scope)
        generiraj_aditivni_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, R1\n')
        p(f'{spaces * " "}JP_SGE {label1}\n')
        p(f'{spaces * " "}MOVE %D 0, R0\n')
        p(f'{spaces * " "}JP {label2}\n')
        p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 1, R0\n')
        p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

def generiraj_aditivni_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<multiplikativni_izraz>"]:
        generiraj_multiplikativni_izraz(instruction.children[0], scope)

    elif children == ["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"]:
        generiraj_aditivni_izraz(instruction.children[0], scope)
        generiraj_multiplikativni_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}ADD R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]:
        generiraj_aditivni_izraz(instruction.children[0], scope)
        generiraj_multiplikativni_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}SUB R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

def generiraj_multiplikativni_izraz(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<cast_izraz>"]:
        generiraj_cast_izraz(instruction.children[0], scope)

    elif children == ["<multiplikativni_izraz>", "OP_PUTA", "<cast_izraz>"]:
        generiraj_multiplikativni_izraz(instruction.children[0], scope)
        generiraj_cast_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'
        label_counter += 1
        label3 = f'L_{label_counter}'
        label_counter += 1
        label4 = f'L_{label_counter}'
        label_counter += 1
        label5 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R2\n')
        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}MOVE %D 0, R3\n')
        p(f'{spaces * " "}LOAD R4, (M_1)\n')
        p(f'{spaces * " "}CMP R1, %D 0\n')
        p(f'{spaces * " "}JP_SGE {label1}\n')
        p(f'{spaces * " "}XOR R1, R4, R1\n')
        p(f'{spaces * " "}ADD R1, %D 1, R1\n')
        p(f'{spaces * " "}ADD R3, %D 1, R3\n')
        p(f'{label1}{(spaces - len(label1))* " "}CMP R2, %D 0\n')
        p(f'{spaces * " "}JP_SGE {label2}\n')
        p(f'{spaces * " "}XOR R2, R4, R2\n')
        p(f'{spaces * " "}ADD R2, %D 1, R2\n')
        p(f'{spaces * " "}ADD R3, %D 1, R3\n')
        p(f'{label2}{(spaces - len(label2))* " "}MOVE %D 0, R0\n')
        p(f'{label3}{(spaces - len(label3)) * " "}CMP R2, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label4}\n')
        p(f'{spaces * " "}SUB R2, %D 1, R2\n')
        p(f'{spaces * " "}ADD R0, R1, R0\n')
        p(f'{spaces * " "}JP {label3}\n')
        p(f'{label4}{(spaces - len(label4)) * " "}AND R3, %D 1, R3\n')
        p(f'{spaces * " "}CMP R3, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label5}\n')
        p(f'{spaces * " "}XOR R0, R4, R0\n')
        p(f'{spaces * " "}ADD R0, %D 1, R0\n')
        p(f'{label5}{(spaces - len(label5)) * " "}PUSH R0\n')

    elif children == ["<multiplikativni_izraz>", "OP_DIJELI", "<cast_izraz>"]:
        generiraj_multiplikativni_izraz(instruction.children[0], scope)
        generiraj_cast_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'
        label_counter += 1
        label3 = f'L_{label_counter}'
        label_counter += 1
        label4 = f'L_{label_counter}'
        label_counter += 1
        label5 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R2\n')
        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}MOVE %D 0, R3\n')
        p(f'{spaces * " "}LOAD R4, (M_1)\n')
        p(f'{spaces * " "}CMP R1, %D 0\n')
        p(f'{spaces * " "}JP_SGE {label1}\n')
        p(f'{spaces * " "}XOR R1, R4, R1\n')
        p(f'{spaces * " "}ADD R1, %D 1, R1\n')
        p(f'{spaces * " "}ADD R3, %D 1, R3\n')
        p(f'{label1}{(spaces - len(label1))* " "}CMP R2, %D 0\n')
        p(f'{spaces * " "}JP_SGE {label2}\n')
        p(f'{spaces * " "}XOR R2, R4, R2\n')
        p(f'{spaces * " "}ADD R2, %D 1, R2\n')
        p(f'{spaces * " "}ADD R3, %D 1, R3\n')
        p(f'{label2}{(spaces - len(label2))* " "}MOVE %D 0, R0\n')
        p(f'{label3}{(spaces - len(label3)) * " "}CMP R1, R2\n')
        p(f'{spaces * " "}JP_SLT {label4}\n')
        p(f'{spaces * " "}SUB R1, R2, R1\n')
        p(f'{spaces * " "}ADD R0, %D 1, R0\n')
        p(f'{spaces * " "}JP {label3}\n')
        p(f'{label4}{(spaces - len(label4)) * " "}AND R3, %D 1, R3\n')
        p(f'{spaces * " "}CMP R3, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label5}\n')
        p(f'{spaces * " "}XOR R0, R4, R0\n')
        p(f'{spaces * " "}ADD R0, %D 1, R0\n')
        p(f'{label5}{(spaces - len(label5)) * " "}PUSH R0\n')

    elif children == ["<multiplikativni_izraz>", "OP_MOD", "<cast_izraz>"]:
        generiraj_multiplikativni_izraz(instruction.children[0], scope)
        generiraj_cast_izraz(instruction.children[2], scope)

        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{spaces * " "}POP R2\n')
        p(f'{spaces * " "}POP R1\n')
        p(f'{label1}{(spaces - len(label1)) * " "}CMP R1, R2\n')
        p(f'{spaces * " "}JP_SLT {label2}\n')
        p(f'{spaces * " "}SUB R1, R2, R1\n')
        p(f'{spaces * " "}JP {label1}\n')
        p(f'{label2}{(spaces - len(label2)) * " "}MOVE R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

def generiraj_cast_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<unarni_izraz>"]:
        generiraj_unarni_izraz(instruction.children[0], scope)

    elif children == ["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]:
        generiraj_cast_izraz(instruction.children[3], scope) 

def generiraj_unarni_izraz(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<postfiks_izraz>"]:
        generiraj_postfiks_izraz(instruction.children[0], scope)

    elif children == ["OP_INC", "<unarni_izraz>"]:
        generiraj_unarni_izraz(instruction.children[1], scope)
        is_local = generiraj_unarni_izraz(instruction.children[1], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}ADD R0, %D 1, R0\n')
        p(f'{spaces * " "}STORE R0, (R1)\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["OP_DEC", "<unarni_izraz>"]:
        generiraj_unarni_izraz(instruction.children[1], scope)
        is_local = generiraj_unarni_izraz(instruction.children[1], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}SUB R0, %D 1, R0\n')
        p(f'{spaces * " "}STORE R0, (R1)\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["<unarni_operator>", "<cast_izraz>"]:
        generiraj_cast_izraz(instruction.children[1], scope)
        operator = instruction.children[0].children[0].symbol

        p(f'{spaces * " "}POP R0\n')

        if operator == "PLUS":
            p(f'{spaces * " "}PUSH R0\n')

        elif operator == "MINUS":
            p(f'{spaces * " "}LOAD R1, (M_1)\n')
            p(f'{spaces * " "}X0R R0, R1, R0\n')
            p(f'{spaces * " "}ADD R0, %D 1, R0\n')
            p(f'{spaces * " "}PUSH R0\n')

        elif operator == "OP_TILDA":
            p(f'{spaces * " "}LOAD R1, (M_1)\n')
            p(f'{spaces * " "}X0R R0, R1, R0\n')
            p(f'{spaces * " "}PUSH R0\n')

        elif operator == "OP_NEG":
            label_counter += 1
            label1 = f'L_{label_counter}'
            label_counter += 1
            label2 = f'L_{label_counter}'

            p(f'{spaces * " "}CMP R0, %D 0\n')
            p(f'{spaces * " "}JP_NE {label1}\n')
            p(f'{spaces * " "}MOVE %D 1, R0\n')
            p(f'{spaces * " "}JP {label2}\n')
            p(f'{label1}{(spaces - len(label1)) * " "}MOVE %D 0, R0\n')
            p(f'{label2}{(spaces - len(label2)) * " "}PUSH R0\n')

def generiraj_postfiks_izraz(instruction, scope, is_array=False):

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<primarni_izraz>"]:
        return generiraj_primarni_izraz(instruction.children[0], scope, is_array)

    elif children == ["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]:
        is_local = generiraj_postfiks_izraz(instruction.children[0], scope, is_array=True)
        generiraj_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}SHL R1, %D 2, R1\n')
        p(f'{spaces * " "}ADD R0, R1, R1\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}LOAD R0, (R1)\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]:
        pass

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]:
        pass

    elif children == ["<postfiks_izraz>", "OP_INC"]:
        generiraj_postfiks_izraz(instruction.children[0], scope)
        is_local = dohvati_postfiks_izraz(instruction.children[0], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}MOVE R0, R2\n')
        p(f'{spaces * " "}ADD R0, %D 1, R0\n')
        p(f'{spaces * " "}STORE R0, (R1)\n')
        p(f'{spaces * " "}PUSH R2\n')

    elif children == ["<postfiks_izraz>", "OP_DEC"]:
        generiraj_postfiks_izraz(instruction.children[0], scope)
        is_local = dohvati_postfiks_izraz(instruction.children[0], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        if is_local:
            p(f'{spaces * " "}ADD R1, R5, R1\n')
        p(f'{spaces * " "}MOVE R0, R2\n')
        p(f'{spaces * " "}SUB R0, %D 1, R0\n')
        p(f'{spaces * " "}STORE R0, (R1)\n')
        p(f'{spaces * " "}PUSH R2\n')

def generiraj_primarni_izraz(instruction, scope, is_array = False):
    global constant_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["IDN"]:
        var_name = instruction.children[0].lexical_unit
        offset = 0
        label = None
        while var_name not in scope.table or scope.table[var_name].dist is None:
            offset += scope.dist
            scope = scope.parent
            if scope.parent is None:
                label = globals[var_name]
                offset = None
                break 

        if label is None:
            offset += scope.table[var_name].dist
            if offset not in constants:
                constant_counter += 1
                constants[offset] = f'C_{constant_counter}'

            if not is_array:
                p(f'{spaces * " "}LOAD R1, ({constants[offset]})\n')
                p(f'{spaces * " "}ADD R1, R5, R1\n')
                p(f'{spaces * " "}LOAD R0, (R1)\n')
                p(f'{spaces * " "}PUSH R0\n')

            else:
                p(f'{spaces * " "}LOAD R0, ({constants[offset]})\n')
                p(f'{spaces * " "}PUSH R0\n')

            return True

        elif offset is None:

            if not is_array:
                p(f'{spaces * " "}LOAD R0, ({label})\n') 
                p(f'{spaces * " "}PUSH R0\n')

            else:
                p(f'{spaces * " "}MOVE {label}, R0\n') 
                p(f'{spaces * " "}PUSH R0\n')

            return False

    elif children == ["BROJ"]:
        item = int(instruction.children[0].lexical_unit)
        if item not in constants:
            constant_counter += 1
            constants[item] = f'C_{constant_counter}'
        label = constants[item]

        p(f'{spaces * " "}LOAD R0, ({label})\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["ZNAK"]:
        item = ord(instruction.children[0].lexical_unit[1])
        if item not in constants:
            constant_counter += 1
            constants[item] = f'C_{constant_counter}'
        label = constants[item]

        p(f'{spaces * " "}LOAD R0, ({label})\n')
        p(f'{spaces * " "}PUSH R0\n')

    elif children == ["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]:
        generiraj_izraz(instruction.children[1], scope)

    # ne bi trebalo biti moguće
    """ elif children == ["NIZ_ZNAKOVA"]: """

def dohvati_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<izraz_pridruzivanja>"]:
        return dohvati_izraz_pridruzivanja(instruction.children[0], scope)

def dohvati_izraz_pridruzivanja(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<log_ili_izraz>"]:
        return dohvati_log_ili_izraz(instruction.children[0], scope)

def dohvati_log_ili_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<log_i_izraz>"]:
        return dohvati_log_i_izraz(instruction.children[0], scope)

def dohvati_log_i_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_ili_izraz>"]:
        return dohvati_bin_ili_izraz(instruction.children[0], scope)

def dohvati_bin_ili_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_xili_izraz>"]:
        return dohvati_bin_xili_izraz(instruction.children[0], scope)

def dohvati_bin_xili_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<bin_i_izraz>"]:
        return dohvati_bin_i_izraz(instruction.children[0], scope)

def dohvati_bin_i_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<jednakosni_izraz>"]:
        return dohvati_jednakosni_izraz(instruction.children[0], scope)

def dohvati_jednakosni_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<odnosni_izraz>"]:
        return dohvati_odnosni_izraz(instruction.children[0], scope)

def dohvati_odnosni_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<aditivni_izraz>"]:
        return dohvati_aditivni_izraz(instruction.children[0], scope)

def dohvati_aditivni_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<multiplikativni_izraz>"]:
        return dohvati_multiplikativni_izraz(instruction.children[0], scope)

def dohvati_multiplikativni_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<cast_izraz>"]:
        return dohvati_cast_izraz(instruction.children[0], scope)

def dohvati_cast_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<unarni_izraz>"]:
        return dohvati_unarni_izraz(instruction.children[0], scope)

def dohvati_unarni_izraz(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["<postfiks_izraz>"]:
        return dohvati_postfiks_izraz(instruction.children[0], scope)

def dohvati_postfiks_izraz(instruction, scope):

    children = list(map(lambda n: n.symbol, instruction.children))
            
    if children == ["<primarni_izraz>"]:
        return dohvati_primarni_izraz(instruction.children[0], scope)

    elif children == ["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]:
        is_local = dohvati_postfiks_izraz(instruction.children[0], scope)
        generiraj_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R1\n')
        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}SHL R1, %D 2, R1\n')
        p(f'{spaces * " "}ADD R0, R1, R0\n')
        p(f'{spaces * " "}PUSH R0\n')

        return is_local

def dohvati_primarni_izraz(instruction, scope):
    global constant_counter
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["IDN"]:
        var_name = instruction.children[0].lexical_unit
        offset = 0
        while var_name not in scope.table or scope.table[var_name].dist is None:
            offset += scope.dist
            scope = scope.parent
            if scope.parent is None:
                p(f'{spaces * " "}MOVE {globals[var_name]}, R0\n')
                p(f'{spaces * " "}PUSH RO\n')
                return False
        
        offset += scope.table[var_name].dist
        if offset not in constants:
            constant_counter += 1
            constants[offset] = f'C_{constant_counter}'

        p(f'{spaces * " "}LOAD R0, ({constants[offset]})\n')
        p(f'{spaces * " "}PUSH RO\n')

        return True

    elif children == ["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]:
        return dohvati_izraz(instruction.children[1], scope)

def generiraj_naredba_petlje(instruction, scope):
    global label_counter

    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        p(f'{label1}{(spaces - len(label1)) * " "}ADD R0, %D 0, R0\n')

        generiraj_izraz(instruction.children[2], scope)

        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label2}\n')

        generiraj_naredba(instruction.children[4], scope)

        p(f'{spaces * " "}JP {label1}\n')
        p(f'{label2}{(spaces - len(label2)) * " "}ADD R0, %D 0, R0\n')

        instruction.attributes["start_label"] = label1
        instruction.attributes["end_label"] = label2

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "D_ZAGRADA", "<naredba>"]:
        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        generiraj_izraz_naredba(instruction.children[2], scope)
        p(f'{spaces * " "}ADD R7, %D 4, R7\n')

        p(f'{label1}{(spaces - len(label1)) * " "}ADD R0, %D 0, R0\n')

        generiraj_izraz_naredba(instruction.children[3], scope)

        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label2}\n')

        generiraj_naredba(instruction.children[5], scope)

        p(f'{spaces * " "}JP {label1}\n')
        p(f'{label2}{(spaces - len(label2)) * " "}ADD R0, %D 0, R0\n')

        instruction.attributes["start_label"] = label1
        instruction.attributes["end_label"] = label2

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        label_counter += 1
        label1 = f'L_{label_counter}'
        label_counter += 1
        label2 = f'L_{label_counter}'

        generiraj_izraz_naredba(instruction.children[2], scope)
        p(f'{spaces * " "}ADD R7, %D 4, R7\n')

        p(f'{label1}{(spaces - len(label1)) * " "}ADD R0, %D 0, R0\n')

        generiraj_izraz_naredba(instruction.children[3], scope)

        p(f'{spaces * " "}POP R0\n')
        p(f'{spaces * " "}CMP R0, %D 0\n')
        p(f'{spaces * " "}JP_EQ {label2}\n')

        generiraj_naredba(instruction.children[6], scope)
        generiraj_izraz(instruction.children[4], scope)

        p(f'{spaces * " "}ADD R7, %D 4, R7\n')

        p(f'{spaces * " "}JP {label1}\n')
        p(f'{label2}{(spaces - len(label2)) * " "}ADD R0, %D 0, R0\n')

        instruction.attributes["start_label"] = label1
        instruction.attributes["end_label"] = label2

def generiraj_naredba_skoka(instruction, scope):
    
    children = list(map(lambda n: n.symbol, instruction.children))

    if children == ["KR_CONTINUE", "TOCKAZAREZ"]:
        pass

    elif children == ["KR_BREAK", "TOCKAZAREZ"]:
        pass

    elif children == ["KR_RETURN", "TOCKAZAREZ"]:
        pass

    elif children == ["KR_RETURN", "<izraz>", "TOCKAZAREZ"]:
        pass

if __name__ == "__main__":
    
    # semantička analiza nad generativnim stablom na standardnom ulazu
    s.semantic_analysis()

    # inicijalizacija i završetak izvođenja programa
    p(f'{spaces * " "}MOVE 40000, R7\n')
    p(f'{spaces * " "}CALL F_MAIN\n')
    p(f'{spaces * " "}HALT\n\n')

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
        p(f'{constants[c]}{(spaces-len(constants[c])) * " "}DW %D {c}\n')

    # zapis maski
    p(f'\nM_1{(spaces-3) * " "}DW %B 11111111111111111111111111111111\n')

    # zatvaranje datoteke
    machine_code.close()

    '''
        TODO:
            <naredba_petlje>
            <naredba_skoka>
            pozivanje funkcija, return izrazi - ovdje paziti na polja kao parametre funkcija
    '''