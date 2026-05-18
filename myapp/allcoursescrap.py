"""
career_data_fetcher.py
======================
Two public functions:

    fetch_by_course_or_department(query: str) -> dict
        Returns scraped + NLP-analysed data for ONE course or department.

    fetch_all_courses_by_department() -> dict
        Returns ALL courses, neatly grouped under their parent departments.

Install dependencies:
    pip install requests beautifulsoup4 nltk rake-nltk pytrends colorama tabulate
"""

import re
import time
import json
import random
import warnings
from collections import Counter
from typing import Optional

import requests
from bs4 import BeautifulSoup

from myapp.models import DEPARTMENT_table, COUSE_table

warnings.filterwarnings("ignore")

# ── Optional NLP libraries ───────────────────────────────────────────────────
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    for _pkg in ("punkt", "stopwords", "punkt_tab"):
        nltk.download(_pkg, quiet=True)
    _NLTK_OK = True
except ImportError:
    _NLTK_OK = False

try:
    from rake_nltk import Rake
    _RAKE_OK = True
except ImportError:
    _RAKE_OK = False

try:
    from pytrends.request import TrendReq
    _PYTRENDS_OK = True
except ImportError:
    _PYTRENDS_OK = False


# ══════════════════════════════════════════════════════════════════════════════
#  KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

# Every course profile lives here.
# Keys are lowercase identifiers; 'department' links them to a parent group.
# COURSE_PROFILES: dict[str, dict] = {
#
#     # ── Computer Science ──────────────────────────────────────────────────
#     "bca": {
#         "label":      "BCA (Bachelor of Computer Applications)",
#         "department": "Computer Science",
#         "search_keywords": [
#             "BCA jobs 2024 India",
#             "computer applications fresher skills demand",
#             "software developer fresher jobs India",
#             "web developer jobs India fresher",
#         ],
#         "skill_seeds": [
#             "Python", "Java", "SQL", "web development", "React",
#             "Node.js", "cloud computing", "machine learning",
#             "data structures", "cybersecurity",
#         ],
#         "job_seeds": [
#             "Software Developer", "Web Developer", "Data Analyst",
#             "System Administrator", "Database Administrator", "IT Support",
#         ],
#     },
#
#     "bsc cs": {
#         "label":      "BSc Computer Science",
#         "department": "Computer Science",
#         "search_keywords": [
#             "BSc CS jobs 2024 India",
#             "computer science fresher skills India",
#             "data science jobs India fresher",
#             "AI engineer fresher India",
#         ],
#         "skill_seeds": [
#             "Python", "C++", "algorithms", "machine learning", "data science",
#             "artificial intelligence", "Linux", "AWS", "DevOps", "R programming",
#         ],
#         "job_seeds": [
#             "Data Scientist", "ML Engineer", "Software Engineer",
#             "Research Analyst", "Cloud Engineer", "DevOps Engineer",
#         ],
#     },
#
#     "mca": {
#         "label":      "MCA (Master of Computer Applications)",
#         "department": "Computer Science",
#         "search_keywords": [
#             "MCA jobs 2024 India",
#             "MCA fresher career opportunities",
#             "full stack developer MCA jobs",
#         ],
#         "skill_seeds": [
#             "Java", "Spring Boot", "Python", "Django", "cloud computing",
#             "microservices", "Docker", "Kubernetes", "SQL", "REST APIs",
#         ],
#         "job_seeds": [
#             "Full Stack Developer", "Software Engineer", "System Analyst",
#             "Cloud Architect", "Project Manager", "Database Developer",
#         ],
#     },
#
#     "Msc": {
#         "label": "Msc (Master of Computer Science)",
#         "department": "Computer Science",
#         "search_keywords": [
#             "MSC jobs 2024 India",
#             "MSC fresher career opportunities",
#             "full stack developer MSC jobs",
#         ],
#         "skill_seeds": [
#             "Java", "Spring Boot", "Python", "Django", "cloud computing",
#             "microservices", "Docker", "Kubernetes", "SQL", "REST APIs",
#         ],
#         "job_seeds": [
#             "Full Stack Developer", "Software Engineer", "System Analyst",
#             "Cloud Architect", "Project Manager", "Database Developer",
#         ],
#     },
#
#     # ── Commerce ──────────────────────────────────────────────────────────
#     "bcom": {
#         "label":      "BCom (Bachelor of Commerce)",
#         "department": "Commerce",
#         "search_keywords": [
#             "BCom jobs 2024 India",
#             "commerce graduate career options",
#             "accountant fresher jobs India",
#             "finance analyst India fresher",
#         ],
#         "skill_seeds": [
#             "Tally", "GST", "accounting", "Excel", "financial analysis",
#             "auditing", "taxation", "SAP", "QuickBooks", "cost accounting",
#         ],
#         "job_seeds": [
#             "Accountant", "Finance Analyst", "Tax Consultant",
#             "Auditor", "Banking Executive", "Credit Analyst",
#         ],
#     },
#
#     "bba": {
#         "label":      "BBA (Bachelor of Business Administration)",
#         "department": "Commerce",
#         "search_keywords": [
#             "BBA jobs 2024 India",
#             "business administration fresher career India",
#             "marketing executive jobs India",
#             "HR executive fresher jobs",
#         ],
#         "skill_seeds": [
#             "marketing", "digital marketing", "sales", "CRM", "leadership",
#             "project management", "Excel", "branding", "SEO", "communication",
#         ],
#         "job_seeds": [
#             "Marketing Executive", "HR Executive", "Sales Manager",
#             "Business Analyst", "Operations Manager", "Brand Manager",
#         ],
#     },
#
#     "mba": {
#         "label":      "MBA (Master of Business Administration)",
#         "department": "Commerce",
#         "search_keywords": [
#             "MBA jobs 2024 India",
#             "MBA fresher career options",
#             "management trainee jobs India",
#         ],
#         "skill_seeds": [
#             "strategy", "leadership", "financial modeling", "business analytics",
#             "supply chain", "project management", "Excel", "PowerBI", "CRM", "consulting",
#         ],
#         "job_seeds": [
#             "Management Trainee", "Business Analyst", "Product Manager",
#             "Consultant", "Operations Manager", "Strategy Analyst",
#         ],
#     },
#
#     # ── Science ───────────────────────────────────────────────────────────
#     "bsc": {
#         "label":      "BSc (General Science)",
#         "department": "Science",
#         "search_keywords": [
#             "BSc graduate jobs 2024 India",
#             "science graduate career options India",
#             "data analyst BSc India",
#             "research jobs fresher India",
#         ],
#         "skill_seeds": [
#             "data analysis", "Excel", "statistics", "Python", "research methodology",
#             "laboratory skills", "scientific writing", "SPSS", "Tableau",
#         ],
#         "job_seeds": [
#             "Research Assistant", "Lab Technician", "Data Analyst",
#             "Quality Analyst", "Science Teacher", "Content Writer",
#         ],
#     },
#
#     "bsc biotech": {
#         "label":      "BSc Biotechnology",
#         "department": "Science",
#         "search_keywords": [
#             "BSc biotechnology jobs 2024 India",
#             "biotech fresher career India",
#             "pharmaceutical research jobs fresher",
#         ],
#         "skill_seeds": [
#             "PCR", "cell culture", "bioinformatics", "ELISA", "genomics",
#             "Python for bioinformatics", "laboratory techniques", "CRISPR", "data analysis",
#         ],
#         "job_seeds": [
#             "Research Assistant", "QA Analyst", "Biotech Analyst",
#             "Lab Technician", "Clinical Research Associate", "Bioinformatics Analyst",
#         ],
#     },
#
#     # ── Arts / Humanities ─────────────────────────────────────────────────
#     "ba english": {
#         "label":      "BA English",
#         "department": "Arts",
#         "search_keywords": [
#             "BA English jobs 2024 India",
#             "content writer jobs India fresher",
#             "copywriter fresher India",
#             "editor jobs fresher India",
#         ],
#         "skill_seeds": [
#             "content writing", "copywriting", "SEO writing", "editing", "proofreading",
#             "creative writing", "blogging", "social media", "communication", "UX writing",
#         ],
#         "job_seeds": [
#             "Content Writer", "Copywriter", "Editor", "Technical Writer",
#             "Social Media Manager", "PR Executive", "Teacher",
#         ],
#     },
#
#     "ba psychology": {
#         "label":      "BA/BSc Psychology",
#         "department": "Arts",
#         "search_keywords": [
#             "psychology graduate jobs 2024 India",
#             "counsellor jobs India fresher",
#             "HR psychology careers India",
#             "UX researcher jobs fresher India",
#         ],
#         "skill_seeds": [
#             "counselling", "psychometric testing", "research methodology",
#             "active listening", "HR management", "UX research",
#             "cognitive behavioural therapy", "SPSS", "data analysis",
#         ],
#         "job_seeds": [
#             "Counsellor", "HR Specialist", "UX Researcher",
#             "School Psychologist", "Market Researcher", "Trainer",
#         ],
#     },
# }

#
# dep=DEPARTMENT_table.objects.all()
# courses=COUSE_table.objects.all()
# course_profiles=[]
#
# for i in courses:
#     course_profiles.append({
#         "name":i.id,
#     })





"""
career_data_fetcher.py - Final Fixed Version
"""

import re
import time
import json
import random
import warnings
import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

import requests
from bs4 import BeautifulSoup

import django
from django.conf import settings

warnings.filterwarnings("ignore")

# ====================== DJANGO SETUP ======================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')  # ← CHANGE TO YOUR PROJECT
django.setup()

from myapp.models import DEPARTMENT_table, COUSE_table   # ← Update app name if needed

# ====================== NLP SETUP ======================
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    for _pkg in ("punkt", "stopwords", "punkt_tab"):
        nltk.download(_pkg, quiet=True)
    _NLTK_OK = True
except ImportError:
    _NLTK_OK = False

try:
    from rake_nltk import Rake
    _RAKE_OK = True
except ImportError:
    _RAKE_OK = False

try:
    from pytrends.request import TrendReq
    _PYTRENDS_OK = True
except ImportError:
    _PYTRENDS_OK = False


# ====================== DYNAMIC PROFILES ======================
COURSE_PROFILES: dict[str, dict] = {}
DEPARTMENT_MAP: dict[str, list[str]] = {}


def get_smart_seeds(course_name: str, department_name: str):
    text = (course_name + " " + department_name).lower().strip()

    # Default
    skill_seeds = ["Communication", "Analytical Thinking", "Research Skills", "Problem Solving"]
    job_seeds = ["Analyst", "Executive", "Trainee", "Specialist"]

    # ==================== ECONOMICS / COMMERCE ====================
    if any(word in text for word in ["economics", "ecnomics", "commerce", "bcom", "bba", "finance", "account"]):
        skill_seeds = ["Financial Accounting", "Microeconomics", "Macroeconomics", "GST & Taxation",
                       "Advanced Excel", "Financial Analysis", "Business Analytics", "Managerial Economics",
                       "Statistics", "Leadership", "Digital Marketing"]
        job_seeds = ["Economic Analyst", "Finance Analyst", "Accountant", "Business Analyst",
                     "Marketing Executive", "HR Executive", "Auditor", "Policy Analyst"]

    # ==================== PHYSICS ====================
    elif "physics" in text:
        skill_seeds = ["Classical Mechanics", "Electromagnetism", "Quantum Physics", "Thermodynamics",
                       "Optics", "Nuclear Physics", "MATLAB", "Scientific Instrumentation", "Data Analysis"]
        job_seeds = ["Physics Teacher", "Research Scientist", "Lab Technician", "R&D Engineer", "Medical Physicist"]

    # ==================== CHEMISTRY ====================
    elif "chemistry" in text:
        skill_seeds = ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Analytical Chemistry",
                       "Spectroscopy", "Chromatography", "Laboratory Techniques", "Chemical Synthesis"]
        job_seeds = ["Chemist", "Quality Control Analyst", "Research Scientist", "Lab Technician", "Pharmaceutical Analyst"]

    # ==================== BIOLOGY / BIOTECH ====================
    elif any(word in text for word in ["biotech", "biology", "botany", "zoology", "microbiology"]):
        skill_seeds = ["Cell Biology", "Molecular Biology", "Genetics", "PCR Techniques", "ELISA",
                       "Bioinformatics", "Microbial Techniques", "DNA Sequencing", "Laboratory Safety"]
        job_seeds = ["Biotech Analyst", "Research Scientist", "Lab Technician", "Clinical Research Associate", "Microbiologist"]

    # ==================== COMPUTER SCIENCE ====================
    elif any(word in text for word in ["computer", "bca", "mca", "cs", "it", "software", "programming"]):
        skill_seeds = ["Python", "Java", "SQL", "Data Structures", "Algorithms", "Web Development",
                       "React", "Node.js", "Machine Learning", "Cloud Computing", "Cybersecurity"]
        job_seeds = ["Software Developer", "Full Stack Developer", "Data Scientist", "System Analyst", "Cloud Engineer"]

    # ==================== ARTS / PSYCHOLOGY ====================
    elif any(word in text for word in ["english", "arts", "psychology", "history", "political", "sociology"]):
        skill_seeds = ["Content Writing", "Creative Writing", "Research Methodology", "Critical Thinking",
                       "Public Speaking", "Counseling Skills", "SEO Writing", "Communication"]
        job_seeds = ["Content Writer", "Teacher", "Counsellor", "HR Specialist", "Journalist", "Editor"]

    return skill_seeds, job_seeds


def build_course_profiles():
    global COURSE_PROFILES, DEPARTMENT_MAP
    COURSE_PROFILES.clear()
    DEPARTMENT_MAP.clear()

    courses = COUSE_table.objects.select_related('Department').all()
    print(f"🔄 Loading {courses.count()} courses from database...")

    for course in courses:
        course_name = course.course.strip()
        dept_name = course.Department.department.strip() if course.Department else "General"

        course_key = re.sub(r'[^a-z0-9\s]', '', course_name.lower()).strip()
        course_key = re.sub(r'\s+', '_', course_key) or f"course_{course.id}"

        skill_seeds, job_seeds = get_smart_seeds(course_name, dept_name)

        COURSE_PROFILES[course_key] = {
            "label": course_name,
            "department": dept_name,
            "search_keywords": [
                f"{course_name} jobs 2025 India",
                f"{course_name} fresher career opportunities",
                f"skills required for {course_name}",
            ],
            "skill_seeds": skill_seeds,
            "job_seeds": job_seeds,
        }

    for key, profile in COURSE_PROFILES.items():
        DEPARTMENT_MAP.setdefault(profile["department"], []).append(key)

    print(f"✅ Loaded {len(COURSE_PROFILES)} courses successfully.")


try:
    build_course_profiles()
except Exception as e:
    print("Skipping course profiles build (database likely not migrated yet).")


# ====================== CLASSIFICATION ======================
_TECH_RE = re.compile(r"python|java|sql|react|node|aws|docker|machine learning", re.I)


def _classify_skills(keywords: list[tuple[str, int]], seeds: list[str]) -> dict:
    cats = {"Technical_Skills": [], "Soft_Skills": [], "Domain_Skills": [], "Other": []}
    seen = set()

    def _add(word: str):
        if not word or len(word.strip()) < 2:
            return
        lw = word.lower().strip()
        if lw in seen:
            return
        seen.add(lw)

        # Strong seed priority
        if any(s.lower() in lw or lw in s.lower() for s in seeds):
            if _TECH_RE.search(word):
                cats["Technical_Skills"].append(word.title())
            else:
                cats["Domain_Skills"].append(word.title())
            return

        # Regex fallback
        if _TECH_RE.search(word):
            cats["Technical_Skills"].append(word.title())
        else:
            cats["Domain_Skills"].append(word.title())

    for seed in seeds:
        _add(seed)
    for kw, freq in keywords:
        if freq >= 2:
            _add(kw.title())

    for k in cats:
        cats[k] = list(dict.fromkeys(cats[k]))[:10]

    return cats


# ====================== SCRAPING FUNCTIONS ======================
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def _fetch_soup(url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception:
        return None


# (Keep all your scraping functions as they are - _scrape_indeed, _scrape_timesjobs, etc.)

# ... [I kept your original scraping functions in the full file you sent]

# For space, the rest of the file (fetch functions, print_result, cache, etc.) remains the same as you provided.

print("✅ career_data_fetcher.py - Fixed Version Loaded!")

def _scrape_indeed(query: str) -> list[dict]:
    url = f"https://in.indeed.com/jobs?q={query.replace(' ', '+')}&l=India"
    soup = _fetch_soup(url)
    results = []
    if not soup:
        return results
    for card in soup.select("div.job_seen_beacon")[:12]:
        title = card.select_one("h2.jobTitle span")
        company = card.select_one("span.companyName")
        snippet = card.select_one("div.job-snippet")
        if title:
            results.append({
                "title":   title.get_text(strip=True),
                "company": company.get_text(strip=True) if company else "",
                "snippet": snippet.get_text(strip=True) if snippet else "",
            })
    return results


def _scrape_timesjobs(query: str) -> list[dict]:
    url = (
        "https://www.timesjobs.com/candidate/job-search.html"
        f"?searchType=personalizedSearch&from=submit"
        f"&txtKeywords={query.replace(' ', '+')}&txtLocation=India"
    )
    soup = _fetch_soup(url)
    results = []
    if not soup:
        return results
    for card in soup.select("li.clearfix.job-bx.wht-shd-bx")[:10]:
        title = card.select_one("h2 a")
        company = card.select_one("h3.joblist-comp-name")
        skills = card.select_one("span.srp-skills")
        if title:
            results.append({
                "title":   title.get_text(strip=True),
                "company": company.get_text(strip=True) if company else "",
                "snippet": skills.get_text(strip=True) if skills else "",
            })
    return results


def _scrape_naukri_skills(query: str) -> list[str]:
    url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs"
    soup = _fetch_soup(url)
    if not soup:
        return []
    return [
        tag.get_text(strip=True)
        for tag in soup.select("a.tag-li, span.tags-gt, li.tag-li")[:40]
        if 2 < len(tag.get_text(strip=True)) < 40
    ]


def _scrape_news_headlines(query: str) -> list[str]:
    url = (
        f"https://news.google.com/rss/search"
        f"?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
    )
    try:
        r = requests.get(url, headers=_HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "xml")
        return [item.title.text for item in soup.find_all("item")[:20]]
    except Exception:
        return []


def _google_trends(keywords: list[str]) -> dict:
    if not _PYTRENDS_OK or not keywords:
        return {}
    try:
        pt = TrendReq(hl="en-US", tz=330)
        batch = keywords[:5]
        pt.build_payload(batch, timeframe="today 12-m", geo="IN")
        df = pt.interest_over_time()
        if df.empty:
            return {}
        return {k: round(float(v), 1) for k, v in df[batch].mean().items()}
    except Exception:
        return {}


# ══════════════════════════════════════════════════════════════════════════════
#  INTERNAL NLP UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def _extract_keywords(texts: list[str], top_n: int = 40) -> list[tuple[str, int]]:
    combined = re.sub(r"[^a-z\s]", " ", " ".join(texts).lower())
    if _NLTK_OK:
        tokens = word_tokenize(combined)
        stop = set(stopwords.words("english")) | _GENERIC_STOP
        tokens = [t for t in tokens if t.isalpha() and t not in stop and len(t) > 2]
    else:
        tokens = [w for w in combined.split() if len(w) > 3 and w not in _GENERIC_STOP]
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
    return Counter(tokens + bigrams).most_common(top_n)


def _rake_phrases(texts: list[str], top_n: int = 15) -> list[str]:
    if not _RAKE_OK:
        return []
    r = Rake(min_length=1, max_length=3)
    r.extract_keywords_from_text(" ".join(texts))
    return r.get_ranked_phrases()[:top_n]


_TECH_RE   = re.compile(
    r"python|java|sql|react|node|aws|azure|gcp|docker|kubernetes|"
    r"machine learning|deep learning|nlp|data|cloud|devops|linux|"
    r"excel|tally|sap|power bi|tableau|django|flask|html|css|"
    r"c\+\+|golang|rust|swift|kotlin|r programming|matlab|spss|"
    r"spring|microservices|rest api|bioinformatics|pcr|elisa|crispr", re.I)
_SOFT_RE   = re.compile(
    r"communication|leadership|teamwork|problem.solving|critical|"
    r"management|presentation|collaboration|time management|analytical", re.I)
_DOMAIN_RE = re.compile(
    r"marketing|accounting|finance|audit|taxation|counselling|research|"
    r"writing|content|seo|hr|sales|branding|ux|ui|design|strategy|"
    r"laboratory|genomics|clinical|psychometric|copywriting", re.I)


def _classify_skills(keywords: list[tuple[str, int]], seeds: list[str]) -> dict:
    cats: dict[str, list[str]] = {
        "Technical_Skills": [], "Soft_Skills": [],
        "Domain_Skills": [],   "Other": [],
    }
    seen: set[str] = set()

    def _add(word: str):
        lw = word.lower()
        if lw in seen:
            return
        seen.add(lw)
        if _TECH_RE.search(word):
            cats["Technical_Skills"].append(word)
        elif _SOFT_RE.search(word):
            cats["Soft_Skills"].append(word)
        elif _DOMAIN_RE.search(word):
            cats["Domain_Skills"].append(word)
        else:
            cats["Other"].append(word)

    for seed in seeds:
        _add(seed)
    for kw, freq in keywords:
        if freq >= 2:
            _add(kw.title())

    for k in cats:
        cats[k] = list(dict.fromkeys(cats[k]))[:10]
    return cats


def _top_jobs(job_titles: list[str], job_seeds: list[str]) -> list[str]:
    counter: Counter = Counter()
    for title in job_titles:
        for seed in job_seeds:
            if seed.lower() in title.lower():
                counter[seed] += 1
        counter[title.strip().title()] += 1
    ranked = [j for j, _ in counter.most_common(15) if len(j) > 3][:10]
    return ranked if ranked else job_seeds[:8]


# ══════════════════════════════════════════════════════════════════════════════
#  CORE SCRAPE PIPELINE  (single course)
# ══════════════════════════════════════════════════════════════════════════════

def _scrape_profile(profile_key: str, verbose: bool = True) -> dict:
    """
    Run the full scrape + NLP pipeline for one course profile.
    Returns a structured dict. Not intended to be called directly by users —
    use the two public functions below.
    """
    profile = COURSE_PROFILES[profile_key]
    if verbose:
        print(f"  ⟳  Fetching data for: {profile['label']} …")

    all_texts: list[str] = []
    job_titles: list[str] = []

    for kw in profile["search_keywords"][:2]:
        for job in _scrape_indeed(kw):
            job_titles.append(job["title"])
            all_texts.append(job["title"] + " " + job["snippet"])
        time.sleep(random.uniform(0.8, 1.5))

        for job in _scrape_timesjobs(kw):
            job_titles.append(job["title"])
            all_texts.append(job["title"] + " " + job["snippet"])
        time.sleep(random.uniform(0.8, 1.5))

    naukri_skills = _scrape_naukri_skills(profile["search_keywords"][0].split()[0])
    all_texts.extend(naukri_skills)
    time.sleep(1.0)

    news: list[str] = []
    for kw in profile["search_keywords"][:2]:
        news += _scrape_news_headlines(kw + " career 2024")
        time.sleep(0.8)
    all_texts.extend(news)

    trend_scores = _google_trends(profile["skill_seeds"][:5])
    keywords     = _extract_keywords(all_texts, top_n=50)
    skills       = _classify_skills(keywords, profile["skill_seeds"])
    jobs         = _top_jobs(job_titles, profile["job_seeds"])
    trends       = _rake_phrases(news, top_n=8) or \
                   [kw for kw, _ in keywords if len(kw.split()) > 1][:8]

    return {
        "course_key":     profile_key,
        "label":          profile["label"],
        "department":     profile["department"],
        "skills":         skills,
        "jobs":           jobs,
        "industry_trends": trends,
        "google_trends":  trend_scores,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ✦  PUBLIC FUNCTION 1 — fetch by course OR department
# ══════════════════════════════════════════════════════════════════════════════

def fetch_by_course_or_department(query: str, verbose: bool = True) -> dict:
    """
    Fetch trending skills and job data for a course or department.

    Parameters
    ----------
    query   : str  — e.g. "BCA", "bsc cs", "Commerce", "Psychology"
    verbose : bool — print progress lines (default True)

    Returns
    -------
    dict with keys:
        query         : the original input
        matched_type  : "course" | "department"
        matched_name  : resolved name(s)
        results       : list of per-course result dicts
            Each result contains:
                course_key, label, department,
                skills (dict of categories → list),
                jobs (list),
                industry_trends (list),
                google_trends (dict)

    Examples
    --------
    >>> data = fetch_by_course_or_department("BCA")
    >>> data = fetch_by_course_or_department("Commerce")
    >>> data = fetch_by_course_or_department("bsc cs")
    """
    q = query.strip().lower()

    # ── Try direct course match ────────────────────────────────────────────
    matched_keys: list[str] = []
    for key in COURSE_PROFILES:
        if q == key or q in key or key in q:
            matched_keys.append(key)
            break  # exact / single match

    # ── Try department match ───────────────────────────────────────────────
    matched_type = "course"
    matched_name = query
    if not matched_keys:
        for dept, keys in DEPARTMENT_MAP.items():
            if q in dept.lower() or dept.lower() in q:
                matched_keys = keys
                matched_type = "department"
                matched_name = dept
                break

    # ── Fuzzy word-overlap fallback ────────────────────────────────────────
    if not matched_keys:
        words = set(q.split())
        for key in COURSE_PROFILES:
            if words & set(key.split()):
                matched_keys.append(key)
        matched_type = "course (fuzzy)"

    if not matched_keys:
        return {
            "query":        query,
            "matched_type": "none",
            "matched_name": query,
            "error":        f"No match found for '{query}'. "
                            f"Available: {', '.join(COURSE_PROFILES)} | "
                            f"Departments: {', '.join(DEPARTMENT_MAP)}",
            "results":      [],
        }

    if verbose:
        print(f"\n[fetch_by_course_or_department] query='{query}' "
              f"→ {matched_type}: '{matched_name}' "
              f"→ courses: {matched_keys}\n")

    results = [_scrape_profile(k, verbose=verbose) for k in matched_keys]

    return {
        "query":        query,
        "matched_type": matched_type,
        "matched_name": matched_name,
        "results":      results,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ✦  PUBLIC FUNCTION 2 — fetch ALL courses grouped by department
# ══════════════════════════════════════════════════════════════════════════════

def fetch_all_courses_by_department(verbose: bool = True) -> dict:
    """
    Fetch trending skills and job data for EVERY course in the knowledge base,
    grouped under their parent departments.

    Parameters
    ----------
    verbose : bool — print progress lines (default True)

    Returns
    -------
    dict with keys:
        departments : dict  →  { department_name: [course_result, …] }
        summary     : dict  →  { department_name: [course_label, …] }
        total_courses : int

    Each course_result is identical to the dicts inside `results`
    from fetch_by_course_or_department().

    Example
    -------
    >>> all_data = fetch_all_courses_by_department()
    >>> cs_courses = all_data["departments"]["Computer Science"]
    >>> for course in cs_courses:
    ...     print(course["label"], course["skills"]["Technical_Skills"])
    """
    if verbose:
        total = len(COURSE_PROFILES)
        print(f"\n[fetch_all_courses_by_department] Fetching {total} courses "
              f"across {len(DEPARTMENT_MAP)} departments …\n")

    grouped: dict[str, list[dict]] = {dept: [] for dept in DEPARTMENT_MAP}
    summary: dict[str, list[str]]  = {dept: [] for dept in DEPARTMENT_MAP}

    for dept, course_keys in DEPARTMENT_MAP.items():
        if verbose:
            print(f"\n{'─'*55}")
            print(f"  Department: {dept}  ({len(course_keys)} courses)")
            print(f"{'─'*55}")
        for key in course_keys:
            result = _scrape_profile(key, verbose=verbose)
            grouped[dept].append(result)
            summary[dept].append(result["label"])

    return {
        "departments":    grouped,
        "summary":        summary,
        "total_courses":  len(COURSE_PROFILES),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  PRETTY PRINTER  (optional helper)
# ══════════════════════════════════════════════════════════════════════════════

def print_result(data: dict) -> None:
    """
    Print a nicely formatted report for the output of either public function.
    Works with both fetch_by_course_or_department() and
    fetch_all_courses_by_department().
    """
    try:
        from tabulate import tabulate
        from colorama import Fore, Style, init
        init(autoreset=True)
        _COLOR = True
    except ImportError:
        _COLOR = False

    def _h(text, color=""):
        return f"{color}{text}\033[0m" if _COLOR else text

    def _print_course(r: dict):
        print("\n" + "═" * 60)
        print(_h(f"  ✦  {r['label']}  [{r['department']}]", "\033[92m"))
        print("═" * 60)

        print(_h("\n📚 Skills", "\033[93m"))
        for cat, items in r["skills"].items():
            if items:
                print(f"  {_h(cat, chr(27)+'[96m')}: {', '.join(items)}")

        print(_h("\n💼 Job Opportunities", "\033[93m"))
        for i, job in enumerate(r["jobs"], 1):
            print(f"  {i:2}. {job}")

        print(_h("\n🔥 Industry Trends", "\033[93m"))
        for i, trend in enumerate(r["industry_trends"], 1):
            print(f"  {i}. {trend.title()}")

        if r.get("google_trends"):
            print(_h("\n📈 Google Trends (India, 12 months)", "\033[93m"))
            for skill, score in r["google_trends"].items():
                print(f"  {skill}: {score}")
        print()

    # ── Route by output type ───────────────────────────────────────────────
    if "departments" in data:
        # fetch_all_courses_by_department output
        print(_h(f"\n{'═'*60}", "\033[95m"))
        print(_h(
            f"  ALL COURSES BY DEPARTMENT  "
            f"({data['total_courses']} courses)", "\033[95m"))
        print(_h(f"{'═'*60}\n", "\033[95m"))
        for dept, courses in data["departments"].items():
            print(_h(f"\n  ◈  Department: {dept}", "\033[95m"))
            for course in courses:
                _print_course(course)
    else:
        # fetch_by_course_or_department output
        if "error" in data:
            print(f"\n⚠  {data['error']}\n")
            return
        print(_h(
            f"\nQuery: '{data['query']}' → "
            f"{data['matched_type']}: '{data['matched_name']}'", "\033[94m"))
        for r in data["results"]:
            _print_course(r)


# ══════════════════════════════════════════════════════════════════════════════
#  SAVE TO JSON  (optional helper)
# ══════════════════════════════════════════════════════════════════════════════

def save_to_json(data: dict, filepath: str = "career_output.json") -> None:
    """Save the output of either public function to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✔ Saved to {filepath}")


# ══════════════════════════════════════════════════════════════════════════════
#  QUICK DEMO  (run this file directly)
# ══════════════════════════════════════════════════════════════════════════════

# if __name__ == "__main__":
#     import sys
#
#     print("=" * 60)
#     print("  Career Data Fetcher — Demo")
#     print("=" * 60)
#     print("\nChoose mode:")
#     print("  1  →  fetch_by_course_or_department  (single query)")
#     print("  2  →  fetch_all_courses_by_department (all courses)")
#     choice = input("\nEnter 1 or 2: ").strip()
#
#     if choice == "1":
#         query = input("Enter course or department name: ").strip()
#         result = fetch_by_course_or_department(query)
#         print_result(result)
#         if input("\nSave to JSON? (y/n): ").strip().lower() == "y":
#             save_to_json(result, "single_query_output.json")
#
#     elif choice == "2":
#         all_data = fetch_all_courses_by_department()
#         print_result(all_data)
#         if input("\nSave to JSON? (y/n): ").strip().lower() == "y":
#             save_to_json(all_data, "all_courses_output.json")
#
#     else:
#         print("Invalid choice. Exiting.")
#         sys.exit(1)



import os
from datetime import datetime, timedelta

CACHE_FILE = "career_data_cache.json"
CACHE_EXPIRY_HOURS = 120  # Refresh data after 24 hours


def get_cached_career_data(refresh: bool = False) -> dict:
    """
    Returns career data from cache (JSON).
    If cache doesn't exist or is expired, it fetches fresh data.
    """
    cache_path = os.path.join(os.path.dirname(__file__), CACHE_FILE)

    # Check if cache exists and is still valid
    if not refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check cache age
            cached_time = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=CACHE_EXPIRY_HOURS):
                print("✅ Loaded from cache")
                return data["career_data"]
        except Exception:
            pass  # If any error, fetch fresh data

    # Fetch fresh data
    print("🔄 Fetching fresh career data...")
    fresh_data = fetch_all_courses_by_department(verbose=False)

    # Save to cache with timestamp
    cache_data = {
        "cached_at": datetime.now().isoformat(),
        "career_data": fresh_data
    }

    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved fresh data to {CACHE_FILE}")
    except Exception as e:
        print(f"⚠️ Could not save cache: {e}")

    return fresh_data


import os
from datetime import datetime, timedelta

CACHE_FILE = "career_data_cache.json"
CACHE_EXPIRY_HOURS = 24


def filter_by_department(data: dict, hod_department: str) -> dict:
    """
    Filter career data to show ONLY the exact matching HOD's department.
    """
    if not hod_department or not data or not data.get("departments"):
        return data

    # Normalize department name for comparison
    hod_dept_clean = hod_department.strip().lower()

    filtered_data = {
        "departments": {},
        "summary": {},
        "total_courses": 0
    }

    # Exact match with better handling
    for dept_name, courses in data["departments"].items():
        dept_name_clean = dept_name.strip().lower()

        # Exact match (recommended)
        if dept_name_clean == hod_dept_clean:
            filtered_data["departments"][dept_name] = courses
            filtered_data["summary"][dept_name] = data.get("summary", {}).get(dept_name, [])
            filtered_data["total_courses"] = len(courses)
            break  # Stop once we find the exact match

    # Fallback: If no exact match, try partial match (optional safety)
    if not filtered_data["departments"]:
        for dept_name, courses in data["departments"].items():
            dept_name_clean = dept_name.strip().lower()
            if hod_dept_clean in dept_name_clean or dept_name_clean in hod_dept_clean:
                filtered_data["departments"][dept_name] = courses
                filtered_data["summary"][dept_name] = data.get("summary", {}).get(dept_name, [])
                filtered_data["total_courses"] = len(courses)
                break

    return filtered_data

def get_hod_cached_career_data(refresh: bool = False, department: str = None) -> dict:
    """
    Returns career data (filtered by HOD's department)
    """
    cache_path = os.path.join(os.path.dirname(__file__), CACHE_FILE)

    # Try to load from cache
    if not refresh and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)

            cached_time = datetime.fromisoformat(cached.get("cached_at", "2000-01-01"))
            if datetime.now() - cached_time < timedelta(hours=CACHE_EXPIRY_HOURS):
                print("✅ Loaded from cache")
                full_data = cached["career_data"]
                return filter_by_department(full_data, department) if department else full_data

        except Exception:
            pass

    # Fetch fresh data
    print("🔄 Fetching fresh career data...")
    fresh_data = fetch_all_courses_by_department(verbose=False)

    # Save to cache
    try:
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "career_data": fresh_data
        }
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved fresh data to {CACHE_FILE}")
    except Exception as e:
        print(f"⚠️ Could not save cache: {e}")

    return filter_by_department(fresh_data, department) if department else fresh_data