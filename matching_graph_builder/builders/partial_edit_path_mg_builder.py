

import itertools
import multiprocessing
import os
import pickle as pkl
import random
from multiprocessing import Pool
from optparse import OptionParser
from pathlib import Path
import networkx as nx



from matching_graph_builder.builders.matching_graph_builder import MatchingGraphBuilderBase
from matching_graph_builder.utils.graph_edit_distance import calculate_ged, is_insertion, is_deletion, is_substitution, \
    relabel_node, is_epsilon_epsilon, remove_isolated_nodes


class RandomPathMatchingGraphBuilder(MatchingGraphBuilderBase):
    def __init__(self, src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,
                 node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot = False,nbr_mgs_to_create = 1, remove_isolated_nodes= True, multipr = False):
        self.nbr_mgs_to_create = nbr_mgs_to_create
        super().__init__(src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name,
                         attribute_names, node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot, remove_isolated_nodes, multipr)

        self.build_seeds()

    def build_seeds(self):
        seeds_dict = {}
        seed_nbrs = list(range(999999))

        for lbl, pairs in self.pair_dict.items():
            seeds_dict[lbl] = random.choices(seed_nbrs, k= len(pairs))

        self.seeds = seeds_dict
        self.save_seeds(f"{self.dataset_name}_{self.nbr_mgs_to_create}_seeds_random_edit_path_mgs.txt")



    def save_seeds(self, param):
            path =f"{os.getcwd()}/randomized_graphs_full/seeds/"
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(f"{path}{param}", 'w') as f:
                for lbl, seeds in self.seeds.items():
                    f.write(str(lbl))
                    f.write('\n')
                    for seed in seeds:
                        f.write(str(seed))
                        f.write('\n')





    def build_matching_graphs(self):
        mgs_dict = {}
        for key in self.pair_dict.keys():
            mgs_dict[key] = []
        # for graph_pair,seed in zip(graph_pair_list, seeds):
        # mgs, mgs_lbls = build_mg_from_pair(graph_class, graph_pair, nbr_mgs_to_build_from_one_path, seed)
        for key in mgs_dict.keys():
            seed_pair_zip = zip(self.pair_dict[key], self.seeds[key])
            # with Pool() as pool:
            # for pair in seed_pair_zip:
            #     mgs_l.append( build_mg_from_pair_para(pair,key, self.nbr_mgs_to_create,
            #                                           self.mg_creation_alpha,
            #                                           self.label_name,
            #                                           self.attribute_names))
            with Pool(processes=multiprocessing.cpu_count()-3) as pool:
                mgs_l = pool.starmap(build_mg_from_pair_para, zip(seed_pair_zip, itertools.repeat(key), itertools.repeat(self.nbr_mgs_to_create),
                                                                  itertools.repeat(self.mg_creation_alpha),
                                                                  itertools.repeat(self.label_name),
                                                                  itertools.repeat(self.attribute_names),
                                                                  itertools.repeat(self.one_hot)))
                for mg_l in mgs_l:
                    for gr,lbl in zip(mg_l[0],mg_l[1]):
                        if len(gr.nodes()) > 0 and len(gr.edges()) > 0:
                            mgs_dict[lbl].append(gr)


        return mgs_dict


def build_mg_from_pair_para(pair_seed_zip, graph_class, nbr_mgs_to_create, mg_creation_alpha, label_name, attribute_names, one_hot):
    mgs, mgs_lbls = [],[]
    graph_pair = pair_seed_zip[0]
    seed = pair_seed_zip[1]
    random.seed(seed)
    src_gr = graph_pair[0]
    tar_gr = graph_pair[1]
    keep_percs = [i / 100 for i in random.sample(range(10, 90), nbr_mgs_to_create)]
    edit_path,_,_ = calculate_ged(src_gr,tar_gr,mg_creation_alpha,label_name, attribute_names, one_hot)
    for keep_percentage in keep_percs:
        sampled_path = random.sample(edit_path, int(keep_percentage * len(edit_path)))
        src_mg, tar_mg = build_mgs_from_edit_path(sampled_path, src_gr, tar_gr, f"_{keep_percentage}")
        mgs.append(src_mg)
        mgs.append(tar_mg)
        mgs_lbls.append(graph_class)
        mgs_lbls.append(graph_class)

    return (mgs, mgs_lbls)

def build_mgs_from_edit_path(edit_path, source_graph, target_graph, keep_percentage_str):

    matching_graph_source = nx.Graph(source_graph,name=f"{source_graph.name}_{target_graph.name}_matching_graph{keep_percentage_str}")
    matching_graph_target = nx.Graph(target_graph, name=f"{target_graph.name}_{source_graph.name}_matching_graph{keep_percentage_str}")
    src_node_names = list(source_graph.nodes)
    tar_node_names = list(target_graph.nodes)
    for src_node_idx, tar_node_idx in edit_path:
        if is_epsilon_epsilon(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            continue
        elif is_insertion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            matching_graph_target.remove_node(tar_node_names[tar_node_idx])
        elif is_deletion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            matching_graph_source.remove_node(src_node_names[src_node_idx])
        elif is_substitution(src_node_names[src_node_idx], tar_node_names[tar_node_idx],source_graph,target_graph):
            matching_graph_source = relabel_node(matching_graph_source, src_node_names[src_node_idx], target_graph,tar_node_names[tar_node_idx])
            matching_graph_target = relabel_node(matching_graph_target,tar_node_names[tar_node_idx], source_graph, src_node_names[src_node_idx])
    matching_graph_source = remove_isolated_nodes(matching_graph_source)
    matching_graph_target = remove_isolated_nodes(matching_graph_target)

    return matching_graph_source, matching_graph_target





