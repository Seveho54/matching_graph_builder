from graph_pkg_core.graph.edge import Edge
from graph_pkg_core.graph.graph import Graph
from graph_pkg_core.graph.label.label_edge import LabelEdge
from graph_pkg_core.graph.label.label_node_vector import LabelNodeVector
from graph_pkg_core.graph.node import Node
import networkx as nx
import numpy as np

def add_nodes(anthony_graph, nx_graph,node_idx_dict, label_name, attribute_names):
    if label_name is not None:
        attributes_list = [label_name]
    else:
        attributes_list = []

    attributes_list.extend(attribute_names)
    for node_name in nx_graph.nodes():
        attr_vals = []
        for att in attributes_list:
            attrs = nx_graph.nodes[node_name][att]
            if isinstance(attrs, list):
                attr_vals.extend(attrs)
            else:
                attr_vals.append(attrs)
        anthony_graph.add_node(Node(node_idx_dict[node_name], LabelNodeVector(np.array(attr_vals))))

    return anthony_graph


def get_edge_data_ptc_mr(nx_graph, edge):
    return nx_graph.get_edge_data(*edge)['0']


def get_edge_data_mao(nx_graph, edge):
    return int(nx_graph.get_edge_data(*edge)['bond_type'])


def add_edges(anthony_graph, nx_graph, node_idx_dict, dataset_name):
    for edge in nx_graph.edges():
        edge_data = None
        if dataset_name == "ptc_mr":
            edge_data = get_edge_data_ptc_mr(nx_graph, edge)
        elif dataset_name== "mao":
            edge_data = get_edge_data_mao(nx_graph, edge)
        try:
            if edge_data is not None:
                anthony_graph.add_edge(Edge(node_idx_dict[edge[0]], node_idx_dict[edge[1]], LabelEdge(edge_data)))
            else:
                anthony_graph.add_edge(Edge(node_idx_dict[edge[0]], node_idx_dict[edge[1]], LabelEdge(0)))
        except AssertionError:
            print("Halt")
    return anthony_graph


def build_node_idx_dict(node_names):
    i = 0
    dict = {}
    for node_name in node_names:
        dict[node_name] = i
        i+=1

    return dict



def convert_graph(nx_graph, label_name, attribute_names = [], dataset_name = None):
    '''
    Accepts a nx graph and converts it to the graph format of anthonys graph_pkg
    '''
    anthony_graph = Graph(nx_graph.name, "{}.graphml".format(nx_graph.name), len(nx_graph.nodes()))
    node_idx_dict = build_node_idx_dict(list(nx_graph.nodes()))
    anthony_graph = add_nodes(anthony_graph, nx_graph,node_idx_dict, label_name, attribute_names)
    anthony_graph = add_edges(anthony_graph, nx_graph, node_idx_dict, dataset_name = dataset_name)



    return anthony_graph

def convert_graph_list(nx_graph_list):
    anthony_graphs = [convert_graph(gr) for gr in nx_graph_list]
    return anthony_graphs

def convert_graph_dict(nx_graph_dict):
    converted_dict = {}
    for key, value in nx_graph_dict.items():
        converted_dict[key] = convert_graph_list(value)

    return converted_dict