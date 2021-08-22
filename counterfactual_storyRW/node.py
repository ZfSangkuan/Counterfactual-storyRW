'''
class Node of sub-graph
mutable
'''

class Node(object):
    '''
    class Node of sub-graph
    mutable
    Each node represents an eventuality in sub-graph, 
        with attribution eventuality, weight, elmo_repr.
    '''

    def __init__(self, eventuality, weight = 0, elmo_repr = None):
        """
        :param eventuality: one-to-one correspondence between node and eventuality
        :type eventuality: aser.Eventuality
        :param weight: Used to compute weighted distribution of each sentence $E_i~Normal$. 
                        Computed by settig weight of premise as 1, and flow down from premise. 
                        DIFFERENT to freq in aser.Relation.
        :type weight: float
        :param elmo_repr: 
        :type elmo_repr: 
        """
        self.eventuality = eventuality
        self.weight = weight
        self.elmo_repr = elmo_repr

    def __str__(self):
        return self.eventuality.words

    def __repr__(self):
        ret = " ".join(self.eventuality.words)
        ret = ret + "/" + str(self.weight)
        return ret
        # return self.eventuality.words + "/" + self.eventuality.weight


    
