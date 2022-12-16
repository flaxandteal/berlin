import pandas
import re
import json
import tqdm
from berlin import multicode
from berlin import state
from berlin import subdivision
from berlin import locode
from berlin import iata

class BackendDict:
    def __init__(self):
        pass

    def retrieve(self, data_sources, progress_bar=False):
        self._data_sources = data_sources
        iata_file = self._data_sources['iata_file']
        state_file = self._data_sources['state_file']
        subdiv_file = self._data_sources['subdiv_file']
        locode_file = self._data_sources['locode_file']

        code_services = {}
        code_service = lambda identifier, code_type: code_services[code_type](identifier)

        with open(subdiv_file[1], 'r') as subdiv_fh:
            subdiv_content = subdiv_fh.read()

        subdiv_content = subdiv_content[subdiv_content.find('{'):]
        subdiv_content = subdiv_content[:(subdiv_content.rfind('}') + 1)]
        subdiv_content = re.sub(r'//.*', '', subdiv_content)

        iatas = pandas.read_csv(iata_file, dtype=str, keep_default_na=False)

        states = pandas.read_csv(state_file, dtype=str, keep_default_na=False)
        states = states.where(pandas.notnull(states), None)

        subdivisions = pandas.read_csv(subdiv_file[0], dtype=str, keep_default_na=False)
        subdivisions = subdivisions.where(pandas.notnull(subdivisions), None)

        subdiv_json = json.loads(subdiv_content)

        locodes = pandas.read_csv(locode_file, dtype=str, keep_default_na=False)
        locodes = locodes.where(pandas.notnull(locodes), None)

        total_to_load = sum(map(len, (iatas, states, subdivisions, locodes, subdiv_json)))

        progress = range(total_to_load)
        if progress_bar:
            progress = tqdm.tqdm(progress)

        pit = iter(progress)

        iata_dict = {}
        if progress_bar:
            progress.set_description("Loading IATA codes...")
        for index, iat in iatas.iterrows():
            y, x = [float(v.strip()) for v in iat['coordinates'].split(',')]
            iata_dict[iat['iata_code']] = iata.Iata(
                iat['iata_code'],
                code_service=code_service,
                type=iat['type'],
                name=iat['name'],
                city=iat['municipality'],
                country=iat['iso_country'],
                region=iat['iso_region'],
                iata=iat['iata_code'],
                y=y,
                x=x,
                elevation=iat['elevation_ft']
            )
            next(pit)

        def iata_service(iat):
            try:
                iat = iata_dict[iat]
            except:
                iat = None
            return iat
        code_services[iata.Iata.code_type] = iata_service

        state_dict = {}
        if progress_bar:
            progress.set_description("Loading ISO3166 states...")
        for index, ste in states.iterrows():
            next(pit)
            code = ste['ISO3166-1-Alpha-2']
            if not code:
                continue

            name = ste['official_name_en']
            if not name:
                name = ste['CLDR display name']

            state_dict[code] = state.State(
                code,
                code_service=code_service,
                name=name,
                short=ste['CLDR display name'],
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
        code_services[state.State.code_type] = state_service

        # FIXME subdiv_file
        subdiv_dict = {}
        if progress_bar:
            progress.set_description("Loading subdivisions...")
        for index, subdiv in subdivisions.iterrows():
            next(pit)
            if subdiv['SUCountry'] not in state_dict or not subdiv['SUCountry'] or not subdiv['SUCode'] or not subdiv['SUName']:
                continue
            code = '{}:{}'.format(subdiv['SUCountry'], subdiv['SUCode'])
            code = code.replace('›', '')
            subdiv_dict[code] = subdivision.SubDivision(
                code,
                code_service=code_service,
                name=subdiv['SUName'],
                supercode=subdiv['SUCountry'],
                subcode=subdiv['SUCode'],
                level='[UNKNOWN]'
            )

            ste = subdiv_dict[code].get_state()
            if ste:
                ste.add_child(subdiv_dict[code])


        #subdivisions = pandas.read_csv(subdiv_file, dtype=str)
        #subdivisions = subdivisions.where(pandas.notnull(subdivisions), None)
        if progress_bar:
            progress.set_description("Loading subdivision detail...")
        for subdiv_code, subdiv in subdiv_json.items():
            next(pit)
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

        def subdivision_service(subdiv):
            if ':' in subdiv:
                try:
                    unit = subdiv_dict[subdiv]
                except:
                    unit = None
            else:
                unit = state_service(subdiv)

            return unit
        code_services[subdivision.SubDivision.code_type] = subdivision_service

        locode_dict = {}
        locode_dict_by_state = {}
        if progress_bar:
            progress.set_description("Loading LOCODEs...")
        for index, lcde in locodes.iterrows():
            next(pit)
            if not lcde['Country']: #RMV
                continue
            code = '{}:{}'.format(lcde['Country'], lcde['Location'])

            if not pandas.isnull(lcde['Subdivision']):
                subdivision_code = lcde['Subdivision']
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
                code,
                code_service=code_service,
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

            subdiv = locode_dict[code].get_subdivision()
            if subdiv:
                subdiv.add_child(locode_dict[code])

        return state_dict, subdiv_dict, locode_dict, locode_dict_by_state, iata_dict
