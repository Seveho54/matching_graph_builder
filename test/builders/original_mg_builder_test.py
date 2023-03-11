from matching_graph_builder.builders.original_mg_builder import OriginalMatchingGraphBuilder
import graph_loader.graphml_loader  as loader
import networkx as nx


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
        self.builder = OriginalMatchingGraphBuilder(src_graphs, src_labels, tar_graphs, tar_labels, self.mg_creation_alpha, self.cross_class, label_name, attribute_names,
                                                    self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, node_subst_fct, dataset_name, prune_edges,
                                                    one_hot = False, rm_isol_nodes= True, multipr = False)

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
        assert len(mgs_dict["mutagen"]) == 6
        assert len(mgs_dict["nonmutagen"]) == 2


    def test_build_mgs_from_edit_path_rm_isol_prune(self):
        builder = OriginalMatchingGraphBuilder([], [], [], [], self.mg_creation_alpha, False, None,[],
                                                    self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, "",
                                                    "dummy", True,
                                                    one_hot = True, rm_isol_nodes= True, multipr = False)


        edit_path = [(0,0),(1,1),(2,2),(3,5),(4,3),(6,4)]
        matching_graph_source, matching_graph_target = builder._build_mgs_from_edit_path(edit_path, self.src_gr, self.tar_gr)
        assert len(matching_graph_source.nodes) == 2
        assert len(matching_graph_target.nodes) == 2

        assert matching_graph_source.has_edge(0,1)
        assert len(matching_graph_source.edges) == 1
        assert matching_graph_target.has_edge(0,1)
        assert len(matching_graph_target.edges) == 1

        for id, attr in matching_graph_source.nodes(data=True):
            assert attr[0] == [0,0,0,1]

        for id, attr in matching_graph_target.nodes(data=True):
            assert attr[0] == [1, 0, 0, 0]

    def test_build_mgs_from_edit_path_keep_isol_prune(self):
        builder = OriginalMatchingGraphBuilder([], [], [], [], self.mg_creation_alpha, False, None,[],
                                                    self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, "",
                                                    "dummy", True,
                                                    one_hot = True, rm_isol_nodes= False, multipr = False)


        edit_path = [(0,0),(1,1),(2,2),(3,5),(4,3),(6,4)]
        matching_graph_source, matching_graph_target = builder._build_mgs_from_edit_path(edit_path, self.src_gr, self.tar_gr)
        assert len(matching_graph_source.nodes) == 3
        assert len(matching_graph_target.nodes) == 3


        assert matching_graph_source.has_edge(0,1)
        assert len(matching_graph_source.edges) == 1
        assert matching_graph_target.has_edge(0,1)
        assert len(matching_graph_target.edges) == 1

        for id, attr in matching_graph_source.nodes(data=True):
            assert attr[0] == [0,0,0,1]

        for id, attr in matching_graph_target.nodes(data=True):
            assert attr[0] == [1, 0, 0, 0]
    def test_build_mgs_from_edit_path_rm_isol_no_prune(self):
        builder = OriginalMatchingGraphBuilder([], [], [], [], self.mg_creation_alpha, False, None,[],
                                                    self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, "",
                                                    "dummy", False,
                                                    one_hot = True, rm_isol_nodes= True, multipr = False)

        edit_path = [(0,0),(1,1),(2,2),(3,5),(4,3),(6,4)]
        matching_graph_source, matching_graph_target = builder._build_mgs_from_edit_path(edit_path, self.src_gr, self.tar_gr)
        assert len(matching_graph_source.nodes) == 2
        assert len(matching_graph_target.nodes) == 3

        assert matching_graph_source.has_edge(0, 1)
        assert len(matching_graph_source.edges) == 1
        assert matching_graph_target.has_edge(0, 1)
        assert matching_graph_target.has_edge(1, 2)
        assert len(matching_graph_target.edges) == 2

        for id, attr in matching_graph_source.nodes(data=True):
            assert attr[0] == [0,0,0,1]

        for id, attr in matching_graph_target.nodes(data=True):
            assert attr[0] == [1, 0, 0, 0]

    def test_build_mgs_from_edit_path_keep_isol_no_prune(self):
        builder = OriginalMatchingGraphBuilder([], [], [], [], self.mg_creation_alpha, False, None, [],
                                               self.node_ins_c, self.node_del_c, self.edge_ins_c, self.edge_del_c, "",
                                               "dummy", False,
                                               one_hot=True, rm_isol_nodes=False, multipr=False)

        edit_path = [(0, 0), (1, 1), (2, 2), (3, 5), (4, 3), (6, 4)]
        matching_graph_source, matching_graph_target = builder._build_mgs_from_edit_path(edit_path, self.src_gr,
                                                                                         self.tar_gr)
        assert len(matching_graph_source.nodes) == 3
        assert len(matching_graph_target.nodes) == 3

        assert matching_graph_source.has_edge(0, 1)
        assert len(matching_graph_source.edges) == 1
        assert matching_graph_target.has_edge(0, 1)
        assert matching_graph_target.has_edge(1, 2)
        assert len(matching_graph_target.edges) == 2

        for id, attr in matching_graph_source.nodes(data=True):
            assert attr[0] == [0, 0, 0, 1]

        for id, attr in matching_graph_target.nodes(data=True):
            assert attr[0] == [1, 0, 0, 0]

