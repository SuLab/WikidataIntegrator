import copy

# from wikidataintegrator.wdi_core import *

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'

prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    PREFIX skos:<http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''


class FastRunContainer(object):
    def __init__(self, base_data_type, engine, base_filter=None):
        self.prop_data = {}
        self.loaded_langs = {}
        self.statements = []
        self.base_filter = {}
        self.base_filter_string = ''
        self.prop_dt_map = {}
        self.current_qid = ''
        self.rev_lookup = {}
        self.base_data_type = base_data_type
        self.engine = engine

        if base_filter and any(base_filter):
            self.base_filter = base_filter

            for k, v in self.base_filter.items():
                if v:
                    self.base_filter_string += '?p p:{0}/ps:{0} wd:{1} . \n'.format(k, v)
                else:
                    self.base_filter_string += '?p p:{0}/ps:{0} ?zz . \n'.format(k)

    def check_data(self, data, append_props=None, cqid=None):
        del_props = set()
        data_props = set()
        if not append_props:
            append_props = []

        for x in data:
            if x.value and x.data_type:
                data_props.add(x.get_prop_nr())
        write_required = False
        match_sets = []
        for date in data:
            # skip to next if statement has no value or no data type defined, e.g. for deletion objects
            current_value = date.get_value()
            if not current_value and not date.data_type:
                del_props.add(date.get_prop_nr())
                continue

            prop_nr = date.get_prop_nr()

            if prop_nr not in self.prop_dt_map:
                self.prop_dt_map.update({prop_nr: FastRunContainer.get_prop_datatype(prop_nr=prop_nr,
                                                                                     engine=self.engine)})
                self.__query_data(prop_nr=prop_nr)

            # more sophisticated data types like dates and globe coordinates need special treatment here
            if self.prop_dt_map[prop_nr] == 'time':
                current_value = current_value[0]
            elif self.prop_dt_map[prop_nr] == 'wikibase-item':
                current_value = 'Q{}'.format(current_value)
            elif self.prop_dt_map[prop_nr] == 'globe-coordinate':
                write_required = True  # temporary workaround for handling globe coordinates

            if not __debug__:
                print(current_value)
            try:
                if not __debug__:
                    print(current_value)
                temp_set = set(self.rev_lookup[current_value])
            except KeyError:
                if not __debug__:
                    print('no matches for rev lookup')
                return True

            match_sets.append(temp_set)

        if cqid:
            matching_qids = {cqid}
        else:
            matching_qids = match_sets[0].intersection(*match_sets[1:])

        if not len(matching_qids) == 1:
            if not __debug__:
                print('no matches')
            return True

        qid = matching_qids.pop()
        self.current_qid = qid
        reconstructed_statements = []

        for prop_nr, dt in self.prop_data[qid].items():
            all_uids = set([x['s2'] for x in dt])
            q_props = set([x['pr'] for x in dt if 'pr' in x])
            for q_prop in q_props:
                if q_prop not in self.prop_dt_map:
                    self.prop_dt_map.update({q_prop: FastRunContainer.get_prop_datatype(prop_nr=q_prop,
                                                                                        engine=self.engine)})
            for uid in all_uids:
                qualifiers = [[x for x in self.base_data_type.__subclasses__() if x.DTYPE ==
                               self.prop_dt_map[y['pr']]][0](value=y['q'], prop_nr=y['pr'], is_qualifier=True)
                              for y in dt if y['s2'] == uid and 'q' in y]

                stmts = [[x for x in self.base_data_type.__subclasses__() if x.DTYPE ==
                          self.prop_dt_map[prop_nr]][0](value=y['v'], prop_nr=prop_nr, qualifiers=qualifiers)
                         for y in dt if y['s2'] == uid][0]

                reconstructed_statements.append(stmts)

        tmp_rs = copy.deepcopy(reconstructed_statements)

        # handle append properties
        for p in append_props:
            app_data = [x for x in data if x.get_prop_nr() == p]
            rec_app_data = [x for x in tmp_rs if x.get_prop_nr() == p]
            comp = [True for x in app_data for y in rec_app_data if x == y]
            if len(comp) != len(app_data):
                return True

        tmp_rs = [x for x in tmp_rs if x.get_prop_nr() not in append_props and x.get_prop_nr() in data_props]

        for date in data:
            # ensure that statements meant for deletion get handled properly
            reconst_props = set([x.get_prop_nr() for x in tmp_rs])
            if (not date.value or not date.data_type) and date.get_prop_nr() in reconst_props:
                if not __debug__:
                    print('returned from delete prop handling')
                return True
            elif not date.value or not date.data_type:
                # Ignore the deletion statements which are not in the reconstituted statements.
                continue

            if date.get_prop_nr() in append_props:
                continue
            bool_vec = [True if date == x and x.get_prop_nr() not in del_props else False for x in tmp_rs]

            if not __debug__:
                bool_vec = []

                print('-----------------------------------')
                for x in tmp_rs:

                    if date == x and x.get_prop_nr() not in del_props:
                        bool_vec.append(True)
                        print(x.get_prop_nr(), x.get_value(), [z.get_value() for z in x.get_qualifiers()])
                        print(date.get_prop_nr(), date.get_value(), [z.get_value() for z in date.get_qualifiers()])
                    else:
                        if x.get_prop_nr() == date.get_prop_nr():
                            print(x.get_prop_nr(), x.get_value(), [z.get_value() for z in x.get_qualifiers()])
                            print(date.get_prop_nr(), date.get_value(), [z.get_value() for z in date.get_qualifiers()])
                        bool_vec.append(False)

            if not any(bool_vec):
                if not __debug__:
                    print(len(bool_vec))
                    print('fast run failed at ', date.get_prop_nr())
                write_required = True
            else:
                tmp_rs.pop(bool_vec.index(True))

        if len(tmp_rs) > 0:
            if not __debug__:
                print('failed because not zero')
                for x in tmp_rs:
                    print('xxx', x.get_prop_nr(), x.get_value(), [z.get_value() for z in x.get_qualifiers()])
                print('failed because not zero--END')
            write_required = True

        return write_required

    def init_language_data(self, lang, lang_data_type):
        """
        Initialize language data store
        :param lang: language code
        :param lang_data_type: 'label', 'description' or 'aliases'
        :return: None
        """
        if lang not in self.loaded_langs:
            self.loaded_langs[lang] = {}

        if lang_data_type not in self.loaded_langs[lang]:
            self.loaded_langs[lang].update({lang_data_type: self.__query_lang(lang=lang,
                                                                              lang_data_type=lang_data_type)})

    def get_language_data(self, qid, lang, lang_data_type):
        """
        get language data for specified qid
        :param qid:
        :param lang: language code
        :param lang_data_type: 'label', 'description' or 'aliases'
        :return: list of strings
        """
        self.init_language_data(lang, lang_data_type)

        current_lang_data = self.loaded_langs[lang][lang_data_type]['results']['bindings']
        all_lang_strings = []
        for sresult in current_lang_data:
            if sresult['p']['value'].split('/')[-1] == qid:
                if 'label' in sresult:
                    all_lang_strings.append(sresult['label']['value'])
        if not all_lang_strings and lang_data_type in {'label', 'description'}:
            all_lang_strings = ['']
        return all_lang_strings

    def check_language_data(self, qid, lang_data, lang, lang_data_type):
        """
        Method to check if certain language data exists as a label, description or aliases
        :param lang_data: list of string values to check
        :type lang_data: list
        :param lang: language code
        :type lang: str
        :param lang_data_type: What kind of data is it? 'label', 'description' or 'aliases'?
        :return:
        """
        all_lang_strings = self.get_language_data(qid, lang, lang_data_type)

        for s in lang_data:
            if s not in all_lang_strings:
                print('fastrun failed at label: ', lang_data_type)
                return True

        return False

    def get_all_data(self):
        return self.prop_data

    def __query_data(self, prop_nr):
        query = '''
            #Tool: wdi_core fastrun
            select ?p ?q ?pr ?s2 ?v where {{
              {0}

              ?p p:{1} ?s2 .

              ?s2 ps:{1} ?v .
              OPTIONAL {{
                ?s2 ?pr ?q .
                FILTER(STRSTARTS(STR(?pr), "http://www.wikidata.org/prop/qualifier/"))
              }}

            }}
        '''.format(self.base_filter_string, prop_nr)

        # query for amount
        '''
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT ?p ?q ?pr ?s2 ?v ?psv ?amount ?upper_bound ?lower_bound ?unit WHERE {
            ?p p:P31/ps:P31 wd:Q11173 .

            ?p p:P2067 ?s2 .

            ?s2 ps:P2067 ?v .
            ?s2 <http://www.wikidata.org/prop/statement/value/P2067> ?psv .
            ?psv wikibase:quantityAmount ?amount .
            ?psv wikibase:quantityUpperBound ?upper_bound .
            ?psv wikibase:quantityLowerBound ?lower_bound .
            ?psv wikibase:quantityUnit ?unit .

            OPTIONAL {
                ?s2 ?pr ?q .
                FILTER(STRSTARTS(STR(?pr), "http://www.wikidata.org/prop/qualifier/"))
              }

            }
        '''

        # query for globe coordinate
        '''
        PREFIX wikibase: <http://wikiba.se/ontology#>
        SELECT ?p ?q ?pr ?s2 ?v ?psv ?geoLatitude ?geoLongitude ?geoGlobe ?geoPrecision WHERE {
            ?p p:P30/ps:P30 wd:Q46 .

            ?p p:P625 ?s2 .

            ?s2 ps:P625 ?v .
            ?s2 <http://www.wikidata.org/prop/statement/value/P625> ?psv .
            ?psv wikibase:geoLatitude ?geoLatitude .
            ?psv wikibase:geoLongitude ?geoLongitude .
            ?psv wikibase:geoGlobe ?geoGlobe .
            ?psv wikibase:geoPrecision ?geoPrecision .
            OPTIONAL {
                ?s2 ?pr ?q .
                FILTER(STRSTARTS(STR(?pr), "http://www.wikidata.org/prop/qualifier/"))
              }

            }
        '''

        if not __debug__:
            print(query)

        r = self.engine.execute_sparql_query(query=query, prefix=prefix)

        for i in r['results']['bindings']:
            i['p'] = i['p']['value'].split('/')[-1]
            if 's2' in i:
                i['s2'] = i['s2']['value'].split('/')[-1]
            if 'q' in i:
                i['q'] = i['q']['value'].split('/')[-1]
            if 'pr' in i:
                i['pr'] = i['pr']['value'].split('/')[-1]

            if 'v' in i:
                if i['v']['type'] == 'literal':
                    i['v'] = i['v']['value']
                elif i['v']['type'] == 'uri':
                    if 'www.wikidata.org/entity/' in i['v']['value']:
                        i['v'] = i['v']['value'].split('/')[-1]
                    else:
                        i['v'] = i['v']['value']

                # TODO: needs check for no-value and some-value sparql results return
                # for some-value, this json is being returned {'value': 't329541227', 'type': 'bnode'}
                if type(i['v']) is not dict and i['v'] in self.rev_lookup:
                    self.rev_lookup[i['v']].append(i['p'])
                else:
                    self.rev_lookup[i['v']] = [i['p']]

        if not __debug__:
            print('Length of reverse lookup table:', len(self.rev_lookup))

        for i in r['results']['bindings']:
            qid = i['p']
            if qid not in self.prop_data:
                self.prop_data[qid] = {prop_nr: []}
            if prop_nr not in self.prop_data[qid]:
                self.prop_data[qid].update({prop_nr: []})

            t = copy.deepcopy(i)
            del t['p']
            self.prop_data[qid][prop_nr].append(t)

        del r

    def __query_lang(self, lang, lang_data_type):
        """

        :param lang:
        :param lang_data_type:
        :return:
        """

        lang_data_type_dict = {
            'label': 'rdfs:label',
            'description': 'schema:description',
            'aliases': 'skos:altLabel'
        }

        query = '''
        #Tool: wdi_core fastrun
        SELECT ?p ?label WHERE {{
            {0}

            OPTIONAL {{
                ?p {1} ?label FILTER (lang(?label) = "{2}") .
            }}
        }}
        '''.format(self.base_filter_string, lang_data_type_dict[lang_data_type], lang)

        if not __debug__:
            print(query)

        return self.engine.execute_sparql_query(query=query, prefix=prefix)

    @staticmethod
    def get_prop_datatype(prop_nr, engine):
        item = engine(wd_item_id=prop_nr)
        return item.entity_metadata['datatype']
