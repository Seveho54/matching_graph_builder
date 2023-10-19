import graph_loader.graphml_loader as loader
import networkx as nx
from matching_graph_builder.builders.mcs_approx_mg_builder import MCSApproxMGBuilder


class TestMCSApproxMGBuilder():

    def setup(self):
        graphs, labels = loader.load_desired_split_cxl("resources/mutagenicity/sample_mg_dict.cxl")
        src_graphs = graphs
        src_labels = labels
        tar_graphs = graphs
        tar_labels = labels
        label_name = "chem"
        dataset_name = "mutagenicity"
        self.builder = MCSApproxMGBuilder(src_graphs, src_labels, tar_graphs, tar_labels, label_name, dataset_name= dataset_name)

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





