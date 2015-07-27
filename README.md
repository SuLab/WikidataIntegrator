# ProteinBoxBot_Core
ProteinBoxBot aims at populating WikiData (http://www.wikidata.org) with content from authoratative resources on Genes, Proteins, Diseases and 
Drugs. Descriptions on the different tasks can be found on the WikiData page describing the bot in detail (https://www.wikidata.org/wiki/User:ProteinBoxBot)

Here we host the different python libraries that contain general functions to add content to WikiData inrespective of the content added. 
This would include finding, updating and creating concepts in WikiData

# list of general function libraries
## PBB_core.py
PBB_core checks if an appropriate item is present in Wikidata where data should be written to. Also, the json representation of the data is generated and the whole item is written to Wikidata.

A scheme of the item selection process:
![Scheme of item selection process](https://bytebucket.org/sulab/wikidatabots/raw/04e6e8a514fa2c7a189e60c466774434ed48b023/ProteinBoxBot_Core/doc/item_selection_overview.svg)


### login
This function enables login on WikiData's API

Descriptions to be added soon.....
