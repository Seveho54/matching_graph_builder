from matching_graph_builder.builders.original_mg_builder import OriginalMatchingGraphBuilder
import graph_loader.graphml_loader  as loader

class TestOriginalMatchingGraphBuilder():

    def setup(self):
        graphs, labels = loader.load_desired_split_cxl("resources/mutagenicity/sample_mg_dict.cxl")
        src_graphs = graphs
        src_labels = labels
        tar_graphs = graphs
        tar_labels = labels
        mg_creation_alpha = 0.5
        cross_class = False
        label_name = "chem"
        attribute_names = []
        node_ins_c, node_del_c, edge_ins_c, edge_del_c = 1.0,1.0,1.0,1.0
        node_subst_fct = ""
        dataset_name = "mutagenicity"
        prune_edges = True
        self.builder = OriginalMatchingGraphBuilder( src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,
                                                     node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, prune_edges,
                                                     one_hot = False, remove_isolated_nodes= True, multipr = False)

