from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode
from berlin import network

class CommandHandler:
    net = None

    def __init__(self, code_bank, printer=print):
        self.code_bank = code_bank
        self._printer = printer
        self._commands = {
            "CONSISTENCY": self.do_consistency,
            "C": self.do_consistency,

            "NETWORK": self.do_network,
            "N": self.do_network,

            "QUERYST": self.do_query_by_state,
            "QS": self.do_query_by_state,

            "QUERY": self.do_query,
            "Q": self.do_query,

            "LQUERY": self.do_locode_query,
            "R": self.do_locode_query,

            "SDQUERY": self.do_subdivision_query,
            "T": self.do_subdivision_query,

            "STQUERY": self.do_state_query,
            "U": self.do_state_query,

            "LOCODE": self.do_locode,
            "L": self.do_locode,

            "SUBDIVISION": self.do_subdivision,
            "B": self.do_subdivision,

            "STATE": self.do_state,
            "S": self.do_state,

            "MATCH": self.do_match,
            "M": self.do_match,

            "HELP": self.do_help,
            "?": self.do_help,

            "POINT": self.do_point,
            "P": self.do_point,

            "SDPOINT": lambda x, y, box_radius=None: self.do_point(x, y, box_radius, True),
            "O": lambda x, y, box_radius=None: self.do_point(x, y, box_radius, True),

            "DISTANCE": self.do_distance,
            "D": self.do_distance
        }

    def run(self, command, *args, **kwargs):
        return self._commands[command](*args, **kwargs)

    def do_help(self, *args, **kwargs):
        if args and args[0] in self._commands:
            comm = args[0]
            doc = self._commands[comm].__doc__
            self._printer("%s\n%s" % (comm, doc))
            byfunc = {comm: doc}
        else:
            byfunc = {}
            for name, func in self._commands.items():
                if func.__name__ not in byfunc:
                    byfunc[func.__name__] = []
                byfunc[func.__name__].append(name)
            self._printer("\n".join([" ".join(l) for l in sorted(byfunc.values(), key=len)]))

        return byfunc

    def set_code_bank(self, code_bank):
        self.code_bank = code_bank

    def do_network(self, code, max_weight):
        net = self.net
        if not net:
            net = network.LocodeNetwork(self.code_bank)
            net.build()
            self.net = net

        result = net.within(code, float(max_weight))
        self._printer(str(result))

    def do_query_by_state(self, ste, *args, **kwargs):
        parser = self.code_bank.get_parser(locode.Locode.code_type, state=ste, distances=False)
        return self._query_runner(parser, *args, **kwargs)

    def do_query(self, *args, **kwargs):
        parser = self.code_bank.get_parser(distances=False)
        return self._query_runner(parser, *args, **kwargs)

    def do_locode_query(self, *args, **kwargs):
        parser = self.code_bank.get_parser(locode.Locode.code_type, distances=False)
        return self._query_runner(parser, *args, **kwargs)

    def do_state_query(self, *args, **kwargs):
        parser = self.code_bank.get_parser(state.State.code_type, distances=False)
        return self._query_runner(parser, *args, **kwargs)

    def do_subdivision_query(self, *args, **kwargs):
        parser = self.code_bank.get_parser(subdivision.SubDivision.code_type, distances=False)
        return self._query_runner(parser, *args, **kwargs)

    def do_distance(self, code, x, y=None):
        lcde1 = self.code_bank.get(code, locode.Locode.code_type)
        if y:
            distance = lcde1.distance(float(x), float(y))
        else:
            lcde2 = self.code_bank.get(x, locode.Locode.code_type)
            if lcde2.coordinates:
                distance = lcde1.distance(*lcde2.coordinates)
            else:
                distance = None

        if distance is not None:
            self._printer("%.4lf (in deg)" % distance)
        else:
            self._printer("[COULD NOT CALCULATE]")

        return distance

    def do_point(self, x, y, box_radius=None, subdivisions=False):
        # 111 being about the ratio of Earth degrees to kilometers
        if subdivisions:
            parser = self.code_bank.get_parser(subdivision.SubDivision.code_type)
        else:
            parser = self.code_bank.get_parser(locode.Locode.code_type)

        nearest_only = not bool(box_radius)
        results = parser.search(float(x), float(y), float(box_radius) / 111. if box_radius else None, nearest_only)

        if nearest_only:
            results = [results]

        lcde = None
        for result in results:
            lcde, distance = result

            if lcde:
                self._printer("DISTANCE (deg): %.4lf" % distance)
                self._printer(lcde.paragraph())

        if not lcde:
            self._printer("[NO NEARBY LOCODE]")

        return lcde

    def _parse_to_components(self, args):
        components = {'name': []}
        this_component = 'name'
        for arg in args:
            if arg and arg[0] == '[' and arg[-1] == ']':
                this_component = arg[1:-1]
                components[this_component] = []
            else:
                components[this_component].append(arg)

        return {k: ' '.join(v) for k, v in components.items()}

    def _query_runner(self, parser, *args, **kwargs):
        if not args:
            self._printer("[MUST HAVE ARGUMENT]")

        try:
            matches = int(args[0])
            args = args[1:]
        except ValueError:
            matches = 1

        components = self._parse_to_components(args)
        self._printer(components)
        lcdes = parser.analyse(matches=matches, **components)

        if matches == 1:
            lcdes = [lcdes]

        for code, lcde, score, log_steps in lcdes:
            if lcde:
                content = "MATCH(%s:%.3lf):\n" % (code, score)
                content += "\n".join([':'.join(map(str, lg)) for lg in log_steps])
                content += "\n"
                subcontent = lcde.paragraph()
                content += "\n".join(["    %s" % s for s in subcontent.split('\n')])
                self._printer(content)
            else:
                self._printer("[NO MATCH]")

        return lcdes

    def do_consistency(self):
        missing = {}
        for lcde in self.code_bank.get_values(locode.Locode.code_type):
            if lcde._subdiv is None and lcde.subdivision_code is not None:
                ste = lcde.supercode
                if ste not in missing:
                    missing[ste] = {}
                subdiv = lcde.subdivision_code
                if subdiv not in missing[ste]:
                    missing[ste][subdiv] = []
                missing[ste][subdiv].append(lcde)

        if missing:
            self._printer("INCONSISTENCIES - The following subdivisions could not be matched")
        else:
            self._printer("CONSISTENT")

        for ste, msg in missing.items():
            ste = self.code_bank.get(ste, state.State.code_type)
            self._printer("%s: %s" % (ste.name, ', '.join(['%s (%s)' % (k, ', '.join([w.name for w in v])) for k, v in msg.items()])))

        return missing

    def do_match(self, code, *args):
        code_type = None
        if code == '[ST]':
            code_type = state.State.code_type
            code = args[0]
            args = args[1:]

        lcde = self.code_bank.sget(code, code_type)
        if not lcde:
            self._printer("[NOT FOUND]")
            score, log_steps = (None, None)
        else:
            components = self._parse_to_components(args)
            parser = self.code_bank.get_parser(code_type, distances=False)
            self._printer(components)
            score, log_steps = parser.match(lcde, **components)
            content = "MATCH(%s:%.3lf):\n" % (code, score)
            content += "\n".join([':'.join(map(str, lg)) for lg in log_steps])
            self._printer(content)

        return lcde, score, log_steps

    def do_locode(self, code):
        lcde = self.code_bank.sget(code, locode.Locode.code_type)
        if not lcde:
            self._printer("[NOT FOUND]")
        else:
            self._printer(lcde.paragraph())

        return lcde

    def do_subdivision(self, code, children=False):
        subdiv = self.code_bank.sget(code, subdivision.SubDivision.code_type)
        if not subdiv:
            self._printer("[NOT FOUND]")
        else:
            self._printer(subdiv.paragraph())

            if children:
                self._printer("\n\n[CHILDREN]\n")
                for child in subdiv.get_children():
                    self._printer(child.describe())

        return subdiv

    def do_state(self, code):
        ste = self.code_bank.sget(code, state.State.code_type)
        if not ste:
            self._printer("[NOT FOUND]")
        else:
            self._printer(ste.paragraph())

        return ste
