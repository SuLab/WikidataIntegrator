[TOC]

# ProteinBoxBot_Core #

# Introduction #
ProteinBoxBot is populating [WikiData](http://www.wikidata.org) with content from authoritative resources on Genes, Proteins, Diseases, Drugs and others. 
Descriptions on the different tasks can be found on the WikiData page describing the bot in detail (https://www.wikidata.org/wiki/User:ProteinBoxBot)

These many different tasks require a common interface to Wikidata. Although there exists a Python library/API wrapper for the [MediaWiki](https://www.mediawiki.org/) framework,
called [Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot), we think it is not sufficient rely on them for the interaction with Wikidata. The main reason is that it does not
implement any constraint or consistency checks of data which is already in Wikidata and which should be written to Wikidata. In other words, there are no checks in Pywikibot 
to prevent writing your data to the wrong item or generate duplicate data on a large scale. With PBB_core, we attempted to implement these checks in a Python library for
Wikidata. In comparision to Pywikibot, PBB_core is not a full Python wrapper for the MediaWiki API but is solely focused on providing an easy means to generate Python
based Wikidata bots, it therefore resembles a basic database connector like JDBC or ODBC. 

# The Core Parts #

PBB_core consists of a central class called WDItemEngine and several helper classes.

## PBB_core.WDItemEngine ##
This is the central class which does all the heavy lifting.

Features:

 * Load a Wikidata item based on data to be written (e.g. a unique central identifier)
 * Load a Wikidata item based on its Wikidata item id (aka QID)
 * Check for conflicts (e.g. multiple items carrying a unique central identifier will trigger an exception)
 * Check if the correct item has been loaded by comparing it to the data provided (if more than two thirds of properties are present with different values than in the data provided)
 * All Wikidata data types implemented
 * A dedicated WDItemEngine.write() method allows loading and consistency checks of data before any write to Wikidata is performed
 * Full access to the whole Wikidata item as a JSON document
 * Minimize the number of HTTP requests for reads and writes to improve performance
 * Methods to perform [SPARQL](query.wikidata.org) and [WDQ](http://wdq.wmflabs.org/) queries from client code
 

The two types of loading data open two different ways to work with Wikidata items: 

* A user can provide data and WDItemEngine will search for and load/modify an existing item or create a new one, solely based on the data provided (preferred)
* A user can work with a predefined list of QIDs to specifically modify the data on these items. 

The internal workflow of WDItemEngine shown in the subsequent figure. The figure depicts the workflow if only data is provided and WDItemEngine will check
for the existence of the appropriate item in Wikidata autonomously. Currently, if a QID is being provided, these checks will not be performed.

![Scheme of item selection process](https://bytebucket.org/sulab/wikidatabots/raw/04e6e8a514fa2c7a189e60c466774434ed48b023/ProteinBoxBot_Core/doc/item_selection_overview.svg)

Examples below illustrate the usage of WDItemEngine.

## PBB_login.WDLogin ##
In order to write bots for Wikidata, a bot account is required and each script needs to go through a Oauth login procedure. In order to obtain a bot account for Wikidata,
a specific task needs to be determined and then proposed to the Wikidata community. If the result of the community discussion is that your bot is useful for Wikidata, 
the bot account will be approved and you can use it.

PBB_login.WDLogin provides the login functionality and also stores the cookies and edit tokens required (For security reasons, every Wikidata edit requires an edit token).
The constructor takes two essential parameters, username and password. Additionally, the server (default www.wikidata.org) and the the token renewal periods can be specified. 


```Python
        
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')     
```

## Wikidata Data Types ##
Currently, Wikidata supports 9 different data types. The data types are represented as their own classes in PBB_core. Each data type has its specialties, which means that some of them
require special parameters (e.g. Globe Coordinates).

The data types currently implemented:

* PBB_core.WDString
* PBB_core.WDItemID
* PBB_core.WDMonolingualText
* PBB_core.WDProperty
* PBB_core.WDQuantity
* PBB_core.WDTime
* PBB_core.WDUrl
* PBB_core.WDGlobeCoordinate
* PBB_core.WDCommonsMedia

For details of how to create values (=instances) with these data types, please (for now) consult the docstrings. Of note, these data type instances hold the values and, if specified,
data type instances for references and qualifiers. Furthermore, calling the get_value() method of an instance returns either an integer, a string or a tuple, depending on the complexity of the data type.

# Examples #

## A Minimal Bot ##
In order to create a minimal bot based on PBB_core, three things are required:

* A login object, as described above.
* A data type object containing a value.
* A WDItemEngine object which takes the data, does the checks and performs the write.

```Python

    import PBB_core
    import PBB_login
        
    # login object
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')
         
    # data type object
    entrez_gene_id = PBB_core.WDString(value='<some_entrez_id>', prop_nr='P351')
    
    # Search for and then edit/create new item
    wd_item = PBB_core.WDItemEngine(item_name='<your_item_name>', domain='genes', data=[entrez_gene_id])
    wd_item.write(login_instance)
```

## A Minimal Bot for Mass Import ##
An enhanced example of the previous bot just puts two of the three things into a for loop and so allows mass creation, or modification of WD items.

```Python

    import PBB_core
    import PBB_login
        
    # login object
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')
    
    # A list of identifiers, can also be loaded from any other data sources
    entrez_id_list = ['<some_entrez_id>', '<some_entrez_id_1>, '<some_entrez_id_2>', '<some_entrez_id_3>', ...]
    
    for entrez_id_string in entrez_id_list:
        # data type object
        entrez_gene_id = PBB_core.WDString(value='entrez_id_string, prop_nr='P351')
        
        # Search for and then edit/create new item
        wd_item = PBB_core.WDItemEngine(item_name='<your_item_name>', domain='genes', data=[entrez_gene_id])
        wd_item.write(login_instance)
```
