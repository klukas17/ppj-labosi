'''
    NAPOMENA: pri pisanju općenitog predloška za LA.py, iskoristio sam 
    dijelove svog vlastitog rješenja 1. laboratorijske vježbe (SimEnka.py)
    na kolegiju "Uvod u teoriju računarstva" koje sam predao ak. god. 2020/2021
'''

import shared_classes

# lista svih pravila, posloženih po prioritetu
rules = []

# čitanje ulazne datoteke i ispisivanje niza leksičkih jedinki na stdout
if __name__ == "__main__":
    
    # čitanje cijelog ulaza u jedan string
    code = ""
    try:
        while True:
            code += input() + "\n"
    except EOFError:
        pass