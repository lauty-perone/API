"""from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import APIRouter, status, HTTPException, Depends
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from db.client import db_client
from db.schemas.user import user_schema_db 
from db.models.user import User

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "f3a990758534c53db0a85c4e02c36eed98e386d48cf14a3d70409a1f5dccd386"

router = APIRouter(prefix= "/jwtauth",
                   tags= ["jwtauth"],
                   responses={status.HTTP_404_NOT_FOUND:{
                       "messagge": "No encontrado"
                   }})

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

crypt = CryptContext(schemes=["bcrypt"], deprecated = "auto")

class UserDB(User):
    password : str

def search_user_db(username : str):

    try:
        user = db_client.users.find_one({"username", username})
        return UserDB(**user_schema_db(user))
    except:
        return {"error": "No se ha encontrado el usuario"}
  
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):

    user = search_user_db(form.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")


    if not crypt.verify(form.password, user["user"]["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}
"""