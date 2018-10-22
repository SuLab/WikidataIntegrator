from collections import defaultdict

from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_helpers import id_mapper


class WikibaseHelper:
    """
    Helper functions for accessing PIDs and QIDs across wikibases

    This functionality depends upon their existing two properties: equivalent property and equivalent class
    with the equivalent property values: 'http://www.w3.org/2002/07/owl#equivalentProperty' and
    'http://www.w3.org/2002/07/owl#equivalentClass' respectively
    """

    def __init__(self, sparql_endpoint_url='https://query.wikidata.org/sparql'):
        self.sparql_endpoint_url = sparql_endpoint_url
        # a map of property URIs to a PID in the wikibase you are using
        try:
            equiv_prop_pid = self.guess_equivalent_property_pid()
        except Exception:
            raise ValueError("Error: No property found with URI 'http://www.w3.org/2002/07/owl#equivalentProperty'")
        uri_pid = id_mapper(equiv_prop_pid, endpoint=self.sparql_endpoint_url, return_as_set=True)
        # remove duplicates/conflicts
        self.URI_PID = {k: list(v)[0] for k, v in uri_pid.items() if len(v) == 1}
        # get equivalent class PID
        if 'http://www.w3.org/2002/07/owl#equivalentClass' not in self.URI_PID:
            raise ValueError("Error: No property found with URI 'http://www.w3.org/2002/07/owl#equivalentClass'")
        equiv_class_pid = self.URI_PID['http://www.w3.org/2002/07/owl#equivalentClass']
        # a map of item URIs to a QID in the wikibase you are using
        uri_qid = id_mapper(equiv_class_pid, endpoint=self.sparql_endpoint_url,
                            return_as_set=True)
        # remove duplicates/conflicts
        self.URI_QID = {k: list(v)[0] for k, v in uri_qid.items() if len(v) == 1}

    def guess_equivalent_property_pid(self):
        # get the equivalent property PID without knowing the PID for equivalent property!!!
        query = '''SELECT * WHERE {
          ?item ?prop <http://www.w3.org/2002/07/owl#equivalentProperty> .
          ?item <http://wikiba.se/ontology#directClaim> ?prop .
        }'''
        pid = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=self.sparql_endpoint_url)
        pid = pid['results']['bindings'][0]['prop']['value']
        pid = pid.split("/")[-1]
        return pid

    def get_pid(self, uri):
        """
        Get the pid for the property in this wikibase instance ( the one at `sparql_endpoint_url` ),
         that corresponds to (i.e. has the equivalent property) `uri`
        """
        # if the wikibase is wikidata, and we give a wikidata uri or a PID with no URI specified:
        if (self.sparql_endpoint_url == 'https://query.wikidata.org/sparql' and
                (uri.startswith("P") or uri.startswith("http://www.wikidata.org/entity/"))):
            # don't look up anything, just return the same value
            return uri
        if uri.startswith("P"):
            uri = "http://www.wikidata.org/entity/" + uri
        return self.URI_PID[uri]

    def get_qid(self, uri):
        # if the wikibase is wikidata, and we give a wikidata uri or a QID with no URI specified:
        if (self.sparql_endpoint_url == 'https://query.wikidata.org/sparql' and
                (uri.startswith("Q") or uri.startswith("http://www.wikidata.org/entity/"))):
            # don't look up anything, just return the same value
            return uri
        if uri.startswith("Q"):
            uri = "http://www.wikidata.org/entity/" + uri
        return self.URI_QID[uri]

    def prop2qid(self, prop, value):
        """
        Lookup the local item QID for a Wikidata item that has a certain `prop` -> `value`
        in the case where the local item has a `equivalent item` statement to that wikidata item
        Example: In my wikibase, I have CDK2 (Q79363) with the only statement:
            equivalent class -> http://www.wikidata.org/entity/Q14911732
            Calling prop2qid("P351", "1017") will return the local QID (Q79363)
        :param prop:
        :param value:
        :return:
        """
        equiv_class_pid = self.URI_PID['http://www.w3.org/2002/07/owl#equivalentClass']
        query = """
        PREFIX wwdt: <http://www.wikidata.org/prop/direct/>
        SELECT ?wditem ?localitem ?id WHERE {{
          SERVICE <https://query.wikidata.org/sparql> {{
            ?wditem wwdt:{prop} "{value}"
          }}
          ?localitem wdt:{equiv_class_pid} ?wditem
        }}"""
        query = query.format(prop=prop, value=value, equiv_class_pid=equiv_class_pid)

        results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=self.sparql_endpoint_url)
        result = results['results']['bindings']
        if len(result) == 0:
            return None
        elif len(result) > 1:
            raise ValueError("More than one wikidata ID found for {} {}: {}".format(prop, value, result))
        else:
            return result[0]['localitem']['value'].split("/")[-1]

    def id_mapper(self, prop, filters=None, return_as_set=False):
        """
        # see wdi_helpers.id_mapper for help on usage
        # QIDs returned are from the wikibase specified in self.sparql_endpoint_url
        # see WikibaseHelper.prop2qid for more details
        Example: Get all human genes:
        prop = "P351"
        filters = [("P703", "Q15978631")]
        h.id_mapper(prop, filters)
        """
        if filters:
            filter_str = "\n".join("?wditem wwdt:{} wwd:{} .".format(x[0], x[1]) for x in filters)
        else:
            filter_str = ""
        query = """
        PREFIX wwdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wwd: <http://www.wikidata.org/entity/>

        SELECT ?localitem ?ext_id WHERE {{
          SERVICE <https://query.wikidata.org/sparql> {{
            ?wditem wwdt:{prop} ?ext_id .
            {filter_str}
          }}
          ?localitem wdt:P3 ?wditem
        }}
        """.format(prop=prop, filter_str=filter_str)

        results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=self.sparql_endpoint_url)['results']['bindings']
        results = [{k: v['value'] for k, v in x.items()} for x in results]
        for r in results:
            r['localitem'] = r['localitem'].split('/')[-1]
        if not results:
            return None

        id_qid = defaultdict(set)
        for r in results:
            id_qid[r['ext_id']].add(r['localitem'])

        if return_as_set:
            return dict(id_qid)
        else:
            return {x['ext_id']: x['localitem'] for x in results}