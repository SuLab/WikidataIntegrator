#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Sebastian Burgstaller and Andra Waagmeester'
__licence__ = 'AGPLv3'

domain_incompatibilities = {
    'drugs': [

    ],
    'genes': [

    ],
    'proteins': [

    ],
    'disease ontology': [

    ],
    'interpro': [

    ]
}

# a collection of values for the property 'subclass of' (P279) which are valid for a certain domain.
valid_instances = {
    'drugs': [
        'Q11173',  # chemical compound (only one single, pure chemical compound)
        'Q79529',  # chemical substance (several defined chemical compounds)
        'Q8054',  # protein
        'Q12140',  # pharmaceutical drug
        'Q422248'  # monoclonal antibodies
    ],
    'genes': [
        'Q7187'
    ],
    'proteins': [
        'Q8054'
    ],
    'disease ontology': [

    ],
    'obo': [

    ],
    'interpro': [
        'Q423026',  # active site
        'Q616005',  # binding site
        'Q898273',  # domain
        'Q417841',  # family
        'Q898362',  # ptm
    ],
    'chromosome': [
        'Q186380',
        'Q37748',  # chromosome
        'Q667636'
    ],
    'scientific_article': [

    ]
}

wd_properties = {
    'P715': {
        'datatype': 'string',
        'name': 'Drugbank ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P279': {
        'datatype': 'item',
        'name': 'subclass of',
        'domain': ['generic'],
        'core_id': 'False'
    },
    'P31': {
        'datatype': 'item',
        'name': 'instance of',
        'domain': ['generic', 'genomes', 'drugs'],
        'core_id': 'False'
    },
    'P636': {
        'datatype': 'item',
        'name': 'route of administration',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P267': {
        'datatype': 'string',
        'name': 'ATC code',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P231': {
        'datatype': 'string',
        'name': 'CAS registry number',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P486': {
        'datatype': 'string',
        'name': 'MeSH ID',
        'domain': ['drugs', 'diseases'],
        'core_id': 'True'
    },
    'P672': {
        'datatype': 'string',
        'name': 'MeSH Code',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P662': {
        'datatype': 'string',
        'name': 'PubChem ID (CID)',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P661': {
        'datatype': 'string',
        'name': 'ChemSpider ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P652': {
        'datatype': 'string',
        'name': 'UNII',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P665': {
        'datatype': 'string',
        'name': 'KEGG ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P683': {
        'datatype': 'string',
        'name': 'ChEBI ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P274': {
        'datatype': 'string',
        'name': 'chemical formula',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P592': {
        'datatype': 'string',
        'name': 'ChEMBL ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P233': {
        'datatype': 'string',
        'name': 'SMILES',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P2017': {
        'datatype': 'string',
        'name': 'Isomeric SMILES',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P234': {
        'datatype': 'string',
        'name': 'InChI',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P235': {
        'datatype': 'string',
        'name': 'InChIKey',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P1805': {
        'datatype': 'string',
        'name': 'Word Health Organisation International Nonproprietary Name',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P657': {
        'datatype': 'string',
        'name': 'RTECS Number',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P595': {
        'datatype': 'string',
        'name': 'IUPHAR ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P2115': {
        'datatype': 'string',
        'name': 'NDF-RT NUI',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P699': {
        'datatype': 'string',
        'name': 'Disease Ontology ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1550': {
        'datatype': 'string',
        'name': 'Orphanet ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P494': {
        'datatype': 'string',
        'name': 'ICD-10',
        'domain': ['diseases'],
        'core_id': 'False'
    },
    'P493': {
        'datatype': 'string',
        'name': 'ICD-9',
        'domain': ['diseases'],
        'core_id': 'False'
    },
    'P492': {
        'datatype': 'string',
        'name': 'OMIM',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1395': {
        'datatype': 'string',
        'name': 'National Cancer Thesaurus ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1748': {
        'datatype': 'string',
        'name': 'NCI Thesaurus ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P351': {
        'datatype': 'string',
        'name': 'Entrez Gene ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P2393': {
        'datatype': 'string',
        'name': 'NCBI Locus tag',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P3406': {
        'datatype': 'string',
        'name': 'Saccharomyces Genome Database ID',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P703': {
        'datatype': 'item',
        'name': 'found in taxon',
        'domain': ['genes', 'chromosome'],
        'core_id': 'False'
    },
    'P594': {
        'datatype': 'string',
        'name': 'Ensembl Gene ID',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P704': {
        'datatype': 'string',
        'name': 'Ensembl Transcript ID',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P353': {
        'datatype': 'string',
        'name': 'Human Gene symbol',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P354': {
        'datatype': 'string',
        'name': 'HGNC symbol',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P593': {
        'datatype': 'string',
        'name': 'homologene id',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P639': {
        'datatype': 'string',
        'name': 'RefSeq RNA ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P1057': {
        'datatype': 'item',
        'name': 'chromosome',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P684': {
        'datatype': 'item',
        'name': 'ortholog',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P638': {
        'datatype': 'string',
        'name': 'PDB ID',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P637': {
        'datatype': 'string',
        'name': 'Refseq Protein ID',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P352': {
        'datatype': 'string',
        'name': 'Uniprot ID',
        'domain': ['proteins'],
        'core_id': 'True'
    },
    'P591': {
        'datatype': 'string',
        'name': 'EC Number',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P705': {
        'datatype': 'string',
        'name': 'Ensembl Protein ID',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P702': {
        'datatype': 'item',
        'name': 'Encoded By',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P18': {
        'datatype': 'url',
        'name': 'Protein Structure Image',
        'domain': ['proteins'],
        'core_id': 'True'
    },
    'P671': {
        'datatype': 'url',
        'name': 'MGI',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P644': {
        'datatype': 'string',
        'name': 'Genomic start position',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P645': {
        'datatype': 'string',
        'name': 'Genomic end position',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P688': {
        'datatype': 'item',
        'name': 'encodes',
        'domain': ['genes', 'proteins'],
        'core_id': 'False'
    },
    'P225': {
        'datatype': 'string',
        'name': 'taxon name',
        'domain': ['genomes'],
        'core_id': 'False'
    },
    'P685': {
        'datatype': 'string',
        'name': 'NCBI Taxonomy ID',
        'domain': ['genomes'],
        'core_id': 'True'
    },
    'P171': {
        'datatype': 'item',
        'name': 'parent taxon',
        'domain': ['genomes'],
        'core_id': 'False'
    },
    'P1065': {
        'datatype': 'url',
        'name': 'Archive url',
        'domain': ['genomes'],
        'core_id': 'True'
    },
    'P856': {
        'datatype': 'url',
        'name': 'offical website',
        'domain': ['genomes'],
        'core_id': 'False'
    },
    'P680': {
        'datatype': 'item',
        'name': 'molecular function',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P681': {
        'datatype': 'item',
        'name': 'cell component',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P682': {
        'datatype': 'item',
        'name': 'biological process',
        'domain': ['proteins'],
        'core_id': 'False'
    },
    'P1554': {
        'datatype': 'item',
        'name': 'uberon id',
        'domain': ['anatomical_structure', 'obo'],
        'core_id': 'False'
    },
    'P1709': {
        'datatype': 'item',
        'name': 'equivalent class',
        'domain': ['genes', 'proteins', 'diseases', 'drugs', 'anatomical_structure'],
        'core_id': 'False'
    },
    'P686': {
        'datatype': 'item',
        'name': 'Gene Ontology ID',
        'domain': ['obo'],
        'core_id': 'True'
    },
    'P2926': {
        'datatype': 'string',
        'name': 'InterPro ID',
        'domain': ['interpro'],
        'core_id': 'True'
    },
    'P2870': {
        'datatype': 'string',
        'name': 'miRBase pre-miRNA ID',
        'domain': ['microRNAs'],
        'core_id': 'True'
    },
    'P2871': {
        'datatype': 'string',
        'name': 'miRBase mature miRNA ID',
        'domain': ['microRNAs'],
        'core_id': 'True'
    },
    'P2646': {
        'datatype': 'string',
        'name': 'mirTarBase ID',
        'domain': ['microRNAs'],
        'core_id': 'True'
    },
    'P2249': {
        'datatype': 'string',
        'name': 'Refseq Genome ID',
        'domain': ['chromosome'],
        'core_id': 'True'
    },
    'P698': {
        'datatype': 'string',
        'name': 'PubMed ID',
        'domain': ['scientific_article'],
        'core_id': 'True'
    }
}
