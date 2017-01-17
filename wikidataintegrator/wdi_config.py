"""
Config global options
Options can be changed at run time. See tests/test_backoff.py for usage example

Options:
BACKOFF_MAX_TRIES: maximum number of times to retry failed request to wikidata endpoint.
        Default: None (retry indefinitely)
        To disable retry, set value to 1
BACKOFF_MAX_VALUE: maximum number of seconds to wait before retrying. wait time will increase to this number
        Default: 3600 (one hour)
"""

config = {'BACKOFF_MAX_TRIES': None,
          'BACKOFF_MAX_VALUE': 3600}