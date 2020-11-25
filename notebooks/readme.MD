# Example Jupyter notebooks 
## Wikidata examples
### Run a SPARQL query
In this example a sparql query is executed and the results are rendered either in its default json output format or as a Pandas dataframe.

[link](RunSparqlQueryWDQS.ipynb) 

## Wikibase examples
Although the WikidataIntegrator library was developed with Wikidata in mind, with the release of the docker version of Wikibase, the code has been adapted to work on Wikibase instances as well. 

### Copy properties from Wikidata
This notebook demonstrates how to use the WikidataIntegrator to copy all wikidata properties to a Wikibase. 
The numbering of properties from Wikidata cannot be maintained, that is why as an initial step a property is created to link to the original Wikidata property. On a freshly installed Wikibase this will be (P1)
In the next step all Wikidata properties are obtained using a SPARQL query. After this SPARQL query obtained the list of properties, each property will be created on the target wikibase, maitaining the same value types as in Wikidata

[link](CreateWikidataProperties.ipynb) 
