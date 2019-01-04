import pandas
import re
import json
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
        states = states.where(pandas.notnull(states), None)
        state_dict = {}
        for index, ste in states.iterrows():
            code = ste['ISO3166-1-Alpha-2']
            if not code:
                continue

            name = ste['official_name_en']
            if not name:
                name = ste['name']

            state_dict[code] = state.State(
                code,
                name=name,
                short=ste['name'],
                alpha2=ste['ISO3166-1-Alpha-2'],
                alpha3=ste['ISO3166-1-Alpha-3'],
                numeric=ste['ISO3166-1-numeric'],
                official_en=ste['official_name_en'],
                official_fr=ste['official_name_fr'],
                continent=ste['Continent'],
            )

        def state_service(ste):
            try:
                ste = state_dict[ste]
            except:
                ste = None
            return ste

        # FIXME subdiv_file
        subdivisions = pandas.read_csv(subdiv_file[0], dtype=str)
        subdivisions = subdivisions.where(pandas.notnull(subdivisions), None)
        subdiv_dict = {}
        for index, subdiv in subdivisions.iterrows():
            if subdiv['SUCountry'] not in state_dict or not subdiv['SUCountry'] or not subdiv['SUCode'] or not subdiv['SUName']:
                continue
            code = '{}:{}'.format(subdiv['SUCountry'], subdiv['SUCode'])
            subdiv_dict[code] = subdivision.SubDivision(
                state_service,
                code,
                name=subdiv['SUName'],
                supercode=subdiv['SUCountry'],
                subcode=subdiv['SUCode'],
                level='[UNKNOWN]'
            )

        with open(subdiv_file[1], 'r') as subdiv_fh:
            subdiv_content = subdiv_fh.read()

        subdiv_content = subdiv_content[subdiv_content.find('{'):]
        subdiv_content = subdiv_content[:(subdiv_content.rfind('}') + 1)]
        subdiv_content = re.sub(r'//.*', '', subdiv_content)
        subdiv_json = json.loads(subdiv_content)
        #subdivisions = pandas.read_csv(subdiv_file, dtype=str)
        #subdivisions = subdivisions.where(pandas.notnull(subdivisions), None)
        for subdiv_code, subdiv in subdiv_json.items():
            if '-' not in subdiv_code:
                continue
            code_pair = [s.strip() for s in subdiv_code.split('-')]
            if code_pair[0] not in state_dict or len(code_pair) != 2:
                continue
            supercode, subcode = code_pair
            code = '{}:{}'.format(supercode, subcode)
            if code in subdiv_dict:
                subdiv_dict[code].level = subdiv['division'].strip()
            #subdiv_dict[code] = subdivision.SubDivision(
            #    state_service,
            #    code,
            #    name=subdiv['name'].strip(),
            #    supercode=supercode,
            #    subcode=subcode,
            #    level=
            #)

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
        locode_dict_by_state = {}
        for index, lcde in locodes.iterrows():
            if not lcde['Country']: #RMV
                continue
            code = '{}:{}'.format(lcde['Country'], lcde['Location'])

            if not pandas.isnull(lcde['SubdivisionFaT']):
                subdivision_code = lcde['SubdivisionFaT']
            else:
                subdivision_code = None

            if lcde['Country'] not in locode_dict_by_state:
                locode_dict_by_state[lcde['Country']] = {}

            alternative_names = []
            for name in (lcde['NameWoDiacritics'], lcde['Name']):
                if '(' in name and ')' in name:
                    altname = re.search(r"\(([^)]*)\)", name).group(1)
                    name = re.sub(r"\([^)]*\)", '', lcde['NameWoDiacritics'])
                    if altname.startswith('ex '):
                        altname = altname[3:]
                    if altname not in alternative_names:
                        alternative_names.append(altname)
                if name not in alternative_names:
                    alternative_names.append(name)
            name = re.sub(r"\([^)]*\)", '', lcde['NameWoDiacritics']).strip()
            alternative_names = [n.strip() for n in alternative_names]

            def coord_to_decimal(coord, neg):
                coord = int(coord)
                degrees = int(coord / 100)
                minutes = (coord % 100)
                result = degrees + minutes / 60.
                if neg:
                    result *= -1
                return result

            if lcde['Coordinates']:
                x, y = lcde['Coordinates'].split(' ')
                x = coord_to_decimal(x[:-1], x[-1] == 'S')
                y = coord_to_decimal(y[:-1], y[-1] == 'W')
                coordinates = (x, y)
            else:
                coordinates = None

            locode_dict[code] = locode.Locode(
                iata_service,
                subdivision_service,
                code,
                name=name,
                supercode=lcde['Country'],
                subcode=lcde['Location'],
                subdivision_code=subdivision_code,
                function_code=lcde['Function'],
                iata_override=lcde['IATA'],
                coordinates=coordinates,
                alternative_names=alternative_names
            )
            locode_dict_by_state[lcde['Country']][code] = locode_dict[code]

        return state_dict, subdiv_dict, locode_dict, locode_dict_by_state
