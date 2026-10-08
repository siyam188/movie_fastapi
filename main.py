from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from typing import Literal
import model
from database import engine,sessionlocal

app=FastAPI()

model.Base.metadata.create_all(bind=engine)
class MovieCreate(BaseModel):
    movie_id: int
    title: str
    director: str
    genre: Literal["action", "comedy", "drama", "thriller"]
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)
class MovieUpdate(BaseModel):
    title: str
    director: str
    genre: Literal["action", "comedy", "drama", "thriller"]
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)

def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:db.close()


@app.get("/movies")
def get_movies(db:Session=Depends(get_db)):
    movies=db.query(model.Movies).all()
    return movies
@app.get("/movies/sort")
def sort_movies(
    sort_by: str = "rating",
    order: str = "desc",
    db: Session = Depends(get_db)
):
    if sort_by == "duration":
        column = model.Movies.duration
    else:
        column = model.Movies.rating

    if order == "asc":
        movies = db.query(model.Movies).order_by(column.asc()).all()
    else:
        movies = db.query(model.Movies).order_by(column.desc()).all()

    return movies

@app.get("/movies/{movie_id}")
def get_movies(movie_id:int,db:Session=Depends(get_db)):
    movie=db.query(model.Movies).filter(model.Movies.movie_id==movie_id).first()
    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie


@app.post("/create/")
def create_movie(
    newmovie:MovieCreate,
    db:Session=Depends(get_db)
):
    movie = model.Movies(**newmovie.model_dump())

    db.add(movie)
    db.commit()

    return JSONResponse(
        status_code=201,
        content={"message": "Create successful"}
    )

@app.put("/movies/{movie_id}")
def edit_movie(
    movie_id:int,
    update_movie:MovieUpdate,
    db:Session=Depends(get_db)
):
    edit_movie=db.query(model.Movies).filter(model.Movies.movie_id==movie_id).first()
    if edit_movie is None:
        raise HTTPException(status_code=404,detail="Movie not Found")
    update_data = update_movie.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(edit_movie, key, value)

    db.commit()
    db.refresh(edit_movie)

    return JSONResponse(
        status_code=200,
        content={"message": "Update successful"}
    ) 


@app.delete("/movies/{movie_id}")
def delete_movie(
    movie_id:int,
    
    db:Session=Depends(get_db)
):
    movie=db.query(model.Movies).filter(model.Movies.movie_id==movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404,detail="Movie not Found")
    

    db.delete(movie)
    db.commit()
    

    return {
        "message": "Movie deleted successfully"
    }