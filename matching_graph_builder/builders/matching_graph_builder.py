import pickle


class MatchingGraphBuilderBase:
    def __init__(self, train_graphs, train_labels, mg_creation_alpha, node_ins_c = 1.0, node_del_c = 1.0, edge_ins_c = 1.0, edge_del_c = 1.0, node_subst_fct = None):
        self.train_labels = train_labels
        self.train_graphs = train_graphs

        self.node_subst_fct = node_subst_fct
        self.edge_del_c = edge_del_c
        self.edge_ins_c = edge_ins_c
        self.node_del_c = node_del_c
        self.node_ins_c = node_ins_c
        self.mg_creation_alpha = mg_creation_alpha
        self.dataset_classes = list(set(train_labels))


    def build_matching_graph(self, source_graph, target_graph):
        raise NotImplementedError

    def build(self, output_folder, cross_class = False, output_format = "two_lists"):
        pair_dict = self.create_pairs_dict(cross_class)
        mgs_dict = {}
        for lbl, graph_pair in pair_dict.items():
            mgs = self.build_matching_graph(graph_pair[0], graph_pair[1])
            if lbl in mgs_dict.keys():
                mgs_dict[lbl].append(mgs)
            else:
                mgs_dict[lbl] = [mgs]

        dump_item = None
        if output_format == "two_lists":
            graphs,lbls = [],[]
            for label, grphs in mgs_dict.items():
                graphs.extend(grphs)
                lbls.extend([label]*len(graphs))
                dump_item = zip(graphs,lbls)
        elif output_format == "dict":
            dump_item = mgs_dict
        else:
            raise NameError("Unsupported save type, only two_lists and dict are supported")

        with open(f"{output_folder}/matching_graphs_alpha:{self.mg_creation_alpha}_cost_node:{self.node_ins_c}_cost_edge:{self.edge_ins_c}.pkl", "wb") as f:
            pickle.dump(dump_item, f)

    def create_pairs_dict(self, cross_class):
        ret_dict = {}
        for cls in self.dataset_classes:
            ret_dict[cls] = []

        for tr_gr_1, tr_l_1 in zip(self.train_graphs,self.train_labels):
            for tr_gr_2, tr_l_2 in zip(self.train_graphs,self.train_labels):
                if ((tr_l_1 == tr_l_2) and not cross_class ) or ((tr_l_1 != tr_l_2) and cross_class):
                    ret_dict[tr_l_1].append((tr_gr_1,tr_gr_2))

        return ret_dict



