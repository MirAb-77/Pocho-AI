
"""
chitchat.py

Local, rule-based small talk + common admissions conversations.

No API call.
No network dependency.
No external services.

This module sits between the Grok chat reply and the static FALLBACK_MESSAGE.

It handles common conversational and admissions-related questions locally so
students still receive useful responses when:
    - the KB does not contain a matching answer
    - Grok is unavailable
    - the API key is missing
    - the network request fails

IMPORTANT:
This module intentionally does NOT try to invent university-specific facts
such as exact deadlines, fees, GPA cutoffs, scholarship amounts, or program
availability. Those should continue to come from the KB / authoritative
admissions data.

If a question is not confidently recognized here, local_chat_reply()
returns None so the existing caller can continue to the normal fallback flow.
"""

import random
import re


# ============================================================================
# HELPERS
# ============================================================================

def _clean_question(question: str) -> str:
    """
    Normalize user input while preserving the original meaning.
    """
    q = (question or "").strip()

    if not q:
        return ""

    # Normalize whitespace.
    q = re.sub(r"\s+", " ", q)

    return q


def _reply(replies):
    """Return one natural response from a list."""
    return random.choice(replies)


# ============================================================================
# SMALL TALK
# ============================================================================

_GREETING = re.compile(
    r"^\s*(?:"
    r"hi+|hello+|hey+|hiya|yo|sup|"
    r"good\s+(?:morning|afternoon|evening)|"
    r"hey\s+there|hello\s+there"
    r")\b",
    re.I,
)

_THANKS = re.compile(
    r"\b(?:"
    r"thanks|thank you|thank u|thx|ty|"
    r"much appreciated|appreciate it|"
    r"thanks a lot|thank you so much"
    r")\b",
    re.I,
)

_BYE = re.compile(
    r"^\s*(?:"
    r"bye|goodbye|good bye|see ya|see you|"
    r"cya|later|take care|talk to you later"
    r")\b",
    re.I,
)

_HOW_ARE_YOU = re.compile(
    r"\b(?:"
    r"how are you|"
    r"how are u|"
    r"how's it going|"
    r"how is it going|"
    r"how have you been|"
    r"how are things"
    r")\b",
    re.I,
)

_WHO_WHAT = re.compile(
    r"\b(?:"
    r"who are you|"
    r"what are you|"
    r"what can you do|"
    r"what can you help with|"
    r"how can you help me|"
    r"what do you do|"
    r"what are your capabilities|"
    r"are you a bot|"
    r"are you an ai|"
    r"are you ai"
    r")\b|"
    r"^\s*help\s*$",
    re.I,
)

_GREETING_REPLIES = [
    (
        "Hey there! I'm the admissions assistant for Meridian State "
        "University. I can help with applications, eligibility, documents, "
        "deadlines, fees, scholarships, international admissions, programs, "
        "and campus life."
    ),
    (
        "Hello! Happy to help with your admission journey. "
        "You can ask me about requirements, deadlines, fees, financial aid, "
        "programs, documents, or what to do next."
    ),
    (
        "Hi! Ask me anything about admissions — from "
        "\"Can I apply?\" and \"What documents do I need?\" to fees, "
        "scholarships, programs, and enrollment."
    ),
]

_THANKS_REPLIES = [
    "You're welcome! Let me know if you have another admissions question.",
    "Anytime! Good luck with your application.",
    "Glad I could help. Feel free to ask about another part of the admissions process.",
    "You're very welcome. If you're unsure about your next application step, just ask.",
]

_BYE_REPLIES = [
    "Take care, and good luck with your application!",
    "See you! Feel free to come back whenever you have another admissions question.",
    "Good luck with your admission journey. Take care!",
]

_HOW_ARE_YOU_REPLIES = [
    "I'm doing well, thanks for asking! What can I help you with regarding your application?",
    "Doing great! I'm ready to help with your admissions questions.",
]

_WHO_WHAT_REPLIES = [
    (
        "I'm the admissions assistant for Meridian State University. "
        "I can help you understand applications, eligibility, documents, "
        "deadlines, fees, financial aid, programs, international admissions, "
        "and enrollment."
    ),
    (
        "I'm Meridian State University's admissions assistant. "
        "Ask me about the application process, requirements, scholarships, "
        "programs, campus information, or what you should do next."
    ),
]


# ============================================================================
# ADMISSIONS RESPONSE BANK
# ============================================================================

# Each entry:
#
# (
#     intent_name,
#     priority,
#     compiled_regex,
#     [responses]
# )
#
# Higher priority = more specific intent.
#
# This prevents a broad pattern such as "master's" from winning over a more
# specific question such as "Can I apply for a master's without IELTS?"

_ADMISSIONS_PATTERNS = [

    # ========================================================================
    # APPLICATION PROCESS
    # ========================================================================

    (
        "how_to_apply",
        90,
        re.compile(
            r"\b(?:"
            r"how (?:do|can) i apply|"
            r"how to apply|"
            r"where do i apply|"
            r"how can i get admission|"
            r"how does applying work|"
            r"how does admission work|"
            r"explain the admission process|"
            r"explain admission|"
            r"what is the application process|"
            r"what is the admission process|"
            r"how do admissions work|"
            r"where do i start"
            r")\b",
            re.I,
        ),
        [
            (
                "The admission process generally starts with choosing a "
                "program and checking its eligibility requirements. You then "
                "prepare the required documents, submit the application, and "
                "monitor your application for updates or additional requests."
            ),
            (
                "A good place to start is: choose your program, check "
                "eligibility, review the required documents, confirm the "
                "deadline, and submit your application. If you tell me your "
                "program and applicant type, I can help you identify the "
                "requirements you should check."
            ),
        ],
    ),

    (
        "application_confusion",
        85,
        re.compile(
            r"\b(?:"
            r"i don't know how to apply|"
            r"i dont know how to apply|"
            r"not sure how to apply|"
            r"confused about applying|"
            r"confused about admission|"
            r"help me apply|"
            r"i don't know where to start|"
            r"i dont know where to start|"
            r"what should i do first|"
            r"what do i do first"
            r")\b",
            re.I,
        ),
        [
            (
                "No problem. Start with your intended program. Then check "
                "three things: whether you're eligible, which documents you "
                "need, and when the application is due. After that, you can "
                "complete the application and submit it."
            ),
        ],
    ),

    # ========================================================================
    # ELIGIBILITY
    # ========================================================================

    (
        "eligibility",
        95,
        re.compile(
            r"\b(?:"
            r"am i eligible|"
            r"do i qualify|"
            r"can i qualify|"
            r"can i get admission|"
            r"can i apply|"
            r"who can apply|"
            r"eligibility|"
            r"eligible for admission|"
            r"qualify for admission|"
            r"admission requirements"
            r")\b",
            re.I,
        ),
        [
            (
                "Eligibility depends on the program, degree level, and your "
                "academic background. The safest approach is to compare your "
                "qualifications with that program's published requirements."
            ),
            (
                "You may be eligible, but eligibility is program-specific. "
                "Check the required previous qualification, minimum academic "
                "requirements, prerequisite subjects, and any required tests."
            ),
        ],
    ),

    (
        "minimum_gpa",
        100,
        re.compile(
            r"\b(?:"
            r"minimum gpa|"
            r"minimum grade|"
            r"minimum grades|"
            r"minimum marks|"
            r"minimum percentage|"
            r"required gpa|"
            r"required grade|"
            r"required marks|"
            r"what gpa do i need|"
            r"what grades do i need|"
            r"what percentage do i need"
            r")\b",
            re.I,
        ),
        [
            (
                "The minimum academic requirement can vary by program and "
                "applicant type. Check the specific program's current "
                "admissions requirements for the exact GPA, grade, or "
                "percentage requirement."
            ),
        ],
    ),

    (
        "low_gpa",
        98,
        re.compile(
            r"\b(?:"
            r"low gpa|"
            r"low grades|"
            r"low marks|"
            r"bad grades|"
            r"poor grades|"
            r"my gpa is|"
            r"my grades are|"
            r"my marks are|"
            r"not good grades|"
            r"weak academic record|"
            r"weak grades"
            r")\b",
            re.I,
        ),
        [
            (
                "A lower GPA does not automatically tell you whether you can "
                "apply. Requirements vary by program. Compare your academic "
                "record with the specific program's minimum requirements."
            ),
            (
                "Don't assume you're automatically ineligible because of your "
                "grades. Check the program's actual academic requirements and "
                "whether it considers additional application factors."
            ),
        ],
    ),

    # ========================================================================
    # CURRENT STUDENTS / PENDING RESULTS
    # ========================================================================

    (
        "pending_results",
        100,
        re.compile(
            r"\b(?:"
            r"apply before final results|"
            r"apply before my results|"
            r"final results are not out|"
            r"final results aren't out|"
            r"results are not released|"
            r"results aren't released|"
            r"awaiting results|"
            r"waiting for final results|"
            r"results pending|"
            r"can i apply while studying|"
            r"can i apply before graduation|"
            r"apply before graduation|"
            r"still studying.*apply"
            r")\b",
            re.I,
        ),
        [
            (
                "You may be able to apply while your final results are "
                "pending, depending on the program's policy. Check whether "
                "pending-result or provisional applications are accepted and "
                "when final documents must be submitted."
            ),
        ],
    ),

    # ========================================================================
    # EDUCATIONAL BACKGROUND
    # ========================================================================

    (
        "previous_qualification",
        88,
        re.compile(
            r"\b(?:"
            r"what qualification do i need|"
            r"what degree do i need|"
            r"what education do i need|"
            r"what should i have completed|"
            r"do i need a bachelor's|"
            r"do i need a bachelors|"
            r"do i need a degree|"
            r"previous degree|"
            r"previous qualification|"
            r"required qualification"
            r")\b",
            re.I,
        ),
        [
            (
                "The required previous qualification depends on the degree "
                "level and program. Undergraduate, master's, and doctoral "
                "programs can have different academic prerequisites."
            ),
        ],
    ),

    # ========================================================================
    # DOCUMENTS
    # ========================================================================

    (
        "required_documents",
        97,
        re.compile(
            r"\b(?:"
            r"what documents|"
            r"which documents|"
            r"required documents|"
            r"documents do i need|"
            r"documents should i submit|"
            r"what do i need to submit|"
            r"what paperwork|"
            r"application documents|"
            r"documents required for admission|"
            r"what papers do i need"
            r")\b",
            re.I,
        ),
        [
            (
                "Required documents depend on your program and applicant "
                "category. Common materials can include academic records, "
                "identification, and supporting documents. Check your "
                "program's application checklist for the exact requirements."
            ),
            (
                "Start with the program-specific document checklist. "
                "Depending on your application, you may need academic "
                "transcripts, identification, test scores, recommendations, "
                "or other supporting materials."
            ),
        ],
    ),

    (
        "transcripts",
        96,
        re.compile(
            r"\b(?:"
            r"transcript|transcripts|"
            r"academic records?|"
            r"academic history|"
            r"marksheet|"
            r"mark sheet|"
            r"grade report|"
            r"school records?"
            r")\b",
            re.I,
        ),
        [
            (
                "Academic transcripts or records are used to verify your "
                "previous education. Make sure the documents you submit meet "
                "the university's format, verification, and completeness "
                "requirements."
            ),
        ],
    ),

    (
        "document_translation",
        98,
        re.compile(
            r"\b(?:"
            r"translate.*documents?|"
            r"translated documents?|"
            r"documents?.*translation|"
            r"documents?.*not in english|"
            r"documents?.*foreign language|"
            r"my documents are not in english"
            r")\b",
            re.I,
        ),
        [
            (
                "If your academic or supporting documents are not in an "
                "accepted language, a certified translation may be required. "
                "Check the document-submission rules before uploading them."
            ),
        ],
    ),

    (
        "certified_documents",
        96,
        re.compile(
            r"\b(?:"
            r"certified copy|"
            r"certified copies|"
            r"attested documents?|"
            r"authenticated documents?|"
            r"verified documents?|"
            r"document verification"
            r")\b",
            re.I,
        ),
        [
            (
                "Some applicants may need certified, verified, attested, or "
                "authenticated documents. The exact requirement depends on "
                "the applicant category and program."
            ),
        ],
    ),

    (
        "upload_documents",
        95,
        re.compile(
            r"\b(?:"
            r"how do i upload|"
            r"where do i upload|"
            r"upload documents?|"
            r"document upload|"
            r"upload my documents?|"
            r"where should i upload"
            r")\b",
            re.I,
        ),
        [
            (
                "Use the designated application portal or submission process "
                "to upload your documents. Follow the instructions for "
                "accepted file types, file size, and document completeness."
            ),
        ],
    ),

    (
        "missing_document",
        99,
        re.compile(
            r"\b(?:"
            r"missing document|"
            r"forgot.*document|"
            r"forgot to upload|"
            r"didn't upload|"
            r"did not upload|"
            r"missing.*application|"
            r"incomplete application"
            r")\b",
            re.I,
        ),
        [
            (
                "If you've missed a required document, check your application "
                "portal first to see whether additional documents can still "
                "be uploaded. If not, contact admissions and explain exactly "
                "what is missing. Avoid creating a duplicate application "
                "unless instructed."
            ),
        ],
    ),

    # ========================================================================
    # DEADLINES
    # ========================================================================

    (
        "application_deadline",
        100,
        re.compile(
            r"\b(?:"
            r"application deadline|"
            r"admission deadline|"
            r"deadline to apply|"
            r"last date to apply|"
            r"when is the application due|"
            r"when do applications close|"
            r"when should i apply|"
            r"when can i apply|"
            r"application closing date"
            r")\b",
            re.I,
        ),
        [
            (
                "Application deadlines depend on the admission term and "
                "program. Check the current deadline for the specific program "
                "and intake you're targeting."
            ),
        ],
    ),

    (
        "application_opening",
        98,
        re.compile(
            r"\b(?:"
            r"when does application open|"
            r"when do applications open|"
            r"application opening date|"
            r"when can applications start|"
            r"when will applications open|"
            r"application opens"
            r")\b",
            re.I,
        ),
        [
            (
                "Application opening dates depend on the admission term and "
                "program. Check the current admissions calendar for the next "
                "available application period."
            ),
        ],
    ),

    (
        "late_application",
        100,
        re.compile(
            r"\b(?:"
            r"late application|"
            r"missed the deadline|"
            r"missed application deadline|"
            r"after the deadline|"
            r"apply late|"
            r"deadline has passed|"
            r"too late to apply"
            r")\b",
            re.I,
        ),
        [
            (
                "If you've missed the deadline, check whether the program "
                "accepts late applications or whether another admission cycle "
                "is available. Don't assume the application is closed without "
                "checking the current policy."
            ),
        ],
    ),

    (
        "deadline_extension",
        99,
        re.compile(
            r"\b(?:"
            r"deadline extension|"
            r"extend the deadline|"
            r"can the deadline be extended|"
            r"extra time.*application|"
            r"more time.*apply"
            r")\b",
            re.I,
        ),
        [
            (
                "Deadline extensions depend on university policy and program "
                "availability. Check the current admissions information or "
                "contact admissions to determine whether an extension is "
                "available."
            ),
        ],
    ),

    # ========================================================================
    # INTAKES
    # ========================================================================

    (
        "intakes",
        95,
        re.compile(
            r"\b(?:"
            r"when are intakes|"
            r"which intake|"
            r"next intake|"
            r"available intakes|"
            r"fall intake|"
            r"spring intake|"
            r"summer intake|"
            r"autumn intake|"
            r"winter intake|"
            r"admission cycle"
            r")\b",
            re.I,
        ),
        [
            (
                "Available admission terms depend on the program. Check the "
                "current admissions calendar to see which intakes are open "
                "for your intended program."
            ),
        ],
    ),

    # ========================================================================
    # FEES / TUITION
    # ========================================================================

    (
        "fees",
        94,
        re.compile(
            r"\b(?:"
            r"tuition|"
            r"tuition fee|"
            r"tuition fees|"
            r"application fee|"
            r"admission fee|"
            r"application cost|"
            r"how much does it cost|"
            r"how much will it cost|"
            r"how much is tuition|"
            r"how much are the fees|"
            r"fees"
            r")\b",
            re.I,
        ),
        [
            (
                "Costs can include application fees, tuition, and other "
                "university charges. The amount depends on the program, "
                "degree level, and applicant category, so check the current "
                "fee information for your specific program."
            ),
            (
                "Tuition and application costs vary by program and student "
                "category. For an exact amount, the authoritative fee schedule "
                "for your program should be used."
            ),
        ],
    ),

    (
        "payment_methods",
        96,
        re.compile(
            r"\b(?:"
            r"how can i pay|"
            r"payment methods?|"
            r"how do i pay|"
            r"can i pay online|"
            r"pay application fee|"
            r"where can i pay"
            r")\b",
            re.I,
        ),
        [
            (
                "Available payment methods depend on the university's current "
                "payment process. Check the application or fee-payment "
                "instructions for the accepted methods."
            ),
        ],
    ),

    (
        "installments",
        97,
        re.compile(
            r"\b(?:"
            r"installments?|"
            r"pay tuition monthly|"
            r"monthly payments?|"
            r"payment plan|"
            r"pay in parts|"
            r"split tuition payments?"
            r")\b",
            re.I,
        ),
        [
            (
                "Payment-plan and installment options depend on university "
                "policy. Check the current tuition-payment information to see "
                "whether a payment plan is available."
            ),
        ],
    ),

    (
        "fee_waiver",
        98,
        re.compile(
            r"\b(?:"
            r"fee waiver|"
            r"waive the application fee|"
            r"application fee waiver|"
            r"do i have to pay.*application fee|"
            r"can application fee be waived"
            r")\b",
            re.I,
        ),
        [
            (
                "Application-fee waivers can depend on eligibility and "
                "applicant category. Check the current admissions policy to "
                "see whether you qualify for a waiver."
            ),
        ],
    ),

    (
        "fee_refund",
        98,
        re.compile(
            r"\b(?:"
            r"application fee refund|"
            r"refund.*application fee|"
            r"get my application fee back|"
            r"refund.*admission fee|"
            r"can i get a refund"
            r")\b",
            re.I,
        ),
        [
            (
                "Application-fee refund policies vary. Check the current fee "
                "policy to determine whether your circumstances qualify for "
                "a refund."
            ),
        ],
    ),

    # ========================================================================
    # SCHOLARSHIPS / FINANCIAL AID
    # ========================================================================

    (
        "scholarships",
        99,
        re.compile(
            r"\b(?:"
            r"scholarships?|"
            r"financial aid|"
            r"financial assistance|"
            r"grants?|"
            r"can i get a scholarship|"
            r"how do scholarships work|"
            r"does the university offer scholarships|"
            r"money for tuition|"
            r"funding"
            r")\b",
            re.I,
        ),
        [
            (
                "Scholarships and financial aid can have separate eligibility "
                "requirements and deadlines from general admission. Check the "
                "current financial-aid information for available awards and "
                "their application requirements."
            ),
            (
                "Financial support may include scholarships, grants, or other "
                "forms of aid depending on eligibility. Check both the "
                "admissions requirements and any separate financial-aid "
                "deadlines."
            ),
        ],
    ),

    (
        "scholarship_deadline",
        100,
        re.compile(
            r"\b(?:"
            r"scholarship deadline|"
            r"when.*scholarship.*apply|"
            r"deadline.*financial aid|"
            r"financial aid deadline|"
            r"when do i apply for scholarship"
            r")\b",
            re.I,
        ),
        [
            (
                "Scholarship and financial-aid deadlines may be different from "
                "the general admissions deadline. Check the current "
                "financial-aid information carefully for separate deadlines."
            ),
        ],
    ),

    (
        "merit_scholarship",
        100,
        re.compile(
            r"\b(?:"
            r"merit scholarship|"
            r"academic scholarship|"
            r"scholarship.*grades|"
            r"scholarship.*gpa|"
            r"scholarship.*marks|"
            r"high grades.*scholarship"
            r")\b",
            re.I,
        ),
        [
            (
                "Merit-based scholarships may consider academic performance "
                "and other eligibility factors. Check the current scholarship "
                "criteria for the specific award."
            ),
        ],
    ),

    (
        "need_based_aid",
        99,
        re.compile(
            r"\b(?:"
            r"need[- ]based|"
            r"financial need|"
            r"can't afford tuition|"
            r"cannot afford tuition|"
            r"low income.*financial aid|"
            r"need financial help"
            r")\b",
            re.I,
        ),
        [
            (
                "Need-based financial assistance may have separate eligibility "
                "and documentation requirements. Check the current "
                "financial-aid information for available programs."
            ),
        ],
    ),

    # ========================================================================
    # ENGLISH / STANDARDIZED TESTS
    # ========================================================================

    (
        "english_tests",
        101,
        re.compile(
            r"\b(?:"
            r"english test|"
            r"english requirement|"
            r"english proficiency|"
            r"english language requirement|"
            r"ielts|"
            r"toefl|"
            r"duolingo|"
            r"pte|"
            r"language test|"
            r"proof of english|"
            r"english score"
            r")\b",
            re.I,
        ),
        [
            (
                "English-language requirements depend on the program and "
                "applicant category. Check which tests are accepted and the "
                "current minimum scores for your specific program."
            ),
        ],
    ),

    (
        "no_english_test",
        105,
        re.compile(
            r"\b(?:"
            r"apply without.*ielts|"
            r"apply without.*toefl|"
            r"without.*ielts|"
            r"without.*toefl|"
            r"no ielts|"
            r"no toefl|"
            r"don't have.*ielts|"
            r"do not have.*ielts|"
            r"without english test|"
            r"can i apply without.*english test"
            r")\b",
            re.I,
        ),
        [
            (
                "Whether an English test is required depends on the program "
                "and applicant category. Some applicants may qualify for an "
                "exemption, but you should check the current language "
                "requirements rather than assume one applies."
            ),
        ],
    ),

    (
        "sat_act",
        100,
        re.compile(
            r"\b(?:"
            r"sat|"
            r"act|"
            r"standardized test|"
            r"entrance test|"
            r"admission test|"
            r"test score"
            r")\b",
            re.I,
        ),
        [
            (
                "Testing requirements depend on the program and applicant "
                "category. Check the current admissions requirements to see "
                "whether SAT, ACT, or another entrance test is required."
            ),
        ],
    ),

    # ========================================================================
    # INTERNATIONAL STUDENTS
    # ========================================================================

    (
        "international_students",
        100,
        re.compile(
            r"\b(?:"
            r"international student|"
            r"international students|"
            r"student from another country|"
            r"students from another country|"
            r"foreign student|"
            r"foreign students|"
            r"can international students apply|"
            r"do you accept international students|"
            r"international applicant|"
            r"international applicants"
            r")\b",
            re.I,
        ),
        [
            (
                "International applicants may have additional requirements "
                "beyond the standard application. These can include academic "
                "documentation, language proficiency, credential evaluation, "
                "and immigration-related requirements."
            ),
            (
                "International admission requirements can differ from "
                "domestic requirements. Check the international-applicant "
                "information for the documents, eligibility rules, tests, and "
                "deadlines that apply to you."
            ),
        ],
    ),

    (
        "international_qualifications",
        99,
        re.compile(
            r"\b(?:"
            r"foreign degree|"
            r"foreign qualification|"
            r"international qualification|"
            r"degree from another country|"
            r"credential evaluation|"
            r"qualification evaluation|"
            r"international transcript"
            r")\b",
            re.I,
        ),
        [
            (
                "Applicants with international qualifications may need "
                "additional documentation or credential evaluation. Check "
                "the requirements for applicants educated outside the country."
            ),
        ],
    ),

    (
        "visa",
        100,
        re.compile(
            r"\b(?:"
            r"student visa|"
            r"visa|"
            r"immigration|"
            r"visa sponsorship|"
            r"visa letter|"
            r"study visa"
            r")\b",
            re.I,
        ),
        [
            (
                "Visa and immigration requirements are separate from academic "
                "admission requirements. International students should review "
                "the current guidance for the documents and steps required "
                "after admission."
            ),
        ],
    ),

    (
        "international_support",
        99,
        re.compile(
            r"\b(?:"
            r"international student support|"
            r"support.*international students?|"
            r"help.*international students?|"
            r"international office|"
            r"international student services?"
            r")\b",
            re.I,
        ),
        [
            (
                "International-student services may provide support with "
                "orientation, immigration-related guidance, campus resources, "
                "and settling into university life. Check the current "
                "international-student services information."
            ),
        ],
    ),

    # ========================================================================
    # UNDERGRADUATE / MASTER'S / PHD
    # ========================================================================

    (
        "masters",
        75,
        re.compile(
            r"\b(?:"
            r"master'?s admission|"
            r"graduate admission|"
            r"apply for masters?|"
            r"ms admission|"
            r"graduate program|"
            r"postgraduate admission"
            r")\b",
            re.I,
        ),
        [
            (
                "Graduate admission requirements vary by program. They may "
                "include a relevant previous degree, academic records, "
                "language proficiency, recommendations, or other materials. "
                "Check the specific master's program requirements."
            ),
        ],
    ),

    (
        "undergraduate",
        75,
        re.compile(
            r"\b(?:"
            r"undergraduate admission|"
            r"bachelor admission|"
            r"bachelor's admission|"
            r"apply for bachelor's|"
            r"apply for bachelors|"
            r"first degree|"
            r"undergraduate program"
            r")\b",
            re.I,
        ),
        [
            (
                "Undergraduate requirements depend on the program and your "
                "academic background. Check the specific bachelor's program "
                "for its academic and application requirements."
            ),
        ],
    ),

    (
        "phd",
        75,
        re.compile(
            r"\b(?:"
            r"phd admission|"
            r"doctoral admission|"
            r"apply for phd|"
            r"doctoral program|"
            r"doctorate admission"
            r")\b",
            re.I,
        ),
        [
            (
                "Doctoral admission requirements are program-specific and may "
                "include academic qualifications, research-related materials, "
                "recommendations, and other requirements. Check the specific "
                "doctoral program."
            ),
        ],
    ),

    # ========================================================================
    # PROGRAMS / MAJORS
    # ========================================================================

    (
        "programs",
        85,
        re.compile(
            r"\b(?:"
            r"what programs|"
            r"what majors|"
            r"what degrees do you offer|"
            r"what programs do you offer|"
            r"what can i study|"
            r"available majors|"
            r"available programs|"
            r"available degrees|"
            r"what can i major in|"
            r"fields of study|"
            r"courses do you offer"
            r")\b",
            re.I,
        ),
        [
            (
                "Meridian State offers different academic programs and majors. "
                "If you have a specific field in mind, ask about that program "
                "and I can help you identify the admissions information you "
                "should check."
            ),
        ],
    ),

    (
        "program_availability",
        86,
        re.compile(
            r"\b(?:"
            r"do you offer.*program|"
            r"do you offer.*degree|"
            r"do you offer.*major|"
            r"is .* program available|"
            r"is .* degree available|"
            r"do you have.*program|"
            r"do you have.*degree"
            r")\b",
            re.I,
        ),
        [
            (
                "Program availability can depend on the current academic "
                "offerings. Tell me the field or exact program you're "
                "interested in and I can help identify the relevant "
                "admissions information."
            ),
        ],
    ),

    (
        "program_duration",
        85,
        re.compile(
            r"\b(?:"
            r"how long.*degree|"
            r"how long.*program|"
            r"how many years.*degree|"
            r"program duration|"
            r"degree duration|"
            r"how long does.*take|"
            r"how many semesters"
            r")\b",
            re.I,
        ),
        [
            (
                "Program duration depends on the degree, curriculum, and "
                "study format. Check the specific program information for "
                "its expected completion time."
            ),
        ],
    ),

    (
        "prerequisites",
        99,
        re.compile(
            r"\b(?:"
            r"prerequisite|"
            r"prerequisites|"
            r"pre-requisite|"
            r"pre-requisites|"
            r"required courses|"
            r"subject requirements|"
            r"do i need.*course|"
            r"previous subjects"
            r")\b",
            re.I,
        ),
        [
            (
                "Some programs require specific previous subjects or "
                "prerequisite courses. Check the exact program requirements "
                "to make sure your academic background satisfies them."
            ),
        ],
    ),

    (
        "change_major",
        90,
        re.compile(
            r"\b(?:"
            r"change my major|"
            r"change my program|"
            r"switch majors?|"
            r"switch programs?|"
            r"change my course|"
            r"change degree"
            r")\b",
            re.I,
        ),
        [
            (
                "Changing a program or major may be possible, but the rules "
                "depend on the program and your academic situation. Check the "
                "current policy before making a change."
            ),
        ],
    ),

    (
        "double_major_minor",
        85,
        re.compile(
            r"\b(?:"
            r"double major|"
            r"minor|"
            r"major and minor|"
            r"two majors|"
            r"second major"
            r")\b",
            re.I,
        ),
        [
            (
                "Whether you can pursue a second major or a minor depends on "
                "academic policies and the programs involved. Check the "
                "requirements for the specific programs you're considering."
            ),
        ],
    ),

    # ========================================================================
    # TRANSFER STUDENTS
    # ========================================================================

    (
        "transfer_student",
        100,
        re.compile(
            r"\b(?:"
            r"transfer student|"
            r"transfer students|"
            r"transfer admission|"
            r"can i transfer|"
            r"transfer from another university|"
            r"transfer from another college"
            r")\b",
            re.I,
        ),
        [
            (
                "Transfer applicants may have different requirements from "
                "first-time applicants. Credit transferability can depend on "
                "the courses you've already completed and the university's "
                "transfer policy."
            ),
        ],
    ),

    (
        "transfer_credits",
        105,
        re.compile(
            r"\b(?:"
            r"transfer credits?|"
            r"will my credits transfer|"
            r"can i transfer my credits|"
            r"transfer previous credits|"
            r"previous coursework|"
            r"credits from another university|"
            r"credits from another college"
            r")\b",
            re.I,
        ),
        [
            (
                "Previous coursework may be eligible for transfer depending "
                "on the courses completed and the university's credit-transfer "
                "policy. An academic evaluation may be required."
            ),
        ],
    ),

    (
        "advanced_standing",
        95,
        re.compile(
            r"\b(?:"
            r"advanced standing|"
            r"enter second year|"
            r"skip first year|"
            r"start second year|"
            r"start third year|"
            r"advanced entry"
            r")\b",
            re.I,
        ),
        [
            (
                "Advanced standing may be available when previous coursework "
                "meets the program's requirements. Eligibility is normally "
                "determined through an academic or transfer-credit evaluation."
            ),
        ],
    ),

    # ========================================================================
    # GAP YEAR / AGE
    # ========================================================================

    (
        "gap_year",
        92,
        re.compile(
            r"\b(?:"
            r"gap year|"
            r"took a year off|"
            r"year off|"
            r"study gap|"
            r"gap in education|"
            r"education gap|"
            r"years not studying|"
            r"not studied for years"
            r")\b",
            re.I,
        ),
        [
            (
                "A gap in your education does not necessarily prevent you "
                "from applying. Eligibility depends on the program's "
                "requirements and your academic background. If asked about "
                "the gap, provide accurate information about that period."
            ),
        ],
    ),

    (
        "age_requirement",
        90,
        re.compile(
            r"\b(?:"
            r"minimum age|"
            r"maximum age|"
            r"age requirement|"
            r"am i too old|"
            r"too old to apply|"
            r"too young to apply|"
            r"age limit"
            r")\b",
            re.I,
        ),
        [
            (
                "Age requirements, if any, depend on the program and applicant "
                "category. Check the specific admissions requirements rather "
                "than assuming age alone determines eligibility."
            ),
        ],
    ),

    # ========================================================================
    # APPLICATION STATUS / DECISION
    # ========================================================================

    (
        "application_status",
        105,
        re.compile(
            r"\b(?:"
            r"application status|"
            r"check my application|"
            r"where is my application|"
            r"application update|"
            r"has my application been reviewed|"
            r"track my application|"
            r"track application"
            r")\b",
            re.I,
        ),
        [
            (
                "Application status is normally checked through the university's "
                "designated application portal or admissions channel. Use the "
                "same account or application details associated with your "
                "submission."
            ),
        ],
    ),

    (
        "decision_timeline",
        101,
        re.compile(
            r"\b(?:"
            r"when will i hear back|"
            r"when do decisions come out|"
            r"admission decision|"
            r"how long.*decision|"
            r"how long.*admission|"
            r"how long.*application|"
            r"processing time|"
            r"when will i get a decision"
            r")\b",
            re.I,
        ),
        [
            (
                "Decision timelines can vary by program, application volume, "
                "and whether additional documents are required. Check the "
                "published admissions timeline and monitor your application "
                "portal for updates."
            ),
        ],
    ),

    (
        "acceptance",
        101,
        re.compile(
            r"\b(?:"
            r"how do i know.*accepted|"
            r"how will i know.*accepted|"
            r"acceptance letter|"
            r"admission letter|"
            r"when.*accepted|"
            r"how.*admission decision|"
            r"will i get an email.*acceptance"
            r")\b",
            re.I,
        ),
        [
            (
                "Admission decisions are typically communicated through the "
                "university's designated application portal or official "
                "communication channels. Keep checking the contact information "
                "associated with your application."
            ),
        ],
    ),

    (
        "rejection",
        100,
        re.compile(
            r"\b(?:"
            r"what if.*rejected|"
            r"if i get rejected|"
            r"application rejected|"
            r"not accepted|"
            r"denied admission|"
            r"admission denied|"
            r"rejected from university"
            r")\b",
            re.I,
        ),
        [
            (
                "If your application isn't successful, check whether the "
                "university offers reconsideration, an appeal process, or "
                "the option to apply again in a future admission cycle."
            ),
        ],
    ),

    (
        "appeal",
        101,
        re.compile(
            r"\b(?:"
            r"appeal admission|"
            r"appeal decision|"
            r"appeal my application|"
            r"challenge admission decision|"
            r"reconsider my application|"
            r"reconsideration"
            r")\b",
            re.I,
        ),
        [
            (
                "If you want an admission decision reconsidered, check whether "
                "the university offers an appeal or reconsideration process "
                "and follow the required procedure and deadline."
            ),
        ],
    ),

    (
        "waitlist",
        100,
        re.compile(
            r"\b(?:"
            r"waitlist|"
            r"waitlisted|"
            r"waiting list|"
            r"placed on.*waitlist"
            r")\b",
            re.I,
        ),
        [
            (
                "If a program uses a waitlist, admission may depend on "
                "available places after the initial decisions. Check your "
                "application portal or admissions communication for the "
                "next steps."
            ),
        ],
    ),

    # ========================================================================
    # ENROLLMENT / OFFER
    # ========================================================================

    (
        "enrollment",
        95,
        re.compile(
            r"\b(?:"
            r"how do i enroll|"
            r"how to enroll|"
            r"enrollment process|"
            r"enrolment process|"
            r"when do i enroll|"
            r"enroll after admission|"
            r"what happens after acceptance"
            r")\b",
            re.I,
        ),
        [
            (
                "Enrollment normally happens after an admission decision and "
                "may require accepting your offer and completing additional "
                "steps. Follow the instructions provided with your admission "
                "decision."
            ),
        ],
    ),

    (
        "accept_offer",
        100,
        re.compile(
            r"\b(?:"
            r"when.*accept.*offer|"
            r"acceptance deadline|"
            r"deadline.*accept.*offer|"
            r"how long.*accept.*offer|"
            r"when do i have to accept|"
            r"accept my offer"
            r")\b",
            re.I,
        ),
        [
            (
                "If you're admitted, your offer should indicate any deadline "
                "for accepting your place or completing enrollment steps. "
                "Check the offer carefully for the applicable date."
            ),
        ],
    ),

    (
        "deposit",
        98,
        re.compile(
            r"\b(?:"
            r"admission deposit|"
            r"enrollment deposit|"
            r"deposit.*admission|"
            r"deposit.*enrollment|"
            r"pay.*deposit"
            r")\b",
            re.I,
        ),
        [
            (
                "Some programs may require a deposit after admission to "
                "confirm enrollment. Check your offer and the current "
                "enrollment instructions for the applicable amount and "
                "deadline."
            ),
        ],
    ),

    (
        "defer",
        100,
        re.compile(
            r"\b(?:"
            r"defer|"
            r"deferred admission|"
            r"postpone my admission|"
            r"delay enrollment|"
            r"defer my offer|"
            r"defer acceptance|"
            r"delay my start"
            r")\b",
            re.I,
        ),
        [
            (
                "Deferral policies vary by program and admission term. If "
                "you've already been admitted but cannot start as planned, "
                "check the university's current deferral policy before making "
                "arrangements."
            ),
        ],
    ),

    # ========================================================================
    # APPLICATION ACCOUNT / TECHNICAL ISSUES
    # ========================================================================

    (
        "login",
        105,
        re.compile(
            r"\b(?:"
            r"forgot.*password|"
            r"forgot.*login|"
            r"can't log in|"
            r"cannot log in|"
            r"login problem|"
            r"application portal.*password|"
            r"can't access.*application|"
            r"cannot access.*application"
            r")\b",
            re.I,
        ),
        [
            (
                "For application-portal login problems, use the portal's "
                "password-recovery option if available. If that doesn't work, "
                "contact the appropriate admissions or technical-support "
                "channel."
            ),
        ],
    ),

    (
        "confirmation_email",
        100,
        re.compile(
            r"\b(?:"
            r"didn't get.*confirmation|"
            r"did not get.*confirmation|"
            r"no confirmation email|"
            r"confirmation email|"
            r"application confirmation|"
            r"application email.*not received"
            r")\b",
            re.I,
        ),
        [
            (
                "If you submitted an application but haven't received a "
                "confirmation, first check your spam or junk folder and verify "
                "your application portal. If there's still no confirmation, "
                "contact admissions."
            ),
        ],
    ),

    (
        "application_number",
        95,
        re.compile(
            r"\b(?:"
            r"application number|"
            r"application id|"
            r"application ID|"
            r"where.*application number|"
            r"find.*application number"
            r")\b",
            re.I,
        ),
        [
            (
                "Your application number is usually provided when you begin or "
                "submit an application. Check your confirmation email or "
                "application portal."
            ),
        ],
    ),

    (
        "change_contact",
        95,
        re.compile(
            r"\b(?:"
            r"change.*email.*application|"
            r"change.*phone.*application|"
            r"update.*contact information|"
            r"change my contact details|"
            r"wrong email.*application|"
            r"wrong phone.*application"
            r")\b",
            re.I,
        ),
        [
            (
                "If your contact information has changed, update it through "
                "the application portal if possible. Otherwise, contact "
                "admissions and provide the information needed to identify "
                "your application."
            ),
        ],
    ),

    (
        "application_mistake",
        100,
        re.compile(
            r"\b(?:"
            r"made a mistake.*application|"
            r"wrong information.*application|"
            r"correct my application|"
            r"edit my application|"
            r"change information.*application|"
            r"entered wrong information"
            r")\b",
            re.I,
        ),
        [
            (
                "If you've submitted incorrect information, avoid submitting "
                "duplicate applications unless instructed to do so. Contact "
                "the appropriate admissions channel and explain exactly what "
                "needs to be corrected."
            ),
        ],
    ),

    (
        "withdraw_application",
        95,
        re.compile(
            r"\b(?:"
            r"withdraw.*application|"
            r"cancel.*application|"
            r"remove.*application|"
            r"drop.*application"
            r")\b",
            re.I,
        ),
        [
            (
                "If you want to withdraw an application, check the university's "
                "application policy or contact admissions for the correct "
                "procedure."
            ),
        ],
    ),

    # ========================================================================
    # RECOMMENDATIONS / ESSAYS / INTERVIEWS
    # ========================================================================

    (
        "recommendation_letters",
        98,
        re.compile(
            r"\b(?:"
            r"recommendation letters?|"
            r"reference letters?|"
            r"letter of recommendation|"
            r"do i need references|"
            r"academic references?"
            r")\b",
            re.I,
        ),
        [
            (
                "Recommendation or reference requirements vary by program. "
                "Check the specific application checklist to see whether "
                "letters are required and who may provide them."
            ),
        ],
    ),

    (
        "personal_statement",
        98,
        re.compile(
            r"\b(?:"
            r"personal statement|"
            r"statement of purpose|"
            r"\bsop\b|"
            r"admission essay|"
            r"application essay|"
            r"essay required|"
            r"motivation letter"
            r")\b",
            re.I,
        ),
        [
            (
                "Some programs may require a personal statement, statement of "
                "purpose, motivation letter, or application essay. Check the "
                "program-specific requirements for the exact instructions."
            ),
        ],
    ),

    (
        "interview",
        98,
        re.compile(
            r"\b(?:"
            r"admission interview|"
            r"do i need an interview|"
            r"will i be interviewed|"
            r"interview required|"
            r"admissions interview"
            r")\b",
            re.I,
        ),
        [
            (
                "Interview requirements can vary by program and applicant "
                "type. Check the specific admissions requirements to see "
                "whether an interview is part of the process."
            ),
        ],
    ),

    # ========================================================================
    # CAMPUS / HOUSING / STUDENT LIFE
    # ========================================================================

    (
        "housing",
        90,
        re.compile(
            r"\b(?:"
            r"housing|"
            r"dorms?|"
            r"student accommodation|"
            r"accommodation|"
            r"residence halls?|"
            r"where can students live|"
            r"does the university have housing|"
            r"is housing available"
            r")\b",
            re.I,
        ),
        [
            (
                "Student housing availability depends on capacity, eligibility, "
                "and current university policy. Check the housing information "
                "for application deadlines, costs, and available options."
            ),
        ],
    ),

    (
        "campus_life",
        85,
        re.compile(
            r"\b(?:"
            r"campus life|"
            r"student life|"
            r"campus|"
            r"what is campus like|"
            r"life on campus"
            r")\b",
            re.I,
        ),
        [
            (
                "Campus life can include housing, student organizations, "
                "facilities, events, academic support, and recreational "
                "activities. Ask about the specific aspect you're interested in."
            ),
        ],
    ),

    (
        "campus_visit",
        90,
        re.compile(
            r"\b(?:"
            r"campus visit|"
            r"visit the campus|"
            r"tour.*campus|"
            r"campus tour|"
            r"can i visit"
            r")\b",
            re.I,
        ),
        [
            (
                "Campus visits can be a useful way to learn about the "
                "university before enrolling. Check the current visitor or "
                "admissions information for available visit options and "
                "scheduling."
            ),
        ],
    ),

    (
        "clubs",
        85,
        re.compile(
            r"\b(?:"
            r"student clubs?|"
            r"clubs and societies|"
            r"student organizations?|"
            r"extracurricular|"
            r"student activities|"
            r"campus organizations?"
            r")\b",
            re.I,
        ),
        [
            (
                "Universities often offer student clubs, societies, "
                "organizations, and extracurricular activities. Check the "
                "current student-life information for the groups and "
                "activities available."
            ),
        ],
    ),

    (
        "facilities",
        85,
        re.compile(
            r"\b(?:"
            r"library|"
            r"gym|"
            r"sports facilities|"
            r"laboratories|"
            r"\blabs\b|"
            r"student center|"
            r"campus facilities"
            r")\b",
            re.I,
        ),
        [
            (
                "Campus facilities can include academic, recreational, and "
                "student-support resources. Ask about the specific facility "
                "you're interested in."
            ),
        ],
    ),

    (
        "transportation",
        80,
        re.compile(
            r"\b(?:"
            r"public transport|"
            r"transportation|"
            r"how do students get.*campus|"
            r"bus.*campus|"
            r"transport.*campus"
            r")\b",
            re.I,
        ),
        [
            (
                "Transportation options depend on the campus location. Check "
                "the university's current campus and student-services "
                "information for available transportation resources."
            ),
        ],
    ),

    # ========================================================================
    # CAREER / INTERNSHIPS
    # ========================================================================

    (
        "career",
        80,
        re.compile(
            r"\b(?:"
            r"internships?|"
            r"career services?|"
            r"job placement|"
            r"career support|"
            r"career opportunities|"
            r"jobs after graduation|"
            r"employment after graduation"
            r")\b",
            re.I,
        ),
        [
            (
                "Career support can include advising, internships, employer "
                "events, career resources, and job-search assistance. Check "
                "the university's current career-services information for "
                "specific opportunities."
            ),
        ],
    ),

    # ========================================================================
    # ACCESSIBILITY / SUPPORT
    # ========================================================================

    (
        "accessibility",
        90,
        re.compile(
            r"\b(?:"
            r"disability support|"
            r"accessibility|"
            r"special accommodations?|"
            r"academic accommodations?|"
            r"support services?|"
            r"student support"
            r")\b",
            re.I,
        ),
        [
            (
                "Student-support and accessibility services may be available "
                "for eligible students. Check the university's current "
                "support-services information for available accommodations "
                "and procedures."
            ),
        ],
    ),

    # ========================================================================
    # ONLINE / PART-TIME / FULL-TIME
    # ========================================================================

    (
        "online_program",
        90,
        re.compile(
            r"\b(?:"
            r"online degree|"
            r"online program|"
            r"study online|"
            r"fully online|"
            r"remote study|"
            r"online classes|"
            r"distance learning"
            r")\b",
            re.I,
        ),
        [
            (
                "Online availability depends on the program. Check the "
                "specific program information to see whether it can be "
                "completed online or requires in-person attendance."
            ),
        ],
    ),

    (
        "study_mode",
        90,
        re.compile(
            r"\b(?:"
            r"part[- ]time|"
            r"full[- ]time|"
            r"part time study|"
            r"full time study|"
            r"study part time|"
            r"study full time|"
            r"hybrid program|"
            r"hybrid study"
            r")\b",
            re.I,
        ),
        [
            (
                "Study options vary by program. Check whether your intended "
                "program is available full-time, part-time, online, or in a "
                "hybrid format and review any enrollment requirements."
            ),
        ],
    ),

    # ========================================================================
    # ORIENTATION / START DATE
    # ========================================================================

    (
        "orientation",
        90,
        re.compile(
            r"\b(?:"
            r"orientation|"
            r"new student orientation|"
            r"welcome week|"
            r"first day.*university"
            r")\b",
            re.I,
        ),
        [
            (
                "New-student orientation helps incoming students understand "
                "academics, campus resources, and university procedures. "
                "Check the current orientation schedule for your intake."
            ),
        ],
    ),

    (
        "class_start",
        90,
        re.compile(
            r"\b(?:"
            r"when do classes start|"
            r"when does semester start|"
            r"semester start date|"
            r"term start|"
            r"first day of classes"
            r")\b",
            re.I,
        ),
        [
            (
                "Class start dates depend on the academic term. Check the "
                "current academic calendar for the exact start date of your "
                "intended term."
            ),
        ],
    ),

    # ========================================================================
    # COST OF LIVING
    # ========================================================================

    (
        "living_cost",
        80,
        re.compile(
            r"\b(?:"
            r"cost of living|"
            r"living expenses|"
            r"monthly expenses|"
            r"how expensive.*live|"
            r"living cost|"
            r"expenses as a student"
            r")\b",
            re.I,
        ),
        [
            (
                "Living costs are separate from tuition and can include "
                "housing, food, transportation, books, and personal expenses. "
                "Check the university's student-life or international-student "
                "resources for current estimates."
            ),
        ],
    ),

    # ========================================================================
    # READMISSION
    # ========================================================================

    (
        "readmission",
        95,
        re.compile(
            r"\b(?:"
            r"readmission|"
            r"re-admission|"
            r"return to university|"
            r"returning after withdrawal|"
            r"previous student.*apply again|"
            r"come back to university"
            r")\b",
            re.I,
        ),
        [
            (
                "Students returning after previously attending may have a "
                "separate readmission process. Check the current policy for "
                "returning students."
            ),
        ],
    ),

    # ========================================================================
    # CONTACT ADMISSIONS
    # ========================================================================

    (
        "contact_admissions",
        70,
        re.compile(
            r"\b(?:"
            r"contact admissions|"
            r"contact the admissions|"
            r"admissions office|"
            r"how do i contact admissions|"
            r"who should i contact|"
            r"email admissions|"
            r"admissions email|"
            r"admissions phone|"
            r"phone number.*admissions"
            r")\b",
            re.I,
        ),
        [
            (
                "For questions that aren't covered by the available "
                "admissions information, the admissions office is the "
                "appropriate place to contact. Use the official contact "
                "details provided by the university."
            ),
        ],
    ),

    # ========================================================================
    # GENERAL NEXT STEP
    # ========================================================================

    (
        "next_step",
        80,
        re.compile(
            r"\b(?:"
            r"what should i do next|"
            r"what do i do next|"
            r"what's next|"
            r"whats next|"
            r"next step|"
            r"what happens next|"
            r"what should i do after applying|"
            r"what should i do after submitting"
            r")\b",
            re.I,
        ),
        [
            (
                "If you've already submitted your application, monitor your "
                "application portal and email for updates or requests for "
                "additional information. If you haven't applied yet, the next "
                "step is usually to verify your program requirements and "
                "prepare your documents."
            ),
        ],
    ),
]


# ============================================================================
# SORT PATTERNS BY PRIORITY
# ============================================================================
#
# This makes the system more reliable as the rule set grows.
# More specific patterns are evaluated before broad patterns.

_ADMISSIONS_PATTERNS.sort(
    key=lambda item: item[1],
    reverse=True,
)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def local_chat_reply(question: str):
    """
    Return a local conversational/admissions response.

    Returns:
        str  -> a locally generated response
        None -> question is not confidently recognized and should continue
                through the existing KB/Grok/static-fallback pipeline.
    """

    q = _clean_question(question)

    if not q:
        return None

    # ------------------------------------------------------------------------
    # SMALL TALK
    # ------------------------------------------------------------------------

    if _GREETING.search(q):
        return _reply(_GREETING_REPLIES)

    if _BYE.search(q):
        return _reply(_BYE_REPLIES)

    if _HOW_ARE_YOU.search(q):
        return _reply(_HOW_ARE_YOU_REPLIES)

    if _WHO_WHAT.search(q):
        return _reply(_WHO_WHAT_REPLIES)

    if _THANKS.search(q):
        return _reply(_THANKS_REPLIES)

    # ------------------------------------------------------------------------
    # ADMISSIONS INTENT MATCHING
    # ------------------------------------------------------------------------

    for _intent_name, _priority, pattern, replies in _ADMISSIONS_PATTERNS:
        if pattern.search(q):
            return _reply(replies)

    # ------------------------------------------------------------------------
    # UNKNOWN
    # ------------------------------------------------------------------------
    #
    # IMPORTANT:
    # Do NOT return a generic admissions answer here.
    #
    # Returning None allows the existing application to continue to:
    #
    #     KB -> Grok -> static FALLBACK_MESSAGE
    #
    # This prevents the local chatbot from pretending it knows an answer
    # when it does not.

    return None
