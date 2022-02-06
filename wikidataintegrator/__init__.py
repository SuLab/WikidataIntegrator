import pkg_resources

import wikidataintegrator.wdi_core
import wikidataintegrator.wdi_fastrun
import wikidataintegrator.wdi_helpers
import wikidataintegrator.wdi_login
import wikidataintegrator.sdc_core

try:
    __version__ = pkg_resources.get_distribution("wikidataintegrator").version
except Exception as e:
    __version__ = ""