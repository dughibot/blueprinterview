from app import app
from resources.postgres import Screener, db, Domain, Question
from providers.screener import get_screener_by_id
from sqlalchemy import update


screener_data = {
    "id": "abcd-123",
    "name": "BPDS",
    "disorder": "Cross-Cutting",
    "content": {
        "sections": [
            {
                "type": "standard",
                "title": "During the past TWO (2) WEEKS, how much (or how often) have you been bothered by the following problems?",
                "answers": [
                    {"title": "Not at all", "value": 0},
                    {"title": "Rare, less than a day or two", "value": 1},
                    {"title": "Several days", "value": 2},
                    {"title": "More than half the days", "value": 3},
                    {"title": "Nearly every day", "value": 4},
                ],
                "questions": [
                    {
                        "question_id": "question_a",
                        "title": "Little interest or pleasure in doing things?",
                    },
                    {
                        "question_id": "question_b",
                        "title": "Feeling down, depressed, or hopeless?",
                    },
                    {
                        "question_id": "question_c",
                        "title": "Sleeping less than usual, but still have a lot of energy?",
                    },
                    {
                        "question_id": "question_d",
                        "title": "Starting lots more projects than usual or doing more risky things than usual?",
                    },
                    {
                        "question_id": "question_e",
                        "title": "Feeling nervous, anxious, frightened, worried, or on edge?",
                    },
                    {
                        "question_id": "question_f",
                        "title": "Feeling panic or being frightened?",
                    },
                    {
                        "question_id": "question_g",
                        "title": "Avoiding situations that make you feel anxious?",
                    },
                    {
                        "question_id": "question_h",
                        "title": "Drinking at least 4 drinks of any kind of alcohol in a single day?",
                    },
                ],
            }
        ],
        "display_name": "BDS",
    },
    "full_name": "Blueprint Diagnostic Screener",
}

domain_data = ["depression", "mania", "anxiety", "substance_use"]

question_domains = [
    {"question_id": "question_a", "domain": "depression"},
    {"question_id": "question_b", "domain": "depression"},
    {"question_id": "question_c", "domain": "mania"},
    {"question_id": "question_d", "domain": "mania"},
    {"question_id": "question_e", "domain": "anxiety"},
    {"question_id": "question_f", "domain": "anxiety"},
    {"question_id": "question_g", "domain": "anxiety"},
    {"question_id": "question_h", "domain": "substance_use"},
]

with app.app_context():
    screener = get_screener_by_id("abcd-123")
    if screener is None:
        for domain in domain_data:
            db.session.add(Domain(name=domain))
        screener = Screener.from_dict(screener_data)
        for qd_mapping in question_domains:
            screener.questions[qd_mapping["question_id"]].domain = qd_mapping["domain"]
        db.session.add(screener)

        db.session.commit()
