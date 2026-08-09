"""
Knowledge base for the Meridian State University Admissions FAQ Assistant.

Structure: a flat list of entries. Each entry is a single fact/answer unit,
tagged with a category and a list of paraphrases ("patterns") a user might
type. The retrieval layer matches the user's raw question text against the
`question` + `patterns` text of every entry using TF-IDF cosine similarity,
picks the best-scoring entry, and (if the score clears CONFIDENCE_THRESHOLD)
hands that entry's `answer` to the LLM as grounding context so it can phrase
a natural reply without inventing facts. Below the threshold, the assistant
returns FALLBACK_MESSAGE instead of calling the LLM at all.

All data below is placeholder/fictional (Meridian State University).
"""

FALLBACK_CONTACT_EMAIL = "admissions@meridianstate.edu"
FALLBACK_CONTACT_PHONE = "+1 (555) 019-2028"
CONFIDENCE_THRESHOLD = 0.5  # blended TF-IDF + keyword-overlap score, 0-1. Below this -> fallback.

FALLBACK_MESSAGE = (
    f"I'm not confident I have an accurate answer to that yet. "
    f"Please contact our admissions team at {FALLBACK_CONTACT_EMAIL} "
    f"or call {FALLBACK_CONTACT_PHONE} and they'll be happy to help."
)

KNOWLEDGE_BASE = [
    {
        "id": "fall_deadline",
        "category": "Deadlines",
        "question": "When is the fall application deadline?",
        "patterns": ["fall deadline", "when do applications close", "last date to apply for fall", "when do apps close", "application closing date"],
        "answer": "The Fall semester application deadline is March 15. We recommend submitting at least a week early in case of technical issues.",
    },
    {
        "id": "early_decision_deadline",
        "category": "Deadlines",
        "question": "When is the Early Decision deadline?",
        "patterns": ["early decision deadline", "ED deadline", "early application date"],
        "answer": "Early Decision applications are due November 1, with decisions released by December 15.",
    },
    {
        "id": "decision_release",
        "category": "Deadlines",
        "question": "When are admission decisions released?",
        "patterns": ["when will I hear back", "decision release date", "when are decisions released"],
        "answer": "Regular Decision applicants are notified by April 15. Early Decision applicants are notified by December 15.",
    },
    {
        "id": "application_fee",
        "category": "Fees",
        "question": "How much does applying cost?",
        "patterns": ["application fee", "cost to apply", "how much is the application"],
        "answer": "The application fee is $50 USD for domestic applicants and $75 USD for international applicants, payable online by card.",
    },
    {
        "id": "fee_waiver",
        "category": "Fees",
        "question": "Is a fee waiver available?",
        "patterns": ["fee waiver", "can't afford application fee", "waive application fee"],
        "answer": "Fee waivers are available for applicants with demonstrated financial need. Request one in the application portal under the 'Fees' section before submitting.",
    },
    {
        "id": "tuition_cost",
        "category": "Fees",
        "question": "What is annual tuition?",
        "patterns": ["tuition cost", "how much is tuition", "yearly fees"],
        "answer": "Annual tuition is $28,400 for domestic students and $41,200 for international students, not including housing or meal plans.",
    },
    {
        "id": "gpa_requirement",
        "category": "Requirements",
        "question": "What GPA do I need to apply?",
        "patterns": ["minimum GPA", "GPA requirement", "what grades do I need"],
        "answer": "There is no strict minimum GPA, but admitted students typically have a high school GPA of 3.3 or above on a 4.0 scale.",
    },
    {
        "id": "test_scores",
        "category": "Requirements",
        "question": "Are SAT or ACT scores required?",
        "patterns": ["SAT required", "ACT required", "standardized test scores"],
        "answer": "Meridian State is test-optional. You may submit SAT or ACT scores to strengthen your application, but they are not required.",
    },
    {
        "id": "required_documents",
        "category": "Requirements",
        "question": "What documents do I need to submit?",
        "patterns": ["required documents", "what do I need to submit", "application checklist"],
        "answer": "You'll need a completed application form, official high school transcript, one letter of recommendation, and a 500-word personal statement.",
    },
    {
        "id": "english_proficiency",
        "category": "Requirements",
        "question": "Do international students need an English test?",
        "patterns": ["TOEFL required", "IELTS required", "English proficiency requirement", "english language test", "toefl"],
        "answer": "International applicants whose first language isn't English must submit TOEFL (min. 80) or IELTS (min. 6.5) scores.",
    },
    {
        "id": "financial_aid_types",
        "category": "Financial Aid",
        "question": "What types of financial aid are available?",
        "patterns": ["financial aid options", "scholarships available", "types of aid", "what scholarships are there", "merit aid options"],
        "answer": "We offer need-based grants, merit scholarships, and federal work-study placements. Most aid is awarded automatically based on your application.",
    },
    {
        "id": "scholarship_deadline",
        "category": "Financial Aid",
        "question": "When is the scholarship application deadline?",
        "patterns": ["scholarship deadline", "merit scholarship due date"],
        "answer": "Merit scholarship consideration uses the same March 15 deadline as regular admission — no separate application is required.",
    },
    {
        "id": "fafsa",
        "category": "Financial Aid",
        "question": "Do I need to file the FAFSA?",
        "patterns": ["FAFSA required", "need-based aid application", "file FAFSA"],
        "answer": "Domestic applicants seeking need-based aid should file the FAFSA by March 1 using school code 004215.",
    },
    {
        "id": "housing_guarantee",
        "category": "Campus Life",
        "question": "Is on-campus housing guaranteed for first-year students?",
        "patterns": ["housing guaranteed", "first year housing", "dorm guarantee"],
        "answer": "Yes, on-campus housing is guaranteed for all first-year students who submit their housing form by June 1.",
    },
    {
        "id": "majors_offered",
        "category": "Academics",
        "question": "What majors or programs does the university offer?",
        "patterns": ["majors offered", "programs available", "what can I study", "degree programs", "what majors do you offer"],
        "answer": "Meridian State offers 42 undergraduate majors across five colleges: Arts & Sciences, Engineering, Business, Education, and Health Sciences.",
    },
    {
        "id": "campus_visit",
        "category": "Campus Life",
        "question": "Can I schedule a campus visit or tour?",
        "patterns": ["campus tour", "schedule a visit", "open house", "visiting campus", "book a tour"],
        "answer": "Yes — campus tours run Monday through Saturday. Book a slot through the 'Visit Us' page on the admissions website.",
    },
    {
        "id": "transfer_students",
        "category": "Process",
        "question": "Can I apply as a transfer student?",
        "patterns": ["transfer application", "transfer student process", "transferring credits", "how transfer applications work", "transfer process"],
        "answer": "Transfer applicants need a minimum 2.75 college GPA and official transcripts from all previously attended institutions. The transfer deadline is May 1.",
    },
    {
        "id": "application_status",
        "category": "Process",
        "question": "How do I check my application status?",
        "patterns": ["check application status", "track my application", "application portal login"],
        "answer": "Log into the applicant portal with the email you used to apply — status updates (received, under review, decision) appear on your dashboard.",
    },
    {
        "id": "contact_admissions",
        "category": "Contact",
        "question": "How do I contact the admissions office?",
        "patterns": ["contact admissions", "admissions office phone number", "admissions email"],
        "answer": f"You can reach the Office of Admissions at {FALLBACK_CONTACT_EMAIL} or {FALLBACK_CONTACT_PHONE}, Monday through Friday, 9am-5pm.",
    },
]
