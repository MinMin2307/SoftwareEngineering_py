from dto.RequesDTO import CreateUserDTO
from model.user import User
from database.database_sm import save_user

def createUser(data: CreateUserDTO):
    user = User(data.first_name, data.last_name)
    save_user(user)
    return user
