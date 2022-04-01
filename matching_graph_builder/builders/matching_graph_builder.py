import pickle


class MatchingGraphBuilderBase:
    def __init__(self, src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name):
        self.label_name = label_name
        self.src_graphs = src_graphs
        self.src_labels = src_labels
        self.tar_graphs = tar_graphs
        self.tar_labels = tar_labels

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

    def build_matching_graphs(self):
        raise NotImplementedError

    # def build_matching_graphs_from_pair(self,src_gr, tar_gr):
    #     raise NotImplementedError

    def build(self, output_folder = None, output_format = "two_lists"):
        mgs_dict = self.build_matching_graphs()

        dump_item = None
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
        ret_dict = {}
        for cls in self.dataset_classes:
            ret_dict[cls] = []

        for i in range(len(self.src_graphs)):
            j = i
            while j < len(self.tar_graphs):
                if ((self.src_labels[i] == self.tar_labels[j]) or cross_class ):
                    if  ((self.src_graphs[i].name != self.tar_graphs[j].name) ):
                        ret_dict[self.src_labels[i]].append((self.src_graphs[i],self.tar_graphs[j]))
                j += 1
        # for tr_gr_1, tr_l_1 in zip(self.src_graphs,self.src_labels):
        #     for tr_gr_2, tr_l_2 in zip(self.tar_graphs,self.tar_labels):
        #         if ((tr_l_1 == tr_l_2) or cross_class ):
        #             if  ((tr_gr_1.name != tr_gr_2.name) ):
        #                 ret_dict[tr_l_1].append((tr_gr_1,tr_gr_2))

        return ret_dict



