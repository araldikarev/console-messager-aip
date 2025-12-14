from server.framework import BaseController, action, CONNECTED_USERS
from dto.models import LoginRequest, RegisterRequest
from sqlmodel import select
from server.db_models import User
from sqlalchemy.exc import IntegrityError
import security

class AuthController(BaseController):

    @action("login")
    async def login(self, req: LoginRequest):
        print(f"[LOGIN] {req.login}")

        async with self.ctx.create_session() as session:
            statement = select(User).where(User.login == req.login)
            result = await session.execute(statement=statement)
            user: User = result.scalars().first()

            if not user:
                await self.ctx.reply_error("Не найден пользователь!")
                return
            
            if user.password_hash != req.password_hash:
                await self.ctx.reply_error("Неверный пароль!")
                return
            
            token = security.create_jwt(user.id, user.username)
            self.ctx.user_id = user.id
            CONNECTED_USERS[user.id] = self.ctx
            print(f"[ONLINE] Подключен пользователь {user.login} (ID: {user.id})")
            
            await self.ctx.reply("auth_success", token)


    @action("register")
    async def register(self, req: RegisterRequest):
        print(f"[REGISTER] {req.login}")

        async with self.ctx.create_session() as session:
            new_user = User(
                login=req.login,
                username=req.username,
                password_hash=req.password_hash
            )

            try:
                session.add(new_user)
                await session.commit()
                
                
                token = security.create_jwt(new_user.id, new_user.username)
                self.ctx.user_id = new_user.id
                CONNECTED_USERS[new_user.id] = self.ctx

                await self.ctx.reply("auth_success", token)

            except IntegrityError:
                await self.ctx.reply_error("Логин уже занят.")

            