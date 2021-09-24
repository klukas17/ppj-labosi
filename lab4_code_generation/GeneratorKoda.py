import SemantickiAnalizator as s

# varijabla za tabulatore u a.frisc datoteci
tabs = "\t\t"

# tablica funkcija
functions = {}

# tablica globalnih varijabli
globals = {}

# adresa početka globalnih varijabli
global_curr = 12

# brojači
function_counter = 0
global_counter = 0
constant_counter = 0

# globalna varijabla za a.frisc datoteku
machine_code = open("a.frisc", "w")

# funkcija generira strojni kod za danu funkciju
def generate_function(f):
    machine_code.write(f'{functions[f]}\n')
    machine_code.write(f'{tabs}RET\n\n')

# funkcija generira strojni kod za danu globalnu varijablu
def generate_global(g):
    machine_code.write(f'{globals[g]}{tabs}')

    # dohvaćanje varijable
    item = s.generative_tree_root.symbol_table.table[g]

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

if __name__ == "__main__":
    
    # semantička analiza nad generativnim stablom na standardnom ulazu
    s.semantic_analysis()

    # inicijalizacija i završetak izvođenja programa
    machine_code.write(f'{tabs}MOVE 40000, R7\n')
    machine_code.write(f'{tabs}CALL F_MAIN\n')
    machine_code.write(f'{tabs}HALT\n\n')

    # dodavanje main funkcije u riječnik funkcija
    functions["main"] = "F_MAIN"

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

    # obrada funkcija
    for f in functions:
        generate_function(f)

    # obrada globalnih varijabli
    for g in globals:
        generate_global(g)

    # zatvaranje datoteke
    machine_code.close()