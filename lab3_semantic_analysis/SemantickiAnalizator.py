from typing import Union

# klasa za modeliranje tablice znakova
class Symbol_Table():
    def __init__(self):
        self.table = {}
        self.parent = None

# apstraktna klasa za modeliranje čvora generativnog stabla
class Abs_Node():
    def __init__(self):
        pass

# klasa za modeliranje unutarnjeg čvora generativnog stabla
class Node(Abs_Node):
    def __init__(self, symbol: str, parent: Abs_Node):
        Abs_Node.__init__(self)
        self.symbol = symbol
        self.children = []
        self.attributes = {}
        self.parent = parent
        self.symbol_table = None
    def __repr__(self) -> str:
        return self.symbol

# klasa za modeliranje lista stabla
class Leaf(Abs_Node):
    def __init__(self, symbol: str, line: int, lexical_unit: str, parent: Abs_Node):
        Abs_Node.__init__(self)
        self.symbol = symbol
        self.line = line
        self.lexical_unit = lexical_unit
        self.parent = parent
    def __repr__(self) -> str:
        return self.symbol

# klasa za modeliranje praznog lista stabla (epsilon produkcija)
class Empty_Leaf(Abs_Node):
    def __init__(self):
        Abs_Node.__init__(self)
    def __repr__(self) -> str:
        return "$"

# apstraknta klasa za modeliranje numeričkog tipa
class Numeric_Type():
    def __init__(self):
        pass

# klasa za modeliranje cijelog broja
class Int(Numeric_Type):
    def __init__(self):
        Numeric_Type.__init__(self)

# klasa za modeliranje znaka
class Char(Numeric_Type):
    def __init__(self):
        Numeric_Type.__init__(self)

# klasa za modeliranje konstante varijable
class Const():
    def __init__(self, primitive: Numeric_Type):
        self.primitive = primitive

# klasa za modeliranje nizova
class Array():
    def __init__(self, primitive: Union[Numeric_Type, Const]):
        self.primitive = primitive

# klasa za modeliranje tipa void
class Void():
    def __init__(self):
        pass

# klasa za modeliranje funkcije
class Function():
    def __init__(self, params, ret_val, node):
        self.params = params
        self.ret_val = ret_val
        self.node = node

# varijabla za spremanje korijena generativnog stabla
generative_tree_root = None

# riječnik u kojem se pamte definicije svih funkcija
function_definitions = {}

# lista svih djelokruga
scopes = []

# funkcija koja sa standardnog ulaza čita generativno stablo
def read_generative_tree() -> None:

    global generative_tree_root
    
    # lista čvorova generativnog stabla čija djeca se trenutno grade
    active_nodes = []

    # čitanje korijena generativnog stabla
    generative_tree_root = Node(input(), None)
    active_nodes.append(generative_tree_root)

    # čitanje standardnog ulaza
    try:
        
        while True:

            line = input()
            if line == "":
                continue

            s = line
            whitespace_count = 0
            while s[0] == ' ':
                whitespace_count += 1
                s = s[1:]

            s = s.split(" ")

            # unutarnji čvor generativnog stabla ili prazan list
            if len(s) == 1:
                s = s[0]

                # prazan list
                if s == "$":
                    active_nodes[whitespace_count-1].children.append(Empty_Leaf())
                
                # unutarnji čvor
                else:
                    curr_node = Node(s, active_nodes[whitespace_count-1])
                    active_nodes[whitespace_count-1].children.append(curr_node)

                    if len(active_nodes) > whitespace_count:
                        active_nodes = active_nodes[:whitespace_count]
                        active_nodes.append(curr_node)
                    else:
                        active_nodes.append(curr_node)

            # uniformna jedinka, tj. list generativnog stabla
            else:
                active_nodes[whitespace_count-1].children.append(Leaf(s[0], s[1], s[2], active_nodes[whitespace_count-1]))
            
    except EOFError:
        pass

# funkcija za ispis produkcije u kojoj je otkrivena semantička greška
def print_error(node: Node):
    error_message = ""
    error_message += node.symbol
    error_message += " ::="
    for child in node.children:
        error_message += " "
        if isinstance(child, Leaf):
            error_message += f'{child.symbol}({child.line},{child.lexical_unit})'
        elif isinstance(child, Node):
            error_message += child.symbol
    print(error_message)
    exit()

# funkcija računa broj znakova u stringu
def count_chars(s: str) -> int:
    ret_val = 0
    curr_index = 0

    while curr_index < len(s):
        if s[curr_index] != "\\":
            ret_val += 1
            curr_index += 1
        else:
            ret_val += 1
            curr_index += 2

    return ret_val

def provjeri_primarni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table

    if children == ["IDN"]:
        IDN = None
        found = False
        curr_scope = node.symbol_table
        var = node.children[0].lexical_unit
        while not found and curr_scope is not None:
            if var in curr_scope.table:
                found = True
                IDN = curr_scope.table[var]
            else:
                curr_scope = curr_scope.parent
        if not found:
            print_error(node)

        if isinstance(IDN, Function):
            node.attributes["tip"] = IDN
            node.attributes["l-izraz"] = 0
        else:
            node.attributes["tip"] = IDN.attributes["tip"] if "tip" in IDN.attributes else None
            node.attributes["l-izraz"] = IDN.attributes["l-izraz"] if "l-izraz" in IDN.attributes else None

    elif children == ["BROJ"]:
        value = int(node.children[0].lexical_unit)
        if value < -2**31 or value > 2**31 - 1: 
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

    elif children == ["ZNAK"]:
        value = node.children[0].lexical_unit
        if len(value) > 1 and value[0] == "\\" and value[1] not in ["t", "n", "0", "'", "\"", "\\"]:
            print_error(node)
        elif len(value) == 1 and (ord(value) < 0 or ord(value) > 255):
            print_error(node)

        node.attributes["tip"] = Char()
        node.attributes["l-izraz"] = 0

    elif children == ["NIZ_ZNAKOVA"]:
        value = node.children[0].lexical_unit
        i = 0
        while i < len(value):
            if value[i] != "\\":
                i += 1
            else:
                i += 1
                if value[i] not in ["t", "n", "0", "'", "\"", "\\"]:
                    print_error(node)
                else:
                    i += 1

        node.attributes["tip"] = Array(Const(Char()))
        node.attributes["l-izraz"] = 0

    elif children == ["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]:
        provjeri_izraz(node.children[1])

        node.attributes["tip"] = node.children[1].attributes["tip"] if "tip" in node.children[1].attributes else None
        node.attributes["l-izraz"] = node.children[1].attributes["l-izraz"] if "l-izraz" in node.children[1].attributes else None

def provjeri_postfiks_izraz(node: Node):
    
    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<primarni_izraz>"]:
        provjeri_primarni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]:
        X = None
        provjeri_postfiks_izraz(node.children[0])
        if isinstance(node.children[0].attributes["tip"], Array):
            X = node.children[0].attributes["tip"].primitive
        else:
            print_error(node)
        provjeri_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = X
        node.attributes["l-izraz"] = 1 if not isinstance(X, Const) else 0

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]:
        pov = None
        provjeri_postfiks_izraz(node.children[0])
        if isinstance(node.children[0].attributes["tip"], Function):
            funct = node.children[0].attributes["tip"]
            if isinstance(funct.params, Void):
                pov = funct.ret_val
            else:
                print_error(node)
        else:
            print_error(node)
        
        node.attributes["tip"] = pov
        node.attributes["l-izraz"] = 0

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]:
        pov = None
        provjeri_postfiks_izraz(node.children[0])
        provjeri_lista_argumenata(node.children[2])
        if isinstance(node.children[0].attributes["tip"], Function):
            funct = node.children[0].attributes["tip"]
            pov = funct.ret_val
            if len(node.children[2].attributes["tipovi"]) != len(funct.params):
                print_error(node)
            else:
                for i in range(len(node.children[2].attributes["tipovi"])):
                    if not check_types(node.children[2].attributes["tipovi"][i], funct.params[i]):
                        print_error(node)

        else:
            print_error(node)

        node.attributes["tip"] = pov
        node.attributes["l-izraz"] = 0

    elif children == ["<postfiks_izraz>", "OP_INC"] or \
         children == ["<postfiks_izraz>", "OP_DEC"]:
        provjeri_postfiks_izraz(node.children[0])
        if not node.children[0].attributes["l-izraz"] == 1 or \
           not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_lista_argumenata(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<izraz_pridruzivanja>"]:
        provjeri_izraz_pridruzivanja(node.children[0])

        node.attributes["tipovi"] = [node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None]

    elif children == ["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]:
        provjeri_lista_argumenata(node.children[0])
        provjeri_izraz_pridruzivanja(node.children[2])

        node.attributes["tipovi"] = node.children[0].attributes["tipovi"] + [node.children[2].attributes["tip"] if "tip" in node.children[2].attributes else None]

def provjeri_unarni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<postfiks_izraz>"]:
        provjeri_postfiks_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["OP_INC", "<unarni_izraz>"] or \
         children == ["OP_DEC", "<unarni_izraz>"]:
        provjeri_unarni_izraz(node.children[1])
        if node.children[1].attributes["l-izraz"] != 1 or \
           not check_types(node.children[1].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

    elif children == ["<unarni_operator>", "<cast_izraz>"]:
        provjeri_cast_izraz(node.children[1])
        if not check_types(node.children[1].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_unarni_operator(node: Node):
    pass

def provjeri_cast_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<unarni_izraz>"]:
        provjeri_unarni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"]  if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"]  if "l-izraz" in node.children[0].attributes else None

    elif children == ["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]:
        provjeri_ime_tipa(node.children[1])
        provjeri_cast_izraz(node.children[3])
        if not check_cast(node.children[3].attributes["tip"], node.children[1].attributes["tip"]):
            print_error(node)
        
        node.attributes["tip"] = node.children[1].attributes["tip"]  if "tip" in node.children[1].attributes else None
        node.attributes["l-izraz"] = 0

def provjeri_ime_tipa(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<specifikator_tipa>"]:
        provjeri_specifikator_tipa(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None

    elif children == ["KR_CONST", "<specifikator_tipa>"]:
        provjeri_specifikator_tipa(node.children[1])
        if isinstance(node.children[1].attributes["tip"], Void):
            print_error(node)

        node.attributes["tip"] = Const(node.children[1].attributes["tip"] if "tip" in node.children[1].attributes else None)

def provjeri_specifikator_tipa(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["KR_VOID"]:
        node.attributes["tip"] = Void()

    elif children == ["KR_CHAR"]:
        node.attributes["tip"] = Char()

    elif children == ["KR_INT"]:
        node.attributes["tip"] = Int()

def provjeri_multiplikativni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<cast_izraz>"]:
        provjeri_cast_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<multiplikativni izraz>", "OP_PUTA", "<cast_izraz>"] or \
         children == ["<multiplikativni izraz>", "OP_DIJELI", "<cast_izraz>"] or \
         children == ["<multiplikativni izraz>", "OP_MOD", "<cast_izraz>"]:
        provjeri_multiplikativni_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_cast_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_aditivni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<multiplikativni_izraz>"]:
        provjeri_multiplikativni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<aditivni_izraz>", "PLUS", "<multiplikativni_izraz>"] or \
         children == ["<aditivni_izraz>", "MINUS", "<multiplikativni_izraz>"]:
        provjeri_aditivni_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_multiplikativni_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_odnosni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<aditivni_izraz>"]:
        provjeri_aditivni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]:
        provjeri_odnosni_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_aditivni_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_jednakosni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<odnosni_izraz>"]:
        provjeri_odnosni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"] or \
         children == ["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]:
        provjeri_jednakosni_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_odnosni_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_bin_i_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<jednakosni_izraz>"]:
        provjeri_jednakosni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]:
        provjeri_bin_i_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_jednakosni_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_bin_xili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<bin_i_izraz>"]:
        provjeri_bin_i_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]:
        provjeri_bin_xili_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_bin_i_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_bin_ili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<bin_xili_izraz>"]:
        provjeri_bin_xili_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]:
        provjeri_bin_ili_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_bin_xili_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_log_i_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<bin_ili_izraz>"]:
        provjeri_bin_ili_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]:
        provjeri_log_i_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_bin_ili_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_log_ili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<log_i_izraz>"]:
        provjeri_log_i_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]:
        provjeri_log_ili_izraz(node.children[0])
        if not check_types(node.children[0].attributes["tip"], Int()):
            print_error(node)
        provjeri_log_i_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_izraz_pridruzivanja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<log_ili_izraz>"]:
        provjeri_log_ili_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]:
        provjeri_postfiks_izraz(node.children[0])
        if not node.children[0].attributes["l-izraz"] == 1:
            print_error(node)
        provjeri_izraz_pridruzivanja(node.children[2])
        if not check_types(node.children[2].attributes["tip"], node.children[0].attributes["tip"]):
            print_error(node)

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = 0

def provjeri_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<izraz_pridruzivanja>"]:
        provjeri_izraz_pridruzivanja(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"] if "l-izraz" in node.children[0].attributes else None

    elif children == ["<izraz>", "ZAREZ", "<izraz_pridruzivanja>"]:
        provjeri_izraz(node.children[0])
        provjeri_izraz_pridruzivanja(node.children[2])

        node.attributes["tip"] = node.children[2].attributes["tip"] if "tip" in node.children[2].attributes else None
        node.attributes["l-izraz"] = 0

def provjeri_slozena_naredba(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    new_symbol_table = Symbol_Table()
    new_symbol_table.parent = node.symbol_table
    node.symbol_table = new_symbol_table

    scopes.append(node.symbol_table)

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["L_VIT_ZAGRADA", "<lista_naredbi>", "D_VIT_ZAGRADA"]:
        provjeri_lista_naredbi(node.children[1])

    elif children == ["L_VIT_ZAGRADA", "<lista_deklaracija>", "<lista_naredbi>", "D_VIT_ZAGRADA"]:
        provjeri_lista_deklaracija(node.children[1])
        provjeri_lista_naredbi(node.children[2])

def provjeri_lista_naredbi(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<naredba>"]:
        provjeri_naredba(node.children[0])

    elif children == ["<lista_naredbi>", "<naredba>"]:
        provjeri_lista_naredbi(node.children[0])
        provjeri_naredba(node.children[1])

def provjeri_naredba(node: Node):
    
    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<slozena_naredba>"]:
        provjeri_slozena_naredba(node.children[0])

    elif children == ["<izraz_naredba>"]:
        provjeri_izraz_naredba(node.children[0])
    
    elif children == ["<naredba_grananja>"]:
        provjeri_naredba_grananja(node.children[0])

    elif children == ["<naredba_petlje>"]:
        provjeri_naredba_petlje(node.children[0])

    elif children == ["<naredba_skoka>"]:
        provjeri_naredba_skoka(node.children[0])

def provjeri_izraz_naredba(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["TOCKAZAREZ"]:
        node.attributes["tip"] = Int()

    elif children == ["<izraz>", "TOCKAZAREZ"]:
        provjeri_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None

def provjeri_naredba_grananja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        provjeri_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)
        provjeri_naredba(node.children[4])

    elif children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]:
        provjeri_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)
        provjeri_naredba(node.children[4])
        provjeri_naredba(node.children[6])

def provjeri_naredba_petlje(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
                
    if children == ["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        provjeri_izraz(node.children[2])
        if not check_types(node.children[2].attributes["tip"], Int()):
            print_error(node)
        provjeri_naredba(node.children[4])

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "D_ZAGRADA", "<naredba>"]:
        provjeri_izraz_naredba(node.children[2])
        provjeri_izraz_naredba[node.children[3]]
        if not check_types(node.children[3].attributes["tip"], Int()):
            print_error(node)
        provjeri_naredba(node.children[5])

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        provjeri_izraz_naredba(node.children[2])
        provjeri_izraz_naredba(node.children[3])
        if not check_types(node.children[3].attributes["tip"], Int()):
            print_error(node)
        provjeri_izraz(node.children[4])
        provjeri_naredba(node.children[6])

def provjeri_naredba_skoka(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["KR_CONTINUE", "TOCKAZAREZ"] or \
       children == ["KR_BREAK", "TOCKAZAREZ"]:
        check = False
        curr_node = node
        while not check and curr_node is not None:
            if isinstance(curr_node, Node) and curr_node.symbol == "<naredba_petlje>":
                check = True
            else:
                curr_node = curr_node.parent
        if not check:
            print_error(node)

    elif children == ["KR_RETURN", "TOCKAZAREZ"]:
        check = False
        curr_node = node
        while not check and curr_node is not None:
            if isinstance(curr_node, Node) and curr_node.symbol == "<definicija_funkcije>":
                n = curr_node.children[0]
                if isinstance(n, Node) and n.symbol == "<ime_tipa>":
                    n = n.children[0]
                    if isinstance(n, Node) and n.symbol == "<specifikator_tipa>":
                        if "tip" in n.attributes and isinstance(n.attributes["tip"], Void):
                            check = True
            if not check:
                curr_node = curr_node.parent
        if not check:
            print_error(node)

    elif children == ["KR_RETURN", "<izraz>", "TOCKAZAREZ"]:
        provjeri_izraz(node.children[1])
        check = False
        curr_node = node
        while not check and curr_node is not None:
            if isinstance(curr_node, Node) and curr_node.symbol == "<definicija_funkcije>":
                n = curr_node.children[0]
                if isinstance(n, Node) and n.symbol == "<ime_tipa>":
                    n = n.children[0]
                    if isinstance(n, Node) and n.symbol == "<specifikator_tipa>":
                        if "tip" in n.attributes and check_types(node.children[1].attributes["tip"], n.attributes["tip"]):
                            check = True
            if not check:
                curr_node = curr_node.parent
        if not check:
            print_error(node)

def provjeri_prijevodna_jedinica(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table

    if children == ["<vanjska_deklaracija>"]:
        provjeri_vanjska_deklaracija(node.children[0])

    elif children == ["<prijevodna_jedinica>", "<vanjska_deklaracija>"]:
        provjeri_prijevodna_jedinica(node.children[0])
        provjeri_vanjska_deklaracija(node.children[1])

def provjeri_vanjska_deklaracija(node: Node):
    
    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<definicija_funkcije>"]:
        provjeri_definicija_funkcije(node.children[0])

    elif children == ["<deklaracija>"]:
        provjeri_deklaracija(node.children[0])

def provjeri_definicija_funkcije(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    new_symbol_table = Symbol_Table()
    new_symbol_table.parent = node.symbol_table
    node.symbol_table = new_symbol_table

    scopes.append(node.symbol_table)

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA", "<slozena_naredba>"]:
        provjeri_ime_tipa(node.children[0])
        if isinstance(node.children[0].attributes["tip"], Const):
            print_error(node)
        new_funct_name = node.children[1].lexical_unit
        if new_funct_name in function_definitions:
            print_error(node)
        if new_funct_name in node.symbol_table.table:
            existing_function = node.symbol_table[new_funct_name]
            if not isinstance(existing_function.params, Void) or \
               type(node.children[0].attributes["tip"]) != type(existing_function.ret_val):
                print_error(node)
        function_definitions[new_funct_name] = node.parent.symbol_table.table[new_funct_name] = Function(Void(), node.children[0].attributes["tip"], node)
        provjeri_slozena_naredba(node.children[5])

    elif children == ["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA", "<slozena_naredba>"]:
        provjeri_ime_tipa(node.children[0])
        if isinstance(node.children[0].attributes["tip"], Const):
            print_error(node)
        new_funct_name = node.children[1].lexical_unit
        if new_funct_name in function_definitions:
            print_error(node)
        provjeri_lista_parametara(node.children[3])
        if new_funct_name in node.symbol_table.table:
            existing_function = node.symbol_table.table[new_funct_name]
            if type(node.children[0].attributes["tip"]) != type(existing_function.ret_val):
                print_error(node)
            if len(existing_function.params) != len(node.children[3].attributes["tipovi"]):
                print_error(node)
            else:
                for i in range(len(existing_function.params)):
                    if type(existing_function.params[i]) != type(node.children[3].attributes["tipovi"][i]):
                        print_error(node)
        function_definitions[new_funct_name] = node.parent.symbol_table.table[new_funct_name] = Function(node.children[3].attributes["tipovi"], node.children[0].attributes["tip"], node)
        provjeri_slozena_naredba(node.children[5])

def provjeri_lista_parametara(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<deklaracija_parametra>"]:
        provjeri_deklaracija_parametra(node.children[0])

        node.attributes["tipovi"] = [node.children[0].attributes["tip"]]
        node.attributes["imena"] = [node.children[0].attributes["ime"]]

    elif children == ["<lista_parametara>", "ZAREZ", "<deklaracija_parametra>"]:
        provjeri_lista_parametara(node.children[0])
        provjeri_deklaracija_parametra(node.children[2])
        if node.children[2].attributes["ime"] in node.children[0].attributes["imena"]:
            print_error(node)

        node.attributes["tipovi"] = node.children[0].attributes["tipovi"] + [node.children[2].attributes["tip"] if "tip" in node.children[2].attributes else None]
        node.attributes["imena"] = node.children[0].attributes["imena"] + [node.children[2].attributes["ime"] if "ime" in node.children[2].attributes else None]

def provjeri_deklaracija_parametra(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<ime_tipa>", "IDN"]:
        provjeri_ime_tipa(node.children[0])
        if isinstance (node.children[0].attributes["tip"], Void):
            print_error(node)
        node.symbol_table.parent.table[node.children[1].lexical_unit] = node

        node.attributes["tip"] = node.children[0].attributes["tip"]
        node.attributes["ime"] = node.children[1].lexical_unit

    elif children == ["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"]:
        provjeri_ime_tipa(node.children[0])
        if isinstance (node.children[0].attributes["tip"], Void):
            print_error(node)

        node.attributes["tip"] = Array(node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None)
        node.attributes["ime"] = node.children[1].lexical_unit

def provjeri_lista_deklaracija(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<deklaracija>"]:
        provjeri_deklaracija(node.children[0])

    elif children == ["<lista_deklaracija>", "<deklaracija>"]:
        provjeri_lista_deklaracija(node.children[0])
        provjeri_deklaracija(node.children[1])

def provjeri_deklaracija(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<ime_tipa>", "<lista_init_deklaratora>", "TOCKAZAREZ"]:
        provjeri_ime_tipa(node.children[0])
        node.children[1].attributes["ntip"] = node.children[0].attributes["tip"] if "tip" in node.children[0].attributes else None
        provjeri_lista_init_deklaratora(node.children[1])

def provjeri_lista_init_deklaratora(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<init_deklarator>"]:
        node.children[0].attributes["ntip"] = node.attributes["ntip"]
        provjeri_init_deklarator(node.children[0])

    elif children == ["<lista_init_deklaratora>", "ZAREZ", "<init_deklarator>"]:
        node.children[0].attributes["ntip"] = node.attributes["ntip"]
        provjeri_lista_init_deklaratora(node.children[0])
        node.children[2].attributes["ntip"] = node.attributes["ntip"]
        provjeri_init_deklarator(node.children[2])

def provjeri_init_deklarator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<izravni_deklarator>"]:
        node.children[0].attributes["ntip"] = node.attributes["ntip"]
        provjeri_izravni_deklarator(node.children[0])
        if isinstance(node.children[0], Array):
            prim = node.children[0].primitive
            if isinstance(prim, Const):
                print_error(node)
        if isinstance(node.children[0], Const):
            print_error(node)

    elif children == ["<izravni_deklarator>", "OP_PRIDRUZI", "<inicijalizator>"]:
        node.children[0].attributes["ntip"] = node.attributes["ntip"]
        provjeri_izravni_deklarator(node.children[0])
        provjeri_inicijalizator(node.children[2])
        deklarator_tip = node.children[0].attributes["tip"]
        if isinstance(deklarator_tip, Array):
            T = deklarator_tip.primitive
            T = T if not isinstance(T, Const) else T.primitive
            if node.children[2].attributes["br-elem"] > node.children[0].attributes["br-elem"]:
                print_error(node)
            for U in node.children[2].attributes["tipovi"]:
                if not check_types(U, T):
                    print_error(node)
        else:
            T = deklarator_tip if not isinstance(deklarator_tip, Const) else deklarator_tip.primitive
            if not check_types(node.children[2].attributes["tip"], T):
                print_error(node)

def provjeri_izravni_deklarator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["IDN"]:
        if isinstance(node.attributes["ntip"], Void):
            print_error(node)
        if node.children[0].lexical_unit in node.symbol_table.table:
            print_error(node)
        node.symbol_table.table[node.children[0].lexical_unit] = node

        node.attributes["tip"] = node.attributes["ntip"]
        node.attributes["l-izraz"] = 1

    elif children == ["IDN", "L_UGL_ZAGRADA", "BROJ", "D_UGL_ZAGRADA"]:
        if isinstance(node.attributes["ntip"], Void):
            print_error(node)
        if node.children[0].lexical_unit in node.symbol_table.table:
            print_error(node)
        br = int(node.children[2].lexical_unit)
        if br <= 0 or br > 1024:
            print_error(node)
        node.symbol_table.table[node.children[0].lexical_unit] = node
        
        node.attributes["tip"] = Array(node.attributes["ntip"])
        node.attributes["br-elem"] = br

    elif children == ["IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"]:
        f_name = node.children[0].lexical_unit
        if f_name in node.symbol_table.table:
            f = node.symbol_table.table[f_name]
            if isinstance(f, Function):
                if isinstance(f.params, Void):
                    if type(f.ret_val) != type(node.attributes["ntip"]):
                        print_error(node)
                else:
                    print_error(node)
            else:
                print_error(node)
        node.symbol_table.table[f_name] = Function(Void(), node.attributes["ntip"], node)

        node.attributes["tip"] = Function(Void(), node.attributes["ntip"], node)

    elif children == ["IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"]:
        provjeri_lista_parametara(node.children[2])
        f_name = node.children[0].lexical_unit
        if f_name in node.symbol_table.table:
            f = node.symbol_table.table[f_name]
            if isinstance(f, Function):
                if node.children[2].attributes["tipovi"] == f.params:
                    if type(node.attributes["ntip"]) != type(f.ret_val):
                        print_error(node)
                else:
                    print_error(node)
            else:
                print_error(node)
        node.symbol_table.table[f_name] = Function(node.children[2].attributes["tipovi"], node.attributes["ntip"], node)

        node.attributes["tip"] = Function(node.children[2].attributes["tipovi"], node.attributes["ntip"], node)

def provjeri_inicijalizator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<izraz_pridruzivanja>"]:
        provjeri_izraz_pridruzivanja(node.children[0])

        curr = node.children[0]
        flag = True
        while isinstance(curr, Node):
            if len(curr.children) > 1:
                flag = False
                break
            else:
                if isinstance(curr.children[0], Node):
                    curr = curr.children[0]
                else:
                    break
        if flag:
            if curr.children[0].symbol == "NIZ_ZNAKOVA":
                node.attributes["br-elem"] = count_chars(curr.children[0].lexical_unit) + 1
                node.attributes["tipovi"] = []
                for _ in range(node.attributes["br-elem"] + 1):
                    node.attributes["tipovi"].append(Char())
            else:
                node.attributes["tip"] = node.children[0].attributes["tip"]
        else:
            node.attributes["tip"] = node.children[0].attributes["tip"]

    elif children == ["L_VIT_ZAGRADA", "<lista_izraza_pridruzivanja>", "D_VIT_ZAGRADA"]:
        provjeri_lista_izraza_pridruzivanja(node.children[1])

        node.attributes["br-elem"] = node.children[1].attribues["br-elem"] if "br-elem" in node.children[1].attributes else None
        node.attributes["tipovi"] = node.children[1].attributes["tipovi"] if "tipovi" in node.children[1].attributes else None

def provjeri_lista_izraza_pridruzivanja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    for child in node.children:
        if isinstance(child, Node):
            child.symbol_table = node.symbol_table
            
    if children == ["<izraz_pridruzivanja>"]:
        provjeri_izraz_pridruzivanja(node.children[0])

        node.attributes["tipovi"] = [node.children[0].attributes["tip"]]
        node.attributes["br-elem"] = 1

    elif children == ["<lista_izraza_pridruzivanja>", "ZAREZ", "<izraz_pridruzivanja>"]:
        provjeri_lista_izraza_pridruzivanja(node.children[0])
        provjeri_izraz_pridruzivanja(node.children[2])

        node.attributes["tipovi"] = node.children[0].attributes["tipovi"] + [node.children[2].attributes["tip"] if "tip" in node.children[2].attributes else None]
        node.attributes["br-elem"] = node.children[0].attributes["br-elem"] + 1

# funkcija provjerava podudarnost tipova
def check_types(A, B) -> bool:
    return check_types_array(A, B)

# funkcija provjerava podudarnost nizova
def check_types_array(A, B) -> bool:
    
    if isinstance(A, Array) and isinstance(B, Array):
        A = A.primitive
        B = B.primitive
        return check_types_const(A, B)

    elif not isinstance(A, Array) and not isinstance(B, Array):
        return check_types_const(A, B)

    else:
        return False

# funkcija provjerava podudarnost konstanti
def check_types_const(A, B) -> bool:
    
    if isinstance(A, Const):
        A = A.primitive

    if isinstance(B, Const):
        B = B.primitive

    return check_types_primitive(A, B)

# funkcija provjerava podudarnost primitiva
def check_types_primitive(A, B) -> bool:
    
    if isinstance(A, Void) and isinstance(B, Void):
        return True

    if isinstance(A, Void) != isinstance(B, Void):
        return False

    if isinstance(A, Int):

        if isinstance(B, Int):
            return True

        else:
            return False

    elif isinstance(A, Char):
        
        if isinstance(B, Char) or isinstance(B, Int):
            return True

        else:
            return False

# funkcija provjerava mogućnost eksplicitnog casta
def check_cast(A, B) -> bool:
    return check_cast_array(A, B)

# funkcija koja provjerava eksplicitni cast polja
def check_cast_array(A, B) -> bool:

    if isinstance(A, Array) and isinstance(B, Array):
        A = A.primitive
        B = B.primitive
        return check_cast_const(A, B)

    elif not isinstance(A, Array) and not isinstance(B, Array):
        return check_cast_const(A, B)

    else:
        return False

# funkcija provjerava eksplicitni cast konstanti
def check_cast_const(A, B) -> bool:
    
    if isinstance(A, Const):
        A = A.primitive

    if isinstance(B, Const):
        B = B.primitive

    return check_cast_primitive(A, B)

# funkcija provjerava eksplicitni cast primitiva
def check_cast_primitive(A, B) -> bool:
    
    if isinstance(A, Void) and isinstance(B, Void):
        return True

    if isinstance(A, Void) != isinstance(B, Void):
        return False

    if isinstance(A, Char) or isinstance(A, Int):

        if isinstance(B, Char) or isinstance(B, Int):
            return True

        else:
            return False

if __name__ == "__main__":
    
    # čitanje generativnog stabla s ulaza
    read_generative_tree()

    # stvaranje tablice znakova u globalnom djelokrugu
    generative_tree_root.symbol_table = Symbol_Table()
    scopes.append(generative_tree_root.symbol_table)

    # početak semantičke analize
    provjeri_prijevodna_jedinica(generative_tree_root)

    # provjera postojanja funkcije main
    if "main" in function_definitions:
        main = function_definitions["main"]
        if not isinstance(main.params, Void) or not isinstance(main.ret_val, Int):
            print("main")
            exit()
    else:
        print("main")
        exit()

    # provjera da su sve deklarirane funkcije i definirane
    for scope in scopes:
        for var in scope.table:
            if isinstance(scope.table[var], Function):
                if var in function_definitions:
                    declared = scope.table[var]
                    defined = function_definitions[var]
                    if type(declared.ret_val) != type(defined.ret_val):
                        print("funkcija")
                        exit()
                    if isinstance(declared.params, Void) != isinstance(defined.params, Void):
                        print("funkcija")
                        exit()
                    if not isinstance(declared.params, Void) and not isinstance(defined.params, Void):
                        if len(declared.params) == len(defined.params):
                            for i in range(len(declared.params)):
                                if type(declared.params[i]) != type(defined.params[i]):
                                    print("funkcija")
                                    exit()
                        else:
                            print("funkcija")
                            exit()
                else:
                    print("funkcija")
                    exit()