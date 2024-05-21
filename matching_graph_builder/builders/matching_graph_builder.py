import pickle


class MatchingGraphBuilderBase:
    '''
    Base class for building matching graphs. There are several implementations of the class.
    '''
    def __init__(self, src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name,
                 one_hot, rm_isol_nodes, multipr):
        self.label_name = label_name
        self.src_graphs = src_graphs
        self.src_labels = src_labels
        self.tar_graphs = tar_graphs
        self.tar_labels = tar_labels
        self.one_hot = one_hot

        self.node_subst_fct = node_subst_fct
        self.edge_del_c = edge_del_c
        self.edge_ins_c = edge_ins_c
        self.node_del_c = node_del_c
        self.node_ins_c = node_ins_c
        self.mg_creation_alpha = mg_creation_alpha
        self.dataset_classes = list(set(src_labels))
        self.attribute_names = attribute_names
        self.dataset_name = dataset_name
        self.cross_class = cross_class
        self.pair_dict = self.create_pairs_dict(cross_class)
        self.rm_isol_nodes = rm_isol_nodes
        self.multipr = multipr

    def build_matching_graphs(self):
        raise NotImplementedError


    def build(self, output_folder = None, output_format = "two_lists"):
        '''
        Creates the matching graphs out of all possible pairs for src x tar and saves them to a file plus
        returns them either as two lists: graphs, labels, or as a dictionary with key: label and value: graphs
        :param output_folder:
        :param output_format:
        :return:
        '''
        mgs_dict = self.build_matching_graphs()

        if output_format == "two_lists":
            graphs,lbls = [],[]
            for label, grphs in mgs_dict.items():
                graphs.extend(grphs)
                lbls.extend([label]*len(grphs))
            dump_item = (graphs,lbls)
        elif output_format == "dict":
            dump_item = mgs_dict
        else:
            raise NameError("Unsupported save type, only two_lists and dict are supported")

        if output_folder is not None:
            with open(f"{output_folder}/matching_graphs_alpha:{self.mg_creation_alpha}_cost_node:{self.node_ins_c}_cost_edge:{self.edge_ins_c}.pkl", "wb") as f:
                pickle.dump(dump_item, f)

        return dump_item

    def create_pairs_dict(self, cross_class):
        '''
        Creates a dictionary of list of tuples for all possible pairs for a given class
        :param cross_class: boolean
            if cross class is true, then the pairs are created across different classes as well
        :return: dictionary containing all the pairs for a given class.
        '''
        ret_dict = {}
        for cls in self.dataset_classes:
            ret_dict[cls] = []

        len_src = len(self.src_labels)
        len_tar = len(self.tar_labels)

        for i in range(len_src):
            for j in range(len_tar):
                if i < len_src and j < len_tar: 
                    if ((self.src_labels[i] != self.tar_labels[j]) or cross_class):
                        if self.src_graphs[i].name != self.tar_graphs[j].name:
                            ret_dict[self.src_labels[i]].append((self.src_graphs[i], self.tar_graphs[j]))

        return ret_dict