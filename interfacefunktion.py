from main import find_and_display_multi_point_path
from main import find_shortest_path_by_nodes_and_draw
from functions import find_and_display_shortest_path

def GraphErstellen():
    print('Wie viele Knoten soll dein Graph haben: ')
    Knoten = intConverter()
    # print(Knoten)
    return Knoten


def WegTyp(Weg, db_driver, G, positions):
    a = input("Bitte wähle aus folgenden Möglichkeiten \n1 für kürzesten Weg \n2 für wenigste Knoten\n")
    if a == '1':
        Zwischenziel(Weg, db_driver, G, positions)
        find_and_display_shortest_path(db_driver, G, positions, Weg[0], Weg[1])
        # find_and_display_multi_point_path(db_driver, G, positions, Weg)
        # prüfung auf direktverbindung
    elif a == '2':
        start_node = Weg[0]
        end_node = Weg[1]
        find_shortest_path_by_nodes_and_draw(G, positions, start_node, end_node)
    else:
        print('Ungültige Eingabe')
        WegTyp()

def Zwischenziel(Weg, db_driver, G, positions):
    b = input("Möchtest du ein Zwischenziel \ny/n \n")
    if b == 'y':
        print('Welchen Knoten möchtest du als Zwischenziel?')
        ZZ = intConverter()
        Weg.append(ZZ)
        find_and_display_multi_point_path(db_driver, G, positions, Weg)
    elif b == 'n':
        print(b)
    else:
        print('Ungültige Eingabe')
        Zwischenziel(Weg, db_driver, G, positions)
    

def Verkehrsmittel():
    e = input('Hallo lieber Nutzer. Wie möchtest du reisen? \n1 zu Fuß \n2 mit dem Rad\n3 mit dem Auto\n4 mit dem Zug\n')
    if e == '1' or e == '2' or e == '3' or e == '4':
        print(f"Du hast {e} gewählt.")
    else:
        print("Ungültige Auswahl. Bitte wähle eine Option zwischen 1 und 4.")
        Verkehrsmittel()
    return e

def BlackList(Weg, db_driver, G, positions):
    b = input("Möchtest du einen Punkt vermeiden \ny/n \n")
    if b == 'y':
        print('Welchen?')
        f = intConverter()
        return f
    elif b == 'n':
        print(b)
    else:
        print('Ungültige Eingabe')
        Zwischenziel(Weg, db_driver, G, positions)
    
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
    
def SEKnoten():
    SEK = []
    print('Gib mir einen Startknoten:')
    a = intConverter()
    print('Gib mir einen Endknoten:')
    b = intConverter()
    SEK.append(a)
    SEK.append(b)
    return (SEK)