import itertools
import multiprocessing
from multiprocessing import Pool

from matching_graph_builder.builders.matching_graph_builder import MatchingGraphBuilderBase
from matching_graph_builder.utils.graph_edit_distance import calculate_ged
import networkx as nx


class OriginalMatchingGraphBuilder(MatchingGraphBuilderBase):
    def __init__(self, src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,
                 node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, prune_edges,
                 one_hot = False, remove_isolated_nodes= True, multipr = False):
        super().__init__(src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name,
                         attribute_names, node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot, remove_isolated_nodes, multipr)
        self.prune = prune_edges


    def build_matching_graphs(self):
        mgs_dict = {}
        for key in self.pair_dict.keys():
            mgs_dict[key] = []
        for key in mgs_dict.keys():
            if self.multipr:
                with Pool(processes=multiprocessing.cpu_count()-3) as pool:
                    mgs_l = pool.starmap(self.build_mg_from_pair, zip(self.pair_dict[key], itertools.repeat(key)))
            else:
                mgs_l = []
                for graph_pair in self.pair_dict[key]:
                    mgs_l.append(self.build_mg_from_pair(graph_pair, key))

            for mg_l in mgs_l:
                for gr,lbl in zip(mg_l[0],mg_l[1]):
                    if len(gr.nodes()) > 0 and len(gr.edges()) > 0:
                        mgs_dict[lbl].append(gr)


        return mgs_dict

    def build_mg_from_pair(self, graph_pair, graph_class):
        mgs, mgs_lbls = [],[]
        src_gr = graph_pair[0]
        tar_gr = graph_pair[1]
        edit_path,_,_ = calculate_ged(src_gr,tar_gr,self.mg_creation_alpha,self.label_name, self.attribute_names, self.one_hot)
        matching_graph_source, matching_graph_target = self._build_mgs_from_edit_path(edit_path, src_gr, tar_gr)
        mgs.append(matching_graph_source)
        mgs.append(matching_graph_target)
        mgs_lbls.append(graph_class)
        mgs_lbls.append(graph_class)
        return (mgs, mgs_lbls)

    def _build_mgs_from_edit_path(self, edit_path, source_graph, target_graph):
        """
        Naive algorithm only keeps those that found a match. Extra nodes that got deleted or inserted are not kept in the matching graph
        :param edit_path: The shortest path found by the bipartite matching
        :param source_graph: T
        :param target_graph:
        :return: Returns a pair of matching graphs, one for each of the two initial graphs.
        """

        source_matching_graph_node_names, target_matching_graph_node_names = self._get_matching_graph_node_names(edit_path, source_graph,
                                                                                                           target_graph)

        source_matching_graph = self.build_matching_graph_by_node_list(source_graph, source_matching_graph_node_names, target_graph.name)
        target_matching_graph = self.build_matching_graph_by_node_list(target_graph, target_matching_graph_node_names, source_graph.name)


        if self.prune:
            source_matching_graph, target_matching_graph = self.prune_unwanted_edges(source_matching_graph, target_matching_graph, source_graph, target_graph)

        source_matching_graph = self.remove_isolated_nodes(source_matching_graph)
        target_matching_graph = self.remove_isolated_nodes(target_matching_graph)

        return source_matching_graph, target_matching_graph

    def _get_matching_graph_node_names(self,edit_path, source_graph, target_graph):
        """
        Given an edit path, the coreesponding source graph and the corresponding target graph, it gets the names
        of the resulting source matching graph and the resulting target matching graph. Only gets the node names of the nodes that
        are substituted. Those that are inserted/deleted are not returned.
        :param target_graph: The source graph
        :param source_graph: The target graph
        :param edit_path:  The cheapest edit path between the two graphs
        :return: A list of the node names of both resulting matching graphs in order
        """
        source_graph_node_list = list(source_graph.nodes)
        target_graph_node_list = list(target_graph.nodes)

        source_matching_graph_node_list = [source_graph_node_list[source_graph_match] for
                                           source_graph_match, target_graph_match
                                           in edit_path
                                           if source_graph_match < len(source_graph_node_list)
                                           and target_graph_match < len(target_graph_node_list)]
        target_matching_graph_node_list = [target_graph_node_list[target_graph_match] for
                                           source_graph_match, target_graph_match
                                           in edit_path
                                           if source_graph_match < len(source_graph_node_list)
                                           and target_graph_match < len(target_graph_node_list)]

        return source_matching_graph_node_list, target_matching_graph_node_list


    def build_matching_graph_by_node_list(self,original_graph, node_names_to_keep, other_graph_name):
        '''
        Builds a matching graph given a the list of nodes contained in the graph and the original graph
        :param original_graph: nx.Graph
            The original graph from which to build the matching grpah from
        :param node_names_to_keep: list, nx.Graph
            list of gra
        :return:
        '''
        desired_matching_graph = self.initialize_matching_graph(original_graph, node_names_to_keep)

        target_matching_edges = self.get_matching_edges(original_graph, desired_matching_graph)
        for mg_edges in target_matching_edges:
            edge_data = mg_edges[1]
            if not edge_data:
                desired_matching_graph.add_edge(*mg_edges[0])
            else:
                desired_matching_graph.add_edge(*mg_edges[0],**mg_edges[1])
        desired_matching_graph = nx.Graph(desired_matching_graph, name="{}_{}_matching_graph".format(original_graph.name, other_graph_name))
        return desired_matching_graph

    def initialize_matching_graph(self, original_graph, node_names_to_keep):
        '''
        Initializes the matching graph with nodes.
        :param original_graph: nx.Graph
            The graph to create the matching graph from
        :param node_names_to_keep: list(Str)
            The node names of the graph
        :return: nx.Graph
        '''
        desired_matching_graph = nx.Graph()
        desired_matching_graph.add_nodes_from(node_names_to_keep)
        nx.set_node_attributes(desired_matching_graph, self.get_attributes(original_graph))
        return desired_matching_graph

    def get_attributes(self,graph):
        '''
        Returns the attributes of each node in a graph.
        :param graph: nx.Graph
        :return: dict, key:Str, value: Tuple
            Returns a dictionary with the node name as the key and the node attributes as the value
        '''
        attrs = {}
        for key, value in graph.nodes.items():
            attrs[key] = value

        return attrs

    def get_matching_edges(self,original_graph, matching_graph):
        '''
        Takes a list of edges of a given graph and its matching graph. It then returns those edges, that
        have their nodes existing in the given matching graph.
        ATTENTION: This only works, because we know that the edges are from the original graph and the matching graph
        is the graph resulting from that original graph
        :param edges: list, tuple(String, String)
            A list of edges
        :param matching_graph: nx.Graph

        :return: list, tuple(String, String)
            a list of edges to keep.
        '''
        node_names = list(matching_graph.nodes)
        matching_graph_edges = []
        edges = original_graph.edges
        for edge in edges:
            if (edge[0] in node_names and edge[1] in node_names):
                edge_lbl = original_graph.get_edge_data(*edge)
                matching_graph_edges.append((edge, edge_lbl))

        return matching_graph_edges

    def prune_unwanted_edges(self,source_matching_graph, target_matching_graph, source_graph=None, target_graph=None):
        '''
        Prunes unwanted edges of the matching graphs. An edge is unwanted, if it exists in one graph, but does not
        exist between the matched nodes of the other graph. Example _0->_0  and _1-> _2  . The edge _0->_1 of source graph
        is only wanted if _0->_2 in target graph exists
        :param source_matching_graph:
        :param target_matching_graph:
        :param edit_path:
        :return:
        '''

        # According to matching graph creation one, the number ofnodes of the matching graphs should always be equal length
        # Because insertions adnd deletions are not taken over
        assert len(source_matching_graph.nodes) == len(target_matching_graph.nodes)

        tmp_source_matching_graph = nx.Graph(source_matching_graph)
        tmp_source_graph = nx.Graph(source_graph)
        tmp_target_matching_graph = nx.Graph(target_matching_graph)
        tmp_target_graph = nx.Graph(target_graph)

        source_graph_node_names = list(source_matching_graph.nodes)
        target_graph_node_names = list(target_matching_graph.nodes)

        source_target_dict = {}
        target_source_dict = {}

        # This works, because the nodes are in order of the graph edit distance edit path. (0->1, 1->0) etc.
        for src, tar in zip(source_graph_node_names, target_graph_node_names):
            source_target_dict[src] = tar
            target_source_dict[tar] = src

        # edges that can be removed from source mg
        source_mg_to_remove_edges = [edge for edge in tmp_source_matching_graph.edges
                                     if not tmp_target_matching_graph.has_edge(source_target_dict[edge[0]],
                                                                               source_target_dict[edge[1]])]

        # edges that can be removed from target mg
        target_mg_to_remove_edges = [edge for edge in tmp_target_matching_graph.edges
                                     if not tmp_source_matching_graph.has_edge(target_source_dict[edge[0]],
                                                                               target_source_dict[edge[1]])]




        tmp_source_matching_graph.remove_edges_from(source_mg_to_remove_edges)
        tmp_target_matching_graph.remove_edges_from(target_mg_to_remove_edges)

        return tmp_source_matching_graph, tmp_target_matching_graph

    def remove_isolated_nodes(self,graph):
        '''
        This method removes nodes that are not contained in any of the edges
        :param graph:
        :return:
        '''
        result = nx.Graph(graph)
        node_names = list(graph.nodes)
        edges = list(graph.edges)
        nodes_in_edges_one = []
        nodes_in_edges_two = []
        if len(edges) > 0:
            nodes_in_edges_one, nodes_in_edges_two = map(list, zip(*edges))

        for node_name in node_names:
            if node_name not in nodes_in_edges_one and node_name not in nodes_in_edges_two:
                result.remove_node(node_name)

        return result
    ########


    # def are_matching_graph_nodes_in_correct_order(source_graph, source_matching_graph,target_graph, target_matching_graph, substitution_path):
    #     '''
    #     Takes two matching graphs and their originals, and checks whether the matching graph.nodes are in the proper order
    #     according to the edit path.
    #     For example: Edit path: [(0,1),(1,0)] Expected node order source: = [0,1] and for target = [1,0]
    #     :param source_graph_node_names:
    #     :param target_graph_node_names:
    #     :param edit_path:
    #     :return: True when the nodes have the proper order, else false
    #     '''
    #     source_graph_node_names = list(source_graph.nodes)
    #     target_graph_node_names = list(target_graph.nodes)
    #
    #     source_matching_graph_node_names = list(source_matching_graph.nodes)
    #     target_matching_graph_node_names = list(target_matching_graph.nodes)
    #
    #
    #     i = 0
    #     for tuple in substitution_path:
    #         expected_node_name_source = source_graph_node_names[tuple[0]]
    #         expected_node_name_target = target_graph_node_names[tuple[1]]
    #
    #         actual_node_name_source_mg = source_matching_graph_node_names[i]
    #         actual_node_name_target_mg = target_matching_graph_node_names[i]
    #
    #         if expected_node_name_source != actual_node_name_source_mg or \
    #                 expected_node_name_target != actual_node_name_target_mg:
    #             return False
    #         i+=1
    #
    #     return True





    # def get_substitutions(source_graph, target_graph, edit_path):
    #     '''
    #     Removes all the deletions and insertions from the edit path, and just returns the path of substitutions
    #     :param source_graph:
    #     :param target_graph:
    #     :param edit_path:
    #     :return: A path containing the list of substitutions
    #     '''
    #     # Remove insertions and deletions
    #     substitution_path = edit_path.copy()
    #
    #     for tuple in edit_path:
    #         if tuple[1] >= len(target_graph.nodes) or tuple[0] >= len(source_graph.nodes):
    #             substitution_path.remove(tuple)
    #
    #     return substitution_path








