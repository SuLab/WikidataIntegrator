import PBB_Core
import pprint
import copy

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

    def __init__(self, base_filter=None):
        self.prop_data = {}
        self.loaded_langs = {}
        self.statements = []
        self.base_filter = {}
        self.base_filter_string = ''
        self.prop_dt_map = {}
        self.current_qid = ''

        if base_filter and any(base_filter):
            self.base_filter = base_filter

            for i in self.base_filter:
                if self.base_filter[i]:
                    self.base_filter_string += '?p p:{0}/ps:{0} wd:{1} . \n'.format(i, self.base_filter[i])
                else:
                    self.base_filter_string += '?p p:{0}/ps:{0} ?zz . \n'.format(i)

        # self.write_required = self.check_data(data=self.data)
        # print(self.write_required)

    def check_data(self, data):
        write_required = False
        match_sets = []
        for date in data:
            prop_nr = date.get_prop_nr()

            if prop_nr not in self.prop_dt_map:
                self.prop_dt_map.update({prop_nr: FastRunContainer.get_prop_datatype(prop_nr=prop_nr)})

            if prop_nr not in self.prop_data:
                self.prop_data.update({prop_nr: self.__query_data(prop_nr=prop_nr)['results']['bindings']})

            current_value = date.get_value()

            # more sophisticated data types like dates and globe coordinates need special treatment here
            if self.prop_data[prop_nr] == 'time':
                current_value = current_value[0]
            elif self.prop_data[prop_nr] == 'globe-coordinate':
                write_required = True  # temporary workaround for handling globe coordinates

            temp_set = set()
            for value in self.prop_data[prop_nr]:
                sresult_value = ''
                if value['v']['type'] == 'literal':
                    sresult_value = value['v']['value']
                elif value['v']['type'] == 'uri':
                    sresult_value = value['v']['value'].split('/')[-1]

                current_qid = value['p']['value'].split('/')[-1]
                if current_value == sresult_value:
                    temp_set.add(current_qid)

            match_sets.append(temp_set)

        matching_qids = match_sets[0].intersection(*match_sets[1:])

        if not matching_qids or len(matching_qids) > 2:
            return True

        qid = matching_qids.pop()
        self.current_qid = qid
        reconstructed_statements = []
        all_qid_results = []
        all_prop_nrs = []
        all_stat_uids = set()
        for prop_nr, prop_data in self.prop_data.items():
            for sresult in prop_data:
                current_qid = sresult['p']['value'].split('/')[-1]
                current_stat_uid = sresult['s2']['value']
                if current_qid == qid:
                    all_qid_results.append(sresult)
                    all_prop_nrs.append(prop_nr)
                    all_stat_uids.add(current_stat_uid)

        for uid in all_stat_uids:
            current_prop_nr = ''
            current_value = ''
            qualifiers = []
            for count, prop_nr in enumerate(all_prop_nrs):
                if all_qid_results[count]['s2']['value'] == uid:
                    current_prop_nr = prop_nr
                    if all_qid_results[count]['v']['type'] == 'literal':
                        current_value = all_qid_results[count]['v']['value']
                    elif all_qid_results[count]['v']['type'] == 'uri':
                        current_value = all_qid_results[count]['v']['value'].split('/')[-1]

                    if 'pr' in all_qid_results[count]:
                        q_prop = all_qid_results[count]['pr']['value'].split('/')[-1]
                        q_value = all_qid_results[count]['q']['value'].split('/')[-1]
                        q_datatype = self.prop_dt_map[q_prop]

                        wd_dtype = [x for x in PBB_Core.WDBaseDataType.__subclasses__() if x.DTYPE == q_datatype][0]
                        qualifiers.append(wd_dtype(value=q_value, prop_nr=q_prop, is_qualifier=True))

            v_datatype = self.prop_dt_map[current_prop_nr]
            wd_dtype = [x for x in PBB_Core.WDBaseDataType.__subclasses__() if x.DTYPE == v_datatype][0]
            statement = wd_dtype(value=current_value, prop_nr=current_prop_nr, qualifiers=qualifiers)
            reconstructed_statements.append(statement)

        tmp_rs = copy.deepcopy(reconstructed_statements)
        for date in data:
            bool_vec = [True if date == x else False for x in tmp_rs]
            if not any(bool_vec):
                write_required = True
            else:
                tmp_rs.pop(bool_vec.index(True))

        if len(tmp_rs) > 0:
            write_required = True

        return write_required

    def check_language_data(self, qid, lang_data, lang, lang_data_type):
        """
        Method to check if certain language data exists as a label, description or aliases
        :param lang: a list of language specific values
        :type lang: str
        :param lang_data_type: What kind of data is it? 'label', 'description' or 'aliases'?
        :return:
        """
        if lang not in self.loaded_langs:
            self.loaded_langs[lang] = {}

        if lang_data_type not in self.loaded_langs[lang]:
            self.loaded_langs[lang].update({lang_data_type: self.__query_lang(lang=lang,
                                                                              lang_data_type=lang_data_type)})

        current_lang_data = self.loaded_langs[lang][lang_data_type]['results']['bindings']
        all_lang_strings = []
        for sresult in current_lang_data:
            if sresult['p']['value'].split('/')[-1] == qid:
                all_lang_strings.append(sresult['label']['value'])

        for s in lang_data:
            if s not in all_lang_strings:
                return True

        return False

    def get_all_data(self):
        return self.prop_data

    def __query_data(self, prop_nr):
        query = '''
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

        print(query)

        return PBB_Core.WDItemEngine.execute_sparql_query(query=query, prefix=prefix)

    def __query_lang(self, lang, lang_data_type):
        """

        :param lang:
        :param lang_data_type:
        :return:
        """

        lang_data_type_dict = {
            'label': 'rdfs:label',
            'description': 'rdfs:description',
            'aliases': 'skos:altLabel'
        }

        query = '''
        SELECT ?p ?label WHERE {{
            {0}

            OPTIONAL {{
                ?p {1} ?label FILTER (lang(?label) = "{2}") .
            }}
        }}
        '''.format(self.base_filter_string, lang_data_type_dict[lang_data_type], lang)
        print(query)

        return PBB_Core.WDItemEngine.execute_sparql_query(query=query, prefix=prefix)

    @staticmethod
    def get_prop_datatype(prop_nr):
        item = PBB_Core.WDItemEngine(wd_item_id=prop_nr)
        return item.entity_metadata['datatype']
