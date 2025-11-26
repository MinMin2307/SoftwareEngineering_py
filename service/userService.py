from dto.RequesDTO import CreateUserDTO
from dto.ResponseDTO import UserResponseDTO
from database.database_sm import save_user

def createUser(data: CreateUserDTO) -> UserResponseDTO:
    user_id = save_user(data.first_name, data.last_name)

    return UserResponseDTO(
        id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        posts=[]
    )
