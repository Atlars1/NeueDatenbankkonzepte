from main import create_and_store_graph
from interfacefunktion import Verkehrsmittel
from interfacefunktion import SEKnoten
from interfacefunktion import WegTyp
from interfacefunktion import BlackList
from interfacefunktion import GraphErstellen


def Interface():
    verkehrsmittel = Verkehrsmittel()
    n = True
    while n is True:
        db_driver, G, positions = create_and_store_graph(GraphErstellen())
        nodes = SEKnoten()
        WegTyp(nodes, db_driver, G, positions)
        db_driver.close()
        BlackList(nodes, db_driver, G, positions)
        if input('Möchtest du noch einen Weg suchen?: y/n \n') == 'n':
            n = False

Interface()
    