from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode

class CommandHandler:
    def __init__(self, state_dict, subdiv_dict, locode_dict, printer):
        self.state_dict = state_dict
        self.subdiv_dict = subdiv_dict
        self.locode_dict = locode_dict
        self._printer = printer
        self._commands = {
            "CONSISTENCY": self.do_consistency,
            "QUERY": self.do_query,
            "Q": self.do_query,
        }

    def run(self, command, *args, **kwargs):
        self._commands[command](*args, **kwargs)

    def do_query(self, *args):
        if not args:
            self._printer("[MUST HAVE ARGUMENT]")

        name = ' '.join(args)

        parser = multicode.RegionParser(self.locode_dict)
        code, lcde = parser.analyse(name=name)

        if lcde:
            content = "BEST MATCH(%s):\n" % code
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
