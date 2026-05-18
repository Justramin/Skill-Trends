# """
# Career Trend Scraper — Trending Skills & Job Opportunities
# Uses web scraping + NLP to extract industry insights by course/department.
#
# Requirements:
#     pip install requests beautifulsoup4 nltk rake-nltk pytrends colorama tabulate
#
# Usage:
#     python career_trend_scraper.py
#     Then follow the interactive prompts.
# """
#
# import os
# import re
# import time
# import json
# import random
# import warnings
# from collections import Counter
#
# import requests
# from bs4 import BeautifulSoup
# from tabulate import tabulate
# from colorama import Fore, Style, init
#
# warnings.filterwarnings("ignore")
# init(autoreset=True)
#
# # ── Optional imports ────────────────────────────────────────────────────────
# try:
#     import nltk
#     from nltk.tokenize import word_tokenize
#     from nltk.corpus import stopwords
#     nltk.download("punkt", quiet=True)
#     nltk.download("stopwords", quiet=True)
#     nltk.download("punkt_tab", quiet=True)
#     NLTK_OK = True
# except ImportError:
#     NLTK_OK = False
#
# try:
#     from rake_nltk import Rake
#     RAKE_OK = True
# except ImportError:
#     RAKE_OK = False
#
# try:
#     from pytrends.request import TrendReq
#     PYTRENDS_OK = True
# except ImportError:
#     PYTRENDS_OK = False
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  COURSE / DEPARTMENT KNOWLEDGE BASE
# # ══════════════════════════════════════════════════════════════════════════════
#
# COURSE_PROFILES = {
#     # ── Computer Science / IT ─────────────────────────────────────────────
#     "bca": {
#         "label": "BCA (Bachelor of Computer Applications)",
#         "search_keywords": [
#             "BCA jobs 2024", "computer applications skills demand",
#             "software developer fresher jobs", "web developer jobs India",
#             "python developer jobs fresher",
#         ],
#         "skill_seeds": [
#             "Python", "Java", "web development", "SQL", "cloud computing",
#             "machine learning", "React", "Node.js", "data structures", "cybersecurity",
#         ],
#         "job_seeds": [
#             "Software Developer", "Web Developer", "Data Analyst",
#             "System Administrator", "Database Administrator", "IT Support",
#         ],
#     },
#     "bsc cs": {
#         "label": "BSc Computer Science",
#         "search_keywords": [
#             "BSc CS jobs 2024", "computer science fresher skills",
#             "data science jobs India", "AI engineer fresher",
#             "software engineer BSc graduate",
#         ],
#         "skill_seeds": [
#             "Python", "C++", "algorithms", "machine learning", "data science",
#             "artificial intelligence", "Linux", "cloud AWS", "DevOps", "R programming",
#         ],
#         "job_seeds": [
#             "Data Scientist", "ML Engineer", "Software Engineer",
#             "Research Analyst", "Cloud Engineer", "DevOps Engineer",
#         ],
#     },
#     "bsc": {
#         "label": "BSc (General Science)",
#         "search_keywords": [
#             "BSc graduate jobs 2024", "science graduate career options",
#             "data analyst BSc", "research jobs fresher India",
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
#     # ── Commerce ──────────────────────────────────────────────────────────
#     "bcom": {
#         "label": "BCom (Bachelor of Commerce)",
#         "search_keywords": [
#             "BCom jobs 2024", "commerce graduate career",
#             "accountant fresher jobs", "finance analyst India",
#             "CA inter jobs",
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
#     "bba": {
#         "label": "BBA (Bachelor of Business Administration)",
#         "search_keywords": [
#             "BBA jobs 2024", "business administration fresher career",
#             "marketing executive jobs India", "HR executive fresher",
#             "sales manager trainee jobs",
#         ],
#         "skill_seeds": [
#             "marketing", "digital marketing", "sales", "CRM", "leadership",
#             "project management", "Excel", "communication", "branding", "SEO",
#         ],
#         "job_seeds": [
#             "Marketing Executive", "HR Executive", "Sales Manager",
#             "Business Analyst", "Operations Manager", "Brand Manager",
#         ],
#     },
#     # ── Humanities / Arts ─────────────────────────────────────────────────
#     "ba english": {
#         "label": "BA English",
#         "search_keywords": [
#             "BA English jobs 2024", "content writer jobs India",
#             "copywriter fresher", "editor jobs fresher",
#             "English graduate career options",
#         ],
#         "skill_seeds": [
#             "content writing", "copywriting", "SEO writing", "editing", "proofreading",
#             "creative writing", "blogging", "communication", "social media", "UX writing",
#         ],
#         "job_seeds": [
#             "Content Writer", "Copywriter", "Editor", "Technical Writer",
#             "Social Media Manager", "PR Executive", "Teacher",
#         ],
#     },
#     "ba psychology": {
#         "label": "BA/BSc Psychology",
#         "search_keywords": [
#             "psychology graduate jobs 2024", "counsellor jobs India",
#             "HR psychology careers", "mental health jobs India",
#             "UX researcher jobs fresher",
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
# # Department → course mapping
# DEPARTMENT_MAP = {
#     "computer science": ["bca", "bsc cs"],
#     "information technology": ["bca", "bsc cs"],
#     "commerce": ["bcom", "bba"],
#     "business": ["bba", "bcom"],
#     "english": ["ba english"],
#     "psychology": ["ba psychology"],
#     "science": ["bsc"],
#     "arts": ["ba english", "ba psychology"],
# }
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  SCRAPING HELPERS
# # ══════════════════════════════════════════════════════════════════════════════
#
# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/120.0.0.0 Safari/537.36"
#     ),
#     "Accept-Language": "en-US,en;q=0.9",
# }
#
#
# def fetch_page(url: str, timeout: int = 10) -> BeautifulSoup | None:
#     """Fetch a URL and return a BeautifulSoup object, or None on failure."""
#     try:
#         resp = requests.get(url, headers=HEADERS, timeout=timeout)
#         resp.raise_for_status()
#         return BeautifulSoup(resp.text, "html.parser")
#     except Exception as e:
#         print(f"{Fore.YELLOW}  ⚠  Could not fetch {url[:60]}… ({e})")
#         return None
#
#
# def scrape_indeed_jobs(query: str, location: str = "India") -> list[dict]:
#     """Scrape job titles and descriptions from Indeed search results."""
#     url = f"https://in.indeed.com/jobs?q={query.replace(' ', '+')}&l={location}"
#     soup = fetch_page(url)
#     jobs = []
#     if not soup:
#         return jobs
#     for card in soup.select("div.job_seen_beacon")[:15]:
#         title_el = card.select_one("h2.jobTitle span")
#         company_el = card.select_one("span.companyName")
#         desc_el = card.select_one("div.job-snippet")
#         if title_el:
#             jobs.append({
#                 "title": title_el.get_text(strip=True),
#                 "company": company_el.get_text(strip=True) if company_el else "N/A",
#                 "snippet": desc_el.get_text(strip=True) if desc_el else "",
#             })
#     return jobs
#
#
# def scrape_timesjobs(query: str) -> list[dict]:
#     """Scrape job listings from TimesJobs."""
#     url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={query.replace(' ', '+')}&txtLocation=India"
#     soup = fetch_page(url)
#     jobs = []
#     if not soup:
#         return jobs
#     for card in soup.select("li.clearfix.job-bx.wht-shd-bx")[:10]:
#         title_el = card.select_one("h2 a")
#         company_el = card.select_one("h3.joblist-comp-name")
#         skills_el = card.select_one("span.srp-skills")
#         if title_el:
#             jobs.append({
#                 "title": title_el.get_text(strip=True),
#                 "company": company_el.get_text(strip=True) if company_el else "N/A",
#                 "snippet": skills_el.get_text(strip=True) if skills_el else "",
#             })
#     return jobs
#
#
# def scrape_naukri_skills(query: str) -> list[str]:
#     """Extract skill tags from Naukri search results."""
#     url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs"
#     soup = fetch_page(url)
#     skills = []
#     if not soup:
#         return skills
#     for tag in soup.select("a.tag-li, span.tags-gt, li.tag-li")[:40]:
#         text = tag.get_text(strip=True)
#         if 2 < len(text) < 40:
#             skills.append(text)
#     return skills
#
#
# def scrape_google_news(query: str) -> list[str]:
#     """Scrape headlines from Google News RSS for trend signals."""
#     url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
#     try:
#         resp = requests.get(url, headers=HEADERS, timeout=10)
#         soup = BeautifulSoup(resp.text, "xml")
#         return [item.title.text for item in soup.find_all("item")[:20]]
#     except Exception:
#         return []
#
#
# def get_google_trends(keywords: list[str]) -> dict:
#     """Fetch Google Trends interest scores (requires pytrends)."""
#     if not PYTRENDS_OK or not keywords:
#         return {}
#     try:
#         pt = TrendReq(hl="en-US", tz=330)
#         batch = keywords[:5]  # API limit
#         pt.build_payload(batch, timeframe="today 12-m", geo="IN")
#         df = pt.interest_over_time()
#         if df.empty:
#             return {}
#         return df[batch].mean().to_dict()
#     except Exception:
#         return {}
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  NLP PROCESSING
# # ══════════════════════════════════════════════════════════════════════════════
#
# GENERIC_STOP = {
#     "jobs", "job", "india", "salary", "work", "hiring", "apply", "now",
#     "company", "experience", "years", "fresher", "required", "skills",
#     "looking", "opportunity", "career", "position", "role", "open",
#     "need", "need", "good", "best", "top", "new", "latest", "please",
#     "immediate", "urgent", "walk-in", "walkin", "etc", "also", "many",
#     "well", "use", "using", "get", "one", "two", "per", "month",
# }
#
#
# def extract_keywords_nlp(texts: list[str], top_n: int = 30) -> list[tuple[str, int]]:
#     """Extract ranked keywords from a list of text strings using NLP."""
#     combined = " ".join(texts).lower()
#     combined = re.sub(r"[^a-z\s\+#]", " ", combined)
#
#     if NLTK_OK:
#         tokens = word_tokenize(combined)
#         stop = set(stopwords.words("english")) | GENERIC_STOP
#         tokens = [t for t in tokens if t.isalpha() and t not in stop and len(t) > 2]
#     else:
#         tokens = [w for w in combined.split() if len(w) > 3 and w not in GENERIC_STOP]
#
#     # bigrams (e.g. "machine learning", "data science")
#     bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
#     counter = Counter(tokens + bigrams)
#     return counter.most_common(top_n)
#
#
# def rake_extract(texts: list[str], top_n: int = 20) -> list[str]:
#     """Use RAKE for keyphrase extraction."""
#     if not RAKE_OK:
#         return []
#     r = Rake(min_length=1, max_length=3)
#     r.extract_keywords_from_text(" ".join(texts))
#     return r.get_ranked_phrases()[:top_n]
#
#
# def classify_skills(keywords: list[tuple[str, int]], seeds: list[str]) -> dict:
#     """Classify extracted keywords into skill categories."""
#     tech_patterns = re.compile(
#         r"python|java|sql|react|node|aws|azure|gcp|docker|kubernetes|"
#         r"machine learning|deep learning|nlp|data|cloud|devops|linux|"
#         r"excel|tally|sap|power bi|tableau|django|flask|html|css|"
#         r"c\+\+|golang|rust|swift|kotlin|r programming|matlab|spss",
#         re.I,
#     )
#     soft_patterns = re.compile(
#         r"communication|leadership|teamwork|problem.solving|critical|"
#         r"management|presentation|collaboration|time management|analytical",
#         re.I,
#     )
#     domain_patterns = re.compile(
#         r"marketing|accounting|finance|audit|taxation|counselling|research|"
#         r"writing|content|seo|hr|sales|branding|ux|ui|design|strategy",
#         re.I,
#     )
#
#     result = {"Technical Skills": [], "Soft Skills": [], "Domain Skills": [], "Other": []}
#     seen = set()
#
#     # Add seeds first (high confidence)
#     for seed in seeds:
#         lw = seed.lower()
#         if lw in seen:
#             continue
#         seen.add(lw)
#         if tech_patterns.search(seed):
#             result["Technical Skills"].append(seed)
#         elif soft_patterns.search(seed):
#             result["Soft Skills"].append(seed)
#         elif domain_patterns.search(seed):
#             result["Domain Skills"].append(seed)
#
#     # Add extracted keywords
#     for kw, freq in keywords:
#         if kw in seen or freq < 2:
#             continue
#         seen.add(kw)
#         if tech_patterns.search(kw):
#             result["Technical Skills"].append(kw.title())
#         elif soft_patterns.search(kw):
#             result["Soft Skills"].append(kw.title())
#         elif domain_patterns.search(kw):
#             result["Domain Skills"].append(kw.title())
#
#     # De-dup and limit
#     for k in result:
#         result[k] = list(dict.fromkeys(result[k]))[:10]
#     return result
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  MAIN ANALYSIS ENGINE
# # ══════════════════════════════════════════════════════════════════════════════
#
# def resolve_input(user_input: str) -> list[str]:
#     """Map user course/department input to internal profile keys."""
#     ui = user_input.strip().lower()
#
#     # Direct course match
#     for key in COURSE_PROFILES:
#         if ui in key or key in ui:
#             return [key]
#
#     # Department match
#     for dept, courses in DEPARTMENT_MAP.items():
#         if ui in dept or dept in ui:
#             return courses
#
#     # Fuzzy: word overlap
#     matches = []
#     for key in COURSE_PROFILES:
#         if any(w in key for w in ui.split()):
#             matches.append(key)
#     return matches if matches else list(COURSE_PROFILES.keys())[:1]
#
#
# def analyse(profile_key: str) -> dict:
#     """Run the full scraping + NLP pipeline for one course profile."""
#     profile = COURSE_PROFILES[profile_key]
#     print(f"\n{Fore.CYAN}━━━ Analysing: {profile['label']} ━━━{Style.RESET_ALL}")
#
#     all_texts: list[str] = []
#     job_titles: list[str] = []
#     raw_skills: list[str] = []
#
#     # 1. Scrape job portals
#     for kw in profile["search_keywords"][:3]:
#         print(f"  {Fore.BLUE}→ Indeed:{Style.RESET_ALL} {kw}")
#         jobs = scrape_indeed_jobs(kw)
#         for j in jobs:
#             job_titles.append(j["title"])
#             all_texts.append(j["title"] + " " + j["snippet"])
#         time.sleep(random.uniform(1.0, 2.0))
#
#         print(f"  {Fore.BLUE}→ TimesJobs:{Style.RESET_ALL} {kw}")
#         jobs2 = scrape_timesjobs(kw)
#         for j in jobs2:
#             job_titles.append(j["title"])
#             all_texts.append(j["title"] + " " + j["snippet"])
#         time.sleep(random.uniform(1.0, 2.0))
#
#     # 2. Scrape skill tags from Naukri
#     print(f"  {Fore.BLUE}→ Naukri skills…{Style.RESET_ALL}")
#     raw_skills = scrape_naukri_skills(profile["search_keywords"][0].split()[0])
#     all_texts.extend(raw_skills)
#     time.sleep(1.5)
#
#     # 3. Google News for industry trends
#     print(f"  {Fore.BLUE}→ Google News trends…{Style.RESET_ALL}")
#     news_items: list[str] = []
#     for kw in profile["search_keywords"][:2]:
#         news_items += scrape_google_news(kw + " career 2024 India")
#         time.sleep(1.0)
#     all_texts.extend(news_items)
#
#     # 4. Google Trends (optional)
#     trend_scores: dict = {}
#     if PYTRENDS_OK:
#         print(f"  {Fore.BLUE}→ Google Trends…{Style.RESET_ALL}")
#         trend_scores = get_google_trends(profile["skill_seeds"][:5])
#
#     # 5. NLP extraction
#     keywords = extract_keywords_nlp(all_texts, top_n=50)
#     rake_phrases = rake_extract(all_texts, top_n=20)
#     skill_map = classify_skills(keywords, profile["skill_seeds"])
#
#     # 6. Top job roles (frequency-ranked)
#     job_counter = Counter()
#     for t in job_titles:
#         for seed in profile["job_seeds"]:
#             if seed.lower() in t.lower():
#                 job_counter[seed] += 1
#         job_counter[t.strip().title()] += 1
#     top_jobs = [j for j, _ in job_counter.most_common(12) if len(j) > 3][:10]
#
#     # 7. Industry trends from news headlines
#     trend_phrases = rake_extract(news_items, top_n=10) if news_items else []
#     if not trend_phrases:
#         trend_phrases = [kw for kw, _ in keywords if len(kw.split()) > 1][:8]
#
#     return {
#         "label": profile["label"],
#         "skills": skill_map,
#         "jobs": top_jobs if top_jobs else profile["job_seeds"],
#         "trends": trend_phrases[:8],
#         "google_trends": trend_scores,
#         "raw_keyword_count": len(keywords),
#     }
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  OUTPUT FORMATTING
# # ══════════════════════════════════════════════════════════════════════════════
#
# def print_report(result: dict) -> None:
#     banner = f"  {result['label']}  "
#     print(f"\n{Fore.GREEN}{'═' * (len(banner)+4)}")
#     print(f"  ✦  {banner}  ✦")
#     print(f"{'═' * (len(banner)+4)}{Style.RESET_ALL}\n")
#
#     # Skills
#     print(f"{Fore.YELLOW}📚 TRENDING SKILLS{Style.RESET_ALL}")
#     skill_rows = []
#     for category, items in result["skills"].items():
#         if items:
#             skill_rows.append([f"{Fore.CYAN}{category}{Style.RESET_ALL}", ", ".join(items)])
#     print(tabulate(skill_rows, tablefmt="rounded_outline"))
#
#     # Jobs
#     print(f"\n{Fore.YELLOW}💼 TOP JOB OPPORTUNITIES{Style.RESET_ALL}")
#     job_rows = [[i + 1, job] for i, job in enumerate(result["jobs"])]
#     print(tabulate(job_rows, headers=["#", "Role"], tablefmt="rounded_outline"))
#
#     # Trends
#     print(f"\n{Fore.YELLOW}🔥 INDUSTRY TRENDS (NLP extracted){Style.RESET_ALL}")
#     for i, trend in enumerate(result["trends"], 1):
#         print(f"  {i}. {trend.title()}")
#
#     # Google Trends scores
#     if result.get("google_trends"):
#         print(f"\n{Fore.YELLOW}📈 GOOGLE TRENDS INTEREST (India, past 12 months){Style.RESET_ALL}")
#         gt_rows = [[k.title(), f"{v:.1f}"] for k, v in result["google_trends"].items()]
#         print(tabulate(gt_rows, headers=["Skill", "Interest Score"], tablefmt="rounded_outline"))
#
#     print()
#
#
# def save_json(results: list[dict], filename: str = "career_trends_output.json") -> None:
#     clean = []
#     for r in results:
#         clean.append({
#             "course": r["label"],
#             "skills": r["skills"],
#             "jobs": r["jobs"],
#             "trends": r["trends"],
#             "google_trends": {k: round(v, 2) for k, v in r.get("google_trends", {}).items()},
#         })
#     with open(filename, "w", encoding="utf-8") as f:
#         json.dump(clean, f, indent=2, ensure_ascii=False)
#     print(f"{Fore.GREEN}✔ Results saved to {filename}{Style.RESET_ALL}")
#
#
# # ══════════════════════════════════════════════════════════════════════════════
# #  CLI ENTRY POINT
# # ══════════════════════════════════════════════════════════════════════════════
#
# BANNER = r"""
# ╔═══════════════════════════════════════════════════════════╗
# ║       🎓  Career Trend Scraper  ·  Powered by NLP 🤖     ║
# ║      Trending Skills & Job Opportunities by Course       ║
# ╚═══════════════════════════════════════════════════════════╝
# """
#
# SUPPORTED = """
# Supported Courses  : BCA, BSc CS, BSc, BCom, BBA, BA English, BA Psychology
# Supported Depts    : Computer Science, IT, Commerce, Business, English,
#                      Psychology, Science, Arts
# Type 'all' to analyse every built-in course profile.
# """
#
#
# def main():
#     print(Fore.MAGENTA + BANNER + Style.RESET_ALL)
#     print(SUPPORTED)
#
#     user_input = input(f"{Fore.CYAN}Enter course or department name: {Style.RESET_ALL}").strip()
#     if not user_input:
#         print("No input provided. Exiting.")
#         return
#
#     if user_input.lower() == "all":
#         profile_keys = list(COURSE_PROFILES.keys())
#     else:
#         profile_keys = resolve_input(user_input)
#         if not profile_keys:
#             print(f"{Fore.RED}Could not match '{user_input}' to any profile. Try again.{Style.RESET_ALL}")
#             return
#
#     print(f"\n{Fore.GREEN}Matched profiles: {', '.join(COURSE_PROFILES[k]['label'] for k in profile_keys)}{Style.RESET_ALL}")
#     confirm = input("Proceed? (y/n): ").strip().lower()
#     if confirm != "y":
#         return
#
#     results = []
#     for key in profile_keys:
#         try:
#             result = analyse(key)
#             print_report(result)
#             results.append(result)
#         except KeyboardInterrupt:
#             print("\nInterrupted.")
#             break
#         except Exception as e:
#             print(f"{Fore.RED}Error analysing {key}: {e}{Style.RESET_ALL}")
#
#     if results:
#         save_choice = input("Save results to JSON? (y/n): ").strip().lower()
#         if save_choice == "y":
#             save_json(results)
#
#
# if __name__ == "__main__":
#     main()