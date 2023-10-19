import graph_loader.graphml_loader  as loader
import networkx as nx

from matching_graph_builder.builders.partial_edit_path_mg_builder import RandomPathMatchingGraphBuilder, build_mgs_from_edit_path


class TestOriginalMatchingGraphBuilder():

    def setup(self):
        graphs, labels = loader.load_desired_split_cxl("resources/mutagenicity/sample_mg_dict.cxl")
        src_graphs = graphs
        src_labels = labels
        tar_graphs = graphs
        tar_labels = labels
        self.mg_creation_alpha = 0.5
        self.cross_class = False
        label_name = "chem"
        attribute_names = []
        self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c = 1.0,1.0,1.0,1.0
        node_subst_fct = ""
        dataset_name = "mutagenicity"
        prune_edges = True
        self.builder = RandomPathMatchingGraphBuilder(src_graphs,
                 src_labels, tar_graphs, tar_labels, self.mg_creation_alpha, self.cross_class, label_name, attribute_names,
                 self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, node_subst_fct, dataset_name, one_hot = False,
                 nbr_mgs_to_create = 5, remove_isolated_nodes= True, multipr = True,
                 enable_inserts = False,
                 alpha_range = [])

        nodes_graph_1 = [(0, {0: [0, 0, 0, 1]}),
                         (1, {0: [0, 0, 0, 1]}),
                         (2, {0: [0, 0, 0, 1]}),
                         (3, {0: [0, 0, 0, 1]})]

        edges_gr_1 = [(0, 1), (1, 3), (2, 3), (3, 1)]

        nodes_graph_2 = [(0, {0: [1, 0, 0, 0]}),
                         (1, {0: [1, 0, 0, 0]}),
                         (2, {0: [1, 0, 0, 0]}),
                         (3, {0: [1, 0, 0, 0]}),
                         (4, {0: [1, 0, 0, 0]})]

        edges_gr_2 = [(0, 1), (1, 2), (2, 3), (4, 1)]

        self.src_gr = nx.Graph()
        self.src_gr.add_nodes_from(nodes_graph_1)
        self.src_gr.add_edges_from(edges_gr_1)

        self.tar_gr = nx.Graph()
        self.tar_gr.add_nodes_from(nodes_graph_2)
        self.tar_gr.add_edges_from(edges_gr_2)

    def test_build_matching_graphs(self):
        mgs_dict = self.builder.build_matching_graphs()
        assert len(mgs_dict["mutagen"]) == 30
        assert len(mgs_dict["nonmutagen"]) == 10


    def test_build_mgs_from_edit_path_insert(self):


        edit_path = [(3,5),(4,3),(0,0),(1,1),(2,2),(6,4)]
        keep_perc = 0.5
        tar_graph_edit_path_dict = {v: k for k, v in edit_path}
        src_graph_edit_path_dict = {k: v for k, v in edit_path}  # too lazy to check for other conversion method to dict

        nbr_operations = int(keep_perc * len(edit_path))
        matching_graph_source, matching_graph_target = build_mgs_from_edit_path(edit_path, tar_graph_edit_path_dict, nbr_operations, self.src_gr,
                                                  self.tar_gr, f"_{keep_perc}", True,
                                                  src_graph_edit_path_dict)
        assert len(matching_graph_source.nodes) == 4
        assert not matching_graph_source.has_node(3)
        assert matching_graph_source.has_node(4)
        assert len(matching_graph_target.nodes) == 5
        assert not matching_graph_target.has_node(3)
        assert matching_graph_target.has_node(5)

        assert matching_graph_source.has_edge(0,1)
        assert matching_graph_source.has_edge(2,4)


        assert matching_graph_target.has_edge(0,1)
        assert matching_graph_target.has_edge(1,2)
        assert matching_graph_target.has_edge(1,4)
        assert matching_graph_target.has_edge(1,5)
        assert matching_graph_target.has_edge(2,5)


        assert matching_graph_source.nodes[0][0] == [1,0,0,0]
        assert matching_graph_source.nodes[1][0] == [0,0,0,1]
        assert matching_graph_source.nodes[2][0] == [0,0,0,1]
        assert matching_graph_source.nodes[4][0] == [1,0,0,0]

        assert matching_graph_target.nodes[0][0] == [0, 0, 0, 1]
        assert matching_graph_target.nodes[1][0] == [1, 0, 0, 0]
        assert matching_graph_target.nodes[2][0] == [1, 0, 0, 0]
        assert matching_graph_target.nodes[4][0] == [1, 0, 0, 0]
        assert matching_graph_target.nodes[5][0] == [0, 0, 0, 1]
    def test_build_mgs_from_edit_path_no_insert(self):


        edit_path = [(3,5),(4,3),(0,0),(1,1),(2,2),(6,4)]
        keep_perc = 0.5
        tar_graph_edit_path_dict = {v: k for k, v in edit_path}
        src_graph_edit_path_dict = {k: v for k, v in edit_path}  # too lazy to check for other conversion method to dict

        nbr_operations = int(keep_perc * len(edit_path))
        matching_graph_source, matching_graph_target = build_mgs_from_edit_path(edit_path, tar_graph_edit_path_dict, nbr_operations, self.src_gr,
                                                  self.tar_gr, f"_{keep_perc}", False,
                                                  src_graph_edit_path_dict)
        assert len(matching_graph_source.nodes) == 2
        assert len(matching_graph_target.nodes) == 4

        assert matching_graph_source.has_edge(0,1)
        assert len(matching_graph_source.edges) == 1
        assert matching_graph_target.has_edge(0,1)
        assert matching_graph_target.has_edge(1,2)
        assert matching_graph_target.has_edge(1,4)
        assert len(matching_graph_target.edges) == 3

        assert matching_graph_source.nodes[1][0] == [0,0,0,1]
        assert matching_graph_source.nodes[0][0] == [1,0,0,0]

        assert matching_graph_target.nodes[0][0] == [0, 0, 0, 1]
        assert matching_graph_target.nodes[1][0] == [1, 0, 0, 0]
        assert matching_graph_target.nodes[2][0] == [1, 0, 0, 0]
        assert matching_graph_target.nodes[4][0] == [1, 0, 0, 0]



