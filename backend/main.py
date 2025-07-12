from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
import joblib
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only! use specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and encoders
model = joblib.load('model/model.pkl')
encoders = joblib.load('model/encoders.pkl')

# ---- Schema ---- #
class Lead(BaseModel):
    credit_score: int
    age_group: str
    family_background: str
    income: int
    comment: str
    email: EmailStr

    @validator('credit_score')
    def validate_credit_score(cls, v):
        if v < 300 or v > 850:
            raise ValueError('Credit score must be between 300 and 850')
        return v

    @validator('income')
    def validate_income(cls, v):
        if v < 0:
            raise ValueError('Income must be non-negative')
        return v

# ---- Keyword-based Re-ranker ---- #
def rerank_score(base_score: float, comment: str) -> float:
    keywords = {
        'urgent': 10,
        'interested': 7,
        'asap': 5,
        'not interested': -10,
        'later': -5,
        'already': -3
    }

    adjustment = 0
    comment_lower = comment.lower()
    for word, impact in keywords.items():
        if word in comment_lower:
            adjustment += impact

    final_score = np.clip(base_score + adjustment, 0, 100)
    return final_score

# ---- Scoring Endpoint ---- #
@app.post("/score")
def get_intent_score(lead: Lead):
    try:
        # Prepare feature input
        input_data = [
            lead.credit_score,
            encoders['age_group'].transform([lead.age_group])[0],
            encoders['family_background'].transform([lead.family_background])[0],
            lead.income
        ]

        # Predict intent score (probability scaled to 0-100)
        base_prob = model.predict_proba([input_data])[0][1]
        base_score = round(base_prob * 100, 2)

        # Apply reranker using comment
        reranked_score = rerank_score(base_score, lead.comment)

        return {
            "email": lead.email,
            "initial_score": base_score,
            "reranked_score": reranked_score,
            "comment": lead.comment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
