from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
import plotly.express as px

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
class QuestionBase(BaseModel):
    content: str = Field(min_length=1)

class PostCreate(PostBase):
    user_id: int


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    image_file: str | None
    image_path: str

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    id: int
    date_posted: datetime
    author: UserResponse

class QuestionResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    id:int
    date_posted:datetime
    author: UserResponse

class QuestionCreate(QuestionBase):
    user_id:int

class Metrics(BaseModel):
    score: int = Field(description="Score from -100 to 100 based on your scoring system")
    label: str = Field(description="The classification label based on the essay analysis")
    evidence: str = Field(description="Direct quotes or strong reasoning from the essay backing up this score")

class Compass(BaseModel):
    individualism_collectivism: Metrics
    rationalism_irrationalism: Metrics
    universalism_relativism: Metrics
    determinism_free_will: Metrics

class CompassResponse(BaseModel):
    philosophical_compass: Compass

class UserCreate(UserBase):
    pass
