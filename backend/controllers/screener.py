from flask import Blueprint, request
from providers.postgres import db, Question, Screener
from sqlalchemy import select
from collections import defaultdict


bp = Blueprint("screener", __name__, url_prefix="/screener")


@bp.route("/<screenerId>/answers", methods=["POST"])
def processAnswers(screenerId: str) -> dict:
    screener = db.session.execute(select(Screener).where(Screener.id == screenerId))

    answers = request.json().get("answers")

    domain_cutoffs = {
        "PHQ-9": {"Depression": 2, "Anxiety": 2},
        "ASSIST": {"Substance Use": 1},
        "ASRM": {"Mania": 2},
    }

    domain_scores = defaultdict(lambda: 0)
    for ans in answers:
        domain_scores[screener.questions[ans["question_id"]]] += ans["value"]

    assessments = []
    for assessment, cutoffs in domain_cutoffs.items():
        for domain, cutoff_val in cutoffs.items():
            if domain_scores[domain] >= cutoff_val:
                assessments.append(assessment)
                break

    return {"results": assessments}


@bp.route("/<screenerId>")
def getScreener(screenerId: str) -> dict:
    screener = db.session.execute(select(Screener).where(Screener.id == screenerId))

    return {
        "id": screener.id,
        "name": screener.name,
        "disorder": screener.disorder,
        "full_name": screener.full_name,
        "content": {
            "display_name": screener.display_name,
            "sections": [
                {
                    "type": section.type,
                    "title": section.title,
                    "answers": [
                        {"title": answer.title, "value": answer.value}
                        for answer in section.answers
                    ],
                    "questions": [
                        {"question_id": question.id, "title": question.title}
                        for question in section.questions
                    ],
                }
                for section in screener.sections
            ],
        },
    }
