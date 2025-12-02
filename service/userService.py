from dto.RequesDTO import CreateUserDTO
from dto.ResponseDTO import UserResponseDTO
from database.database_sm import save_user, get_userByName


def createUser(data: CreateUserDTO) -> UserResponseDTO:
    existing_user = get_userByName(data.first_name, data.last_name)
    if existing_user is None:
        user_id = save_user(data.first_name, data.last_name)
        return UserResponseDTO(
            id=user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            posts=[]
        )
    return UserResponseDTO(
        id=existing_user[0],
        first_name=existing_user[1],
        last_name=existing_user[2],
        posts=[]
    )




