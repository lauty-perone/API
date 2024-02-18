from db.schemas.user import user_schema
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import APIRouter, status, HTTPException, Depends
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.client import db_client

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

class User(BaseModel):
    id: Optional[str]
    username: str
    email: str
    disabled : bool 

class UserDB(User):
    password: str 

#Busca un usuario por nombre de usuario y lo retorna sin la contraseña
def search_user(username : str):
    try:
        user = db_client.users.find_one({"username": username})
        return User(**user_schema(user))
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    
#Busca un usuario por nombre de usuario en la base de datos y 
#lo retorna con la contraseña para verificarla luego
def search_user_db(username : str):
    try:
        user = db_client.users.find_one({"username": username})
        return UserDB(**user_schema(user))
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")

#Loguea al usuario y retorna el JWT encriptado
@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):

    user = search_user_db(form.username)
    
    #Verifica si la contraseña ingresada es igual a la contraseña de la base de datos encriptada
    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")

    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), 
            "token_type": "bearer"}

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception

    except JWTError:
        raise exception

    return search_user(username)

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")

    return user

@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user