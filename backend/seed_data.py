"""Seed the database with realistic Assam jobs mock data."""
import asyncio
import os
import uuid
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import re

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')

client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

THUMBS = {
    'govt': 'https://images.pexels.com/photos/13161243/pexels-photo-13161243.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=400&w=600',
    'defence': 'https://images.unsplash.com/photo-1615482317155-9d26e2574de2?crop=entropy&cs=srgb&fm=jpg&w=600&q=80',
    'railway': 'https://images.pexels.com/photos/10662882/pexels-photo-10662882.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=400&w=600',
    'banking': 'https://images.unsplash.com/photo-1660795864432-6e63a88bfb40?crop=entropy&cs=srgb&fm=jpg&w=600&q=80',
    'teaching': 'https://images.unsplash.com/photo-1660795307991-f9d5254a139c?crop=entropy&cs=srgb&fm=jpg&w=600&q=80',
    'police': 'https://images.pexels.com/photos/31351550/pexels-photo-31351550.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=400&w=600',
    'private': 'https://images.pexels.com/photos/36817668/pexels-photo-36817668.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=400&w=600',
}

def slug(t):
    s = re.sub(r'[^a-z0-9\s-]', '', t.lower()).strip()
    return re.sub(r'\s+', '-', s)[:100]

JOBS = [
    {
        'title': 'Assam Police Constable Recruitment 2025 – 1200 Posts, Apply Online',
        'organization': 'Assam Police',
        'category': 'police', 'job_type': 'recruitment',
        'description': 'Assam Police has released notification for recruitment of Constable (Unarmed Branch) in Assam Police. Eligible candidates may apply online through the official website. Total vacancy 1200 posts available across various districts of Assam.',
        'qualification': 'HSLC (10th) passed from a recognized board',
        'age_limit': '18 to 25 years', 'application_fee': 'Rs. 250/- (General), Rs. 150/- (SC/ST/OBC)',
        'vacancy_count': '1200', 'salary': 'Rs. 14,000 - 49,000/-',
        'last_date': '15 August 2025', 'start_date': '01 July 2025',
        'apply_link': 'https://slprbassam.in', 'notification_link': '#', 'official_website': 'https://police.assam.gov.in',
        'how_to_apply': 'Visit the official website slprbassam.in, register with valid email and mobile, fill the application form, upload documents, pay fees and submit before the last date.',
        'selection_process': 'Physical Standard Test (PST), Physical Efficiency Test (PET), Written Examination, Document Verification, Medical Examination',
        'is_featured': True,
    },
    {
        'title': 'Indian Air Force AFCAT Recruitment 2025 – 379 Posts, Online Apply',
        'organization': 'Indian Air Force',
        'category': 'defence', 'job_type': 'recruitment',
        'description': 'Indian Air Force has released notification for AFCAT (02/2025) for the post of Flying Branch, Ground Duty (Technical), Ground Duty (Non-Technical). Total 379 vacancies. Eligible Indian citizens (male/female) can apply online.',
        'qualification': 'Graduation/B.Tech/BE/PG depending on branch',
        'age_limit': '20 to 24 years (Flying), 20 to 26 years (Ground Duty)', 'application_fee': 'Rs. 550/- + GST',
        'vacancy_count': '379', 'salary': 'Rs. 56,100 - 1,77,500/- (Level 10)',
        'last_date': '30 July 2025', 'start_date': '02 June 2025',
        'apply_link': 'https://afcat.cdac.in', 'notification_link': '#', 'official_website': 'https://careerindianairforce.cdac.in',
        'how_to_apply': 'Visit afcat.cdac.in, register, fill application form online, upload photo and signature, pay fee and submit.',
        'selection_process': 'AFCAT Online Exam, AFSB Interview, Medical Test',
        'is_featured': True,
    },
    {
        'title': 'APSC Combined Competitive Examination 2025 – 913 Posts',
        'organization': 'Assam Public Service Commission',
        'category': 'govt', 'job_type': 'recruitment',
        'description': 'Assam Public Service Commission (APSC) has invited online applications for Combined Competitive Examination 2025 for recruitment to various Group A and Group B services under Government of Assam. Total 913 vacancies announced.',
        'qualification': 'Graduation from a recognized University',
        'age_limit': '21 to 38 years', 'application_fee': 'Rs. 297.20/- (General), Rs. 197.20/- (SC/ST/OBC)',
        'vacancy_count': '913', 'salary': 'As per Govt of Assam pay scales',
        'last_date': '20 August 2025', 'start_date': '15 July 2025',
        'apply_link': 'https://apsc.nic.in', 'notification_link': '#', 'official_website': 'https://apsc.nic.in',
        'how_to_apply': 'Apply online through apsc.nic.in portal. Register, fill form, upload documents, pay fees and submit.',
        'selection_process': 'Preliminary Exam, Main Exam, Interview',
        'is_featured': True,
    },
    {
        'title': 'SBI Clerk Recruitment 2025 – 13735 Junior Associate Posts',
        'organization': 'State Bank of India',
        'category': 'banking', 'job_type': 'recruitment',
        'description': 'State Bank of India (SBI) has released notification for recruitment of Junior Associates (Customer Support & Sales) in clerical cadre. Total 13735 vacancies including 254 vacancies in Assam Circle.',
        'qualification': 'Graduation in any discipline',
        'age_limit': '20 to 28 years', 'application_fee': 'Rs. 750/- (General/OBC), Nil (SC/ST/PwBD)',
        'vacancy_count': '13735', 'salary': 'Rs. 19,900 - 47,920/-',
        'last_date': '07 July 2025', 'start_date': '17 June 2025',
        'apply_link': 'https://sbi.co.in/careers', 'notification_link': '#', 'official_website': 'https://sbi.co.in',
        'how_to_apply': 'Visit sbi.co.in/careers, click on current openings, apply online with required documents.',
        'selection_process': 'Preliminary Exam, Main Exam, Language Test',
        'is_featured': False,
    },
    {
        'title': 'RRB NTPC Recruitment 2025 – 11558 Posts in Indian Railways',
        'organization': 'Railway Recruitment Board',
        'category': 'railway', 'job_type': 'recruitment',
        'description': 'Railway Recruitment Board has announced 11558 Non-Technical Popular Categories (NTPC) vacancies for graduate and undergraduate posts across Indian Railways including Northeast Frontier Railway (NFR).',
        'qualification': '12th / Graduation depending on post',
        'age_limit': '18 to 33 years', 'application_fee': 'Rs. 500/- (General), Rs. 250/- (Reserved)',
        'vacancy_count': '11558', 'salary': 'Rs. 19,900 - 35,400/-',
        'last_date': '20 July 2025', 'start_date': '14 June 2025',
        'apply_link': 'https://www.rrbcdg.gov.in', 'notification_link': '#', 'official_website': 'https://indianrailways.gov.in',
        'how_to_apply': 'Visit official RRB regional website, register and apply online.',
        'selection_process': 'CBT 1, CBT 2, Skill Test/Typing Test, Document Verification',
        'is_featured': True,
    },
    {
        'title': 'DEE Assam LP/UP Teacher Recruitment 2025 – 4500 Posts',
        'organization': 'Directorate of Elementary Education, Assam',
        'category': 'teaching', 'job_type': 'recruitment',
        'description': 'Directorate of Elementary Education Assam has invited applications for recruitment of Assistant Teachers in LP and UP schools. Total 4500 posts available across various districts of Assam.',
        'qualification': 'HS passed with D.El.Ed / B.Ed and TET qualified',
        'age_limit': '18 to 40 years', 'application_fee': 'Rs. 250/- (General), Rs. 150/- (SC/ST/OBC)',
        'vacancy_count': '4500', 'salary': 'Rs. 14,000 - 70,000/-',
        'last_date': '25 July 2025', 'start_date': '01 July 2025',
        'apply_link': 'https://dee.assam.gov.in', 'notification_link': '#', 'official_website': 'https://dee.assam.gov.in',
        'how_to_apply': 'Apply online through DEE Assam official portal with TET certificate.',
        'selection_process': 'Merit based on TET score + academic qualifications + interview',
        'is_featured': False,
    },
    {
        'title': 'Indian Army Agniveer Recruitment 2025 – 25000 Posts Rally',
        'organization': 'Indian Army',
        'category': 'defence', 'job_type': 'recruitment',
        'description': 'Indian Army has invited online applications for Agniveer recruitment 2025 across various trades. Recruitment rally to be held in Assam at multiple locations. Total 25000 vacancies.',
        'qualification': '10th / 12th depending on trade',
        'age_limit': '17.5 to 21 years', 'application_fee': 'Rs. 250/-',
        'vacancy_count': '25000', 'salary': 'Rs. 30,000 - 40,000/- per month',
        'last_date': '10 August 2025', 'start_date': '01 July 2025',
        'apply_link': 'https://joinindianarmy.nic.in', 'notification_link': '#', 'official_website': 'https://joinindianarmy.nic.in',
        'how_to_apply': 'Register online at joinindianarmy.nic.in, apply for Agniveer, appear for online CEE then rally.',
        'selection_process': 'Online Common Entrance Exam (CEE), Physical Test, Medical Examination',
        'is_featured': True,
    },
    {
        'title': 'IBPS PO Recruitment 2025 – 4455 Probationary Officer Posts',
        'organization': 'Institute of Banking Personnel Selection',
        'category': 'banking', 'job_type': 'recruitment',
        'description': 'IBPS has invited applications for recruitment of Probationary Officers / Management Trainees in 11 Public Sector Banks. Total 4455 vacancies.',
        'qualification': 'Graduation in any discipline',
        'age_limit': '20 to 30 years', 'application_fee': 'Rs. 850/- (General), Rs. 175/- (SC/ST/PwBD)',
        'vacancy_count': '4455', 'salary': 'Rs. 36,000 - 63,840/-',
        'last_date': '21 July 2025', 'start_date': '01 July 2025',
        'apply_link': 'https://ibps.in', 'notification_link': '#', 'official_website': 'https://ibps.in',
        'how_to_apply': 'Apply online at ibps.in, register, fill form and pay fees.',
        'selection_process': 'Prelims, Mains, Interview',
        'is_featured': False,
    },
    {
        'title': 'AAU Jorhat Recruitment 2025 – Various Faculty & Non-Faculty Posts',
        'organization': 'Assam Agricultural University',
        'category': 'govt', 'job_type': 'recruitment',
        'description': 'Assam Agricultural University, Jorhat has invited applications for recruitment of various Teaching and Non-Teaching positions including Professor, Associate Professor, and Junior Assistant.',
        'qualification': 'PG / PhD in relevant field for teaching; HS/Graduation for non-teaching',
        'age_limit': '21 to 45 years', 'application_fee': 'Rs. 500/- (General), Rs. 250/- (Reserved)',
        'vacancy_count': '125', 'salary': 'As per UGC norms',
        'last_date': '30 July 2025', 'start_date': '05 July 2025',
        'apply_link': 'https://aau.ac.in', 'notification_link': '#', 'official_website': 'https://aau.ac.in',
        'how_to_apply': 'Download form from aau.ac.in, fill and send to the registrar office.',
        'selection_process': 'Written Test + Interview',
        'is_featured': False,
    },
    {
        'title': 'NHM Assam Recruitment 2025 – 1500 Staff Nurse, GNM, ANM Posts',
        'organization': 'National Health Mission, Assam',
        'category': 'govt', 'job_type': 'recruitment',
        'description': 'National Health Mission Assam has invited applications for various contractual posts of Staff Nurse, GNM, ANM, Lab Technician, Pharmacist under NHM Assam.',
        'qualification': 'GNM / ANM / B.Sc Nursing / Diploma',
        'age_limit': '21 to 43 years', 'application_fee': 'Rs. 0/- (No fee)',
        'vacancy_count': '1500', 'salary': 'Rs. 14,500 - 23,500/-',
        'last_date': '18 July 2025', 'start_date': '08 July 2025',
        'apply_link': 'https://nhm.assam.gov.in', 'notification_link': '#', 'official_website': 'https://nhm.assam.gov.in',
        'how_to_apply': 'Apply online at nhm.assam.gov.in portal.',
        'selection_process': 'Computer Based Test + Document Verification',
        'is_featured': False,
    },
    # ADMIT CARDS
    {
        'title': 'APSC CCE Prelims Admit Card 2025 – Download Now',
        'organization': 'Assam Public Service Commission',
        'category': 'govt', 'job_type': 'admit_card',
        'description': 'APSC has released the admit card for Combined Competitive Examination Prelims 2025. Candidates can download their admit cards from the official APSC website.',
        'qualification': 'N/A', 'age_limit': 'N/A', 'application_fee': 'N/A',
        'vacancy_count': 'N/A', 'salary': 'N/A',
        'last_date': 'Exam: 25 July 2025', 'start_date': 'Available now',
        'apply_link': 'https://apsc.nic.in', 'notification_link': '#', 'official_website': 'https://apsc.nic.in',
        'how_to_apply': 'Login at apsc.nic.in with registration number and password to download admit card.',
        'selection_process': 'N/A',
        'is_featured': False,
    },
    {
        'title': 'SSC CGL Tier 1 Admit Card 2025 – NER Region',
        'organization': 'Staff Selection Commission',
        'category': 'govt', 'job_type': 'admit_card',
        'description': 'SSC has released CGL Tier 1 admit cards for North Eastern Region candidates including Assam. Exam scheduled for August 2025.',
        'qualification': 'N/A', 'age_limit': 'N/A', 'application_fee': 'N/A',
        'vacancy_count': 'N/A', 'salary': 'N/A',
        'last_date': 'Exam: 10 August 2025', 'start_date': 'Available now',
        'apply_link': 'https://ssc.nic.in', 'notification_link': '#', 'official_website': 'https://ssc.nic.in',
        'how_to_apply': 'Login at ssc.nic.in with credentials to download admit card.',
        'selection_process': 'N/A',
        'is_featured': False,
    },
    # RESULTS
    {
        'title': 'Assam HSLC Result 2025 – SEBA Class 10 Result Declared',
        'organization': 'Board of Secondary Education, Assam',
        'category': 'govt', 'job_type': 'result',
        'description': 'SEBA has declared the HSLC (Class 10) examination result 2025. Students can check their results on the official website resultsassam.nic.in.',
        'qualification': 'N/A', 'age_limit': 'N/A', 'application_fee': 'N/A',
        'vacancy_count': 'N/A', 'salary': 'N/A',
        'last_date': 'N/A', 'start_date': 'Released',
        'apply_link': 'https://resultsassam.nic.in', 'notification_link': '#', 'official_website': 'https://sebaonline.org',
        'how_to_apply': 'Visit resultsassam.nic.in and enter your roll number to check result.',
        'selection_process': 'N/A',
        'is_featured': True,
    },
    {
        'title': 'AHSEC HS Final Year Result 2025 Declared',
        'organization': 'Assam Higher Secondary Education Council',
        'category': 'govt', 'job_type': 'result',
        'description': 'AHSEC has announced the Higher Secondary Final Year (Class 12) results for Arts, Science and Commerce streams.',
        'qualification': 'N/A', 'age_limit': 'N/A', 'application_fee': 'N/A',
        'vacancy_count': 'N/A', 'salary': 'N/A',
        'last_date': 'N/A', 'start_date': 'Released',
        'apply_link': 'https://resultsassam.nic.in', 'notification_link': '#', 'official_website': 'https://ahsec.assam.gov.in',
        'how_to_apply': 'Check at ahsec.assam.gov.in or resultsassam.nic.in with roll number.',
        'selection_process': 'N/A',
        'is_featured': False,
    },
    # ANSWER KEYS
    {
        'title': 'Assam Police SI Answer Key 2025 – Download PDF',
        'organization': 'SLPRB Assam',
        'category': 'police', 'job_type': 'answer_key',
        'description': 'SLPRB Assam has released the official answer key for Sub-Inspector written examination 2025. Candidates can raise objections within 7 days.',
        'qualification': 'N/A', 'age_limit': 'N/A', 'application_fee': 'N/A',
        'vacancy_count': 'N/A', 'salary': 'N/A',
        'last_date': 'Objections: 18 July 2025', 'start_date': 'Released',
        'apply_link': 'https://slprbassam.in', 'notification_link': '#', 'official_website': 'https://slprbassam.in',
        'how_to_apply': 'Download answer key PDF from slprbassam.in.',
        'selection_process': 'N/A',
        'is_featured': False,
    },
    # ADMISSIONS
    {
        'title': 'Gauhati University PG Admission 2025 – Apply Online',
        'organization': 'Gauhati University',
        'category': 'govt', 'job_type': 'admission',
        'description': 'Gauhati University has invited applications for admission to various PG courses for the academic session 2025-26.',
        'qualification': 'Graduation in relevant discipline',
        'age_limit': 'No upper age limit', 'application_fee': 'Rs. 750/-',
        'vacancy_count': 'Various', 'salary': 'N/A',
        'last_date': '15 August 2025', 'start_date': '10 July 2025',
        'apply_link': 'https://gauhati.ac.in', 'notification_link': '#', 'official_website': 'https://gauhati.ac.in',
        'how_to_apply': 'Apply online at gauhati.ac.in admission portal.',
        'selection_process': 'Entrance Test / Merit based',
        'is_featured': False,
    },
    # SCHOLARSHIPS
    {
        'title': 'Assam CM Scholarship 2025 – Apply Online for Higher Studies',
        'organization': 'Government of Assam',
        'category': 'govt', 'job_type': 'scholarship',
        'description': 'Government of Assam has launched the Chief Minister Scholarship scheme for meritorious students pursuing higher education within and outside the state.',
        'qualification': 'Class 12 passed with 60% or above',
        'age_limit': 'Up to 25 years', 'application_fee': 'No fee',
        'vacancy_count': '5000', 'salary': 'Rs. 50,000/- per annum',
        'last_date': '31 August 2025', 'start_date': '01 July 2025',
        'apply_link': 'https://scholarships.assam.gov.in', 'notification_link': '#', 'official_website': 'https://scholarships.assam.gov.in',
        'how_to_apply': 'Apply online through scholarships.assam.gov.in portal.',
        'selection_process': 'Merit based + family income verification',
        'is_featured': False,
    },
    # Private
    {
        'title': 'TCS Off Campus Drive 2025 – Assam Freshers Welcome',
        'organization': 'Tata Consultancy Services',
        'category': 'private', 'job_type': 'recruitment',
        'description': 'TCS is hiring freshers across Assam for Software Engineer, Digital, and BPS roles. Off-campus drive registration is open for 2024/2025 batch.',
        'qualification': 'B.E/B.Tech/MCA/M.Sc',
        'age_limit': 'As per company norms', 'application_fee': 'No fee',
        'vacancy_count': '2000+', 'salary': 'Rs. 3.36 - 7 LPA',
        'last_date': '31 July 2025', 'start_date': '10 July 2025',
        'apply_link': 'https://tcs.com/careers', 'notification_link': '#', 'official_website': 'https://tcs.com',
        'how_to_apply': 'Register at tcs.com/careers, apply for relevant role, take TCS NQT exam.',
        'selection_process': 'TCS NQT, Technical Interview, HR Interview',
        'is_featured': False,
    },
    {
        'title': 'Reliance Jio Field Engineer Recruitment 2025 – 800 Posts in Northeast',
        'organization': 'Reliance Jio',
        'category': 'private', 'job_type': 'recruitment',
        'description': 'Reliance Jio is hiring Field Engineers, Sales Executives and Technical Support staff across Assam and Northeast India.',
        'qualification': 'Diploma/Graduation in any stream',
        'age_limit': '18 to 30 years', 'application_fee': 'No fee',
        'vacancy_count': '800', 'salary': 'Rs. 18,000 - 35,000/-',
        'last_date': '20 July 2025', 'start_date': 'Open',
        'apply_link': 'https://careers.jio.com', 'notification_link': '#', 'official_website': 'https://jio.com',
        'how_to_apply': 'Apply via careers.jio.com or walk-in to nearest Jio store.',
        'selection_process': 'Online Test + Interview',
        'is_featured': False,
    },
]

async def seed():
    await db.jobs.delete_many({})
    for j in JOBS:
        cat = j['category']
        thumb = THUMBS.get(cat, THUMBS['govt'])
        doc = {
            'id': str(uuid.uuid4()),
            'slug': slug(j['title']),
            'thumbnail': thumb,
            'posted_date': datetime.utcnow() - timedelta(days=len(JOBS) - JOBS.index(j)),
            'views': 0,
            'location': 'Assam',
            **j,
        }
        await db.jobs.insert_one(doc)
    print(f"Seeded {len(JOBS)} jobs")

if __name__ == '__main__':
    asyncio.run(seed())
