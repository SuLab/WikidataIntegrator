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

Examples below will illustrate the usage of WDItemEngine.

### login ###
This function enables login on WikiData's API

Descriptions to be added soon.....


```Python
        

        
```
