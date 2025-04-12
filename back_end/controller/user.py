from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from dependencise import get_mongo_db
from pydantic import BaseModel, Field
import bcrypt
from typing import Dict

# 定义数据模型
class UserRegister(BaseModel):
    username: str
    telephone: str
    password: str
    real_name: str
    age: int
    sex: str
    mail: str

class UserLogin(BaseModel):
    userortel: str
    password: str

class UserFindback(BaseModel):
    telephone: str
    password: str


user_router = APIRouter(tags=['用户注册登录api'])

# 用户注册
@user_router.post('/register', status_code=status.HTTP_201_CREATED)
async def user_register(user: UserRegister, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        user_collection = mongo_db['USER']

        # 检查用户名或手机号是否已存在
        existing_user = await user_collection.find_one({
            "$or": [{"username": user.username}, {"telephone": user.telephone}]
        })

        if existing_user:
            return {"status": 400, "msg": "用户名或手机号已存在"}

        # 对密码进行哈希加密
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

        # 插入用户数据
        user_data = user.dict()
        user_data['password'] = hashed_password.decode('utf-8')  # 保存加密后的密码

        result = await user_collection.insert_one(user_data)

        return {"status": 200, "msg": "注册成功"}

    except Exception as e:
        return {"status": 500, "msg": f"注册失败: {str(e)}"}


# 用户登录
@user_router.post('/login')
async def user_login(user: UserLogin, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        user_collection = mongo_db['USER']

        # 查找用户
        found_user = await user_collection.find_one({
            "$or": [{"username": user.userortel}, {"telephone": user.userortel}]
        })

        if found_user:
            # 验证密码
            if bcrypt.checkpw(user.password.encode('utf-8'), found_user['password'].encode('utf-8')):

                return {"code": 200, "msg": "登录成功"}
            else:
                return {"code": 401, "msg": "密码错误"}
        else:
            return {"code": 404, "msg": "用户名或手机号不存在"}

    except Exception as e:
        return {"code": 500, "msg": f"登录失败: {str(e)}"}


# 找回密码
@user_router.post('/findback')
async def user_findback(user: UserFindback, mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    try:
        user_collection = mongo_db['USER']

        # 找到用户并更新密码
        update_result = await user_collection.update_one(
            {"telephone": user.telephone},
            {"$set": {"password": bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')}}
        )

        if update_result.modified_count > 0:
            return {"status": 200, "msg": "密码修改成功"}
        else:
            return {"status": 404, "msg": "未找到该用户"}

    except Exception as e:
        return {"status": 500, "msg": f"密码修改失败: {str(e)}"}