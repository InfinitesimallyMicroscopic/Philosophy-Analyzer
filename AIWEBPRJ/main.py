from fastapi import FastAPI, Request, HTTPException, status, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import PostCreate, PostResponse, UserResponse, UserCreate, QuestionResponse,QuestionCreate, Compass, CompassResponse
import json
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from models import Question, User
from database import Base, engine, get_db
import requests
from google import genai
from dotenv import load_dotenv
from google import genai
import time
from google.genai import types
import pandas as pd
import plotly.express as px
import pydantic
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from groq import Groq
from openai import OpenAI

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
GEMINI_API_KEY="AQ.Ab8RN6JXoC8_PBBzPRbEgoPV34NEa2c20UcmY_LFZd_h4ON0UA"
# Database setup



# @app.get("/ask")
# def get_form(request:Request):
#     return templates.TemplateResponse(
#         request,
#         name="main.html"
#     )

# @app.post("/ask")
# def handle_form(
#     db: Annotated[Session, Depends(get_db)],
#     question: str = Form(...),
# ):  
#     new_question = models.Question(content=question, user_id = 1)
#     db.add(new_question)
#     db.commit()

#     return {"id": new_question.id,
#             "question": new_question.content,
#             "date_posted": new_question.date_posted}
# Load environment variables from the .env file
load_dotenv()

# The client automatically picks up the GEMINI_API_KEY variable
# client = OpenAI(
#     api_key="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",
#     base_url="https://api.groq.com/openai/v1"
# )
client = genai.Client()
# Test the connection


prompt = """
"Analyze the following philosophical essay. Evaluate where the author stands "
        "on the five spectrums provided in the schema. For each metric, provide a score, "
        "a descriptive label, and the textual evidence/reasoning behind your decision."
"""



@app.get("/ask")
def get_form(request:Request):
    return templates.TemplateResponse(
        request,
        "main.html",
    )

@app.post("/ask")
def handle_form(
        request:Request,
        db: Annotated[Session, Depends(get_db)],
        question: str = Form(...),
):
    response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=f"{prompt}. Here is the text: {question} "
    )

    if response.text is None:
        raise HTTPException (
            status_code=500, detail = "Failed to parse"
        )
    question_data = json.loads(response.text)

    new_question = Question(content=question, user_id=1, response_text=response.text)

    print(response.text)



    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    data_container = {
    "left_var": ['indiviualism', 'rationalism', 'universalism', 'determinism'],
    "right_var": ['collectivism', 'irrationalism', 'relativism', 'free will'],
    "right_scores": [],
    "left_scores": [],
    'label_list': [],
    'evidence_list': []
    }

    for k, v in question_data["philosophical_compass"].items():
        data_container["right_scores"].append(v["score"])
        new_val = (100 - v["score"])
        data_container["left_scores"].append(new_val)
        data_container['label_list'].append(v['label'])
        data_container["evidence_list"].append(v['evidence'])

    df = pd.DataFrame(data_container)
    fig = go.Figure()
    combined_var = zip(df['left_var'],df['right_var'])


    df['combined']=[f'{left} vs {right}' for left, right in combined_var]

    fig.add_trace(go.Bar(
        y=df["combined"],
    x=-df["left_scores"],
    orientation="h",
    name="Left",
    customdata=df[["left_scores", 'left_var', 'label_list', 'evidence_list']],
    hovertemplate=("%{customdata[1]}: %{customdata[0]} <br>"+
                   "label: %{customdata[2]}<br>"+
                   "evidence: %{customdata[3]}<br>"+
                    "<extra></extra>"),
    marker_color="#ef4444"
    ))

    fig.add_trace(go.Bar(
        y=df["combined"],
        x=df["right_scores"],
        orientation="h",
        name="Right",
        customdata=df[['right_var', 'right_scores']],
        hovertemplate="%{customdata[0]}: %{customdata[1]}<extra></extra>",
        marker_color="#3b82f6"
    ))



    fig.update_layout(
        barmode="relative",
        title="Diverging bar chart",
        xaxis_title="Value",
        yaxis_title="Category",
        yaxis_autorange="reversed"
    )

    plot_html = pio.to_html(fig, full_html=False, include_plotlyjs=True)



    return templates.TemplateResponse(request,
        'main.html',
                                      {
        'diverging_chart': plot_html,
        "question_data":question_data,
        "user_id": new_question.user_id,                                   
        "question_id": new_question.id,
        "date_posted": new_question.date_posted,
        "response": response.text
    }
)







'''@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user:UserCreate, db:Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists'
        )
    
    result = db.execute(select(models.User.email).where(models.User.email == user.email))
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    

    new_user = models.User(
        username=user.username,
        email=user.email
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user'''
    
# @app.get(
#     "/users/{user_id}/questions/{question_id}",
#     response_model= QuestionResponse
# )
# def get_question(question_id: int, user_id:int, db: Annotated[Session, Depends(get_db)]):
    

#     result = db.execute(select(models.Question).where(models.Question.id == question_id))
#     question = result.scalars().first()
#     if question:
#         return question
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail='Question not found'
#     )

# @app.get(
#         "/users/{user_id}/questions",
#         response_model=list[QuestionResponse]
# )   
# def get_questions(
#     user_id: int,
#     request: Request,
#     db: Annotated[Session, Depends(get_db)]
# ):
#     result = db.execute(select(models.User).where(models.User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(
#             status_code = status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user.questions

# @app.post(
#     '/api/questions',
#     response_model=QuestionResponse,
#     status_code=status.HTTP_201_CREATED
# )
# def create_question(
#     question: QuestionCreate,
#     db: Annotated[Session, Depends(get_db)]
# ):
#     result = db.execute(select(models.User).where(models.User.id == question.user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='User not found'
#         )
    
#     new_question = models.Question(
#         content=question.content,
#         user_id=question.user_id
#     )
#     db.add(new_question)
#     db.commit()
#     db.refresh(new_question)
#     return new_question




