[TOC]

# ProteinBoxBot_Core #

# Introduction #
ProteinBoxBot_core (PBB_core) is a library for reading and writing to Wikidata/Wikibase. We created it for populating [WikiData](http://www.wikidata.org) with content from authoritative resources on Genes, Proteins, Diseases, Drugs and others. 
Details on the different tasks can be found on [the botx Wikidata page](https://www.wikidata.org/wiki/User:ProteinBoxBot).

[Pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot) is an existing framework for interacting with the [MediaWiki](https://www.mediawiki.org/) API. The reason why we came up with our own solution is
 that we need a high integration with the []Wikidata SPARQL endpoint](query.wikidata.org) in order to ensure data consistency (duplicate check, consistency checks, correct item selection, etc.). 

Compared to Pywikibot, PBB_core currently is not a full Python wrapper for the MediaWiki API but is solely focused on providing an easy means to generate Python
based Wikidata bots, it therefore resembles a basic database connector like JDBC or ODBC. 

# The Core Parts #

PBB_core supports two modes it can be operated in, a normal mode, updating each item at a time and a 'fastrun' mode, which is pre-loading data locally and then just updating items if the new data provided is differing from what is in Wikidata. The latter mode allows for great speedups (measured up to 9x) when tens of thousand of Wikidata 
items need to be checked if the require updates but only a small number will finally be updated, a situation usually encountered when keeping Wikidata in sync with an external resource. 

PBB_core consists of a central class called WDItemEngine and WDLogin for authenticating with Wikidata/Wikipedia.

## PBB_core.WDItemEngine ##
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

* A user can provide data and WDItemEngine will search for and load/modify an existing item or create a new one, solely based on the data provided (preferred). This also performs consistency checks based on a set of SPARQL queries. 
* A user can work with a selected QID to specifically modify the data on the item. This requires that the users knows what what he/she is doing and should only be used with great care, as this does not perform consistency checks. 

Examples below illustrate the usage of WDItemEngine.

## PBB_login.WDLogin ##
In order to write bots for Wikidata, a bot account is required and each script needs to go through a Oauth login procedure. For obtaining a bot account in Wikidata,
a specific task needs to be determined and then proposed to the Wikidata community. If the community discussion results in your bot code and account being considered useful for Wikidata, you are ready to go.
However, the code of PBB_core can also run with normal user accounts, the differences are primarily that you have lower writing limits per minute. 

PBB_login.WDLogin provides the login functionality and also stores the cookies and edit tokens required (For security reasons, every Wikidata edit requires an edit token).
The constructor takes two essential parameters, username and password. Additionally, the server (default www.wikidata.org) and the the token renewal periods can be specified. 


```Python     
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')     
```

## Wikidata Data Types ##
Currently, Wikidata supports 11 different data types. The data types are represented as their own classes in PBB_core. Each data type has its specialties, which means that some of them
require special parameters (e.g. Globe Coordinates).

The data types currently implemented:

* PBB_core.WDString
* PBB_core.WDItemID
* PBB_core.WDMonolingualText
* PBB_core.WDQuantity
* PBB_core.WDProperty
* PBB_core.WDQuantity
* PBB_core.WDTime
* PBB_core.WDUrl
* PBB_core.WDGlobeCoordinate
* PBB_core.WDCommonsMedia
* PBB_core.WDMath

For details of how to create values (=instances) with these data types, please (for now) consult the docstrings in the source code. Of note, these data type instances hold the values and, if specified,
data type instances for references and qualifiers. Furthermore, calling the get_value() method of an instance returns either an integer, a string or a tuple, depending on the complexity of the data type.

# Examples (in normal mode) #

## A Minimal Bot ##
In order to create a minimal bot based on PBB_core, three things are required:

* A login object, as described above.
* A data type object containing a value.
* A WDItemEngine object which takes the data, does the checks and performs the write.

```Python

    import PBB_Core
    import PBB_login
        
    # login object
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')
         
    # data type object, e.g. for a NCBI gene entrez ID
    entrez_gene_id = PBB_Core.WDString(value='<some_entrez_id>', prop_nr='P351')
    
    # data goes into a list, because many data objects can be provided to 
    data = [entrez_gene_id]
    
    # Search for and then edit/create new item
    wd_item = PBB_Core.WDItemEngine(item_name='<your_item_name>', domain='genes', data=[entrez_gene_id])
    wd_item.write(login_instance)
```

## A Minimal Bot for Mass Import ##
An enhanced example of the previous bot just puts two of the three things into a for loop and so allows mass creation, or modification of WD items.

```Python

    import PBB_Core
    import PBB_login
        
    # login object
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')
    
    # We have raw data, which should be written to Wikidata, namely two human NCBI entrez gene IDs mapped to two Ensembl Gene IDs
    raw_data = {
        '50943': 'ENST00000376197',
        '1029': 'ENST00000498124'
    }
    
    for entrez_id, ensembl in raw_data.items():
        # data type object
        entrez_gene_id = PBB_Core.WDString(value=entrez_id, prop_nr='P351')
        ensembl_transcript_id = PBB_Core.WDString(value='entrez_id_string', prop_nr='P704')
        
        # data goes into a list, because many data objects can be provided to 
        data = [entrez_gene_id, ensembl_transcript_id]
        
        # Search for and then edit/create new item
        wd_item = PBB_Core.WDItemEngine(item_name='<your_item_name>', domain='genes', data=data)
        wd_item.write(login_instance)
```

# Examples (fast run mode) #
In order to use the fast run mode, you need to know the property/value combination which determines the data corpus you would like to operate on.
E.g. for operating on human genes, you need to know that [P351](http://www.wikidata.org/entity/P351) is the NCBI entrez gene ID and you also need to know that you are dealing with humans, 
best represented by the [found in taxon property (P703)](http://www.wikidata.org/entity/P703) with the value [Q5](http://www.wikidata.org/entity/Q5) for human. 

Here, the above example from normal mode with the small modifications required for running in fastrun mode. To enable it, WDItemEngine requires two parameters, fast_run=True/False and fast_run_base_filter which 
 is a dictionary holding the properties to filter for as keys and the item QIDs as dict values. If the value is not a QID but a literal, just provide an empty string. For the above example, the dictionary looks like this:
 
```Python
    fast_run_base_filter = {'P351': '', 'P704': 'Q5'}
```
 

```Python

    import PBB_Core
    import PBB_login
        
    # login object
    login_instance = PBB_login.WDLogin(user='<bot user name>', pwd='<bot password>')
    
    fast_run_base_filter = {'P351': '', 'P704': 'Q5'}
    fast_run = True
    
    # We have raw data, which should be written to Wikidata, namely two human NCBI entrez gene IDs mapped to two Ensembl Gene IDs
    # You can iterate over any data source as long as you can map the values to Wikidata properties.
    raw_data = {
        '50943': 'ENST00000376197',
        '1029': 'ENST00000498124'
    }
    
    for entrez_id, ensembl in raw_data.items():
        # data type object
        entrez_gene_id = PBB_Core.WDString(value=entrez_id, prop_nr='P351')
        ensembl_transcript_id = PBB_Core.WDString(value='entrez_id_string', prop_nr='P704')
        
        # data goes into a list, because many data objects can be provided to 
        data = [entrez_gene_id, ensembl_transcript_id]
        
        # Search for and then edit/create new item
        wd_item = PBB_Core.WDItemEngine(item_name='<your_item_name>', domain='genes', data=data, fast_run=fast_run, fast_run_base_filter=fast_run_base_filter)
        wd_item.write(login_instance)
```

FYI: Fastrun mode checks for equality of property/value pairs, qualifers, labels, aliases and description, but it ignores references!