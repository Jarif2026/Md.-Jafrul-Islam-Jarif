import sqlite3
from typing import Literal
from fastapi import FastAPI, HTTPException, status
from schemas import MovieCreate, MovieUpdate

app = FastAPI()

DB_NAME = "movies.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def startup():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            movie_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            director TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            rating REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.get("/movies")
def get_all_movies():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/movies/sort")
def sort_movies(
    sort_by: Literal["duration", "rating"] = "rating",
    order: Literal["asc", "desc"] = "desc"
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM movies ORDER BY {sort_by} {order.upper()}")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/movies/{movie_id}")
def get_movie_by_id(movie_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE movie_id = ?", (movie_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    return dict(row)


@app.post("/create_movies", status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT movie_id FROM movies WHERE movie_id = ?", (movie.movie_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Movie with ID {movie.movie_id} already exists"
        )
    
    cursor.execute("""
        INSERT INTO movies (movie_id, title, director, genre, duration, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (movie.movie_id, movie.title, movie.director, movie.genre, movie.duration, movie.rating))
    
    conn.commit()
    conn.close()
    return movie


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieUpdate):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT movie_id FROM movies WHERE movie_id = ?", (movie_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    cursor.execute("""
        UPDATE movies
        SET title = ?, director = ?, genre = ?, duration = ?, rating = ?
        WHERE movie_id = ?
    """, (movie.title, movie.director, movie.genre, movie.duration, movie.rating, movie_id))
    
    conn.commit()
    conn.close()
    
    updated_data = movie.dict()
    updated_data["movie_id"] = movie_id
    return updated_data


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT movie_id FROM movies WHERE movie_id = ?", (movie_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found"
        )
    
    cursor.execute("DELETE FROM movies WHERE movie_id = ?", (movie_id,))
    conn.commit()
    conn.close()
    return {"message": f"Movie with ID {movie_id} has been successfully deleted"}