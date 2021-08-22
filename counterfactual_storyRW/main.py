from pprint import pprint
import os
import sys
import time
import json
from aser.database.kg_connection import ASERKGConnection
from aser.eventuality import Eventuality
from aser.extract.aser_extractor import DiscourseASERExtractor, SeedRuleASERExtractor
from node import Node

FREQ_THRESHOLD = 0.1

def conn_to_aser_kg(aser_kg_dir):
    print("Loading ASER db from {} ...".format(aser_kg_dir))
    aser_kg_conn = ASERKGConnection(os.path.join(aser_kg_dir, "KG.db"), mode="cache")
    print("Loading ASER db done..")
    return aser_kg_conn

def _flow_down_from_single_node(node, ith_sent, list_nodes, dict_relation):
    sum_freq_cnt_of_node = 0
    list_tail_nodes = []
    list_tail_freq = []
    h_eid = node.eventuality.eid
    for h_t_eid, freq_cnt_relation in dict_relation:
        if h_t_eid[0] == h_eid:
            t_eid = h_t_eid[1]
            for i in range(ith_sent+1, 5):
                for nd in list_nodes[i]:
                    if nd.eventuality.eid == t_eid:
                        list_tail_nodes.append(nd)
                        list_tail_freq.append(freq_cnt_relation)
                        sum_freq_cnt_of_node += freq_cnt_relation
    for i in range(len(list_tail_nodes)):
        list_tail_nodes[i].weight += node.weight * list_tail_freq[i] / sum_freq_cnt_of_node


def build_sub_graph(aser_kg_conn, dicourse_extractor, seedrule_extractor, text_dict):
    '''
    Build sub-graph related to original story from aser KG, on which we make causal inference.
    Sub-graph consists of Nodes and edges.
    '''
    # init sub-graph
    print("-" * 40)
    print("start build sub-graph")
    list_raw_text = []  # 5 sentences of original story
    list_nodes = [set(), set(), set(), set(), set()]
    dict_relation = dict()  # dict: (h_eid, t_eid) -> freq_cnt

    # init list_raw_text with sentences of original story
    list_raw_text.extend([text_dict["premise"], text_dict["initial"]])
    for str in text_dict["original_ending"].split('. '):
        list_raw_text.append(str)
    pprint(list_raw_text)

    # init sub-graph with eventualities of original story
    for i in range(5):
        # extract eventuality from single sentence each time
        dicourse_e_from_sent = dicourse_extractor.extract_eventualities_from_text(list_raw_text[i], output_format="Eventuality", in_order=True)
        seedrule_e_from_sent = seedrule_extractor.extract_eventualities_from_text(list_raw_text[i], output_format="Eventuality", in_order=True)
        assert len(dicourse_e_from_sent) == 1 and len(seedrule_e_from_sent) == 1
        dicourse_eventualites_from_sent = dicourse_e_from_sent[0]
        seedrule_eventualites_from_sent = seedrule_e_from_sent[0]

        # if len(dicourse_eventualites_from_sent) < 1 and len(seedrule_eventualites_from_sent) < 1:    # if cannot extract any eventuality from one sentence
        #     print("ERROR: cannot extract any eventuality from some sentence(s)")
        #     return list_raw_text, list_nodes, dict_relation # then return empty graph

        # for eventuality_from_clause in dicourse_eventualites_from_sent: # for eventuality of each clauses in one sentence
        #     set_of_eventualites_ith_sentence = list_nodes[i]
        #     set_of_eventualites_ith_sentence.add(Node(eventuality_from_clause))

        if len(dicourse_eventualites_from_sent) >= 1:
            for eventuality_from_clause in dicourse_eventualites_from_sent: # for eventuality of each clauses in one sentence
                set_of_eventualites_ith_sentence = list_nodes[i]
                set_of_eventualites_ith_sentence.add(Node(eventuality_from_clause))
        elif len(seedrule_eventualites_from_sent) >= 1:
            for eventuality_from_clause in seedrule_eventualites_from_sent: # for eventuality of each clauses in one sentence
                set_of_eventualites_ith_sentence = list_nodes[i]
                set_of_eventualites_ith_sentence.add(Node(eventuality_from_clause))
        else:
            print("ERROR: cannot extract any eventuality from some sentence(s)")
            return list_raw_text, list_nodes, dict_relation # then return empty graph

    pprint(list_nodes)

    # fetch related eventualities of original story from ASER to build sub-graph
    print("start fetch related")
    for i in range(4):  # 4-i hops for ith sentence
        print("\tin loop {}, no. nodes: {}".format(i, len(list_nodes[i])))
        for node in list_nodes[i]:
            h_e = node.eventuality
            related_eventualities = aser_kg_conn.get_related_eventualities(h_e)
            print("\t\trelated eventuality: {}".format(related_eventualities))
            for t_e, relation in related_eventualities:
                freq_cnt = sum(relation.relations.values())
                print("\t\t\tfreq_cont: {}".format(freq_cnt))
                if freq_cnt > FREQ_THRESHOLD:
                    dict_relation[(relation.hid, relation.tid)] = freq_cnt
                    list_nodes[i+1].add(Node(t_e))
    pprint(list_nodes)
    pprint(dict_relation)
                
    # Set weight of premise to 1,
    # then flow down the whole DAG to get weights of each node
    for premise_node in list_nodes[0]:
        premise_node.weight = 1
        _flow_down_from_single_node(premise_node, 0, list_nodes, dict_relation)
    for i in range(1,4):
        for node in list_nodes[i]:
            _flow_down_from_single_node(node, i, list_nodes, dict_relation)

    return list_raw_text, list_nodes, dict_relation


def compute_eventuality_dist_Ei(list_nodes, dict_relation):
    pass


if __name__ == "__main__":
    # st = time.time()

    # Connect to ASER Knowledge Graph
    # aser_kg_dir = sys.argv[1]
    # aser_kg_dir = "./data/"
    aser_kg_dir = "/Users/zhifanshangguan/Downloads/DataBase/aser_core_gutenberg/"
    aser_kg_conn = conn_to_aser_kg(aser_kg_dir)
    

    # Load text from file
    # file_train_sup_sml = open('train_supervised_small.json', 'r')
    # raw_train_sup_sml = json.load(file_train_sup_sml)
    # text = "My army will find your boat. In the meantime, I'm sure we could find you suitable accommodations."
    # text = "On my way to work I stopped to get some coffee. I went through the drive through and placed my order. I paid the cashier and patiently waited for my drink. When she handed me the drink, the lid came off and spilled on me. The coffee hurt and I had to go home and change clothes."
    # text_json = {"story_id": "080198fc-d0e7-42b3-8e63-b2144e59d816", "premise": "On my way to work I stopped to get some coffee.", "initial": "I went through the drive through and placed my order.", "counterfactual": "I went inside to place my order.", "original_ending": "I paid the cashier and patiently waited for my drink. When she handed me the drink, the lid came off and spilled on me. The coffee hurt and I had to go home and change clothes.", "edited_ending": ["I paid the cashier and patiently waited at the counter for my drink.", "When she handed me the drink, the lid came off and spilled on me.", "The coffee hurt and I had to go home and change clothes."]}
    # text_json = {"story_id": "dbb0ad3e-9389-44ee-8290-7c3458e3fa0f", "premise": "Kim and her glass went on a field trip to an aquarium.", "initial": "Everyone enjoyed looking at the sea creatures.", "counterfactual": "Everyone did not enjoy looking at the sea  creatures so decided to go home.", "original_ending": "But when they went to the shark exhibit, Kim was scared. She stayed behind as the other students watched the sharks. Everyone made fun of Kim.", "edited_ending": ["Instead of going home they went to the shark exhibit, Kim was scared.", "She stayed behind as the other students watched the sharks.", "Everyone made fun of Kim."]}
    text_json = {"story_id": "e5955040-5b87-4acb-a8c7-7e81d0ffb9f5", "premise": "Susie was sitting on her barstool.", "initial": "She kept kicking the counter with her feet.", "counterfactual": "She kept herself steady with her feet.", "original_ending": "Suddenly, her kick sent her falling backwards. The chair hit the ground with a thud and broke. Susie hurt her head and was really scared.", "edited_ending": ["Suddenly, an earthquake sent her falling backwards.", "The chair hit the ground with a thud and broke.", "Susie hurt her head and was really scared."]}
    # text_json = {"story_id": "dc234072-2e69-4999-9e2f-632d3ea30b78", "premise": "Celeste rode her motorcycle across the woods.", "initial": "When she almost arrived at the intersection, a moose appeared.", "counterfactual": "When she almost arrived at the intersection, a deer appeared.", "original_ending": "She didn't have enough time to brake and drove towards the moose. They were both knocked out. She eventually got up and called the police.", "edited_ending": ["She didn't have enough time to brake and drove towards the deer,", "They were both knocked out.", "She eventually got up and called the police."]}
    # text = json.loads(text_json)
    text = text_json["premise"] + " " + text_json["initial"] + " " + text_json["original_ending"]
    # text_dict = json.loads(text)
    text_dict = text_json   # debug
    

    # Get ASER Extractor
    dicourse_extractor = DiscourseASERExtractor(corenlp_path="/Users/zhifanshangguan/stanza_corenlp", corenlp_port=9000)
    seedrule_extractor = SeedRuleASERExtractor(corenlp_path="/Users/zhifanshangguan/stanza_corenlp", corenlp_port=9000)
    res_e = dicourse_extractor.extract_eventualities_from_text(text, output_format="Eventuality", in_order=True)
    print("dicourse_extractor: ")
    pprint(res_e)
    res_e = seedrule_extractor.extract_eventualities_from_text(text, output_format="Eventuality", in_order=True)
    print("seedrule_extractor: ")
    pprint(res_e)


    # Build sub-graph which consists of list_nodes and dict_edges
    list_raw_text, list_nodes, dict_relation \
        = build_sub_graph(aser_kg_conn, dicourse_extractor, seedrule_extractor, text_dict)


    # raw text to ELMo

    # STEP 1 compute eventuality dist E_i
    # event representation -> distribution
    compute_eventuality_dist_Ei(list_nodes, dict_relation)

    # STEP 2 compute situation dist U_i|E_{<i} with Variational Inference technology


    # STEP 3 make causal inference on E_i|U_i,E_{<i}


    
