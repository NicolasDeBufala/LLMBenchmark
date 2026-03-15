from src.prompts.PromptBaseClass import PromptBaseClass
import json

expected_json_format = {
    "tables": [
        {
            "database": "string",
            "schema": "string",
            "table_name": "string",
            "references": [
                {
                    "type": "table or partition or expression",
                    "name": "string"
                }
            ]
        }
    ]
}


class PromptLineageSimple(PromptBaseClass):

    def __init__(self, idSchema: str):
        super().__init__(idSchema, "lineageSimple")

    def get_prompt(self, option: str = "") -> tuple[str, str]:

        return "Tu vas recevoir un extrait d'un modèle PowerBI. Ton objectif est d'extraire de ce document l'ensemble des noms de table Snowflake utilisées dans ce modèle." \
            "Pour chaque table Snowflake trouvée, indique les informations suivantes : database, schema, table_name, et l'ensemble des tables/partitions/expressions qui font référence à cette table Snowflake." \
                "Le format attendu est donc un JSON au format suivant : " + json.dumps(expected_json_format) +"\n Ne renvoie que le JSON, sans explication supplémentaires."\
                    " Si plusieurs databases sont possibles pour un champ, celle de production (PRD/PROD) est à choisir. Si le paramètre a une valeur par défaut, celle ci doit être choisie. Si aucune table Snowflake n'est référencée, la liste de table doit donc rester vide."\
                        "Si une table est citée au milieu d'une expression de code M, la database en question est la même que la database globale de l'expression. Le nom d'une database est toujours différent du nom du schéma et de la table. La database est généralement définie à l'aide d'une rexpression comme 'Database', et est ré-utilisée dans tout l'extract."\
                            "Par exemple : 'Source = Value.NativeQuery(Snowflake.Databases(\"ua86299.north-europe.azure.snowflakecomputing.com\",Warehouse,[Role=Role]){[Name=Database]}[Data]' en début d'expression indique que chaque table citée ensuite doit provenir de la même database. Si database = DB_CDM_PRD, alors les références suivantes 'from COMMON.DIM_ACCOUNT_ACTIVITY aa LEFT JOIN CARRIER.DIM_GEOGRAPHY g' doit être traduit en ' DB_CDM_PRD.COMMON.DIM_ACCOUNT_ACTIVITY' et 'DB_CDM_PRD.CARRIER.DIM_GEOGRAPHY'  ", "lineageSimple"
