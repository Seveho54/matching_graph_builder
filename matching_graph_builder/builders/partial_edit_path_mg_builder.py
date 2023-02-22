

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
                 node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot = False,
                 nbr_mgs_to_create = 1, remove_isolated_nodes= True, multipr = False,
                 enable_inserts = False,
                 alpha_range = []):
        self.nbr_mgs_to_create = nbr_mgs_to_create
        super().__init__(src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name,
                         attribute_names, node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot, remove_isolated_nodes, multipr)
        self.alphas = None
        self.alpha_range = alpha_range
        self.build_seeds()
        self.enable_inserts = enable_inserts

    def build_seeds(self):
        seeds_dict = {}
        alphas_dict = {}
        seed_nbrs = list(range(999999))

        for lbl, pairs in self.pair_dict.items():
            seeds_dict[lbl] = random.choices(seed_nbrs, k = len(pairs))
            if self.alpha_range != []:
                alphas_dict[lbl] = random.choices(self.alpha_range, k = len(pairs))

        self.seeds = seeds_dict
        self.alphas = alphas_dict
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




    # ToDo: Actually only inserts need to be enabled in order for everything to work. Flag, inserts enabled? => if insert percentage => Inserts enabled
    # Force inserts?
    # Important check: Same label subs only happens if c(del) + c(ins ) >= c(subs)
    def build_matching_graphs(self):
        mgs_dict = {}
        for key in self.pair_dict.keys():
            mgs_dict[key] = []
        # for graph_pair,seed in zip(graph_pair_list, seeds):
        # mgs, mgs_lbls = build_mg_from_pair(graph_class, graph_pair, nbr_mgs_to_build_from_one_path, seed)
        for key in mgs_dict.keys():
            mgs_l = []
            seed_pair_zip = zip(self.pair_dict[key], self.seeds[key])
            # for idx, pair in enumerate(seed_pair_zip):
            #     if self.alphas is not None:
            #         self.mg_creation_alpha = self.alphas[key][idx]
            #     mgs_l.append( build_mg_from_pair_para(pair,key, self.nbr_mgs_to_create,
            #                                           self.mg_creation_alpha,
            #                                           self.label_name,
            #                                           self.attribute_names,
            #                                           self.one_hot,
            #                                           self.enable_inserts))
            with Pool(processes=multiprocessing.cpu_count()-3) as pool:
                if self.alphas != {}:
                    alpha_param = self.alphas[key]
                else:
                    alpha_param = itertools.repeat(self.mg_creation_alpha)
                mgs_l = pool.starmap(build_mg_from_pair_para, zip(seed_pair_zip, itertools.repeat(key), itertools.repeat(self.nbr_mgs_to_create),
                                                                  alpha_param,
                                                                  itertools.repeat(self.label_name),
                                                                  itertools.repeat(self.attribute_names),
                                                                  itertools.repeat(self.one_hot),
                                                                  itertools.repeat(self.enable_inserts)))
                for mg_l in mgs_l:
                    for gr,lbl in zip(mg_l[0],mg_l[1]):
                        if len(gr.nodes()) > 0 and len(gr.edges()) > 0:
                            mgs_dict[lbl].append(gr)


        return mgs_dict


def build_mg_from_pair_para(pair_seed_zip, graph_class, nbr_mgs_to_create, mg_creation_alpha, label_name, attribute_names, one_hot, enable_inserts):
    mgs, mgs_lbls = [],[]
    graph_pair = pair_seed_zip[0]
    seed = pair_seed_zip[1]
    random.seed(seed)
    src_gr = graph_pair[0]
    tar_gr = graph_pair[1]
    keep_percs = [i / 100 for i in random.sample(range(10, 90), nbr_mgs_to_create)]
    edit_path,_,_ = calculate_ged(src_gr,tar_gr,mg_creation_alpha,label_name, attribute_names, one_hot)
    tar_graph_edit_path_dict = {v:k for k,v in edit_path}

    for keep_percentage in keep_percs:
        random.shuffle(edit_path)
        nbr_operations = int(keep_percentage * len(edit_path))
        src_mg, tar_mg = build_mgs_from_edit_path(edit_path, tar_graph_edit_path_dict, nbr_operations, src_gr, tar_gr, f"_{keep_percentage}", enable_inserts)
        mgs.append(src_mg)
        # if not enable_inserts:
        mgs.append(tar_mg)
        mgs_lbls.append(graph_class)
        mgs_lbls.append(graph_class)

    return (mgs, mgs_lbls)


def get_new_node_name(src_node_names,tar_node_name, matching_graph_target ):
    new_node_attrs = matching_graph_target.nodes(data=True)[tar_node_name]
    new_node = (len(src_node_names), new_node_attrs)
    return new_node


def handle_insertion(matching_graph_source, matching_graph_target,src_node_names, tar_node_idx, tar_node_names, enable_inserts, full_edit_path,tar_graph_edit_path_dict):
    if enable_inserts:
        tar_node_name = tar_node_names[tar_node_idx]
        tar_edges = matching_graph_target.edges(tar_node_name)
        new_node = get_new_node_name(src_node_names, tar_node_name, matching_graph_target)
        edges_to_add = []
        for u,v in tar_edges:
            counterpart = None
            if tar_node_name == u:
                counterpart = v
            elif tar_node_name == v:
                counterpart = u
            if counterpart is not None:
                if tar_graph_edit_path_dict[counterpart] < len(matching_graph_source.nodes()):
                    edges_to_add.append((tar_graph_edit_path_dict[counterpart], new_node[0]))


        matching_graph_source.add_nodes_from([new_node])
        matching_graph_source.add_edges_from(edges_to_add)

        for id, vals in matching_graph_source.nodes(data=True):
            if len(vals) == 0:
                print("Failure")
        return matching_graph_source


    else:
        matching_graph_target.remove_node(tar_node_names[tar_node_idx])
        return matching_graph_target



def build_mgs_from_edit_path(full_edit_path, tar_graph_edit_path_dict, nbr_operations, source_graph, target_graph, keep_percentage_str, enable_inserts):

    matching_graph_source = nx.Graph(source_graph,name=f"{source_graph.name}_{target_graph.name}_matching_graph{keep_percentage_str}")
    matching_graph_target = nx.Graph(target_graph, name=f"{target_graph.name}_{source_graph.name}_matching_graph{keep_percentage_str}")
    src_node_names = list(source_graph.nodes)
    tar_node_names = list(target_graph.nodes)
    for src_node_idx, tar_node_idx in full_edit_path[:nbr_operations]:
        if is_epsilon_epsilon(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            continue
        elif is_insertion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            if enable_inserts:
                matching_graph_source = handle_insertion(matching_graph_source, matching_graph_target, src_node_names, tar_node_idx, tar_node_names, enable_inserts, full_edit_path,tar_graph_edit_path_dict)
                matching_graph_target = handle_insertion(matching_graph_source, matching_graph_target, src_node_names, tar_node_idx, tar_node_names, False, full_edit_path,tar_graph_edit_path_dict)
            else:
                matching_graph_target = handle_insertion(matching_graph_source, matching_graph_target, src_node_names, tar_node_idx, tar_node_names, enable_inserts, full_edit_path,tar_graph_edit_path_dict)

        elif is_deletion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            matching_graph_source.remove_node(src_node_names[src_node_idx])
        elif is_substitution(src_node_names[src_node_idx], tar_node_names[tar_node_idx],source_graph,target_graph):
            matching_graph_source = relabel_node(matching_graph_source, src_node_names[src_node_idx], target_graph,tar_node_names[tar_node_idx])
            matching_graph_target = relabel_node(matching_graph_target,tar_node_names[tar_node_idx], source_graph, src_node_names[src_node_idx])
    matching_graph_source = remove_isolated_nodes(matching_graph_source)
    matching_graph_target = remove_isolated_nodes(matching_graph_target)

    return matching_graph_source, matching_graph_target





