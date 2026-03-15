# Schema KOR pour l'objet
from kor.nodes import Object, Text, Number

def clone_kor_object(obj, keepDescription=True, keepExamples=True):
    if type(obj) == Text:
        return Text(
            id=obj.id,
            description=obj.description if keepDescription else "",
            many=obj.many,
            examples=obj.examples if keepExamples else []
        )
    
    if type(obj) == Number:
        return Number(
            id=obj.id,
            description=obj.description if keepDescription else "",
            many=obj.many,
            examples=obj.examples if keepExamples else []
        )
    else:
        return Object(
        id=obj.id,
        description=obj.description if keepDescription else "",
        many=obj.many,
        examples=obj.examples if keepExamples else [],
        attributes=[clone_kor_object(attr, keepDescription, keepExamples) for attr in obj.attributes]
    )


languages_schema = Object(
    id="languages",
    description="Langues parlées par la personne",
    attributes=[
        Text(id="name", description="Nom de la langue"),
        Text(id="level", description= "Niveau dans la langue. Si le niveau semble exprimé en pastilles, le convertir avec l\'echelle suivante de 1 à 5 pastilles : [Débutant, Intermédiaire, Avancé, Courant, Maternel]"),
    ],
    examples=[],
    many=True,
)

educations_schema = Object(
    id="educations",
    description="Ecole, université, ou tout autre diplôme",
    attributes=[
        Text(id="name", description="Nom de l\'école, université, et/ou diplôme"),
        Number(id="year", description= "Année d\'obtention"),
    ],
    many=True,
    examples=[],
)

certifications_schema = Object(
    id="certifications",
    description="Certifications et formations n'étant pas des diplômes",
    attributes=[
        Text(id="name", description="Nom complet de la formation ou de la certification."),
        Text(id="date", description= "Année d'obtention de la certification, si renseignée. si renseignée, format: MM-YYYY ou YYYY si le mois n'est pas renseigné. Si deux années sont renseignées, seule l'année la plus élevée doit être mise"),
    ],
    many=True,
    examples=[],
)

activity_domains_schema = Object(
    id="activityDomains",
    description="Domaines/Secteurs d'activité professionnelles où la personne a de l'expérience/habitude de travailler.",
    attributes=[
        Text(id="domaine", description="Nom du domaine (exemple : Energie, Santé, Administration publique)"),
    ],
    many=True,
    examples=[],
)

skills_schema = Object(
    id="skillsDomains",
    description="Domaines de compétences. Ces domaines s'articulent autour d'un thème et d'un ensemble de compétence groupées autour de ce thème",
    attributes=[
        Text(id="domain", description="Nom du domaine/groupe de compétence (exemple : Langages de programmation, Outils)"),
        Text(id="skills", description= "Compétence. Généralement séparée par une virgule ou un retour à la ligne.", many=True),
    ],
    many=True,
    examples=[]
)

missions_schema = Object(
    id="missions",
    description="Missions et expériences professionnelles de la personne.",
    attributes=[
        Text(id="poste", description="Poste/Métier durant la mission. Si manquant, renseigner \"POSTE_MANQUANT\" dans ce champs."),
        Text(id="startDate", dlescription="Date de début de la mission/emploi, parfois précédé par le mot 'Depuis', format attendu : MM-YYYY avec MM le mois (en chiffre) et YYYY l'année (en chiffres). Les informations à extraire sont parfois renseignées au format MM/YYYY, dans ce cas remplace le \"/\" par un \"-\". Si pas de date renseignée, renseigne \"01-1950\"."),# Si le mois est renseigné en lettres, convertit le en nombre."),
        Text(id="endDate", description="Date de fin de la mission/emploi, format attendu : MM-YYYY avec MM le mois (en chiffre) et YYYY l'année (en chiffres). Si  pas de date de fin renseignée, laisser ce champs vide."),
        Text(id="company", description="Nom de l\'entreprise de la mission. Présent généralement dans l\'entête de la mission, avant le poste et les dates. Ne pas inclure un éventuel département, groupe, ou service, dans ce champs."),
        Text(id="department", description="Nom du groupe, service, ou département de l'entreprise où la mission se déroulait. Généralement situé après le nom de l'entreprise. Cela peut correspondre à un service ou sous groupe de l'entreprise (par exemple, 'Relation clients') ou une branche dans un autre pays/ville ('Canada' par exemple dans 'Talan - Canada'). Si introuvable, laisser vide."),
        Text(id="contextSummary", description="Contexte de la mission en quelques phrases. Reprend autant que possible le texte original. Correspond parfois au texte suivant les terme \"Objet\" ou \"Contexte\" de la mission ou du projet. Si introuvable, remplir avec \"CONTEXTE MANQUANT\""),
        Text(id="location", description="Lieu géographique de la mission (ville et/ou pays). Ce lieu est défini en début de mission, pas à la fin. Si introuvable, laisser vide."),
        Text(id="tasks", description="Tâches réalisées dans le cadre de la mission. Généralement séparées par des retour à la ligne, mais peuvent continuer sur plusieurs lignes. Renvoie l'intégralité du texte de chaque tâche.", many=True),
        Text(id="skills", description="Compétences/Logiciels/outils utilisés dans la mission. Généralement séparé par des virgules. Souvent définies après le terme 'Environnement' ou 'Environnement technique', ou 'Outils'.", many=True),           
    ],
    many=True,
    partial=True,
    examples=[],
)

missions_wrapper = Object(
    id="allMissions",
    description="Missions et expériences professionnelles de la personne. Regroupe toutes les missions dans une meme entrée 'missions' en tant que liste. Evite de générer plusieurs listes. Renvoie un JSON valide et complet. N'ajoute pas de commentaires supplémentaires, ni d'autres champs. Renvoie un JSON valide et complet.",
    attributes=[missions_schema]
)


resume_schema = Object(
            id= "extractCvInfo",
            description= "CV d'une personne. Extrait toutes les informations que tu peux trouver depuis le texte en entrée, pour compléter les champs définis. Utilise les informations liées aux missions et expériences professionnelles uniquement pour remplir le champs missions.",
            attributes=[
                Text(id="poste", description="Métier/Poste général de la personne. Si introuvable, remplir avec le texte suivant : '###'"),
                Number(id="seniority", description="Nombre d\'années d\'expériences professionnelles de la personne. Si introuvable ou impossible à calculer, mettre 0."),
                Text(id="introduction",description= "Court résumé professionnel de la personne. Généralement situé au début du CV. Laisser vide si introuvable"),
                languages_schema,
                skills_schema,
                educations_schema,
                certifications_schema,
                activity_domains_schema,
                missions_schema
                ],
            examples=[],
)