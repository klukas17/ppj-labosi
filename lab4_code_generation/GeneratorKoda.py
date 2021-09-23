import SemantickiAnalizator as s

# varijabla za tabulatore u a.frisc datoteci
tabs = "\t\t"

if __name__ == "__main__":
    
    # semantička analiza nad generativnim stablom na standardnom ulazu
    s.semantic_analysis()

    # pisanje u datoteku a.frisc
    f = open("a.frisc", "w")

    # inicijalizacija i završetak izvođenja programa
    f.write(f'{tabs}MOVE 40000, R7\n')
    f.write(f'{tabs}CALL F_MAIN\n')
    f.write(f'{tabs}HALT\n')

    # zatvaranje datoteke
    f.close()