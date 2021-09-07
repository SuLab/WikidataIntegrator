import datetime
import json
from collections import defaultdict
from functools import partial
from itertools import islice
from time import sleep
import pandas as pd
from tqdm import tqdm

from .. import wdi_core


def take(n, iterable):
    # copied from more_itertools.chunked
    return list(islice(iterable, n))


def chunked(iterable, n):
    # copied from more_itertools.chunked
    return iter(partial(take, n, iter(iterable)), [])


PROPS = {
    'instance of': 'P31',
    'title': 'P1476',
    'published in': 'P1433',
    'volume': 'P478',
    'publication date': 'P577',
    'page(s)': 'P304',
    'issue': 'P433',
    'author name string': 'P2093',
    'author': 'P50',
    'PubMed ID': 'P698',
    'MED': 'P698',
    'DOI': 'P356',
    'series ordinal': 'P1545',
    'PMCID': 'P932',
    'PMC': 'P932',
    'reference URL': 'P854',
    'ISSN': 'P236',
    'ISBN-13': 'P212',
    'orcid id': "P496",
    'stated in': "P248",
    'retrieved': 'P813',
    'mapping relation type': 'P4390',
    'arxiv id': 'P818',
}

# https://www.wikidata.org/wiki/Property:P4390
RELATIONS = {
    'close': 'Q39893184',
    'exact': 'Q39893449',
    'related': 'Q39894604',
    'broad': 'Q39894595',
    'narrow': 'Q39893967'
}


def try_write(wd_item, record_id, record_prop, login, edit_summary='', write=True):
    """
    Write a PBB_core item. Log if item was created, updated, or skipped.
    Catch and log all errors.

    :param wd_item: A wikidata item that will be written
    :type wd_item: PBB_Core.WDItemEngine
    :param record_id: An external identifier, to be used for logging
    :type record_id: str
    :param record_prop: Property of the external identifier
    :type record_prop: str
    :param login: PBB_core login instance
    :type login: PBB_login.WDLogin
    :param edit_summary: passed directly to wd_item.write
    :type edit_summary: str
    :param write: If `False`, do not actually perform write. Action will be logged as if write had occured
    :type write: bool
    :return: True if write did not throw an exception, returns the exception otherwise
    """
    if wd_item.require_write:
        if wd_item.create_new_item:
            msg = "CREATE"
        else:
            msg = "UPDATE"
    else:
        msg = "SKIP"

    try:
        if write:
            wd_item.write(login=login, edit_summary=edit_summary)
        wdi_core.WDItemEngine.log("INFO", format_msg(record_id, record_prop, wd_item.wd_item_id, msg) + ";" + str(
            wd_item.lastrevid))
    except wdi_core.WDApiError as e:
        print(e)
        wdi_core.WDItemEngine.log("ERROR",
                                  format_msg(record_id, record_prop, wd_item.wd_item_id, json.dumps(e.wd_error_msg),
                                             type(e)))
        return e
    except Exception as e:
        print(e)
        wdi_core.WDItemEngine.log("ERROR", format_msg(record_id, record_prop, wd_item.wd_item_id, str(e), type(e)))
        return e

    return True


def format_msg(external_id, external_id_prop, wdid, msg, msg_type=None, delimiter=";"):
    """
    Format message for logging

    :return: str
    """
    fmt = ('{}' + delimiter) * 4 + '{}'  # '{};{};{};{};{}'
    d = {'external_id': external_id,
         'external_id_prop': external_id_prop,
         'wdid': wdid,
         'msg': msg,
         'msg_type': msg_type}
    for k, v in d.items():
        if isinstance(v, str) and delimiter in v and '"' in v:
            v = v.replace('"', "'")
        if isinstance(v, str) and delimiter in v:
            d[k] = '"' + v + '"'

    s = fmt.format(d['external_id'], d['external_id_prop'], d['wdid'], d['msg'], d['msg_type'])
    return s


def prop2qid(prop, value, endpoint='https://query.wikidata.org/sparql'):
    """
    Lookup a wikidata item ID from a property and string value. For example, get the item QID for the
     item with the entrez gene id (P351): "899959"
    >>> prop2qid('P351','899959')

    :param prop: property
    :type prop: str
    :param value: value of property
    :type value: str
    :return: wdid as string or None
    """
    arguments = '?item wdt:{} "{}"'.format(prop, value)
    query = 'SELECT * WHERE {{{}}}'.format(arguments)
    results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=endpoint)
    result = results['results']['bindings']
    if len(result) == 0:
        # not found
        return None
    elif len(result) > 1:
        raise ValueError("More than one wikidata ID found for {} {}: {}".format(prop, value, result))
    else:
        return result[0]['item']['value'].split("/")[-1]


def id_mapper(prop, filters=None, raise_on_duplicate=False, return_as_set=False, prefer_exact_match=False,
              endpoint='https://query.wikidata.org/sparql'):
    """
    Get all wikidata ID <-> prop <-> value mappings
    Example: id_mapper("P352") -> { 'A0KH68': 'Q23429083',
                                     'Q5ZWJ4': 'Q22334494',
                                     'Q53WF2': 'Q21766762', .... }
    Optional filters can filter query results.
    Example (get all uniprot to wdid, where taxon is human): id_mapper("P352",(("P703", "Q15978631"),))

    :param prop: wikidata property
    :type prop: str
    :param filters: list of tuples, where the first item is a property, second is a value
    :param raise_on_duplicate: If an ID is found on more than one wikidata item, what action to take?
        This is equivalent to the Distinct values constraint. e.g.: http://tinyurl.com/ztpncyb
        Note that a wikidata item can have more than one ID. This is not checked for
        True: raise ValueError
        False: only one of the values is kept if there are duplicates (unless return_as_set if True)
    :type raise_on_duplicate: bool
    :param return_as_set: If True, all values in the returned dict will be a set of strings
    :type return_as_set: bool
    :param prefer_exact_match: If True, the mapping relation type qualifier will be queried. If an ID mapping has
    multiple values, the ones marked as an 'exactMatch' will be returned while the others discarded. If none have
    an exactMatch qualifier, all will be returned. If multiple has 'exactMatch', they will not be discarded.
    https://www.wikidata.org/wiki/Property:P4390
    :type prefer_exact_match: bool


    If `raise_on_duplicate` is False and `return_as_set` is True, the following can be returned:
    { 'A0KH68': {'Q23429083'}, 'B023F44': {'Q237623', 'Q839742'} }

    :return: dict

    """
    query = "SELECT ?id ?item ?mrt WHERE {"
    query += "?item p:{} ?s .\n?s ps:{} ?id .\n".format(prop, prop)
    query += "OPTIONAL {?s pq:P4390 ?mrt}\n"
    if filters:
        for f in filters:
            query += "?item wdt:{} wd:{} .\n".format(f[0], f[1])
    query = query + "}"
    results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=endpoint)['results']['bindings']
    results = [{k: v['value'] for k, v in x.items()} for x in results]
    for r in results:
        r['item'] = r['item'].split('/')[-1]
        if 'mrt' in r:
            r['mrt'] = r['mrt'].split('/')[-1]
    if not results:
        return None

    if prefer_exact_match:
        df = pd.DataFrame(results)
        if 'mrt' not in df:
            df['mrt'] = ''
        df.mrt = df.mrt.fillna('')
        df['keep'] = True

        # check if a QID has more than one extID
        # i.e single value constraint
        # example: https://www.wikidata.org/w/index.php?title=Q3840916&oldid=645203228#P486 (D018311)
        # example 2: https://www.wikidata.org/w/index.php?title=Q388113&oldid=648588555#P486 (D000037, D000033)
        df.sort_values("item", inplace=True)
        dupe_df = df[df.duplicated(subset=["item"], keep=False)]
        for item, subdf in dupe_df.groupby("item"):
            # if there is one with exact match, take it, otherwise, skip
            if sum(subdf.mrt == RELATIONS['exact']) == 1:
                df.loc[(df.item == item) & (df.mrt != RELATIONS['exact']), 'keep'] = False

                # check if a extID has more than one QID
                # example: https://www.wikidata.org/w/index.php?title=Q846227&oldid=648565663#P486
                # https://www.wikidata.org/w/index.php?title=Q40207875&oldid=648565770#P486
        df.sort_values("id", inplace=True)
        dupe_df = df[df.duplicated(subset=["id"], keep=False)]
        for ext_id, subdf in dupe_df.groupby("id"):
            # if there is one with exact match, take it, otherwise, skip
            if sum(subdf.mrt == RELATIONS['exact']) == 1:
                df.loc[(df.id == ext_id) & (df.mrt != RELATIONS['exact']), 'keep'] = False

        df = df[df.keep]
        results = df.to_dict("records")

    id_qid = defaultdict(set)
    for r in results:
        id_qid[r['id']].add(r['item'])
    dupe = {k: v for k, v in id_qid.items() if len(v) > 1}
    if raise_on_duplicate and dupe:
        raise ValueError("duplicate ids: {}".format(dupe))

    if return_as_set:
        return dict(id_qid)
    else:
        return {x['id']: x['item'] for x in results}


def get_values(pid, values, endpoint='https://query.wikidata.org/sparql'):
    """
    This is a basic version of id_mapper, but restrict to values in `values`.
    Missing IDs are ignored

    :param pid: PID
    :param values: list of strings
    :param endpoint: sparql endpoint url
    :return:
    Example: Get the QIDs for the items with these PMIDs:
     get_values("P698", ["9719382", "9729004", "16384941"]) -> {'16384941': 'Q24642869', '9719382': 'Q33681179'}
    """
    chunks = chunked(values, 100)
    d = dict()
    for chunk in tqdm(chunks, total=round(len(values) / 100)):
        value_quotes = '"' + '" "'.join(map(str, chunk)) + '"'
        query = """select * where {
              values ?x {**value_quotes**}
              ?item wdt:**pid** ?x
            }""".replace("**value_quotes**", value_quotes).replace("**pid**", pid)
        results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=endpoint)['results']['bindings']
        dl = [{k: v['value'] for k, v in item.items()} for item in results]
        d.update({x['x']: x['item'].replace("http://www.wikidata.org/entity/", "") for x in dl})
    return d


def get_last_modified_header(entity="http://www.wikidata.org", endpoint='https://query.wikidata.org/sparql'):
    # this will work on wikidata or any particular entity
    query = "select ?d where {{<{}> schema:dateModified ?d}}".format(entity)
    results = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=endpoint)['results']['bindings']
    results = [{k: v['value'] for k, v in x.items()} for x in results]
    t = results[0]['d']
    try:
        # wikidata format
        dt = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # wikibase format
        dt = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ')
    return dt


def wait_for_last_modified(timestamp, delay=30, entity="http://www.wikidata.org",
                           endpoint='https://query.wikidata.org/sparql'):
    # wait until the last modified timestamp is newer than `timestamp`
    assert isinstance(timestamp, datetime.datetime)
    t = tqdm(desc="Waiting for endpoint update:  / {} ".format(timestamp))
    while True:
        last_modified_header = get_last_modified_header(entity=entity, endpoint=endpoint)
        t.set_description("Waiting for endpoint update: {} / {} ".format(last_modified_header, timestamp))
        t.update(1)
        if last_modified_header >= timestamp:
            break
        sleep(delay)


from .mapping_relation_helper import MappingRelationHelper
from .publication import PublicationHelper
from .release import Release
from .wikibase_helper import WikibaseHelper
