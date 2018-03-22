from wikidataintegrator import wdi_core
from wikidataintegrator import wdi_login
from wikidataintegrator import wdi_helpers

#login = wdi_login.WDLogin(user='<bot user name>', pwd='<bot password>')     

PMID=29559558
print wdi_helpers.PubmedItem(PMID).get_or_create(login)

