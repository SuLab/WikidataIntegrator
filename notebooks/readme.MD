# Example Jupyter notebooks 
## wikidata examples
### Run a SPARQL query
In this example a sparql query is executed and the results are rendered either in its default json output format or as a Pandas dataframe.

[link](RunSparqlQueryWDQS.ipynb) 

### Login to wikidata
To be able to edit items on wikidata a bot needs to access the system with a bot account. This example demonstrates how to obtain a login token from the wikidata api
[link](LoginWikidata.ipynb) 

### Obtain a wikidata item for local parsing/editing
With the following example a Wikidata item is obtained through the action api of Wikidata through its json representation. 
[link](ObtainAWikidataItemAsPythonDict.ipynb) 

## wikibase examples
Although the WikidataIntegrator library was developed with Wikidata in mind, with the release of the docker version of Wikibase, the code has been adapted to work on Wikibase instances as well. 

### Copy properties from wikidata
This notebook demonstrates how to use the WikidataIntegrator to copy all wikidata properties to a Wikibase. 
The numbering of properties from Wikidata cannot be maintained, that is why as an initial step a property is created to link to the original Wikidata property. On a freshly installed Wikibase this will be (P1)
In the next step all Wikidata properties are obtained using a SPARQL query. After this SPARQL query obtained the list of properties, each property will be created on the target wikibase, maitaining the same value types as in Wikidata

[link](CreateWikidataProperties.ipynb) 
