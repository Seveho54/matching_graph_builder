import pickle

def load_graphs_from_pkl(pkl_file_path):
    '''
    Loads a list of networkx graphs from a pickle file
    Expecting the file to have a list of graphs and a list of labels
    :param pkl_file_path:
    :return:
    '''
    pickle_in = open(pkl_file_path, "rb")
    graphs_list, garphs_lbls = pickle.load(pickle_in)
    pickle_in.close()

    return graphs_list, garphs_lbls

def load_graphs_dict_from_pkl(pkl_file_path):
    pickle_in = open(pkl_file_path, "rb")
    graphs_dict = pickle.load(pickle_in)
    pickle_in.close()

    return graphs_dict