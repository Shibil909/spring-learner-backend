from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from dotenv import load_dotenv
from utils.helpers import load_questions, get_user_progress, get_motivation_message
from utils.helpers import update_day_status, get_last_completed_date, write_passed_date
from services.analyze_assessment import AssessmentAnalyzer
from services.reward_sender import EmailSender
import os
from datetime import datetime, timedelta
from pydantic import BaseModel
from utils.log_config import setup_logger
from fastapi import BackgroundTasks

logger = setup_logger(__name__) 

load_dotenv()
PROGRESS_DB_PATH = os.getenv("PROGRESS_DB_PATH")
QUESTIONS_DIR = os.getenv("QUESTIONS_DIR")
PASSED_DATE_FILE = os.getenv("PASSED_DATE_FILE")
assessment_analyzer = AssessmentAnalyzer()
email_sender = EmailSender()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_progress")
def get_progress():
    try:
        progress = get_user_progress(PROGRESS_DB_PATH)
        logger.info(f"loaded progress sucessfully")
        return progress
    except Exception as e:
        logger.error(f"get progress endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Internal Server Error: {str(e)}"}
        )


@app.get("/get_questions/{day}")
def get_questions(day: str):
    """
    Load questions for the given day and include motivational message
    """
    try:
        # build file path like assets/questions/day_1.json
        file_path = os.path.join(QUESTIONS_DIR, f"{day}.json")
        
        if not os.path.exists(file_path):
            logger.error(f"question serving error: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Questions for {day} not found")

        # --- Unlock check ---
        last_completed_date = get_last_completed_date(PASSED_DATE_FILE)
        print(last_completed_date)
        if last_completed_date:
            diff = datetime.utcnow() - last_completed_date
            if diff < timedelta(hours=12):
                remaining = timedelta(hours=12) - diff
                remaining_str = str(remaining).split('.')[0]  # HH:MM:SS
                return JSONResponse(
                status_code=403,
                content={
                    "message": "payye thinna panayum thinna",
                    "remaining": remaining_str
                    }
                )

        questions = load_questions(file_path, day)
        motivation_message = get_motivation_message(PROGRESS_DB_PATH, day)
        logger.info(f"question served successfully")
        return {
            "day": day,
            "day_header": motivation_message,
            "questions": questions
        }

    except ValueError as ve:
        logger.error(f"question serving error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"question serving error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# -------------------
# Request schema
# -------------------

class TaskAnswer(BaseModel):
    task_key: str
    response: str

class Answer(BaseModel):
    question_id: int
    type: str
    response: Optional[str] = None
    tasks: Optional[List[TaskAnswer]] = None

class SubmitAnswersRequest(BaseModel):
    day: str
    answers: List[Answer]


# -------------------
# Endpoint
# -------------------
@app.post("/submit_answers")
def submit_answers(payload: SubmitAnswersRequest, background_tasks: BackgroundTasks):
    try:

        question_file = payload.day + ".json"
        question_json_path = os.path.join(QUESTIONS_DIR, question_file)
        result = assessment_analyzer.evaluate_assessment(question_json_path, payload.day, [a.dict() for a in payload.answers])

        # --- Update progress DB if passed ---
        if result["pass"]:

            # update current day in progress db as completed
            update_day_status(PROGRESS_DB_PATH, payload.day, "completed")

            # write passed date
            write_passed_date(PASSED_DATE_FILE, payload.day)

            # Unlock next day
            current_day_num = int(payload.day.split("_")[1])
            next_day = f"day_{current_day_num + 1}"

            # check if next day not greater than 10
            if (current_day_num + 1) <= 10:
                update_day_status(PROGRESS_DB_PATH, next_day, "unlocked")

            
           
                # schedule reward mail in background
                background_tasks.add_task(email_sender.send_reward_sendgrid, payload.day)

        logger.info(f"Assessment evaluated sucessfully")
        return result
    except FileNotFoundError as fe:
        logger.error(f"Assessment Evaluation error: {str(fe)}")
        raise HTTPException(status_code=404, detail=str(fe))
    except Exception as e:
        logger.error(f"Assessment Evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
if __name__ == "__main__":
    pass

