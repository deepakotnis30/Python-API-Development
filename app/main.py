from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from fastapi import Depends
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()

class Post(BaseModel):
    title:'str'
    content:'str'
    published: bool = True    

while True:
    try: 
        conn = psycopg.connect(
        host='localhost',
        dbname='fastapi',
        user='postgres',
        password='test123',
        row_factory=dict_row
        )
        cursor = conn.cursor()
        print("Database connection successful")
        break
    
    except Exception as error:
        print("Connection to database failed")
        print("Error:", error)
        time.sleep(2)

my_posts=[{"title":"title of post1","content":"content of post 1","id": 1},
          {"title":"favorite foods","content":"I like Pizza","id" :2}]

def find_post(id):
    for p in my_posts:       
        if p['id'] == id:            
            return p
    
        
def find_index_post(id):
    for i,p in enumerate(my_posts):       
        if p['id'] == id:            
            return i
        
@app.get("/")
def root():
    return {"message": "Welcome to My API Testing123!!!"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    #post = db.query(models.Post).filter(models.Post.id == 1).first()
    posts= db.query(models.Post).all()
    return {"data": posts}
    #return {"status": "success"}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    #cursor.execute("""SELECT * FROM posts""")
    #posts = cursor.fetchall()
    #print(posts)
    return{"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post:Post, db: Session = Depends(get_db)):
    #cursor.execute("""INSERT INTO POSTS(title, content, published) VALUES (%s,%s,%s) RETURNING * """,
    #              (post.title, post.content, post.published))
    #new_post =cursor.fetchone()
    #conn.commit()    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return{"data": new_post}
    

#update post

@app.put("/posts/{id}")
def update_post(id:int, post:Post, db: Session = Depends(get_db)):
    #cursor.execute("UPDATE posts SET title=%s, content=%s, published=%s where id=%s RETURNING *", 
    #               (post.title, post.content, post.published, id))
    #updated_post =cursor.fetchone()
    #conn.commit()    
    #index = find_index_post(id)
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(updated_post)
    return{"data": updated_post}


@app.get("/posts/{id}")
def get_post(id:int, response: Response, db: Session = Depends(get_db)):
    #cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
    #post = cursor.fetchone()
    #print(post)
    #post = find_post(id)
    post = db.query(models.Post).filter(models.Post.id == id).first()
    #print(post)
    if not post :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")     
    return{"post_detail":post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):
    #cursor.execute("DELETE FROM posts WHERE id = %s returning *", (id,))
    #delete_post =cursor.fetchone()
    #conn.commit()    
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)