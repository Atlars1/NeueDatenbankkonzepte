import matplotlib.pyplot as plt
import networkx as nx

def find_shortest_path(db_driver, start_node, end_node):
    with db_driver.driver.session(database=db_driver.db_name) as session:
        result = session.run("MATCH (start:Node {id: $start_id}), (end:Node {id: $end_id}) "
                             "CALL apoc.algo.dijkstra(start, end, 'CONNECTS', 'weight') YIELD path, weight "
                             "RETURN path, weight",
                             start_id=start_node, end_id=end_node)
        return result.single()

def find_and_display_shortest_path(db_driver, G, positions, start_node, end_node):
    path_result = find_shortest_path(db_driver, start_node, end_node)

    if path_result:
        print("Shortest Path: ", path_result["path"])
        print("Total Weight: ", path_result["weight"])

        path_nodes = [node["id"] for node in path_result["path"].nodes]
        path_edges = list(zip(path_nodes, path_nodes[1:]))

        plt.figure(figsize=(10, 8))
        nx.draw(G, pos=positions, with_labels=True, node_size=700, node_color='skyblue')
        nx.draw_networkx_nodes(G, pos=positions, nodelist=path_nodes, node_color='red', node_size=700)
        nx.draw_networkx_edges(G, pos=positions, edgelist=path_edges, edge_color='red', width=2)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels)
        plt.axis('off')
        plt.show()
    else:
        print("Kein Pfad gefunden.")