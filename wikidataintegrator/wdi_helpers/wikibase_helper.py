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
        uri_pid = id_mapper(self.guess_equivalent_property_pid(), endpoint=self.sparql_endpoint_url,
                            return_as_set=True)
        # remove duplicates/conflicts
        self.URI_PID = {k: list(v)[0] for k, v in uri_pid.items() if len(v) == 1}
        # get equivalent class PID
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
