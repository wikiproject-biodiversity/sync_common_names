"""
Authors:
Andra Waagmeester (andra' at ' micelio.be)


This file is part of the Wikiproject Biodiversity.
The code is intended to run using the BiodivesityBot account on Wikidats

"""

import os
from wikidataintegrator import wdi_core, wdi_login

LANGUAGE = os.environ['LANGUAGE']
WBUSER = os.environ['WDUSER']
WBPASS = os.environ['WDPASS']

# Log into Wikidata
login = wdi_login.WDLogin(WBUSER, WBPASS)

# Query for common names in a select language, of which the header does not contain that label in the language
# Initially only query 10. Gradually increase that number
query = f"""SELECT DISTINCT ?commonname ?taxon  WHERE {{
   ?taxon p:P1843 [ ps:P1843 ?commonname ;
                    prov:wasDerivedFrom ?ref ; ] .


   FILTER (lang(?commonname) = "{LANGUAGE}")
   BIND (lcase(?commonname) as ?lcasecommonname)
   FILTER NOT EXISTS {{{{?taxon skos:altLabel ?commonname }} UNION {{?taxon rdfs:label ?commonname }}
                     {{?taxon skos:altLabel ?lcasecommonname }} UNION {{?taxon rdfs:label ?lcasecommonname }}}}

}}
LIMIT 10"""
common_names = wdi_core.WDItemEngine.execute_sparql_query(query=query, as_dataframe=True)

# Write those labels to Wikidata.
for index, row in common_names.iterrows():
    item = wdi_core.WDItemEngine(wd_item_id=row["taxon"].replace("http://www.wikidata.org/entity/", ""))
    aliases = item.get_aliases(lang=LANGUAGE)
    aliases.append(row["commonname"])
    item.set_aliases(aliases=aliases, lang=LANGUAGE)
    print(item.write(login))