from typing import Union
from typing_extensions import ParamSpec

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
        self.attributes = {}
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

# varijabla za spremanje korijena generativnog stabla
generative_tree_root = None

# lista čvorova generativnog stabla čija djeca se trenutno grade
active_nodes = []

# funkcija koja sa standardnog ulaza čita generativno stablo
def read_generative_tree() -> None:

    global generative_tree_root

    # čitanje korijena generativnog stabla
    generative_tree_root = Node(input())
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
                    curr_node = Node(s)
                    active_nodes[whitespace_count-1].children.append(curr_node)

                    if len(active_nodes) > whitespace_count:
                        active_nodes[whitespace_count] = curr_node
                    else:
                        active_nodes.append(curr_node)

            # uniformna jedinka, tj. list generativnog stabla
            else:
                active_nodes[whitespace_count-1].children.append(Leaf(s[0], s[1], s[2]))
            
    except EOFError:
        pass

def provjeri_primarni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["IDN"]:
        # TODO: provjera
        pass

        node.attributes["tip"] = node.children[0].atrributes["tip"]
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"]

    elif children == ["BROJ"]:
        # TODO: provjera
        pass

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

    elif children == ["ZNAK"]:
        # TODO: provjera
        pass

        node.attributes["tip"] = Char()
        node.attributes["l-izraz"] = 0

    elif children == ["NIZ_ZNAKOVA"]:
        # TODO: provjera
        pass

        node.attributes["tip"] = Array(Const(Char()))
        node.attributes["l-izraz"] = 0

    elif children == ["L_ZAGRADA", "<izraz>", "D_ZAGRADA"]:
        provjeri_izraz(node.children[1])

        node.attributes["tip"] = node.children[1].attributes["tip"]
        node.attributes["l-izraz"] = node.children[1].attributes["l-izraz"]

def provjeri_postfiks_izraz(node: Node):
    
    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<primarni_izraz>"]:
        provjeri_primarni_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"]
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"]

    elif children == ["<postfiks_izraz>", "L_UGL_ZAGRADA", "<izraz>", "D_UGL_ZAGRADA"]:
        provjeri_postfiks_izraz(node.children[0])
        # TODO provjera
        provjeri_izraz(node.children[2])
        # TODO provjera

        node.attributes["tip"] = None # TODO
        node.attributes["l-izraz"] = None # TODO

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "D_ZAGRADA"]:
        provjeri_postfiks_izraz(node.children[0])
        # TODO provjera
        
        node.attributes["tip"] = None # TODO
        node.attributes["l-izraz"] = 0

    elif children == ["<postfiks_izraz>", "L_ZAGRADA", "<lista_argumenata>", "D_ZAGRADA"]:
        provjeri_postfiks_izraz(node.children[0])
        provjeri_lista_argumenata(node.children[2])
        # TODO provjera

        node.attributes["tip"] = None # TODO
        node.attributes["l-izraz"] = 0

    elif children == ["<postfiks_izraz>", "OP_INC"] or \
         children == ["<postfiks_izraz>", "OP_DEC"]:
        provjeri_postfiks_izraz(node.children[0])
        # TODO provjera

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_lista_argumenata(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<izraz_pridruzivanja>"]:
        provjeri_izraz_pridruzivanja(node.children[0])

        node.attributes["tipovi"] = None # TODO

    elif children == ["<lista_argumenata>", "ZAREZ", "<izraz_pridruzivanja>"]:
        provjeri_lista_argumenata(node.children[0])
        provjeri_izraz_pridruzivanja(node.children[2])

        node.attributes["tipovi"] = None # TODO

def provjeri_unarni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<postfiks_izraz>"]:
        provjeri_postfiks_izraz(node.children[0])

        node.attributes["tip"] = node.children[0].attributes["tip"]
        node.attributes["l-izraz"] = node.children[0].attributes["l-izraz"]

    elif children == ["OP_INC", "<unarni_izraz>"] or children == ["OP_DEC", "<unarni_izraz>"]:
        provjeri_unarni_izraz(node.children[1])
        # TODO provjera

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

    elif children == ["<unarni_operator>", "<cast_izraz>"]:
        provjeri_cast_izraz(node.children[1])
        # TODO provjera

        node.attributes["tip"] = Int()
        node.attributes["l-izraz"] = 0

def provjeri_unarni_operator(node: Node):
    pass

def provjeri_cast_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<unarni_izraz"]:
        pass

    elif children == ["L_ZAGRADA", "<ime_tipa>", "D_ZAGRADA", "<cast_izraz>"]:
        pass

def provjeri_ime_tipa(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["specifikator_tipa"]:
        pass

    elif children == ["KR_CONST", "<specifikator_tipa>"]:
        pass

def provjeri_specifikator_tipa(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["KR_VOID"]:
        pass

    elif children == ["KR_CHAR"]:
        pass

    elif children == ["KR_INT"]:
        pass

def provjeri_multiplikativni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<cast_izraz>"]:
        pass

    elif children == ["<multiplikativni izraz>", "OP_PUTA", "<cast_izraz>"] or \
         children == ["<multiplikativni izraz>", "OP_DIJELI", "<cast_izraz>"] or \
         children == ["<multiplikativni izraz>", "OP_MOD", "<cast_izraz>"]:
        pass

def provjeri_aditivni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<multiplikativni_izraz>"]:
        pass

    elif children == ["<aditivni_izraz", "PLUS", "<multiplikativni_izraz>"] or \
         children == ["<aditivni_izraz", "MINUS", "<multiplikativni_izraz>"]:
        pass

def provjeri_odnosni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<aditivni_izraz>"]:
        pass

    elif children == ["<odnosni_izraz>", "OP_LT", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_GT", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_LTE", "<aditivni_izraz>"] or \
         children == ["<odnosni_izraz>", "OP_GTE", "<aditivni_izraz>"]:
        pass

def provjeri_jednakosni_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<odnosni_izraz>"]:
        pass

    elif children == ["<jednakosni_izraz>", "OP_EQ", "<odnosni_izraz>"] or \
         children == ["<jednakosni_izraz>", "OP_NEQ", "<odnosni_izraz>"]:
        pass

def provjeri_bin_i_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<jednakosni_izraz>"]:
        pass

    elif children == ["<bin_i_izraz>", "OP_BIN_I", "<jednakosni_izraz>"]:
        pass

def provjeri_bin_xili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<bin_i_izraz>"]:
        pass

    elif children == ["<bin_xili_izraz>", "OP_BIN_XILI", "<bin_i_izraz>"]:
        pass

def provjeri_bin_ili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<bin_xili_izraz>"]:
        pass

    elif children == ["<bin_ili_izraz>", "OP_BIN_ILI", "<bin_xili_izraz>"]:
        pass

def provjeri_log_i_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<bin_ili_izraz>"]:
        pass

    elif children == ["<log_i_izraz>", "OP_I", "<bin_ili_izraz>"]:
        pass

def provjeri_log_ili_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<log_i_izraz>"]:
        pass

    elif children == ["<log_ili_izraz>", "OP_ILI", "<log_i_izraz>"]:
        pass

def provjeri_izraz_pridruzivanja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<log_ili_izraz>"]:
        pass

    elif children == ["<postfiks_izraz>", "OP_PRIDRUZI", "<izraz_pridruzivanja>"]:
        pass

def provjeri_izraz(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<izraz_pridruzivanja>"]:
        pass

    elif children == ["<izraz>", "ZAREZ", "<izraz_pridruzivanja"]:
        pass

def provjeri_slozena_naredba(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["L_VIT_ZAGRADA", "<lista_naredbi>", "D_VIT_ZAGRADA"]:
        pass

    elif children == ["L_VIT_ZAGRADA", "<lista_deklaracija>", "<lista_naredbi>", "D_VIT_ZAGRADA"]:
        pass

def provjeri_lista_naredbi(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<naredba>"]:
        pass

    elif children == ["<lista_naredbi>", "<naredba>"]:
        pass

def provjeri_naredba(node: Node):
    pass

def provjeri_izraz_naredba(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["TOCKAZAREZ"]:
        pass

    elif children == ["<izraz>", "TOCKAZAREZ"]:
        pass

def provjeri_naredba_grananja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        pass

    elif children == ["KR_IF", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>", "KR_ELSE", "<naredba>"]:
        pass

def provjeri_naredba_petlje(node: Node):

    children = list(map(lambda n: n.symbol, node.children))
    
    if children == ["KR_WHILE", "L_ZAGRADA", "<izraz>", "D_ZAGRADA", "<naredba>"]:
        pass

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "D_ZAGRADA", "<naredba>"]:
        pass

    elif children == ["KR_FOR", "L_ZAGRADA", "<izraz_naredba>", "<izraz_naredba>", "izraz", "D_ZAGRADA", "<naredba>"]:
        pass

def provjeri_naredba_skoka(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["KR_CONTINUE", "TOCKAZAREZ"] or \
       children == ["KR_BREAK", "TOCKAZAREZ"]:
       pass

    elif children == ["KR_RETURN", "TOCKAZAREZ"]:
        pass

    elif children == ["KR_RETURN", "<izraz>", "TOCKAZAREZ"]:
        pass

def provjeri_prijevodna_jedinica(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<vanjska_deklaracija>"]:
        pass

    elif children == ["<prijevodna jedinica>", "<vanjska_deklaracija>"]:
        pass

def provjeri_vanjska_deklaracija(node: Node):
    pass

def provjeri_definicija_funkcije(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<ime_tipa>", "IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA", "<slozena_naredba>"]:
        pass

    elif children == ["<ime_tipa>", "IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA", "<slozena_naredba>"]:
        pass

def provjeri_lista_parametara(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<deklaracija_parametara>"]:
        pass

    elif children == ["<lista_parametara", "ZAREZ", "<deklaracija_parametara>"]:
        pass

def provjeri_deklaracija_parametara(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<ime_tipa>", "IDN"]:
        pass

    elif children == ["<ime_tipa>", "IDN", "L_UGL_ZAGRADA", "D_UGL_ZAGRADA"]:
        pass

def provjeri_lista_deklaracija(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<deklaracija>"]:
        pass

    elif children == ["<lista_deklaracija>", "<deklaracija>"]:
        pass

def provjeri_deklaracija(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<ime_tipa>", "<lista_init_deklaratora>", "TOCKAZAREZ"]:
        pass

def provjeri_lista_init_deklaratora(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<init_deklarator>"]:
        pass

    elif children == ["<lista_init_deklaratora>", "ZAREZ", "<init_deklarator>"]:
        pass

def provjeri_init_deklarator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<izravni_deklarator>"]:
        pass

    elif children == ["<izravni_deklarator>", "OP_PRIDRUZI", "<inicijalizator>"]:
        pass

def provjeri_izravni_deklarator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["IDN"]:
        pass

    elif children == ["IDN", "L_UGL_ZAGRADA", "BROJ", "D_UGL_ZAGRADA"]:
        pass

    elif children == ["IDN", "L_ZAGRADA", "KR_VOID", "D_ZAGRADA"]:
        pass

    elif children == ["IDN", "L_ZAGRADA", "<lista_parametara>", "D_ZAGRADA"]:
        pass

def provjeri_inicijalizator(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<lista_pridruzivanja>"]:
        pass

    elif children == ["L_VIT_ZAGRADA", "<lista_izraza_pridruzivanja>", "D_VIT_ZAGRADA"]:
        pass

def provjeri_lista_izraza_pridruzivanja(node: Node):

    children = list(map(lambda n: n.symbol, node.children))

    if children == ["<izraz_pridruzivanja>"]:
        pass

    elif children == ["<lista_izraza_pridruzivanja>", "ZAREZ", "<izraz_pridruzivanja>"]:
        pass

if __name__ == "__main__":
    
    # čitanje generativnog stabla s ulaza
    read_generative_tree()   