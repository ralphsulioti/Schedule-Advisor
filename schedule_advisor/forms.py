import requests
from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.db import models

from schedule_advisor.models import Class, User
from schedule_advisor.settings import SIS_API_URL


# Retrieved from https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/
# Retrieved from https://stackoverflow.com/questions/11923317/creating-django-forms


def add_default_none(choices):
    return [(None, "Select an option...")] + choices


class SubjectForm(forms.Form):
    subject = forms.CharField(max_length=50)


class ClassSearchForm(forms.Form):
    catalog_number_regex_validator = RegexValidator(
        r"^\d{4}$", "Only 4-digit numbers are allowed as catalog numbers!"
    )

    @staticmethod
    def get_results(cleaned_data, pages=None):
        # cleaned_data: e.g. {'semester': '1238', 'subject': 'KOR', 'keyword': 'Elementary'}
        url_parts = [SIS_API_URL]
        if cleaned_data.get("semester", ""):
            url_parts.append(f"term={cleaned_data['semester']}")
        if cleaned_data.get("subject", ""):
            url_parts.append(f"subject={cleaned_data['subject']}")
        if cleaned_data.get("catalog_number", ""):
            url_parts.append(f"catalog_nbr={cleaned_data['catalog_number']}")
        url = "&".join(url_parts)
        results = []
        current_page = 0
        while pages is None or current_page < pages:
            current_page += 1
            page_results = requests.get(f"{url}&page={str(current_page)}").json()
            if not page_results:
                break
            results += page_results
        # print(cleaned_data)

        if cleaned_data.get("keyword", "") != "":
            keywords = cleaned_data["keyword"].split()
            new_results = []
            for course in results:
                if all([kwd.lower() in course["descr"].lower() for kwd in keywords]):
                    new_results.append(course)
                # for kwd in keywords:
                #    if kwd.lower() in course["descr"].lower():
                #        new_results.append(course)
            results = new_results

        if len(results) == 0:
            return None

        return results

    @staticmethod
    def get_results_from_database(cleaned_data):
        classes = Class.objects
        if cleaned_data.get("semester", ""):
            classes = classes.filter(semester=cleaned_data["semester"])
        if cleaned_data.get("subject", ""):
            classes = classes.filter(subject=cleaned_data["subject"])
        if cleaned_data.get("catalog_number", ""):
            classes = classes.filter(catalog_number=cleaned_data["catalog_number"])
        if cleaned_data.get("keyword", "") != "":
            keywords = cleaned_data["keyword"].split()
            new_results = []
            for course in classes:
                if all([kwd.lower() in course.name.lower() for kwd in keywords]):
                    new_results.append(course)
            return sorted(
                new_results,
                key=lambda c: (
                    c.subject,
                    c.catalog_number,
                    c.class_section,
                    c.component,
                ),
            )
        return sorted(
            list(classes),
            key=lambda c: (c.subject, c.catalog_number, c.class_section, c.component),
        )

    SEMESTER_CHOICES = [
        ("1238", "Fall 2023"),
        ("1236", "Summer 2023"),
        ("1232", "Spring 2023"),
        ("1231", "January 2023"),
        ("1228", "Fall 2022"),
        ("1226", "Summer 2022"),
        ("1222", "Spring 2022"),
        ("1221", "January 2022"),
        ("1218", "Fall 2021"),
        ("1216", "Summer 2021"),
        ("1212", "Spring 2021"),
        ("1211", "January 2021"),
        ("1208", "Fall 2020"),
        ("1206", "Summer 2020"),
        ("1202", "Spring 2020"),
        ("1201", "January 2020"),
    ]

    semester = forms.ChoiceField(
        label="Semester",
        choices=SEMESTER_CHOICES,
        initial=SEMESTER_CHOICES[0][0],
        widget=forms.HiddenInput(),
    )

    SUBJECT_CHOICES = sorted(
        [
            ("AAS", "African-American and African Studies (AAS)"),
            ("ACCT", "Accounting (ACCT)"),
            ("AIRS", "Air Science (AIRS)"),
            ("ALAR", "Architecture and Landscape Architecture (ALAR)"),
            ("AMST", "American Studies (AMST)"),
            ("ANTH", "Anthropology (ANTH)"),
            ("APMA", "Applied Mathematics (APMA)"),
            ("ARAB", "Arabic (ARAB)"),
            ("ARAD", "Arts Administration (ARAD)"),
            ("ARAH", "History of Art and Architecture (ARAH)"),
            ("ARCH", "Architecture (ARCH)"),
            ("ARCY", "Archaeology (ARCY)"),
            ("ARH", "Architectural History (ARH)"),
            ("ARTH", "History of Art (ARTH)"),
            ("ARTR", "Arabic in Translation (ARTR)"),
            ("ARTS", "Studio Art (ARTS)"),
            ("ASL", "American Sign Language (ASL)"),
            ("ASTR", "Astronomy (ASTR)"),
            ("BIMS", "Biomedical Sciences (BIMS)"),
            ("BIOC", "Biochemistry (BIOC)"),
            ("BIOL", "Biology (BIOL)"),
            ("BIOP", "Biophysics (BIOP)"),
            ("BME", "Biomedical Engineering (BME)"),
            ("BUS", "Business (BUS)"),
            ("CASS", "College Art Scholars Seminar (CASS)"),
            ("CE", "Civil Engineering (CE)"),
            ("CELL", "Cell Biology (CELL)"),
            ("CHE", "Chemical Engineering (CHE)"),
            ("CHEM", "Chemistry (CHEM)"),
            ("CHIN", "Chinese (CHIN)"),
            ("CHTR", "Chinese in Translation (CHTR)"),
            ("CLAS", "Classics (CLAS)"),
            ("COGS", "Cognitive Science (COGS)"),
            ("COMM", "Commerce (COMM)"),
            ("CONC", "Commerce-Non-Credit (CONC)"),
            ("CPE", "Computer Engineering (CPE)"),
            ("CREO", "Creole (CREO)"),
            ("CS", "Computer Science (CS)"),
            ("DANC", "Dance (DANC)"),
            ("DEM", "Democracy Initiative (DEM)"),
            ("DH", "Digital Humanities (DH)"),
            ("DRAM", "Drama (DRAM)"),
            ("DS", "Data Science (DS)"),
            ("EALC", "East Asian Languages, Literatures, and Cultures (EALC)"),
            ("EAST", "East Asian Studies (EAST)"),
            ("ECE", "Electrical and Computer Engineering (ECE)"),
            ("ECON", "Economics (ECON)"),
            ("EDHS", "Education-Human Services (EDHS)"),
            ("EDIS", "Education-Curriculum, Instruction, & Special Ed (EDIS)"),
            ("EDLF", "Education-Leadership, Foundations, and Policy (EDLF)"),
            ("EDNC", "Education-Non-Credit (EDNC)"),
            ("EGMT", "Engagement (EGMT)"),
            ("ENCW", "English-Creative Writing (ENCW)"),
            ("ENGL", "English Literature (ENGL)"),
            ("ENGR", "Engineering (ENGR)"),
            ("ENTP", "Entrepreneurship (ENTP)"),
            ("ENVH", "Environmental Humanities (ENVH)"),
            ("ENWR", "English-Academic, Professional, & Creative Writing (ENWR)"),
            ("ESL", "English as a Second Language (ESL)"),
            ("ETP", "Enviromental Thought and Practice (ETP)"),
            ("EURS", "European Studies (EURS)"),
            ("EVAT", "Environmental Sciences-Atmospheric Sciences (EVAT)"),
            ("EVEC", "Environmental Sciences-Ecology (EVEC)"),
            ("EVGE", "Environmental Sciences-Geosciences (EVGE)"),
            ("EVHY", "Environmental Sciences-Hydrology (EVHY)"),
            ("EVSC", "Environmental Sciences (EVSC)"),
            ("FREN", "French (FREN)"),
            ("FRTR", "French in Translation (FRTR)"),
            ("GBAC", "Graduate Business Analytics Commerce (GBAC)"),
            ("GBUS", "Graduate Business (GBUS)"),
            ("GCCS", "Global Commerce in Culture and Society (GCCS)"),
            ("GCNL", "Clinical Nurse Leader (GCNL)"),
            ("GCOM", "Graduate Commerce (GCOM)"),
            ("GDS", "Global Development Studies (GDS)"),
            ("GERM", "German (GERM)"),
            ("GETR", "German in Translation (GETR)"),
            ("GHSS", "Graduate Humanities and Social Sciences (GHSS)"),
            ("GNUR", "Graduate Nursing (GNUR)"),
            ("GREE", "Greek (GREE)"),
            ("GSGS", "Global Studies-Global Studies (GSGS)"),
            ("GSMS", "Global Studies: Middle East and South Asia (GSMS)"),
            ("GSSJ", "Global Studies-Security and Justice (GSSJ)"),
            ("GSVS", "Global Studies-Environments and Sustainability (GSVS)"),
            ("HBIO", "Human Biology (HBIO)"),
            ("HEBR", "Hebrew (HEBR)"),
            ("HHE", "Health, Humanities & Ethics (HHE)"),
            ("HIAF", "History-African History (HIAF)"),
            ("HIEA", "History-East Asian History (HIEA)"),
            ("HIEU", "History-European History (HIEU)"),
            ("HILA", "History-Latin American History (HILA)"),
            ("HIME", "History-Middle Eastern History (HIME)"),
            ("HIND", "Hindi (HIND)"),
            ("HISA", "History-South Asian History (HISA)"),
            ("HIST", "History-General History (HIST)"),
            ("HIUS", "History-United States History (HIUS)"),
            ("HR", "Human Resources (HR)"),
            ("HSCI", "College Science Scholars Seminar (HSCI)"),
            ("IMP", "Interdisciplinary Thesis (IMP)"),
            ("INST", "Interdisciplinary Studies (INST)"),
            ("ISBU", "Interdisciplinary Studies-Business (ISBU)"),
            ("ISHU", "Interdisciplinary Studies-Humanities (ISHU)"),
            ("ISIN", "Interdisciplinary Studies-Code of Inquiry (ISIN)"),
            ("ISLS", "Interdisciplinary Studies-Liberal Studies Seminar (ISLS)"),
            ("ISSS", "Interdisciplinary Studies-Social Sciences (ISSS)"),
            ("IT", "Informational Technology (IT)"),
            ("ITAL", "Italian (ITAL)"),
            ("ITTR", "Italian in Translation (ITTR)"),
            ("JAPN", "Japanese (JAPN)"),
            ("JPTR", "Japanese in Translation (JPTR)"),
            ("JWST", "Jewish Studies (JWST)"),
            ("KICH", "Maya K'iche' (KICH)"),
            ("KINE", "Kinesiology (KINE)"),
            ("KLPA", "Kinesiology Lifetime Physical Activity (KLPA)"),
            ("KOR", "Korean (KOR)"),
            ("LAR", "Landscape Architecture (LAR)"),
            ("LASE", "Liberal Arts Seminar (LASE)"),
            ("LAST", "Latin American Studies (LAST)"),
            ("LATI", "Latin (LATI)"),
            ("LAW", "Law (LAW)"),
            ("LING", "Linguistics (LING)"),
            ("LNGS", "General Linguistics (LNGS)"),
            ("LPPA", "Leadership Public Policy - Analysis (LPPA)"),
            ("LPPL", "Leadership Public Policy - Leadership (LPPL)"),
            ("LPPP", "Leadership Public Policy - Policy (LPPP)"),
            ("LPPS", "Leadership Public Policy - Substance (LPPS)"),
            ("MAE", "Mechanical & Aerospace Engineering (MAE)"),
            ("MATH", "Mathematics (MATH)"),
            ("MDST", "Media Studies (MDST)"),
            ("MED", "Medicine (MED)"),
            ("MESA", "Middle Eastern & South Asian Languages & Cultures (MESA)"),
            ("MEST", "Middle Eastern Studies (MEST)"),
            ("MICR", "Microbiology (MICR)"),
            ("MISC", "Military Science (MISC)"),
            ("MSE", "Materials Science and Engineering (MSE)"),
            ("MSP", "Medieval Studies (MSP)"),
            ("MUBD", "Music-Marching Band (MUBD)"),
            ("MUEN", "Music-Ensembles (MUEN)"),
            ("MUPF", "Music-Private Performance Instruction (MUPF)"),
            ("MUSI", "Music (MUSI)"),
            ("NASC", "Naval Science (NASC)"),
            ("NCPR", "Non-Credit Professional Review (NCPR)"),
            ("NESC", "Neuroscience (NESC)"),
            ("NUCO", "Nursing Core (NUCO)"),
            ("NUIP", "Nursing Interprofessional (NUIP)"),
            ("NURS", "Nursing (NURS)"),
            ("PATH", "Pathology (PATH)"),
            ("PC", "Procurement and Contracts Management (PC)"),
            ("PERS", "Persian (PERS)"),
            ("PETR", "Persian in Translation (PETR)"),
            ("PHAR", "Pharmacology (PHAR)"),
            ("PHIL", "Philosophy (PHIL)"),
            ("PHS", "Public Health Sciences (PHS)"),
            ("PHY", "Physiology (PHY)"),
            ("PHYS", "Physics (PHYS)"),
            ("PLAC", "Planning Application (PLAC)"),
            ("PLAD", "Politics-Departmental Seminar (PLAD)"),
            ("PLAN", "Urban and Environmental Planning (PLAN)"),
            ("PLAP", "Politics-American Politics (PLAP)"),
            ("PLCP", "Politics-Comparative Politics (PLCP)"),
            ("PLIR", "Politics-International Relations (PLIR)"),
            ("PLPT", "Politics-Political Theory (PLPT)"),
            ("PMCC", "Premodern Cultures and Communities (PMCC)"),
            ("POL", "Polish (POL)"),
            ("PORT", "Portuguese (PORT)"),
            ("PPL", "Political Philosophy, Policy, and Law (PPL)"),
            ("PSHM", "Professional Studies-Health Sciences Management (PSHM)"),
            ("PSLP", "PS-Leadership Program (PSLP)"),
            ("PSPA", "Professional Studies-Public Administration (PSPA)"),
            ("PSPM", "Professional Studies-Project Management (PSPM)"),
            ("PSPS", "Professional Studies - Public Safety (PSPS)"),
            ("PST", "Political and Social Thought (PST)"),
            ("PSYC", "Psychology (PSYC)"),
            ("RELA", "Religion-African Religions (RELA)"),
            ("RELB", "Religion-Buddhism (RELB)"),
            ("RELC", "Religion-Christianity (RELC)"),
            ("RELG", "Religion-General Religion (RELG)"),
            ("RELH", "Religion-Hinduism (RELH)"),
            ("RELI", "Religion-Islam (RELI)"),
            ("RELJ", "Religion-Judaism (RELJ)"),
            ("RELS", "Religion-Special Topic (RELS)"),
            ("RSC", "Regional Studies Consortium (RSC)"),
            ("RUSS", "Russian (RUSS)"),
            ("RUTR", "Russian in Translation (RUTR)"),
            ("SANS", "Sanskrit (SANS)"),
            ("SARC", "Architecture School (SARC)"),
            ("SAST", "South Asian Studies (SAST)"),
            ("SATR", "South Asian Literature in Translation (SATR)"),
            ("SEC", "CYB SEC Analysis (SEC)"),
            ("SLAV", "Slavic (SLAV)"),
            ("SLFK", "Slavic Folklore & Oral Literature (SLFK)"),
            ("SOC", "Sociology (SOC)"),
            ("SPAN", "Spanish (SPAN)"),
            ("STAT", "Statistics (STAT)"),
            ("STS", "Science, Technology, and Society (STS)"),
            ("SWAH", "Swahili (SWAH)"),
            ("SYS", "Systems & Information Engineering (SYS)"),
            ("TURK", "Turkish (TURK)"),
            ("UD", "Urban Design (UD)"),
            ("UNST", "University Studies (UNST)"),
            ("URDU", "Urdu (URDU)"),
            ("USEM", "University Seminar (USEM)"),
            ("WGS", "Women, Gender, and Sexuality (WGS)"),
        ],
        key=lambda s: s[1],
    )

    subject = forms.ChoiceField(
        label="Subject", choices=add_default_none(SUBJECT_CHOICES), required=False
    )

    catalog_number = forms.CharField(
        label="Catalog Number",
        max_length=4,
        min_length=4,
        required=False,
        validators=[catalog_number_regex_validator],
    )

    keyword = forms.CharField(
        label="Keyword",
        max_length="50",
        min_length="1",
        strip=True,
        empty_value="",
        required=False,
    )


class AdviseeChoiceForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
