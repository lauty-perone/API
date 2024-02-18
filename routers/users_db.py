from fastapi import APIRouter, HTTPException, status
from db.models.user import User
from db.schemas.user import  users_schema, user_schema
from db.client import db_client
from bson import ObjectId
from passlib.context import CryptContext

router = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}})

#Devuelve todos los usuarios de la DB
@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

#Retorna un usuario por id
@router.get("/{id}")  # Path
async def user(id: str):
    return search_user("_id", ObjectId(id))


@router.get("/")  # Query
async def user(id: str):
    return search_user("_id", ObjectId(id))

#Crea un usuario
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def user(user: User):
    
    #Comprueba si el email (clave única) ya existe en la DB
    if type(search_user("email", user.email)) == User:
           raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND, detail="El usuario ya existe")

    #Convierte el objeto user que es un JSON a un diccionario
    dict_user = dict(user)
    
    #Encripta la contraseña
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")
    dict_user["password"] = pwd_context.hash(dict_user["password"])
    del dict_user["id"]

    #Inserta en la base de datos
    id = db_client.users.insert_one(dict_user).inserted_id

    #Crea un usuario para retornarlo buscandolo en la DB
    new_user = user_schema(db_client.users.find_one({"_id": id}))
    
    return User(**new_user)

#Actualiza un usuario, hay que pasarle todos los campos(inclusive el id)
@router.put("/", response_model=User)
async def user(user: User):

    dict_user = dict(user)
    #Encripta la contraseña
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")
    password = dict_user["password"]
    dict_user["password"] = pwd_context.hash(password)
    del dict_user["id"]

    try:
        #Actualiza el usuario buscando primero el del id ingresado y le pasa los campos para actualizar
        db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)}, dict_user)
    except:
        return {"Error": "No se ha actualizado el usuario"}

    #Devuelve el id del usuario
    return search_user("_id", ObjectId(user.id))

#Elimina un usuario por su id a tráves de una Path
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):

    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})

    if not found:
        return {"error": "No se ha eliminado el usuario"}


#Se encarga de buscar por clave(str) y por valor(JSON) en la DB
def search_user(field: str, key):

    try:
        user = db_client.users.find_one({field: key})
        return User(**user_schema(user))
    except:
        return {"error": "No se ha encontrado el usuario"}