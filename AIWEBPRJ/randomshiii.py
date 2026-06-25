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
import textwrap

Sample_Response = {
  "philosophical_compass": {
    "individualism_collectivism": {
      "score": 50,
      "label": "Balanced / Communitarian",
      "evidence": "The author strikes a precise middle ground, arguing that while individual rights are vital, they are meaningless without a stable social contract. The text balances phrases like 'personal autonomy' directly with 'civic responsibility' throughout the critique."
    },
    "rationalism_irrationalism": {
      "score": 95,
      "label": "Strict Rationalist",
      "evidence": "The argument is built entirely on mathematical modeling and formal deductive logic. The author dismisses any emotional appeals as 'cognitive noise' and demands that all policy decisions be rooted strictly in peer-reviewed empirical data."
    },
    "universalism_relativism": {
      "score": 55,
      "label": "Contextual Universalist",
      "evidence": "The essay argues that while basic human rights are universal, the expression and execution of those rights must adapt to local customs. It attempts to bridge the gap by stating 'the core values are absolute, but the cultural lenses vary.'"
    },
    "determinism_free_will": {
      "score": 50,
      "label": "Compatibilist",
      "evidence": "The text explicitly argues that free will and determinism can coexist. It states that while our environment and genetics heavily constrain our available options, we still retain the conscious agency to choose our path among those limitations."
    }
  }
}

data_container = {
"left_var": ['indiviualism', 'rationalism', 'universalism', 'determinism'],
"right_var": ['collectivism', 'irrationalism', 'relativism', 'free will'],
"right_scores": [],
"left_scores": [],
'label_list': [],
'evidence_list': []
}

for k, v in Sample_Response["philosophical_compass"].items():
    data_container["right_scores"].append(v["score"])
    new_val = (100 - v["score"])
    data_container["left_scores"].append(new_val)
    data_container['label_list'].append(v['label'])
    data_container["evidence_list"].append(v['evidence'])
    lines=[textwrap.wrap(str(text), width=30) for text in data_container['evidence_list']]



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

fig.add_vline(
    x=0,
    line_width=2,
    line_color="black"
)

fig.update_layout(
    barmode="relative",
    title=dict(
        text='Philosophical Compass',
        subtitle=dict(
            text='smth',
            font=dict(
                color='black',
                size=14
            )
        ),
        x=0.5,
        xanchor='center',
        font=dict(size=24, color='blue', family='Arial')
    ),
    xaxis_title="Value",
    yaxis_title="Category",
    yaxis_autorange="reversed",
    showlegend=False,
    
)




fig.write_html("my_diverging_chart.html", auto_open=True)

