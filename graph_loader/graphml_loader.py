import os
import random
import xml.dom.minidom as xml_parser

import networkx as nx


def _read_graphml_file(path):
    '''
    Reads a graphml file to a nx.Graph from a given path
    :param path: String
        the path of the graphml file
    :return: nx.Graph
        a networkx Graph
    '''
    graph = nx.read_graphml(path)
    graph = nx.Graph(graph, name= os.path.basename(path).replace(".graphml",""))
    return graph

def _load_cxl_file(cxl_file_path):
    '''
    Returns all the paths of all the graphml files in a cxl
    :param cxl_file_path: String
        Path of the cxl file
    :return: list,list
        Two lists containing the paths of the graphml files and their labels
    '''
    if not os.path.isabs(cxl_file_path):
        cxl_file_path = os.getcwd() + "/" + cxl_file_path
    dir_name = os.path.dirname(cxl_file_path)

    graph_list_doc = xml_parser.parse(cxl_file_path)

    xml_parser.parse(cxl_file_path).getElementsByTagName("print")[0].getAttribute("file")
    graph_tags_list = graph_list_doc.getElementsByTagName("print")
    list_of_file_names_and_labels = [
        (dir_name + "/" + graph_entry.getAttribute("file"), graph_entry.getAttribute("class")) for graph_entry in
        graph_tags_list]

    return map(list, zip(*list_of_file_names_and_labels))


def _load_graph_collection(graph_paths):
    '''
    Takes a list of graph paths and loads all the files
    :param graph_paths: list of Strings
    :return: list nx.Graph
        returns a list of nx.Graphs
    '''
    return [_read_graphml_file(file_path) for file_path in graph_paths]


def _load_data(cxl_file_path):
    '''
    Loads all the graphs contained in a cxl file and returns them in a list as well as a list of their labels
    :param cxl_file_path: String
    :return: list of nx.Graphs, labels of graphs
    '''
    file_paths, file_labels = _load_cxl_file(cxl_file_path)

    graphs = _load_graph_collection(file_paths)

    return graphs, file_labels


def graph_class_dict(all_graphs):
    '''
    Extracts the class of a given graph from its name. ATTENTION: Graph has to have name of form
    class_name  , else it will not work

    :param all_graphs:
    :return:
    '''
    dict = {}
    for graph in all_graphs:
        parts = graph.name.split("_")
        graph_class = parts[0]
        if not graph_class in dict:
            dict[graph_class] = [graph]
        else:
            dict[graph_class].append(graph)

    return dict


def _build_split(all_graphs, split):
    '''
    Splits a given set of graphs into a certain percentage split like [60,20,20] with a given seed for replication
    purposes
    :param all_graphs:
    :param split:
    :return:
    '''
    list_of_indices = list(range(0, len(all_graphs)))

    random.seed(367)
    train_idxs = random.sample(list_of_indices, int(len(list_of_indices) * (split[0])))

    rest = set(list_of_indices) - set(train_idxs)

    valid_idxs = random.sample(rest, int(len(rest) * split[1]))

    test_idxs = rest - set(valid_idxs)

    return train_idxs, valid_idxs, test_idxs



def load_graphs_folder(path):
    '''
    Loads all the matching graphs in a given folder
    :param path:
    :return:
    '''
    graphs = []
    mg_path = path
    for filename in os.listdir(mg_path):
        if filename.endswith(".graphml"):
            graphs.append(_read_graphml_file(mg_path + "/" + filename))
    return graphs


def load_desired_split_cxl(split_path):
    '''
    Loads all the graphs in a given cxl file. Important! The corresponding graphml files need to be in the same folder as the cxl.
    :param split_path:
    :return:
    '''
    split, split_lbls = _load_data(cxl_file_path=split_path)


    return split, split_lbls

def load_train_val_test_splits_cxl(train_cxl, val_cxl, test_cxl):
    '''
    Loads a given train, valid and test split from three cxl files
    :param train_cxl:
    :param val_cxl:
    :param test_cxl:
    :return:
    '''
    train, train_lbls = load_desired_split_cxl(train_cxl)
    val, val_lbls = load_desired_split_cxl(val_cxl)
    test, test_lbls = load_desired_split_cxl(test_cxl)

    return train, train_lbls, val, val_lbls, test, test_lbls