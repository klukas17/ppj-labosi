'''
    NAPOMENA: pri pisanju datoteke LA.py, iskoristio sam dijelove svog 
    vlastitog rješenja 1. laboratorijske vježbe (SimEnka.py) na kolegiju 
    "Uvod u teoriju računarstva" koje sam predao ak. god. 2020/2021
'''

# ! import shared_classes ne radi

from .. import shared_classes
from sys import stdin

# lista svih pravila, posloženih po prioritetu
rules = []

# datoteka za čitanje pravila parsiranja koja je pripremio GLA
def read_rules() -> None:
    rules = open("analizator/rules.txt", "r")

    rules.close()

# čitanje ulazne datoteke i ispisivanje niza leksičkih jedinki na stdout
if __name__ == "__main__":
    
    # čitanje cijelog ulaza u jedan string
    code = stdin.read()

    read_rules()

    index = 0
    while index < len(code):
        pass