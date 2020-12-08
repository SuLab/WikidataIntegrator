# Wikidata Integrator #
[![Build Status](https://travis-ci.org/SuLab/WikidataIntegrator.svg?branch=main)](https://travis-ci.org/SuLab/WikidataIntegrator)
[![Pyversions](https://img.shields.io/pypi/pyversions/wikidataintegrator.svg)](https://pypi.python.org/pypi/wikidataintegrator)
[![PyPi](https://img.shields.io/pypi/v/wikidataintegrator.svg)](https://pypi.python.org/pypi/wikidataintegrator)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/SuLab/WikidataIntegrator/main)
[<img src="https://img.shields.io/badge/slack-@genewiki/wdi_bot_dev-green.svg?logo=slack">](https://suwulab.slack.com/archives/C014ADW3SGZ)

# Slack channel 
We have a slack channel for Wikidata bot developers using the Wikidata Integrator. Send us a [request](mailto:andra@micel.io) to join this channel. 

# Installation #
The easiest way to install WikidataIntegrator is using `pip` or `pip3`. WikidataIntegrator supports python 3.6 and higher, hence the suggestion for pip3. If python2 is installed pip will lead to an error indicating missing dependencies. 

```
pip3 install wikidataintegrator
```

You can also clone the repo and execute with administrator rights or install into a virtualenv.

```bash

git clone https://github.com/sebotic/WikidataIntegrator.git

cd WikidataIntegrator

python3 setup.py install
```

To test for correct installation, start a python console and execute the following (Will retrieve the Wikidata item for ['Human'](http://www.wikidata.org/entity/Q5)):

```python
from wikidataintegrator import wdi_core

my_first_wikidata_item = wdi_core.WDItemEngine(wd_item_id='Q5')

# to check successful installation and retrieval of the data, you can print the json representation of the item
my_first_wikidata_item.get_wd_json_representation()
```

# Introduction #
WikidataIntegrator is a library for reading and writing to Wikidata/Wikibase. We created it for populating [Wikidata](http://www.wikidata.org) with content from authoritative resources on Genes, Proteins, Diseases, Drugs and others. 
Details on the different tasks can be found on [the bot's Wikidata page](https://www.wikidata.org/wiki/User:ProteinBoxBot).

[Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) is an existing framework for interacting with the [MediaWiki](https://www.mediawiki.org/) API. The reason why we came up with our own solution is that we need a high integration with the [Wikidata SPARQL endpoint](query.wikidata.org) in order to ensure data consistency (duplicate check, consistency checks, correct item selection, etc.). 

Compared to Pywikibot, WikidataIntegrator currently is not a full Python wrapper for the MediaWiki API but is solely focused on providing an easy means to generate Python based Wikidata bots, it therefore resembles a basic database connector like JDBC or ODBC. 

## Note: Rate Limits ##
New users may hit rate limits (of 8 edits per minute) when editing or creating items. [Autoconfirmed users](https://www.wikidata.org/wiki/Wikidata:User_access_levels#Autoconfirmed_users), (an account with at least 4 days of age and at least 50 edits), should not need to worry about hitting these limits. Users who anticipate making large numbers of edits to Wikidata should create a separate [bot](https://www.wikidata.org/wiki/Wikidata:Bots) account and [request approval](https://www.wikidata.org/wiki/Wikidata:Requests_for_permissions/Bot). 

# The Core Parts #

wdi_core supports two modes it can be operated in, a normal mode, updating each item at a time and a 'fastrun' mode, which is pre-loading data locally and then just updating items if the new data provided is differing from what is in Wikidata. The latter mode allows for great speedups (measured up to 9x) when tens of thousand of Wikidata 
items need to be checked if they require updates but only a small number will finally be updated, a situation usually encountered when keeping Wikidata in sync with an external resource. 

wdi_core consists of a central class called WDItemEngine and WDLogin for authenticating with Wikidata/Wikipedia.

## wdi_core.WDItemEngine ##
This is the central class which does all the heavy lifting.

Features:

 * Load a Wikidata item based on data to be written (e.g. a unique central identifier)
 * Load a Wikidata item based on its Wikidata item id (aka QID)
 * Checks for conflicts automatically (e.g. multiple items carrying a unique central identifier will trigger an exception)
 * Checks automatically if the correct item has been loaded by comparing it to the data provided
 * All Wikidata data types implemented
 * A dedicated WDItemEngine.write() method allows loading and consistency checks of data before any write to Wikidata is performed
 * Full access to the whole Wikidata item as a JSON document
 * Minimize the number of HTTP requests for reads and writes to improve performance
 * Method to easily execute [SPARQL](query.wikidata.org) queries on the Wikidata endpoint. 
 

There are two ways of working with Wikidata items: 

* A user can provide data, and WDItemEngine will search for and load/modify an existing item or create a new one, solely based on the data provided (preferred). This also performs consistency checks based on a set of SPARQL queries. 
* A user can work with a selected QID to specifically modify the data on the item. This requires that the user knows what he/she is doing and should only be used with great care, as this does not perform consistency checks. 

Examples below illustrate the usage of WDItemEngine.

## wdi_login.WDLogin ##

### Login with username and password ###
In order to write bots for Wikidata, a bot account is required and each script needs to go through a login procedure. For obtaining a bot account in Wikidata,
a specific task needs to be determined and then proposed to the Wikidata community. If the community discussion results in your bot code and account being considered useful for Wikidata, you are ready to go.
However, the code of wdi_core can also run with normal user accounts, the differences are primarily that you have lower writing limits per minute. 

wdi_login.WDLogin provides the login functionality and also stores the cookies and edit tokens required (For security reasons, every Wikidata edit requires an edit token).
The constructor takes two essential parameters, username and password. Additionally, the server (default www.wikidata.org) and the the token renewal periods can be specified. 


```Python     
    login_instance = wdi_login.WDLogin(user='<bot user name>', pwd='<bot password>')     
```

### Login using OAuth1 ###
The Wikimedia universe currently only support authentication via OAuth1. If WDI should be used as a backend for a webapp or the bot should use OAuth for authentication, WDI supports this
You just need to specify consumer token and consumer secret when instantiating wdi_login.WDLogin. In contrast to username and password login, OAuth is a 2 step process as manual user confirmation
for OAuth login is required. This means that the method continue_oath() needs to be called after creating the wdi_login.WDLogin instance.

Example:
```Python     
    login_instance = wdi_login.WDLogin(consumer_key='<your_consumer_key>', pwd='<your_consumer_secret>')
    login_instance.continue_oauth()
```

The method continue_oauth() will either promt the user for a callback URL (normal bot runs) or it will take a parameter so in the case of WDI being
used as a backend for e.g. a web app, where the callback will provide the authentication information directly to the backend and so
 no copy and paste of the callback URL is required.


## Wikidata Data Types ##
Currently, Wikidata supports 17 different data types. The data types are represented as their own classes in wdi_core. Each data type has its specialties, which means that some of them
require special parameters (e.g. Globe Coordinates).

The data types currently implemented:

* wdi_core.WDCommonsMedia
* wdi_core.WDExternalID
* wdi_core.WDForm
* wdi_core.WDGeoShape
* wdi_core.WDGlobeCoordinate
* wdi_core.WDItemID
* wdi_core.WDLexeme
* wdi_core.WDMath
* wdi_core.WDMonolingualText
* wdi_core.WDMusicalNotation
* wdi_core.WDProperty
* wdi_core.WDQuantity
* wdi_core.WDSense
* wdi_core.WDString
* wdi_core.WDTabularData
* wdi_core.WDTime
* wdi_core.WDUrl

For details of how to create values (=instances) with these data types, please (for now) consult the docstrings in the source code. Of note, these data type instances hold the values and, if specified,
data type instances for references and qualifiers. Furthermore, calling the get_value() method of an instance returns either an integer, a string or a tuple, depending on the complexity of the data type.


# Helper Methods #

## Execute SPARQL queries ##
The method wdi_core.WDItemEngine.execute_sparql_query() allows you to execute SPARQL queries without a hassle. It takes the actual
query string (query), optional prefixes (prefix) if you do not want to use the standard prefixes of Wikidata, the actual entpoint URL (endpoint),
 and you can also specify a user agent for the http header sent to the SPARQL server (user_agent). The latter is very useful to let
 the operators of the endpoint know who you are, especially if you execute many queries on the endpoint. This allows the operators of
 the endpoint to contact you (e.g. specify a email address or the URL to your bot code repository.)

## Logging ##
The method wdi_core.WDItemEngine.log() allows for using the Python built in logging functionality to collect errors and other logs.
It takes two parameters, the log level (level) and the log message (message). It is advisable to separate log file columns by colons
and always use the same number of fields, as this allows you to load the log file into databases or dataframes of R or Python.

There is a helper method wdi_helpers.try_write() which allows both writing and logging at the same time. Calling this function with the WDItemEngine item to be written,
will call the write() method on the item and log the action in a standard format in a log file, while capturing all exceptions and writing them to the log as well. This
method uses wdi_helpers.format_msg internally to format the logging. 

If logs are written using wdi_helpers.try_write() they can be automatically parsed by an external tool called '[Bot Log Parser](https://github.com/SuLab/scheduled-bots/blob/master/scheduled_bots/logger/bot_log_parser.py)', which generates a clickable html output for easy viewing and sharing. See [example output](http://jenkins.sulab.org/job/Disease_Ontology/21/artifact/Disease_Ontology/logs/DOIDBot-20171002_23%3A00.html).

## Wikidata Search ##
 The method wdi_core.WDItemEngine.get_wd_search_results() allows for string search in
 Wikidata. This means that labels, descriptions and aliases can be searched for a string of interest. The method takes five arguments:
 The actual search string (search_string), an optional server (in case the Wikibase instance used is not Wikidata), an optional user_agent, an
 optional max_results (default 500), and an optional language (default 'en').
 
## Merge Wikidata items ##
Sometimes, Wikidata items need to be merged. An API call exists for that, and wdi_core implements a method accordingly.
`wdi_core.WDItemEngine.merge_items(from_id, to_id, login_obj, server='https://www.wikidata.org', ignore_conflicts='')` takes five
arguments: the QID of the item which should be merged into another item (from_id), the QID of the item the first item should be
merged into (to_id), a login object of type wdi_login.WDLogin() (login_obj) to provide the API call with the required authentication
information, a server (server) if the Wikibase instance is not Wikidata and a flag for ignoring merge conflicts (ignore_conflicts).
The last parameter will do a partial merge for all statements which do not conflict. This should generally be avoided because it 
leaves a crippled item in Wikidata. Before a merge, any potential conflicts should be resolved first.

## Pubmed Articles ##
The class wdi_core.wdi_helpers.PubmedItem allows you to create article items. Given a PMID, it will create an item representing this journal article. It can also retrieve existing items. This is useful for quickly creating items to use in reference statements.

## Database Release ##
The class wdi_core.wdi_helpers.Release allows you to create an item for a database release. These should be used in reference statements. See [here](https://www.wikidata.org/wiki/User:ProteinBoxBot/evidence#Guidelines_for_Referencing_Databases.2C_Ontologies_and_similar_Web-native_information_entities.) 
for more information. 

## Test for conformance to a Shape Expression ##
Shape Expressions (ShEx) is a structural schema language for RDF graphs. It allows to express the graph structures such a Wikidata items. 
The class wdi_core.check_shex_conformance tests a wikidata item on conformance to a given ShEx.
In the example below the wikidata item [helium (!560)](https://www.wikidata.org/wiki/Q560)  is checked for conformance to a schema expressed as shape expression for [chemical element (E46)](https://www.wikidata.org/wiki/EntitySchema:E46). 


```Python
from wikidataintegrator import wdi_core

print("Q560 conforms to E46"+wdi_core.WDItemEngine.check_shex_conformance("Q560", "E46"))
```

# Examples (in normal mode) #

## An Example Bot ##
https://github.com/stuppie/wikidatacon_wdi_demo

## A Minimal Bot ##
In order to create a minimal bot based on wdi_core, three things are required:

* A login object, as described above.
* A data type object containing a value.
* A WDItemEngine object which takes the data, does the checks and performs the write.

```Python

    from wikidataintegrator import wdi_core, wdi_login
        
    # login object
    login_instance = wdi_login.WDLogin(user='<bot user name>', pwd='<bot password>')
         
    # data type object, e.g. for a NCBI gene entrez ID
    entrez_gene_id = wdi_core.WDString(value='<some_entrez_id>', prop_nr='P351')
    
    # data goes into a list, because many data objects can be provided to 
    data = [entrez_gene_id]
    
    # Search for and then edit/create new item
    wd_item = wdi_core.WDItemEngine(data=data)
    wd_item.write(login_instance)
```

## A Minimal Bot for Mass Import ##
An enhanced example of the previous bot just puts two of the three things into a for loop and so allows mass creation, or modification of WD items.

```Python

    from wikidataintegrator import wdi_core, wdi_login
        
    # login object
    login_instance = wdi_login.WDLogin(user='<bot user name>', pwd='<bot password>')
    
    # We have raw data, which should be written to Wikidata, namely two human NCBI entrez gene IDs mapped to two Ensembl Gene IDs
    raw_data = {
        '50943': 'ENST00000376197',
        '1029': 'ENST00000498124'
    }
    
    for entrez_id, ensembl in raw_data.items():
        # data type object
        entrez_gene_id = wdi_core.WDString(value=entrez_id, prop_nr='P351')
        ensembl_transcript_id = wdi_core.WDString(value=ensembl, prop_nr='P704')
        
        # data goes into a list, because many data objects can be provided to 
        data = [entrez_gene_id, ensembl_transcript_id]
        
        # Search for and then edit/create new item
        wd_item = wdi_core.WDItemEngine(data=data)
        wd_item.write(login_instance)
```

# Examples (fast run mode) #
In order to use the fast run mode, you need to know the property/value combination which determines the data corpus you would like to operate on.
E.g. for operating on human genes, you need to know that [P351](http://www.wikidata.org/entity/P351) is the NCBI entrez gene ID and you also need to know that you are dealing with humans, 
best represented by the [found in taxon property (P703)](http://www.wikidata.org/entity/P703) with the value [Q15978631](http://www.wikidata.org/entity/Q15978631) for homo sapiens.

IMPORTANT: In order for the fast run mode to work, the data you provide in the constructor must contain at least one unique value/id only present on one Wikidata item, e.g. an NCBI entrez gene ID, Uniprot ID, etc.
Usually, these would be the same unique core properties used for defining domains in wdi_core, e.g. for genes, proteins, drugs or your custom domains.

Below, the normal mode run example from above, slightly modified, to meet the requirements for the fastrun mode. To enable it, WDItemEngine requires two parameters, fast_run=True/False and fast_run_base_filter which 
 is a dictionary holding the properties to filter for as keys and the item QIDs as dict values. If the value is not a QID but a literal, just provide an empty string. For the above example, the dictionary looks like this:
 
```Python
    fast_run_base_filter = {'P351': '', 'P703': 'Q15978631'}
```
 
The full example:
```Python

    from wikidataintegrator import wdi_core, wdi_login
        
    # login object
    login_instance = wdi_login.WDLogin(user='<bot user name>', pwd='<bot password>')
    
    fast_run_base_filter = {'P351': '', 'P703': 'Q15978631'}
    fast_run = True
    
    # We have raw data, which should be written to Wikidata, namely two human NCBI entrez gene IDs mapped to two Ensembl Gene IDs
    # You can iterate over any data source as long as you can map the values to Wikidata properties.
    raw_data = {
        '50943': 'ENST00000376197',
        '1029': 'ENST00000498124'
    }
    
    for entrez_id, ensembl in raw_data.items():
        # data type object
        entrez_gene_id = wdi_core.WDString(value=entrez_id, prop_nr='P351')
        ensembl_transcript_id = wdi_core.WDString(value=ensembl, prop_nr='P704')
        
        # data goes into a list, because many data objects can be provided to 
        data = [entrez_gene_id, ensembl_transcript_id]
        
        # Search for and then edit/create new item
        wd_item = wdi_core.WDItemEngine(data=data, fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
        wd_item.write(login_instance)
```

Note: Fastrun mode checks for equality of property/value pairs, qualifers (not including qualifier attributes), labels, aliases and description, but it ignores references by default! References can be checked in fastrun mode by setting `fast_run_use_refs` to `True`.
