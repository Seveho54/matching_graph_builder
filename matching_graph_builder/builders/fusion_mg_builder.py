import os
import random
from pathlib import Path
import os
import random
from pathlib import Path

import networkx as nx
from matching_graph_builder.utils.graph_edit_distance import calculate_ged, is_insertion, is_deletion, relabel_node


class FusionMatchingGraphBuilder(RandomPathMatchingGraphBuilder):
    def __init__(self, src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name, attribute_names,
                 node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name, one_hot =False, nbr_mgs_to_create = 1):
        self.nbr_mgs_to_create = nbr_mgs_to_create
        super().__init__(src_graphs, src_labels, tar_graphs, tar_labels, mg_creation_alpha, cross_class, label_name,
                         attribute_names, node_ins_c, node_del_c, edge_ins_c, edge_del_c, node_subst_fct, dataset_name)

        self.build_seeds()


    def save_seeds(self, param):
            path =f"{os.getcwd()}/fusion_graphs_full/seeds/"
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(f"{path}{param}", 'w') as f:
                for lbl, seeds in self.seeds.items():
                    f.write(str(lbl))
                    f.write('\n')
                    for seed in seeds:
                        f.write(str(seed))
                        f.write('\n')





def build_mg_from_pair_para(pair_seed_zip, graph_class, nbr_mgs_to_create, mg_creation_alpha, label_name, attribute_names):
    mgs, mgs_lbls = [],[]
    graph_pair = pair_seed_zip[0]
    seed = pair_seed_zip[1]
    random.seed(seed)
    src_gr = graph_pair[0]
    tar_gr = graph_pair[1]
    keep_percs = [i / 100 for i in random.sample(range(10, 90), nbr_mgs_to_create)]
    edit_path,_,_ = calculate_ged(src_gr,tar_gr,mg_creation_alpha,label_name, attribute_names, self.one_hot)
    for keep_percentage in keep_percs:
        sampled_path = random.sample(edit_path, int(keep_percentage * len(edit_path)))
        src_mg, tar_mg = build_mgs_from_edit_path(sampled_path, src_gr, tar_gr, f"_{keep_percentage}")
        mgs.append(src_mg)
        mgs.append(tar_mg)
        mgs_lbls.append(graph_class)
        mgs_lbls.append(graph_class)

    return (mgs, mgs_lbls)

def get_substitutions(edit_path, src_node_names, tar_node_names):
    substs, dels, ins = [],[],[]
    for src_node_idx, tar_node_idx in edit_path:
        if is_insertion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            substs.append((src_node_idx, tar_node_idx))
        elif is_insertion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            ins.append((src_node_idx, tar_node_idx))
        elif is_deletion(src_node_idx, src_node_names, tar_node_idx, tar_node_names):
            dels.append((src_node_idx, tar_node_idx))

    return substs, dels, ins

def execute_subs(sampled_path, matching_graph_source,src_node_names, target_graph, tar_node_names):
    subs_dict = {t:t for t in tar_node_names}

    for src_node_idx, tar_node_idx in sampled_path:
        subs_dict[tar_node_names[tar_node_idx]] = src_node_names[src_node_idx]
        matching_graph_source = relabel_node(matching_graph_source, src_node_names[src_node_idx], target_graph,tar_node_names[tar_node_idx])
    return subs_dict

def build_mg_from_pair_para(pair_seed_zip, graph_class, nbr_mgs_to_create, mg_creation_alpha, label_name, attribute_names):
    mgs, mgs_lbls = [],[]
    graph_pair = pair_seed_zip[0]
    seed = pair_seed_zip[1]
    random.seed(seed)
    src_gr = graph_pair[0]
    tar_gr = graph_pair[1]
    keep_percs = [i / 100 for i in random.sample(range(40, 90), nbr_mgs_to_create)]
    edit_path,_,_ = calculate_ged(src_gr,tar_gr,mg_creation_alpha,label_name, attribute_names,self.one_hot)
    for keep_percentage in keep_percs:
        src_mg, tar_mg = build_mgs_from_edit_path(edit_path, src_gr, tar_gr, keep_percentage)

    return (mgs, mgs_lbls)

def build_mgs_from_edit_path(edit_path, source_graph, target_graph, keep_percentage):
    keep_percentage_str = f"_{keep_percentage}"

    matching_graph_source = nx.Graph(source_graph,name=f"{source_graph.name}_{target_graph.name}_matching_graph{keep_percentage_str}")
    src_node_names = list(source_graph.nodes)
    tar_node_names = list(target_graph.nodes)

    substitutions, dels, ins = get_substitutions(edit_path, src_node_names, tar_node_names)
    sampled_path = random.sample(substitutions, int(keep_percentage * len(edit_path)))
    subst_dict = execute_subs(sampled_path, matching_graph_source,src_node_names,target_graph, tar_node_names)
    for insertion in ins:
        matching_graph_source.add_node(insertion[1],target_graph.nodes(data=True)[insertion[1]])
        edges = target_graph.edges(insertion[1])
        for edge in edges:
            part = edge[0] if edge[0] != insertion[1] else edge[1]
            part_dict = subst_dict[part]
            matching_graph_source.add_edge(insertion[1], part_dict)
    return matching_graph_source, matching_graph_target





