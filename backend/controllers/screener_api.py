from flask import Blueprint, request
from providers.screener import get_screener_by_id
from collections import defaultdict


bp = Blueprint("screener", __name__, url_prefix="/screener")


@bp.route("/<screener_id>/answers", methods=["POST"])
def process_answers(screener_id: str) -> dict:
    """Processes answers to a diagnostic screener.
    Returns the assessments that should be assigned based on those answers. Possible assessments are:
    PHQ-9, ASSIST, and ASRM
    Arguments:
        screener_id: the id of the screener we are processing. This comes from the url path.
    Returns:
        dictionary representing the json response. Looks like:
            { "results": List[str] }
    """
    screener = get_screener_by_id(screener_id)

    answers = request.json.get("answers")

    domain_cutoffs = {
        "PHQ-9": {"depression": 2, "anxiety": 2},
        "ASSIST": {"substance_use": 1},
        "ASRM": {"mania": 2},
    }

    domain_scores = defaultdict(lambda: 0)
    for ans in answers:
        domain_scores[screener.questions[ans["question_id"]].domain] += ans["value"]
    print("domain scores", domain_scores)
    assessments = []
    for assessment, cutoffs in domain_cutoffs.items():
        for domain, cutoff_val in cutoffs.items():
            if domain_scores[domain] >= cutoff_val:
                assessments.append(assessment)
                break

    return {"results": assessments}


@bp.route("/<screener_id>")
def get_screener(screener_id: str) -> dict:
    """Handles requests to get a screener.
    Looks up the screener data in the db and returns it as a dictionary.
    Arguments:
        screener_id: the id of the screener we want to return. This comes from the url path.
    Returns:
        dictionary representing the json response. See the API contract for details
    """
    screener = get_screener_by_id(screener_id)
    print("got screener,", screener)

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
