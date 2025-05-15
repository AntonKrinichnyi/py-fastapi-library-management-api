from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import AuthorModel, BookModel
from schemas import AuthorBaseSchema, AuthorCreateSchema, BookSchema, BookCreateSchema
from crud import create_author, get_author, get_authors, create_book, get_books, get_books_by_author


app = FastAPI()


@app.post("/authors/", response_model=AuthorBaseSchema)
def create_author(author: AuthorCreateSchema, db: Session = Depends(get_db)) -> AuthorBaseSchema:
    author_is_exists = db.query(AuthorModel).filter(AuthorModel.name == author.name).first()
    if author_is_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author already exists"
        )

    db_author = create_author(db, author)
    
    return AuthorBaseSchema(name=db_author.name, bio=db_author.bio)


@app.get("/authors/{author_id}", response_model=AuthorBaseSchema)
def get_author(author_id: int, db: Session = Depends(get_db)) -> AuthorBaseSchema:
    db_author = get_author(db, author_id)
    if db_author is None:
        raise  HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    return AuthorBaseSchema(name=db_author.name, bio=db_author.bio)


@app.get("/authors/", response_model=list[AuthorBaseSchema])
def get_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[AuthorBaseSchema]:
    authors = get_authors(db, skip, limit)
    if authors is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authors not found"
        )
    return [AuthorBaseSchema(name=author.name, bio=author.bio) for author in authors]


@app.post("/books/", response_model=BookSchema)
def create_book(book: BookCreateSchema, db: Session = Depends(get_db)) -> BookSchema:
    book_is_exists = db.query(BookModel).filter(BookModel.title == book.title).first()
    if book_is_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already exists"
        )
    author = db.query(AuthorModel).filter(AuthorModel.id == book.author_id).first()
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Author not found"
        )
    db_book = create_book(db, book)
    return BookSchema(
        id=db_book.id,
        title=db_book.title,
        summary=db_book.summary,
        published_date=db_book.published_date,
        author=author
    )


@app.get("/books/", response_model=list[BookSchema])
def get_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)) -> list[BookSchema]:
    books = get_books(db, skip, limit)
    if books is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Books not found"
        )
    return [
        BookSchema(
            id=book.id,
            title=book.title,
            summary=book.summary,
            published_date=book.published_date,
            author=db.query(AuthorModel).filter(AuthorModel.id == book.author_id).first()
        ) for book in books
    ]


@app.get("/books/{author_id}", response_model=BookSchema)
def get_book_by_authors(author_id: int, db: Session = Depends(get_db)) -> BookSchema:
    db_author = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if db_author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    db_books = get_books_by_author(db, author_id)
    if db_books is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This author don't have any books"
        )
    return [
        BookSchema(
            id=book.id,
            title=book.title,
            summary=book.summary,
            published_date=book.published_date,
            author=db_author
        ) for book in db_books
    ]
