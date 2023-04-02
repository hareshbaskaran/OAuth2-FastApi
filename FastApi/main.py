from typing import List,Annotated
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
import schemas
import crud, models
from datetime import datetime, timedelta
from typing import Any, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from auth import SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,oauth2_scheme,pwd_context
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#router integration
router = FastAPI().api_route

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

#middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.post("/products/")
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_name(db, name=product.name)
    if db_product:
        raise HTTPException(status_code=400, detail="Product name already registered")
    return crud.create_product(db=db, product=product)

@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Union[models.User, None]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return user

# Registration endpoint
@app.post("/register", response_model=schemas.UserCreate)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# Phone number login endpoint
@app.post("/login/phone", response_model=schemas.Token)
async def login_with_phone_number(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_phone_number(db, phone_number=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    if not crud.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

