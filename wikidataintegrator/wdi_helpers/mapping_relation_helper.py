from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_helpers import RELATIONS, PROPS
from wikidataintegrator.wdi_helpers.wikibase_helper import WikibaseHelper
from functools import lru_cache


class MappingRelationHelper:
    ABV_MRT = {
        "close": "http://www.w3.org/2004/02/skos/core#closeMatch",
        "exact": "http://www.w3.org/2004/02/skos/core#exactMatch",
        "related": "http://www.w3.org/2004/02/skos/core#relatedMatch",
        "broad": "http://www.w3.org/2004/02/skos/core#broadMatch",
        "narrow": "http://www.w3.org/2004/02/skos/core#narrowMatch"
    }

    def __init__(self, sparql_endpoint_url='https://query.wikidata.org/sparql'):
        if sparql_endpoint_url == 'https://query.wikidata.org/sparql':
            self.mrt_qids = {self.ABV_MRT[k]: v for k, v in RELATIONS.items()}
            self.mrt_pid = PROPS['mapping relation type']
        else:
            mrt_pid, mrt_qids = self.get_pids_qids(sparql_endpoint_url)
            self.mrt_pid = mrt_pid
            self.mrt_qids = mrt_qids

    @classmethod
    @lru_cache()
    def get_pids_qids(cls, sparql_endpoint_url):
        h = WikibaseHelper(sparql_endpoint_url=sparql_endpoint_url)
        mrt_pid = h.get_pid("http://www.w3.org/2004/02/skos/core#mappingRelation")
        mrt_qids = {x: h.get_qid(x) for x in cls.ABV_MRT.values()}
        return mrt_pid, mrt_qids

    def set_mrt(self, s, mrt: str):
        """
        accepts a statement and adds a qualifer setting the mrt
        modifies s in place

        :param s: a WDBaseDataType statement
        :param mrt: one of {'close', 'broad', 'exact', 'related', 'narrow'}
        :return: s
        """
        valid_mrts_abv = self.ABV_MRT.keys()
        valid_mrts_uri = self.ABV_MRT.values()
        if mrt in valid_mrts_abv:
            mrt_uri = self.ABV_MRT[mrt]
        elif mrt in valid_mrts_uri:
            mrt_uri = mrt
        else:
            raise ValueError("mrt must be one of {}, found {}".format(valid_mrts_abv, mrt))
        mrt_qid = self.mrt_qids[mrt_uri]

        q = wdi_core.WDItemID(mrt_qid, self.mrt_pid, is_qualifier=True)
        s.qualifiers.append(q)
        return s
