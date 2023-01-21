import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

try:
    connection = psycopg2.connect(user="postgres", password="kris@2013",host='localhost',database="fastapi", cursor_factory=RealDictCursor)
    print(connection.get_dsn_parameters())
    cursor = connection.cursor()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

@router.get("/posts")
def get_posts():
    cursor.execute("""select * from posts""")
    posts = cursor.fetchall
    print(posts)
    return {"data": posts}

@router.post("/posts")
def create_posts(post: Post):
    cursor.execute(""" insert into posts (title, content, published) values (%s, %s, %s) returning * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    connection.commit() 
    return {"data": new_post}

@router.get("/posts/{post_id}")
def get_post(post_id: int, response: Response):
    cursor.execute("""select * from posts where id = %s""", (str(post_id)))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    return {"data": post}

@router.put("/posts/{post_id}")
def update_post(post_id: int, post: Post):
    cursor.execute("""update posts set title = %s, content = %s, published = %s where id = %s returning *""", (post.title, post.content, post.published, str(post_id)))
    connection.commit()
    updated_post = cursor.fetchone()

    if update_post == None:
        raise HTTPException(status_code=404, detail="no record found")
    
    return {"data": updated_post}
    
    
@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute("""delete from posts where id = %s""", (str(post_id)))
    connection.commit()
    return {"message": "post deleted successfully"}


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    cursor.execute("""insert into users (email, password) values (%s, %s) returning *""", (user.email, user.password))
    connection.commit()
    new_user = cursor.fetchone()
    return {"data": new_user}
     

@router.get('/users/{id}')
def get_user(id: int):
    cursor.execute("""select * from users where id = %s""", (str(id)))
    user = cursor.fetchone()
    if user == None:
        raise HTTPException(status_code=404, detail="no record found")
    return {"data": user}