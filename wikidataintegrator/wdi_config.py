"""
Config global options
Options can be changed at run time. See tests/test_backoff.py for usage example

Options:
BACKOFF_MAX_TRIES: maximum number of times to retry failed request to wikidata endpoint.
        Default: None (retry indefinitely)
        To disable retry, set value to 1
BACKOFF_MAX_VALUE: maximum number of seconds to wait before retrying. wait time will increase to this number
        Default: 3600 (one hour)
USER_AGENT_DEFAULT: default user agent string used for http requests. Both to wikibase api, query service and others.
    See: https://meta.wikimedia.org/wiki/User-Agent_policy
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("wikidataintegrator").version
except Exception as e:
    __version__ = ""

config = {
    'BACKOFF_MAX_TRIES': None,
    'BACKOFF_MAX_VALUE': 3600,
    'USER_AGENT_DEFAULT': 'wikidataintegrator/{}'.format(__version__),
    'MAXLAG': 5,
    'PROPERTY_CONSTRAINT_PID': 'P2302',
    'DISTINCT_VALUES_CONSTRAINT_QID': 'Q21502410'
}