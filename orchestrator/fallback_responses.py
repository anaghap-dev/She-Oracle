"""
Fallback response library for SHE-ORACLE.

When all Gemini models are unavailable (quota exhausted, API down, network
error), the planner picks a curated static plan from this library based on
the request domain.  Each plan is a fully-formed dict that matches the exact
schema the frontend expects — so the UI renders normally with no special
error handling needed on the client side.

These are NOT generic lorem-ipsum placeholders.  They are actionable,
India-specific strategic plans drawn from real government schemes, legal
provisions, and career data — useful in their own right.
"""
import random

# ---------------------------------------------------------------------------
# Shared footer added to every fallback plan
# ---------------------------------------------------------------------------
_FALLBACK_NOTE = (
    "Note: This plan was generated from SHE-ORACLE's curated knowledge base "
    "because the AI service is temporarily unavailable. Core guidance is fully "
    "valid. Restart your query once service resumes for a personalised plan."
)

_FALLBACK_RESOURCES = [
    {
        "name": "MyScheme Portal",
        "type": "Platform",
        "url_or_contact": "https://myscheme.gov.in",
        "how_it_helps": "Official one-stop portal to find all central and state government schemes you are eligible for.",
    },
    {
        "name": "iSaathi Helpline",
        "type": "Contact",
        "url_or_contact": "1800-180-1551",
        "how_it_helps": "Free government helpline for women in distress — connects to legal aid, counselling, and shelter.",
    },
    {
        "name": "National Commission for Women",
        "type": "Contact",
        "url_or_contact": "ncwapps.nic.in / 7827-170-170",
        "how_it_helps": "File complaints, get legal support, and access welfare programs for women.",
    },
]

# ---------------------------------------------------------------------------
# Domain: career
# ---------------------------------------------------------------------------
_CAREER_PLANS = [
    {
        "goal": "Career growth and advancement for women in India",
        "domain": "career",
        "executive_summary": (
            "India's job market has expanded significantly for skilled women professionals. "
            "The strategy focuses on skill certification, targeted networking, and negotiation "
            "to move from where you are now to your target role within 90 days."
        ),
        "situation_analysis": (
            "Women in India face a structural pay gap of 19-34% and are under-represented in "
            "senior roles. Addressing this requires a deliberate combination of upskilling, "
            "visibility building, and leveraging legal protections. The good news: demand for "
            "skilled women professionals is at an all-time high across tech, finance, and healthcare."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Identify and close the top 2-3 skill gaps for your target role", "why": "Skill gaps are the #1 reason women get passed over in promotions", "timeline": "Weeks 1-4"},
            {"id": 2, "subgoal": "Build a credible professional profile on LinkedIn and resume", "why": "60% of hiring decisions are made before the interview based on profile strength", "timeline": "Week 1"},
            {"id": 3, "subgoal": "Get certified in one high-demand skill (cloud, data, PM, finance)", "why": "Certifications add 15-30% to salary negotiations", "timeline": "Days 30-60"},
            {"id": 4, "subgoal": "Apply to 10 targeted roles with a tailored application", "why": "Targeted applications have 4x higher response rates than mass applying", "timeline": "Day 45 onwards"},
            {"id": 5, "subgoal": "Negotiate salary using market data benchmarks", "why": "Women who negotiate earn 7-13% more over their lifetime", "timeline": "At offer stage"},
        ],
        "immediate_actions": [
            {"action": "Go to LinkedIn and set 'Open to Work' with your target role", "resource": "linkedin.com/jobs", "expected_outcome": "Recruiters start finding you within 48 hours"},
            {"action": "Enroll in one free certification: Google, AWS, or NASSCOM FutureSkills", "resource": "grow.google / aws.amazon.com/training / futureskills.nasscom.in", "expected_outcome": "Certification in 4-8 weeks that directly boosts your resume"},
            {"action": "Research your target role salary on AmbitionBox and Glassdoor", "resource": "ambitionbox.com / glassdoor.co.in", "expected_outcome": "Know your market value before any negotiation"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Profile and skill foundation", "milestones": ["Updated LinkedIn and resume", "Enrolled in certification", "Identified 20 target companies"], "resources_needed": ["LinkedIn Premium (optional)", "Free certification platform"]},
            {"phase": "60 Days", "focus": "Applications and networking", "milestones": ["Certification complete", "Applied to 10-15 roles", "3 informational interviews done"], "resources_needed": ["Job portals: Naukri, LinkedIn, Indeed"]},
            {"phase": "90 Days", "focus": "Offers and negotiation", "milestones": ["At least 2 interview processes active", "Salary negotiation done", "Offer accepted or pipeline clear"], "resources_needed": ["Salary data from AmbitionBox", "Offer letter review"]},
        ],
        "key_resources": [
            {"name": "NASSCOM FutureSkills Prime", "type": "Platform", "url_or_contact": "futureskills.nasscom.in", "how_it_helps": "Free and subsidised tech certification for working professionals"},
            {"name": "AmbitionBox Salary Tool", "type": "Platform", "url_or_contact": "ambitionbox.com", "how_it_helps": "Verified salary data by role, company, and city for negotiation"},
            {"name": "Sheroes Community", "type": "Platform", "url_or_contact": "sheroes.com", "how_it_helps": "Women's career community with mentors, job listings, and peer support"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Rejection from multiple applications", "mitigation": "Diversify: apply to startups and mid-size companies, not just top brands. Get feedback from recruiters."},
            {"risk": "Gender bias in hiring", "mitigation": "Use anonymous application platforms where possible. Focus on merit-based proof: certifications, portfolio, GitHub."},
            {"risk": "Skill course takes longer than expected", "mitigation": "Choose courses with self-paced options so job applications aren't blocked."},
        ],
        "success_metrics": [
            "Certification obtained within 60 days",
            "Minimum 5 interview calls generated within 90 days",
            "Final offer at or above market rate",
            "New role started within 120 days",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
    {
        "goal": "Women re-entering the workforce after a career break",
        "domain": "career",
        "executive_summary": (
            "Career re-entry after a break (maternity, caregiving, health) is fully achievable "
            "with the right sequencing. Several large Indian employers now have structured "
            "returnship programs specifically for women. This plan guides you through "
            "refreshing skills, targeting return-friendly employers, and closing the gap."
        ),
        "situation_analysis": (
            "India has over 120 million women outside the formal workforce, many of whom left "
            "due to family responsibilities. Returnship programs at companies like Infosys, TCS, "
            "Goldman Sachs, and Accenture India actively recruit experienced women after breaks. "
            "The key barriers are confidence, skill currency, and gaps on the resume — all solvable."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Update skills to current market standards in your field", "why": "A 2-3 year break creates a skills delta — closing it signals readiness to employers", "timeline": "Weeks 1-6"},
            {"id": 2, "subgoal": "Apply to formal returnship programs at large companies", "why": "Returnship programs are designed for exactly your profile and have 60-80% conversion to full-time", "timeline": "Week 3 onwards"},
            {"id": 3, "subgoal": "Build a network in your previous domain", "why": "Referral hires account for 40% of senior placements", "timeline": "Week 2 onwards"},
        ],
        "immediate_actions": [
            {"action": "Check returnship programs: Infosys Rekindle, TCS BPS Returnship, Goldman Sachs Returnship India", "resource": "infosys.com/careers / tcs.com/careers", "expected_outcome": "Applications submitted to structured programs with mentorship support"},
            {"action": "Join the 'Women Back to Work' group on LinkedIn", "resource": "linkedin.com", "expected_outcome": "Connect with others in the same journey and get referrals"},
            {"action": "Take a 4-week refresher course on Coursera or Udemy in your domain", "resource": "coursera.org / udemy.com", "expected_outcome": "Skills updated, can confidently discuss recent developments in interviews"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Skills refresh and applications", "milestones": ["Refresher course enrolled", "3 returnship applications submitted", "LinkedIn updated"], "resources_needed": ["Coursera / NPTEL", "LinkedIn"]},
            {"phase": "60 Days", "focus": "Interviews and networking", "milestones": ["2+ returnship interviews", "5 reconnections with prior colleagues"], "resources_needed": ["Interview prep resources"]},
            {"phase": "90 Days", "focus": "Placement and onboarding", "milestones": ["Returnship or direct hire offer", "Transition plan for home responsibilities"], "resources_needed": ["Offer negotiation support"]},
        ],
        "key_resources": [
            {"name": "Infosys Rekindle Program", "type": "Returnship", "url_or_contact": "infosys.com/careers", "how_it_helps": "6-month paid returnship for experienced women in tech"},
            {"name": "NPTEL Online Courses", "type": "Platform", "url_or_contact": "nptel.ac.in", "how_it_helps": "Free IIT-quality courses with certification for skill refresher"},
            {"name": "Sheroes Returnship Board", "type": "Platform", "url_or_contact": "sheroes.com/jobs", "how_it_helps": "Job board specifically for women returning to work"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Employers question the career break", "mitigation": "Frame the break as a life management achievement. Highlight any freelance, volunteer, or learning activity during it."},
            {"risk": "Salary offered is below pre-break level", "mitigation": "Negotiate based on market rate, not break duration. Your experience still commands market value."},
        ],
        "success_metrics": [
            "At least one returnship or direct application accepted within 90 days",
            "Salary within 15% of pre-break level",
            "Skills refresher completed within 45 days",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Domain: legal
# ---------------------------------------------------------------------------
_LEGAL_PLANS = [
    {
        "goal": "Understanding and exercising workplace legal rights in India",
        "domain": "legal",
        "executive_summary": (
            "Indian women have strong legal protections under multiple acts — POSH, Maternity "
            "Benefit Act, Equal Remuneration Act, and the new Bharatiya Nyaya Sanhita. "
            "This plan covers how to document violations, escalate through the right channels, "
            "and access free legal aid."
        ),
        "situation_analysis": (
            "Workplace violations against women in India range from sexual harassment (covered "
            "by POSH Act 2013) to maternity benefit denial, pay discrimination, and wrongful "
            "termination. Most women are unaware that every company with 10+ employees is "
            "legally required to have an Internal Complaints Committee (ICC). Filing a complaint "
            "is the first step — and you are legally protected from retaliation."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Document every incident with dates, times, witnesses, and screenshots", "why": "Documentation is the foundation of any legal case — without it, claims are hard to prove", "timeline": "Immediately"},
            {"id": 2, "subgoal": "Identify and approach your company's ICC or HR", "why": "POSH mandates a 90-day investigation — formal reporting triggers this clock", "timeline": "Within 1 week"},
            {"id": 3, "subgoal": "Consult a free legal aid lawyer if internal process fails", "why": "NALSA provides free legal services to women — use this before spending on private lawyers", "timeline": "If ICC fails or is biased"},
            {"id": 4, "subgoal": "File with the Labour Commissioner or NCW if employer is unresponsive", "why": "External escalation has real consequences for employers — penalties and public record", "timeline": "30 days after internal complaint if unresolved"},
        ],
        "immediate_actions": [
            {"action": "Write down every incident with exact date, time, location, what was said/done, and who witnessed it", "resource": "Secure private document (Google Drive with 2FA)", "expected_outcome": "Legal-grade evidence record that can be submitted to any authority"},
            {"action": "Email HR formally requesting confirmation of your ICC details and complaint process", "resource": "Company email — keep all copies", "expected_outcome": "Creates a paper trail; puts company on notice"},
            {"action": "Call NALSA (National Legal Services Authority) for free legal advice", "resource": "nalsa.gov.in / 15100", "expected_outcome": "Free consultation with a qualified lawyer within 48 hours"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Document, report internally, get legal advice", "milestones": ["Complete incident log", "ICC complaint filed", "Free legal consultation done"], "resources_needed": ["NALSA 15100", "Company ICC"]},
            {"phase": "60 Days", "focus": "ICC investigation period", "milestones": ["ICC investigation underway", "Interim relief requested if needed", "Evidence submitted"], "resources_needed": ["Legal aid lawyer", "NCW if ICC is biased"]},
            {"phase": "90 Days", "focus": "Resolution or external escalation", "milestones": ["ICC verdict received", "Labour Commissioner complaint if unsatisfied", "Compensation or remedial action"], "resources_needed": ["Labour Commissioner office", "High Court if needed"]},
        ],
        "key_resources": [
            {"name": "NALSA Free Legal Aid", "type": "Contact", "url_or_contact": "nalsa.gov.in / 15100", "how_it_helps": "Free legal services for women — consultation, representation, documentation"},
            {"name": "NCW Online Complaint", "type": "Platform", "url_or_contact": "ncwapps.nic.in", "how_it_helps": "National Commission for Women — file complaints about harassment, discrimination, rights violations"},
            {"name": "SHe-Box Portal", "type": "Platform", "url_or_contact": "shebox.nic.in", "how_it_helps": "Official government portal to file POSH complaints against central government employees"},
            {"name": "Labour Commissioner", "type": "Contact", "url_or_contact": "labour.gov.in", "how_it_helps": "Handles pay discrimination, wrongful termination, and labor law violations"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Employer retaliation after complaint", "mitigation": "Retaliation is illegal under POSH Section 17. Document any adverse action after filing — it strengthens your case significantly."},
            {"risk": "ICC is biased or employer-controlled", "mitigation": "POSH requires an external member on every ICC. If biased, escalate to the Local Complaints Committee (LCC) through the District Collector."},
            {"risk": "Fear of job loss", "mitigation": "While genuine, the law protects you. Simultaneously, start a quiet job search so you have options."},
        ],
        "success_metrics": [
            "Incident log completed within 48 hours",
            "Formal complaint filed within 7 days",
            "ICC investigation completed within 90 days (legal requirement)",
            "Violation acknowledged or remedied, or external escalation underway",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Domain: financial
# ---------------------------------------------------------------------------
_FINANCIAL_PLANS = [
    {
        "goal": "Financial independence and wealth building for women in India",
        "domain": "financial",
        "executive_summary": (
            "Financial independence for Indian women requires three parallel tracks: income "
            "growth, debt elimination, and systematic investment. Government schemes provide "
            "substantial support through subsidised loans, insurance, and pension programs "
            "specifically for women."
        ),
        "situation_analysis": (
            "Only 20% of Indian women have independent financial accounts, and fewer than 10% "
            "actively invest. Cultural barriers, income gaps, and limited financial literacy "
            "contribute to this. However, multiple government schemes (Mahila Samman, PM Jan "
            "Dhan, Sukanya Samriddhi) plus growing fintech access are creating real pathways "
            "to financial sovereignty."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Open a dedicated savings account and emergency fund (3-6 months expenses)", "why": "Emergency fund prevents debt spirals and gives negotiating power", "timeline": "Week 1"},
            {"id": 2, "subgoal": "Start a monthly SIP in a diversified mutual fund (even Rs. 500/month)", "why": "Compounding over 10 years turns Rs. 1000/month into Rs. 2.3 lakh at 12% returns", "timeline": "Week 2"},
            {"id": 3, "subgoal": "Enroll in Mahila Samman Savings Certificate for guaranteed 7.5% returns", "why": "Government-backed, higher rate than FD, specifically for women", "timeline": "Month 1"},
            {"id": 4, "subgoal": "Get a term life insurance and health insurance policy in your own name", "why": "Women with dependents are severely under-insured — one health emergency erases savings", "timeline": "Month 1-2"},
        ],
        "immediate_actions": [
            {"action": "Open a zero-balance Jan Dhan account if you don't have one, or upgrade to a full savings account at any PSU bank", "resource": "Nearest SBI/PNB branch or PM Jan Dhan Yojana portal", "expected_outcome": "Dedicated account that is yours alone, linked to your Aadhaar"},
            {"action": "Download Groww or Zerodha Kite and start a SIP of whatever you can afford", "resource": "groww.in / zerodha.com", "expected_outcome": "Investing habit formed; even Rs. 500/month builds discipline"},
            {"action": "Check your Post Office for the Mahila Samman Savings Certificate (MSSC) — deposit up to Rs. 2 lakh at 7.5% for 2 years", "resource": "India Post nearest branch", "expected_outcome": "Guaranteed return higher than any FD, government-backed"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Foundation accounts and emergency fund", "milestones": ["Savings account opened", "Emergency fund started", "MSSC account opened", "SIP started"], "resources_needed": ["Any PSU bank", "India Post", "Groww/Zerodha"]},
            {"phase": "60 Days", "focus": "Insurance and tax planning", "milestones": ["Term insurance policy active", "Health insurance active", "Tax-saving investments identified (80C, 80D)"], "resources_needed": ["LIC / HDFC Life", "Star Health / Niva Bupa"]},
            {"phase": "90 Days", "focus": "Income growth and debt clearing", "milestones": ["High-interest debt plan in place", "Income increased by upskilling or side income", "3-month expenses in emergency fund"], "resources_needed": ["Skill platforms", "Debt consolidation guidance"]},
        ],
        "key_resources": [
            {"name": "Mahila Samman Savings Certificate", "type": "Scheme", "url_or_contact": "India Post / indiapost.gov.in", "how_it_helps": "7.5% guaranteed interest for 2 years, up to Rs. 2 lakh — only for women"},
            {"name": "PM Jan Dhan Yojana", "type": "Scheme", "url_or_contact": "pmjdy.gov.in", "how_it_helps": "Zero-balance account with Rs. 10,000 overdraft, Rs. 2 lakh accident insurance, Rs. 30,000 life cover"},
            {"name": "Groww Mutual Fund Platform", "type": "Platform", "url_or_contact": "groww.in", "how_it_helps": "Start SIP from Rs. 100/month, zero commission, direct plans"},
            {"name": "NPS Swavalamban (Atal Pension Yojana)", "type": "Scheme", "url_or_contact": "npscra.nsdl.co.in", "how_it_helps": "Government co-contributes to your pension — especially valuable for informal sector workers"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Not enough money to start investing", "mitigation": "Start with Rs. 100/month SIP — the habit matters more than the amount in the first 6 months."},
            {"risk": "Family pressure to hand over control of finances", "mitigation": "Keep at least one account solely in your name. Legal right to your own income is protected under Indian law."},
            {"risk": "Investment losses in market downturns", "mitigation": "Keep emergency fund in FD/MSSC (guaranteed), invest only surplus in equity SIPs for long-term (10+ year) goals."},
        ],
        "success_metrics": [
            "Emergency fund of 3 months expenses built within 6 months",
            "SIP running consistently for 3+ months",
            "At least one insurance policy active in your own name",
            "Net worth tracking started (simple spreadsheet is fine)",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Domain: education
# ---------------------------------------------------------------------------
_EDUCATION_PLANS = [
    {
        "goal": "Scholarships and education pathways for women in India",
        "domain": "education",
        "executive_summary": (
            "India has over 50 central government scholarship programs specifically for women, "
            "plus state-level and private scholarships. The key is knowing which ones you are "
            "eligible for and applying systematically before deadlines. This plan covers the "
            "top scholarships by category and application strategy."
        ),
        "situation_analysis": (
            "Women in India are eligible for scholarships from NSP (National Scholarship "
            "Portal), UGC, AICTE, state governments, and private foundations. Many go "
            "unclaimed because applicants don't know about them or miss deadlines. The "
            "National Scholarship Portal alone has 104 scholarship schemes with combined "
            "coverage of over 1 crore students annually."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Register on the National Scholarship Portal and check eligibility for all applicable schemes", "why": "NSP is the single gateway to 104 central government scholarships — one registration, multiple applications", "timeline": "Week 1"},
            {"id": 2, "subgoal": "Apply to at least 3 scholarships you are eligible for before their deadlines", "why": "Multiple applications increase the probability of receiving at least one", "timeline": "Weeks 1-3"},
            {"id": 3, "subgoal": "Explore free skill development programs under PMKVY and NSDC", "why": "Free certified training worth Rs. 10,000-50,000 available to eligible candidates", "timeline": "Month 1"},
        ],
        "immediate_actions": [
            {"action": "Register on scholarships.gov.in with your Aadhaar, bank account, and academic documents", "resource": "scholarships.gov.in (National Scholarship Portal)", "expected_outcome": "Access to all 104 central government scholarships in one place"},
            {"action": "Check AICTE Pragati Scholarship for technical education (Rs. 50,000/year for women)", "resource": "aicte-pragati-saksham-gov.in", "expected_outcome": "Annual scholarship covering tuition and expenses for tech programs"},
            {"action": "Apply to Begum Hazrat Mahal National Scholarship for Class 9-12 minority girls", "resource": "maef.nic.in", "expected_outcome": "Rs. 10,000-12,000 annual scholarship for minority community students"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Registration and applications", "milestones": ["NSP registered", "3+ scholarship applications submitted", "PMKVY enrollment checked"], "resources_needed": ["Aadhaar", "Bank account", "Marksheets", "Income certificate"]},
            {"phase": "60 Days", "focus": "Results and skill programs", "milestones": ["Scholarship results checked", "Free skill program enrolled", "State-level scholarships applied"], "resources_needed": ["State scholarship portal", "NSDC portal"]},
            {"phase": "90 Days", "focus": "Funding received and next cycle", "milestones": ["Scholarship amount disbursed", "Academic plan updated", "Next year scholarships identified"], "resources_needed": ["Bank account linked to NSP"]},
        ],
        "key_resources": [
            {"name": "National Scholarship Portal", "type": "Platform", "url_or_contact": "scholarships.gov.in", "how_it_helps": "104 central government scholarships — one registration covers all"},
            {"name": "AICTE Pragati Scholarship", "type": "Scheme", "url_or_contact": "aicte-pragati-saksham-gov.in", "how_it_helps": "Rs. 50,000/year for women in AICTE-approved technical programs"},
            {"name": "PMKVY Free Skill Training", "type": "Scheme", "url_or_contact": "pmkvyofficial.org", "how_it_helps": "Free industry-certified skill training with stipend for eligible candidates"},
            {"name": "SWAYAM Free University Courses", "type": "Platform", "url_or_contact": "swayam.gov.in", "how_it_helps": "Free UGC-credit courses from IITs, IIMs, and central universities"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Missing scholarship deadlines", "mitigation": "Set phone reminders for each scholarship deadline. NSP typically opens August-October every year."},
            {"risk": "Application rejected due to document issues", "mitigation": "Get income certificate, caste certificate, and domicile certificate from your local tehsildar in advance — they take 1-2 weeks."},
            {"risk": "Scholarship amount not sufficient for full fees", "mitigation": "Stack multiple scholarships — you can receive state + central + private scholarships simultaneously in many cases."},
        ],
        "success_metrics": [
            "NSP registration completed within 7 days",
            "Minimum 3 scholarship applications submitted before deadlines",
            "At least one scholarship received",
            "Free skill certification completed",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Domain: grants
# ---------------------------------------------------------------------------
_GRANTS_PLANS = [
    {
        "goal": "Government grants and startup funding for women entrepreneurs in India",
        "domain": "grants",
        "executive_summary": (
            "India has a robust ecosystem of grants, loans, and incubators for women "
            "entrepreneurs — from PM Mudra Yojana (up to Rs. 10 lakh, no collateral) to "
            "Startup India Seed Fund (up to Rs. 20 lakh) and WEP (Women Entrepreneurship "
            "Platform). The key is knowing which scheme fits your business stage."
        ),
        "situation_analysis": (
            "Women-led businesses in India face a funding gap of $158 billion, yet the "
            "government has deployed over Rs. 1.5 lakh crore through Mudra alone. The "
            "problem is awareness and application quality — most eligible women either don't "
            "know the schemes exist, or their business plans don't meet the basic criteria. "
            "This plan solves both problems."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Identify the right funding scheme for your business stage and size", "why": "Different schemes have different eligibility — applying to the wrong one wastes time and affects your CIBIL", "timeline": "Week 1"},
            {"id": 2, "subgoal": "Prepare a basic business plan (1-2 pages) with cost breakdown and revenue model", "why": "All schemes require a business plan — even a simple one dramatically improves approval rates", "timeline": "Weeks 1-2"},
            {"id": 3, "subgoal": "Apply to PM Mudra Yojana through any PSU bank branch", "why": "Mudra loans up to Rs. 10 lakh with no collateral, specifically designed for micro-entrepreneurs", "timeline": "Week 2"},
            {"id": 4, "subgoal": "Register on Women Entrepreneurship Platform (WEP) for mentorship and network", "why": "WEP connects you to incubators, investors, and market linkages — beyond just funding", "timeline": "Week 1"},
        ],
        "immediate_actions": [
            {"action": "Register on WEP (wep.gov.in) — free, takes 10 minutes, gives access to mentors, loans, and incubators", "resource": "wep.gov.in", "expected_outcome": "Access to government-curated mentors, schemes, and women-specific opportunities"},
            {"action": "Visit your nearest PSU bank branch and ask specifically for PM Mudra Yojana — Shishu (up to Rs. 50,000), Kishore (up to Rs. 5 lakh), or Tarun (up to Rs. 10 lakh)", "resource": "mudra.org.in / any SBI, PNB, Bank of Baroda branch", "expected_outcome": "Collateral-free business loan with subsidised interest rate"},
            {"action": "Write a 1-page business plan: what you sell, who buys it, how much it costs to start, expected monthly revenue", "resource": "Template at sidbi.in or any MSME Development Centre", "expected_outcome": "Required document for all funding applications — your single most important asset"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Registration and documentation", "milestones": ["WEP registered", "Udyam registration done (free, for MSME benefits)", "Business plan drafted", "Mudra application submitted"], "resources_needed": ["udyamregistration.gov.in", "mudra.org.in", "wep.gov.in"]},
            {"phase": "60 Days", "focus": "Loan processing and incubator applications", "milestones": ["Mudra loan decision received", "Applied to 1-2 state-level women entrepreneur schemes", "Incubator application submitted if eligible"], "resources_needed": ["State MSME department", "Startup India portal"]},
            {"phase": "90 Days", "focus": "Funding received and deployment", "milestones": ["Funding in hand", "Business officially launched or scaled", "Monthly revenue tracking started", "Next funding round planned"], "resources_needed": ["Bank account", "GST registration if applicable"]},
        ],
        "key_resources": [
            {"name": "PM Mudra Yojana", "type": "Scheme", "url_or_contact": "mudra.org.in", "how_it_helps": "Up to Rs. 10 lakh, no collateral, low interest — the most accessible business loan for women"},
            {"name": "Women Entrepreneurship Platform (WEP)", "type": "Platform", "url_or_contact": "wep.gov.in", "how_it_helps": "Government platform for mentorship, funding access, incubators, and skill development"},
            {"name": "Startup India Seed Fund", "type": "Scheme", "url_or_contact": "startupindia.gov.in/seedfund", "how_it_helps": "Up to Rs. 20 lakh grant for early-stage tech startups — no repayment required"},
            {"name": "CGTMSE Scheme", "type": "Scheme", "url_or_contact": "cgtmse.in", "how_it_helps": "Credit guarantee for collateral-free loans up to Rs. 2 crore for MSMEs"},
            {"name": "Stand-Up India", "type": "Scheme", "url_or_contact": "standupmitra.in", "how_it_helps": "Rs. 10 lakh to Rs. 1 crore loans for SC/ST and women entrepreneurs — one loan per bank branch guaranteed"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Loan application rejected", "mitigation": "Apply to multiple banks simultaneously for Mudra — each bank has independent discretion. SIDBI also has a direct lending arm."},
            {"risk": "Business plan is weak", "mitigation": "Contact your nearest MSME Development and Facilitation Office (MSME-DFO) — they provide free business plan support."},
            {"risk": "No CIBIL score or poor CIBIL", "mitigation": "Mudra Shishu (up to Rs. 50,000) is accessible even with no credit history. Start there, repay on time, and graduate to higher amounts."},
            {"risk": "Business fails after taking loan", "mitigation": "CGFMU insurance covers micro-enterprise loans. Restructuring options available through bank — communicate early rather than defaulting."},
        ],
        "success_metrics": [
            "WEP and Udyam registration completed within 7 days",
            "Business plan document completed within 14 days",
            "At least one funding application submitted within 30 days",
            "Funding received and business operational within 90 days",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Domain: general (used when domain is unknown or 'general')
# ---------------------------------------------------------------------------
_GENERAL_PLANS = [
    {
        "goal": "Comprehensive empowerment strategy for women in India",
        "domain": "general",
        "executive_summary": (
            "SHE-ORACLE's general empowerment framework covers four pillars: financial "
            "independence, legal awareness, career growth, and access to government schemes. "
            "This plan gives you a foundation across all four so you can identify and act on "
            "your most pressing priority."
        ),
        "situation_analysis": (
            "Empowerment for Indian women requires simultaneous action across career, legal, "
            "financial, and social dimensions. Government support is substantial but fragmented "
            "across 50+ ministries. This plan helps you navigate the ecosystem and take "
            "immediate, concrete steps regardless of where you are starting from."
        ),
        "subgoals": [
            {"id": 1, "subgoal": "Assess your current position on 4 pillars: career, legal rights, finances, and support network", "why": "You cannot plan what you cannot measure — a clear baseline reveals where to act first", "timeline": "Day 1"},
            {"id": 2, "subgoal": "Identify and connect with one government support structure in your area", "why": "Mahila Police Volunteers, District Legal Services Authority, and Women's Help Desks are free and underutilised", "timeline": "Week 1"},
            {"id": 3, "subgoal": "Set up basic financial independence: own bank account, savings habit, basic insurance", "why": "Financial autonomy is the foundation — it gives you options in every other domain", "timeline": "Week 2"},
            {"id": 4, "subgoal": "Know your top 3 legal rights as a woman and how to exercise them", "why": "Most violations go unchallenged because women don't know their rights are being violated", "timeline": "Week 1"},
        ],
        "immediate_actions": [
            {"action": "Call the Women's Helpline 181 to understand what government support is available in your district", "resource": "181 (nationwide, free, 24/7)", "expected_outcome": "Awareness of local resources and immediate support if needed"},
            {"action": "Register on MyScheme.gov.in with your Aadhaar to see all government schemes you are eligible for", "resource": "myscheme.gov.in", "expected_outcome": "Personalised list of 10-50 government schemes you can apply for right now"},
            {"action": "Open a Mahila Samman Savings Certificate at your post office for guaranteed 7.5% returns", "resource": "India Post nearest branch", "expected_outcome": "Savings growing at higher rate than any bank FD, in your name"},
        ],
        "roadmap": [
            {"phase": "30 Days", "focus": "Foundation: know your rights, open your accounts, connect with support", "milestones": ["MyScheme eligibility check done", "Bank account in own name", "181 helpline contact noted", "Top legal rights understood"], "resources_needed": ["Aadhaar", "MyScheme portal", "India Post"]},
            {"phase": "60 Days", "focus": "Growth: apply to relevant schemes, build income, start investing", "milestones": ["1-2 scheme applications submitted", "Skill course enrolled", "SIP started at any amount"], "resources_needed": ["NSP scholarships portal", "PMKVY", "Groww/Zerodha"]},
            {"phase": "90 Days", "focus": "Independence: career growth, financial buffer, legal literacy", "milestones": ["Emergency fund started", "Career next step defined", "Network of 3+ mentors or peers built"], "resources_needed": ["Sheroes community", "LinkedIn", "NALSA free legal aid"]},
        ],
        "key_resources": [
            {"name": "Women's Helpline 181", "type": "Contact", "url_or_contact": "181", "how_it_helps": "24/7 free helpline connecting women to police, legal aid, shelter, and counselling"},
            {"name": "MyScheme Portal", "type": "Platform", "url_or_contact": "myscheme.gov.in", "how_it_helps": "Find all government schemes you are eligible for based on your profile"},
            {"name": "NALSA Free Legal Services", "type": "Contact", "url_or_contact": "nalsa.gov.in / 15100", "how_it_helps": "Free legal advice and representation for women"},
            {"name": "Sheroes Women's Community", "type": "Platform", "url_or_contact": "sheroes.com", "how_it_helps": "Peer support, mentors, jobs, and resources for women at every stage"},
            *_FALLBACK_RESOURCES,
        ],
        "risk_mitigation": [
            {"risk": "Overwhelmed by too many options", "mitigation": "Pick ONE action from immediate_actions and complete it today. Momentum matters more than comprehensiveness."},
            {"risk": "Family or social resistance", "mitigation": "Start with actions that are private and don't require permission — bank account, online learning, helpline calls."},
            {"risk": "Geographic barriers (rural areas)", "mitigation": "181, NALSA, and MyScheme all work via phone. Post office and PSU bank branches exist in every taluka."},
        ],
        "success_metrics": [
            "MyScheme eligibility check completed within 3 days",
            "At least one government scheme applied to within 30 days",
            "Financial account in own name opened within 7 days",
            "One concrete next step defined and acted on within the first week",
        ],
        "tool_insights": {"note": _FALLBACK_NOTE},
    },
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_DOMAIN_MAP: dict[str, list] = {
    "career": _CAREER_PLANS,
    "legal": _LEGAL_PLANS,
    "financial": _FINANCIAL_PLANS,
    "education": _EDUCATION_PLANS,
    "grants": _GRANTS_PLANS,
    "general": _GENERAL_PLANS,
}


def get_fallback_plan(domain: str, goal: str = "") -> dict:
    """
    Return a curated fallback plan for the given domain.

    Picks randomly from the available plans for the domain so repeated
    requests don't always return identical content.  If the domain is
    unknown, falls back to 'general'.
    """
    plans = _DOMAIN_MAP.get(domain, _GENERAL_PLANS)
    plan = random.choice(plans).copy()
    # Personalise goal field with what the user actually typed, if provided
    if goal:
        plan["goal"] = goal
    return plan
