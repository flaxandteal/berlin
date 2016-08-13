import pandas
from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode
from berlin import iata

class BackendDict:
    def __init__(self):
        pass

    def retrieve(self, data_sources):
        self._data_sources = data_sources
        iata_file = self._data_sources['iata_file']
        state_file = self._data_sources['state_file']
        subdiv_file = self._data_sources['subdiv_file']
        locode_file = self._data_sources['locode_file']

        iatas = pandas.read_csv(iata_file, dtype=str, header=None)
        iatas.columns = ('ix', 'name', 'city', 'country', 'iata', 'icao', 'y', 'x', 'elevation', 'timezone', 'dst', 'tz_id')
        iata_dict = {}
        for index, iat in iatas.iterrows():
            iata_dict[iat['iata']] = iata.Iata(
                iat['iata'],
                name=iat['name'],
                city=iat['city'],
                country=iat['country'],
                iata=iat['iata'],
                icao=iat['icao'],
                y=iat['y'],
                x=iat['x'],
                elevation=iat['elevation'],
                timezone=iat['timezone'],
                dst=iat['dst'],
                tz_id=iat['tz_id']
            )

        def iata_service(iat):
            try:
                iat = iata_dict[iat]
            except:
                iat = None
            return iat

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
        subdivisions = subdivisions.where(pandas.notnull(subdivisions), None)
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
        locodes = locodes.where(pandas.notnull(locodes), None)
        locode_dict = {}
        for index, lcde in locodes.iterrows():
            code = '{}:{}'.format(lcde['Country'], lcde['Location'])

            if not pandas.isnull(lcde['SubdivisionFaT']):
                subdivision_code = lcde['SubdivisionFaT']
            else:
                subdivision_code = None

            locode_dict[code] = locode.Locode(
                iata_service,
                subdivision_service,
                code,
                name=lcde['Name'],
                supercode=lcde['Country'],
                subcode=lcde['Location'],
                subdivision_code=subdivision_code,
                state=lcde['Country'],
                function_code=lcde['Function'],
                iata_override=lcde['IATA']
            )

        return state_dict, subdiv_dict, locode_dict
