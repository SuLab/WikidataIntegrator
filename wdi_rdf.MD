# Introducing the wdi_rdf extension to WDI

The wdi_rdf extension was added to the Wikidata integrator. It builds on [Wikidata/triplify-json](https://github.com/Wikidata/triplify-json). This extension replicates the RDF output of a Wikidata item. 

Wikidata is great, for one because it natively delivers its content also as RDF. This allows venturing out to other wikibases or even non-wikibase linked data resources. The RDF output of Wikidata is also richer in content than the default json output. Notably are the conversion to SI units of Wikidata statements of the datatype unit. In the json those units are expressed as entered, when relying on the RDF, it is possible to compare the different values with units by their SI conversions. The RDF also captures merges and additional metadata. 

The RDF of a (set of) wikidata item(s) can be obtained directly through the web browser by adding .ttl to the concept URI. For example The RDF version of the Wikidata item on [BRAF](https://www.wikidata.org/wiki/Q17853226) is obtained by chaning the webaddres "https://www.wikidata.org/wiki/Q17853226" to "https://www.wikidata.org/entity/Q17853226.ttl". i.e. is chaning "wiki" -> "entity" and adding ".ttl

## Shape Expressions
Wikidata has an EntitySchema extension that uses [Shape Expressions (ShEx)](https://shex.io) to describe the schema of an underlying schema. In the Gene Wiki projec We leverage this schema language to check wikidata items for consistency on a given narrative or [use case](https://bmcbiol.biomedcentral.com/articles/10.1186/s12915-020-00940-y). Since Wikidata (and wikibase) delivers RDF natively as described above, or through its [query service](https://query.wikidata.org/). Leveraging these RDF entry points allows checking for consistency to these EntitySchemas. This can be done using the EntitySchema interface of Wikidata, third party tools, e.g. [wikishape](https://wikishape.weso.es/) or the [check_shex_conformance](https://github.com/SuLab/WikidataIntegrator/blob/main/wikidataintegrator/wdi_core.py#L205) function on wdi_core.

## Pre-ingestion checks for conformance to EntitySchemas
All these checks for conformance on EntitySchemas are done post data ingestion. The data needs first to be converted to RDF using the internal scripts of Wikibase. However, in bot operations, we would also like to be able to run conformance test pre-ingestion to Wikidata. This wdi_rdf extension is mainly developed with this usecase in mind (i.e. checking the schema of the data before it is added to Wikidata.

## Subsetting
However, the overall datamodel of Wikidata contains some redundancy. Next to full statements, there are also the "truthy" statements where context and provenance (ie. qualifiers and references) are removed. With this library it is also possible to extract subsets of the RDF representation of a wikidata item by selecting either the full RDF graph or subsections of it. 
