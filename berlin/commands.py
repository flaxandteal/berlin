from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode

class CommandHandler:
    def __init__(self, state_dict, subdiv_dict, locode_dict, locode_dict_by_state, printer=print):
        self.state_dict = state_dict
        self.subdiv_dict = subdiv_dict
        self.locode_dict = locode_dict
        self._locode_parser = multicode.RegionParser(locode_dict)
        self.locode_dict_by_state = locode_dict_by_state
        self.combined_dict = subdiv_dict.copy()
        self.combined_dict.update(locode_dict)
        self._printer = printer
        self._commands = {
            "CONSISTENCY": self.do_consistency,
            "C": self.do_consistency,

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

            "DISTANCE": self.do_distance,
            "D": self.do_distance
        }

    def run(self, command, *args, **kwargs):
        self._commands[command](*args, **kwargs)

    def do_help(self, *args, **kwargs):
        if args and args[0] in self._commands:
            comm = args[0]
            self._printer("%s\n%s" % (comm, self._commands[comm].__doc__))
        else:
            byfunc = {}
            for name, func in self._commands.items():
                if func.__name__ not in byfunc:
                    byfunc[func.__name__] = []
                byfunc[func.__name__].append(name)
            self._printer("\n".join([" ".join(l) for l in sorted(byfunc.values(), key=len)]))

    def do_query_by_state(self, ste, *args, **kwargs):
        parser = multicode.RegionParser(self.locode_dict_by_state[ste], distances=False)
        self._query_runner(parser, *args, **kwargs)

    def do_query(self, *args, **kwargs):
        parser = multicode.RegionParser(self.combined_dict, distances=False)
        self._query_runner(parser, *args, **kwargs)

    def do_locode_query(self, *args, **kwargs):
        self._query_runner(self._locode_parser, *args, **kwargs)

    def do_state_query(self, *args, **kwargs):
        parser = multicode.RegionParser(self.state_dict, distances=False)
        self._query_runner(parser, *args, **kwargs)

    def do_subdivision_query(self, *args, **kwargs):
        parser = multicode.RegionParser(self.subdiv_dict, distances=False)
        self._query_runner(parser, *args, **kwargs)

    def do_distance(self, code, x, y=None):
        lcde1 = self.locode_dict[code]
        if y:
            distance = lcde1.distance(float(x), float(y))
        else:
            lcde2 = self.locode_dict[x]
            if lcde2.coordinates:
                distance = lcde1.distance(*lcde2.coordinates)
            else:
                distance = None

        if distance is not None:
            self._printer("%.4lf (in deg)" % distance)
        else:
            self._printer("[COULD NOT CALCULATE]")

    def do_point(self, x, y, box_radius=None):
        # 111 being about the ratio of Earth degrees to kilometers
        lcde, distance = self._locode_parser.search(float(x), float(y), box_radius / 111., bool(box_radius))
        if lcde:
            self._printer("DISTANCE (deg): %.4lf" % distance)
            self._printer(lcde.paragraph())
        else:
            self._printer("[NO NEARBY LOCODE]")

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

    def do_consistency(self):
        missing = {}
        for lcde in self.locode_dict.values():
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
            ste = self.state_dict[ste]
            self._printer("%s: %s" % (ste.name, ', '.join(['%s (%s)' % (k, ', '.join([w.name for w in v])) for k, v in msg.items()])))

    def do_match(self, code, *args):
        if code == '[ST]':
            dictionary = self.state_dict
            code = args[0]
            args = args[1:]
        else:
            dictionary = self.combined_dict

        if code not in dictionary:
            self._printer("[NOT FOUND]")
        else:
            lcde = dictionary[code]
            components = self._parse_to_components(args)
            parser = multicode.RegionParser(dictionary, distances=False)
            self._printer(components)
            score, log_steps = parser.match(lcde, **components)
            content = "MATCH(%s:%.3lf):\n" % (code, score)
            content += "\n".join([':'.join(map(str, lg)) for lg in log_steps])
            self._printer(content)

    def do_locode(self, code):
        if code not in self.locode_dict:
            self._printer("[NOT FOUND]")
        else:
            lcde = self.locode_dict[code]
            self._printer(lcde.paragraph())

    def do_subdivision(self, code):
        if code not in self.subdiv_dict:
            self._printer("[NOT FOUND]")
        else:
            subdiv = self.subdiv_dict[code]
            self._printer(subdiv.paragraph())

    def do_state(self, code):
        if code not in self.state_dict:
            self._printer("[NOT FOUND]")
        else:
            ste = self.state_dict[code]
            self._printer(ste.paragraph())
