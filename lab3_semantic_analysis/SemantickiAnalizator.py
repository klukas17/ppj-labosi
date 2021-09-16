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

# varijabla za spremanje korijena generativnog stabla
generative_tree_root = None

# lista čvorova generativnog stabla čija djeca se trenutno grade
active_nodes = []

# funkcija koja sa standardnog ulaza čita generativno stablo
def read_generative_tree() -> Abs_Node:

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

if __name__ == "__main__":
    
    # čitanje generativnog stabla s ulaza
    read_generative_tree()   