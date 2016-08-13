import pandas
from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode

class BackendDict:
    def __init__(self):
        pass

    def retrieve(self, data_sources):
        self._data_sources = data_sources
        state_file = self._data_sources['state_file']
        subdiv_file = self._data_sources['subdiv_file']
        locode_file = self._data_sources['locode_file']

        states = pandas.read_csv(state_file, dtype=str)
        state_dict = {}
        for index, ste in states.iterrows():
            code = ste['CountryCode']
            state_dict[code] = state.State(
                code,
                name=ste['CountryName'],
                alpha2=ste['CountryCode']
            )

        def state_service(ste):
            try:
                ste = state_dict[ste]
            except:
                ste = None
            return ste

        subdivisions = pandas.read_csv(subdiv_file, dtype=str)
        subdiv_dict = {}
        for index, subdiv in subdivisions.iterrows():
            code = '{}:{}'.format(subdiv['SUCountry'], subdiv['SUCode'])
            subdiv_dict[code] = subdivision.SubDivision(
                state_service,
                code,
                name=subdiv['SUName'],
                supercode=subdiv['SUCountry'],
                subcode=subdiv['SUCode'],
                level='[UNKNOWN]'
            )

        def subdivision_service(ste, subdiv):
            if subdiv:
                try:
                    unit = subdiv_dict['{}:{}'.format(ste, subdiv)]
                except:
                    unit = None
            else:
                unit = state_service(ste)

            return unit

        locodes = pandas.read_csv(locode_file, dtype=str)
        locode_dict = {}
        for index, lcde in locodes.iterrows():
            code = '{}:{}'.format(lcde['Country'], lcde['Location'])

            if not pandas.isnull(lcde['SubdivisionFaT']):
                subdivision_code = lcde['SubdivisionFaT']
            else:
                subdivision_code = None

            locode_dict[code] = locode.Locode(
                subdivision_service,
                code,
                name=lcde['Name'],
                supercode=lcde['Country'],
                subcode=lcde['Location'],
                subdivision_code=subdivision_code,
                state=lcde['Country']
            )

        return state_dict, subdiv_dict, locode_dict
