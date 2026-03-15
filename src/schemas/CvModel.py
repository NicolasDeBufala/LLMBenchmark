from pydantic import BaseModel, field_validator
from typing import Optional, List
from sqlalchemy import Column, String, LargeBinary, ARRAY, Boolean, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import JSONB
import datetime

class Comment(BaseModel):
    id: str
    date: str
    content: str
    active: bool #Active, solved
    dateSolve: Optional[str]
    author: str
    parentId: Optional[str]
    section: str
    mission: Optional[str]

    def __init__(self, **kwargs):    
        if "dateSolve" not in kwargs :
            kwargs["dateSolve"] = ""
        if "content" not in kwargs :
            kwargs["content"] = "emptyComment"
        if "date" not in kwargs :
            now = datetime.now()
            kwargs["date"] = now.strftime('%d-%m-%Y %H:%M')
        if "active" not in kwargs :
            kwargs["active"] = True
        if "author" not in kwargs :
            kwargs["author"] = "John Doe"
        super().__init__(**kwargs)


    def solve_comment(self):
        self.active = False
        now = datetime.now()
        self.dateSolve =  now.strftime('%d-%m-%Y')
    

class BaseModelWithComments(BaseModel):
    comments: Optional[List[Comment]] = []

    # update_order: bool

    def __init__(self, **kw):
        super().__init__(**kw)
        # self.update_order=False

    def get_comments(self):
        # if self.comments and self.update_order:
        #     self.update_order = False
        #     self.sort_comments()
        self.sort_comments()
        return self.comments


    def sort_comments(self):
        self.comments = sorted(self.comments, reverse=True, key=cmp_to_key(comment_sort_order))

    def add_comment(self, text, author):
        if self.comments is None:
            self.comments = []
        self.comments.insert(0, Comment(content=text, author=author))

    def has_comments(self):
        if self.comments is None:
            return False
        else:
            return len(self.comments) > 0

    def has_unresolved_comments(self):
        if self.comments is None:
            return False
        else:
            for comm in self.comments:
                if comm.active:
                    return True
            return False        


def cmp_date(d1: str, d2: str):
    dt1 = datetime.strptime(d1, "%d-%m-%Y %H:%M")
    dt2 = datetime.strptime(d2, "%d-%m-%Y %H:%M")
    if dt1 < dt2:
        return -1
    elif dt2 == dt1:
        return 0
    else:
        return 1


def comment_sort_order(x: Comment, y: Comment):
    if x.active:
        if y.active:
            return cmp_date(x.date, y.date)
        else :
            return 1
    else:
        if y.active:
            return -1
        else:
            return cmp_date(x.date, y.date)
            


class Mission(BaseModel):
    startDate: str
    endDate: Optional[str]
    company: str
    department: Optional[str]
    poste: str
    description: Optional[str]
    context_summary: str
    tasks: List[str]
    skills: List[str]
    location: Optional[str]

    def __init__(self, **kwargs):
        # print("Mission : ", kwargs)    
        if "location" not in kwargs :
            kwargs["location"] = ""
        if "skills" not in kwargs :
            kwargs["skills"] = []
        if "tasks" not in kwargs :
            kwargs["tasks"] = []
        if "context_summary" not in kwargs :
            kwargs["context_summary"] = ""
        if "description" not in kwargs :
            kwargs["description"] = ""
        if "poste" not in kwargs :
            kwargs["poste"] = ""
        if "company" not in kwargs :
            kwargs["company"] = ""
        if "department" not in kwargs :
            kwargs["department"] = ""
        if "startDate" not in kwargs:
            kwargs["startDate"] = "01-1950"
        if "endDate" not in kwargs:
            kwargs["endDate"] = ""
            # print("endDate was reset ")
        if "endDate" in kwargs and type(kwargs["endDate"]) != str:
            # print("endDate was of type ", type(kwargs["endDate"]), "and was reset since its value was ", kwargs["endDate"])
            kwargs["endDate"] = "01-1950"

        for k in kwargs:
            if type(kwargs[k]) == str:
                kwargs[k] = kwargs[k].strip()
                if(kwargs[k]) in ["xxx", "/", "XXX", "##", "xxxx", "xxxxx", "N/A", "Inconnu"]:
                    # print(k, kwargs[k])
                    kwargs[k] = "###"     


        super().__init__(**kwargs)


class Language(BaseModel):
    name: str
    level: str
    numeric_level: Optional[int]

    def __init__(self, **kwargs):    
        if "level" not in kwargs or kwargs["level"] == None:
            kwargs["level"] = "Non renseigné"
        if "numeric_level" not in kwargs or kwargs["numeric_level"] == None:
            kwargs["numeric_level"] = -1
        for k in kwargs:
            if type(kwargs[k]) == str:
                kwargs[k] = kwargs[k].strip()
                if(kwargs[k]) in ["xxx", "/", "XXX", "##", "xxxx", "xxxxx", "N/A", "Inconnu"]:
                    kwargs[k] = "###"
        super().__init__(**kwargs)


class Education(BaseModel):
    name: str
    year: int

    def __init__(self, **kwargs):    
        if "year" not in kwargs or kwargs["year"] == None:
            kwargs["year"] = -1
        super().__init__(**kwargs)


class Certification(BaseModel):
    name: str
    date: Optional[str]

    def __init__(self, **kwargs):
        for k in kwargs:
            if type(kwargs[k]) == String:
                kwargs[k] = kwargs[k].strip()
                if(kwargs[k]) in ["xxx", "/", "XXX", "##", "xxxx", "xxxxx", "N/A", "Inconnu"]:
                    kwargs[k] = "###"
        super().__init__(**kwargs)


class SkillsByDomain(BaseModel):
    domain: str
    skills: List[str]

    def __init__(self, **kwargs):    
        if "skills" not in kwargs or kwargs["skills"] == None:
            kwargs["skills"] = []
        kwargs["domain"] = kwargs["domain"].strip()
        super().__init__(**kwargs)


class ActivityDomain(BaseModel):
    domain: str

    def __init__(self, **kwargs):    
        kwargs["domain"] = kwargs["domain"].strip()
        super().__init__(**kwargs)

class OptionalCharacteristic(BaseModel):
    name: str
    checked: bool

dico_labels_annotation = {"noSkills": "Pas de compétences",
                          "englishCV": "CV en anglais",
                          "noJobTitle": "Pas de titre de poste", 
                          "noMissions": "Pas de missions/expériences professionnelles",
                          "noEducation": "Pas de formation/diplôme",
                          "noLanguages": "Pas de langues parlées",
                          "noSeniority": "Pas de niveau de séniorité",
                          "notAnonymized": "Pas anonymisé du tout",
                          "noIntroduction": "Pas d'introduction",
                          "noSkillDomains": "Pas de domaines de compétences",
                          "cvInColumnFormat": "Le CV est structuré en au moins deux colonnes",
                          "noCertifications": "Pas de certifications",
                          "noActivityDomains": "Pas de domaines d'activité",
                          "cvInOriginalFormat": "Le CV a une forme originale/inattendue/peu commune",
                          "bulletForSkillLevels": "Niveau de compétences avec des pastilles/bullet",
                          "problemAnonymisation": "Problème d'anonymisation (nom, mail, téléphone, etc...)",
                          "bulletForLanguageLevels": "Niveau en langues définis avec des pastilles/bullet"
                          }

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class CVData(BaseModel):
    id: str
    firstname: str
    lastname: str
    poste: str
    introduction: str
    seniority: int
    missions: List[Mission]
    languages: List[Language]
    educations: List[Education]
    certifications: List[Certification]
    skills: List[SkillsByDomain]
    activity_domains: List[ActivityDomain]
    comments: Optional[BaseModelWithComments] = None  # Allow None for comments
    id_user: Optional[str] = None
    label: str
    status: int
    primary_cv: bool

    def __init__(self, **kwargs):
        if "poste" not in kwargs or kwargs["poste"] is None or kwargs["poste"] == "":
            kwargs["poste"] = "###"
        if "introduction" not in kwargs or kwargs["introduction"] is None or kwargs["introduction"] == "":
            kwargs["introduction"] = "###"
        
        super().__init__(**kwargs)
    
    @field_validator('seniority', mode='before')
    @classmethod
    def validate_seniority(cls, v):
        """Validate seniority is an integer. Coerce floats to int by truncating."""
        if v is None:
            return 0
        if isinstance(v, float):
            # Coerce float to int (4.5 → 4)
            return int(v)
        if isinstance(v, str):
            try:
                return int(float(v))
            except (ValueError, TypeError):
                return 0
        return int(v) if v else 0
    @classmethod
    def from_json(cls, row: dict):
        try:
            cv = CVData(
            id=row.get("id", ""),
            firstname=row.get("firstname", "###"),
            lastname=row.get("lastname", "###"),
            poste=row.get("poste", "POSTE MANQUANT"),
            introduction=row.get("introduction", ""),
            seniority=row.get("seniority", 0),
            missions=[Mission(**mission) for mission in row.get("missions", [])],
            languages=[Language(**lang) for lang in row.get("languages", [])],
            educations=[Education(**edu) for edu in row.get("educations", [])],
            certifications=[Certification(**cert) for cert in row.get("certifications", [])],
            skills=[SkillsByDomain(**skill) for skill in (row.get("skillsDomains", []) or row.get("skills", []))],
            activity_domains=[ActivityDomain(**domain) for domain in row.get("activity_domains", [])],
            comments= {"comments": []},
            id_user=row.get("id_user", "llm_result"),
            label=row.get("label", "CV INITIAL V2"),
            status=row.get("status", 0),
            primary_cv=True,
        )
            return cv
        except Exception as e:
            print(f"Error parsing CV data: {e}")
            print(f"CV data was: {row}")
            return None
        
    
class CVDb(Base):
    __tablename__ = 'cvs'

    id = Column(String, primary_key=True, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    poste = Column(String, nullable=False)
    seniority= Column(Integer, nullable=False)
    introduction = Column(String)
    missions = Column(ARRAY(JSONB))
    languages = Column(ARRAY(JSONB))
    educations = Column(ARRAY(JSONB))
    certifications = Column(ARRAY(JSONB))
    skills = Column(ARRAY(JSONB))
    activity_domains = Column(ARRAY(JSONB))
    comments = Column(JSONB)
    id_user = Column(String)
    status = Column(Integer) #0 : Just created or has comment to resolve, 1 if sent to a manager and waiting for review 2 if valid.
    label = Column(String, default="")
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    primary_cv = Column(Boolean, default=False)
