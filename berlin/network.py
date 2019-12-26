from . import state
from . import locode
from . import subdivision

try:
    import networkx as nx
except ImportError:
    nx = None

NEARBY = {'subdiv': 10, 'locode': 5}

class LocodeNetwork:
    def __init__(self, bank, nearby=NEARBY):
        if not nx:
            raise RuntimeError("Network calculations require networkx to be available")

        self.bank = bank
        self.graph = nx.Graph()
        self.nearby = nearby

    def build(self):
        for ste in self.bank._bank[state.State.code_type].values():
            self.graph.add_node(ste.identifier)

        for subdiv in self.bank._bank[subdivision.SubDivision.code_type].values():
            self.graph.add_node(subdiv.identifier)

            ste = subdiv.get_state()
            if ste:
                self.graph.add_edge(subdiv.identifier, ste.identifier, weight=3)

        for lcde in self.bank._bank[locode.Locode.code_type].values():
            self.graph.add_node(lcde.identifier)

            subdiv = lcde.get_state()
            if subdiv:
                self.graph.add_edge(lcde.identifier, subdiv.identifier, weight=1)

        for ste in self.bank._bank[state.State.code_type].values():
            for sd1 in ste.get_children():
                for sd2 in ste.get_children():
                    if sd1 != sd2 and sd1.coordinates and sd2.coordinates:
                        distance = sd1.distance(*sd2.coordinates)
                        if distance * 10 < self.nearby['subdiv']:
                            self.graph.add_edge(sd1.identifier, sd2.identifier, weight=int(10 * distance / self.nearby['subdiv']))

        # Could use multicode's rtree?
        for subdiv in self.bank._bank[subdivision.SubDivision.code_type].values():
            for lcde1 in subdiv.get_children():
                for lcde2 in subdiv.get_children():
                    if lcde1 != lcde2 and lcde1.coordinates and lcde2.coordinates:
                        distance = lcde1.distance(*lcde2.coordinates)
                        if distance * 10 < self.nearby['locode']:
                            self.graph.add_edge(lcde1.identifier, lcde2.identifier, weight=int(10 * distance / self.nearby['locode']))

    def within(self, identifier, distance):
        #graph = nx.ego_graph(self.graph, identifier, radius=distance)
        return nx.single_source_shortest_path_length(self.graph, identifier, cutoff=distance)
