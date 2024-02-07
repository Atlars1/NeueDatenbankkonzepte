from main import create_and_store_graph
from main import find_and_display_shortest_path

def Interface():
    db_driver, G, positions = create_and_store_graph()
    find_and_display_shortest_path(db_driver, G, positions)
    db_driver.close()
    verkehrsmittel = Verkehrsmittel()
    GraphErstellen()
    BlackList()
    WegTyp()
    # Wegfindung

def GraphErstellen():
    print('Wie viele Knoten soll dein Graph haben: ')
    Knoten = intConverter()
    print(Knoten)


def WegTyp():
    a = input("Bitte wähle aus folgenden Möglichkeiten \n1 für kürzesten Weg \n2 für wenigste Knoten\n")
    if a == '1':
        Zwischenziel()
        # prüfung auf direktverbindung
    elif a == '2':
        Zwischenziel()
    else:
        print('Ungültige Eingabe')
        WegTyp()

def Zwischenziel():
    b = input("Möchtest du ein Zwischenziel \ny/n \n")
    if b == 'y':
        print('Welchen?')
        ZZ = intConverter()
        return ZZ
    elif b == 'n':
        print(b)
    else:
        print('Ungültige Eingabe')
        Zwischenziel()
    

def Verkehrsmittel():
    e = input('Hallo lieber Nutzer. Wie möchtest du reisen? \n1 zu Fuß \n2 mit dem Rad\n3 mit dem Auto\n4 mit dem Zug\n')
    if e == '1' or e == '2' or e == '3' or e == '4':
        print(f"Du hast {e} gewählt.")
    else:
        print("Ungültige Auswahl. Bitte wähle eine Option zwischen 1 und 4.")
        Verkehrsmittel()
    return e

def BlackList():
    b = input("Möchtest du einen Punkt vermeiden \ny/n \n")
    if b == 'y':
        print('Welchen?')
        f = intConverter()
        return f
    elif b == 'n':
        print(b)
    else:
        print('Ungültige Eingabe')
        Zwischenziel()
    
    # f auf blachlist setzen

def intConverter():
    b = input('')
    try:
        number = int(b)
        print(f"Die eingegebene Zahl ist {number}.")
        return number
    except ValueError:
        print("Das ist keine gültige Zahl. Bitte geben Sie eine ganze Zahl ein.")
        return intConverter()
    
    
    

Interface()
    