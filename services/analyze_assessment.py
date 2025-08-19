from utils.helpers import load_json
from utils.log_config import setup_logger

logger = setup_logger(__name__)

class AssessmentAnalyzer:
    """
    result evaluator
    """
    def __init__(self):
        pass

    def evaluate_assessment(self, question_json_path: str, day: str, answers: list)-> dict:
        """
        Evaluate assessment
        ARGS:
            question_json_path (str): json file path for corresponding day
            day (str): day
            answers (dict): answers from users
        Return:
            result (dict): result of assessment
        """
        try:
            questions_data = load_json(question_json_path)

            # build lookup {question_id: question_dict}
            questions_lookup = {q["id"]: q for q in questions_data}
            
            total_points = 0        # total points for the assessment
            scored_points = 0       # scored points for the assessment

            for ans in answers:
                qid = ans["question_id"]
                qtype = ans["type"]

                # YES/NO or MCQ
                if qtype in ["yes_no", "mcq"]:
                    correct_answer = questions_lookup[qid]["correctAnswer"]
                    total_points += 1
                    if ans["response"] == correct_answer:
                        scored_points += 1
                
                # PRACTICAL
                if qtype == "practical":
                    total_points += 1
                    if ans["response"] == "completed":
                        scored_points += 1
                
                 # PROJECT
                if qtype == "project":
                    tasks = ans.get("tasks", [])
                    correct_tasks = sum(1 for t in tasks if t["response"] == "completed")
                    total_tasks = len(tasks)
                    total_points += total_tasks
                    scored_points += correct_tasks
            
            # pass or not
            passed = scored_points >= (total_points / 2)
            return {
                "day": day,
                "score": scored_points,
                "total": total_points,
                "pass": passed
            }
        except Exception as e:
            logger.error(f"Assessment evaluation error: {str(e)}")