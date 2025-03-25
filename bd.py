from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from models import Base, User, ImageProcessingRequest


# Подключение к локальной базе данных (замени `user`, `password`, `dbname` на свои данные)
DATABASE_URL = "postgresql+asyncpg://postgres:241285@localhost/imagefilter"

# Создаем движок и сессию
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def create_or_get_user(telegram_id: int, username: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = user.scalar_one_or_none()

            if not user:
                user = User(telegram_id=telegram_id, username=username)
                session.add(user)
                await session.commit()
                return user

        return user

async def add_image_processing_request(telegram_id: int, uploaded_image_id: str, processing_type: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            user = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = user.scalar_one_or_none()

            if not user:
                return None  # Если пользователя нет, обработка невозможна

            new_request = ImageProcessingRequest(
                user_id=user.id,
                uploaded_image_id=uploaded_image_id,
                processing_type=processing_type
            )
            session.add(new_request)
        await session.commit()
        return new_request.id

async def update_processed_image(request_id: int, processed_image_id: str):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            request = await session.get(ImageProcessingRequest, request_id)

            if request:
                request.processed_image_id = processed_image_id
                await session.commit()
                return True

        return False

async def get_user_requests(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ImageProcessingRequest.uploaded_image_id, ImageProcessingRequest.processed_image_id, ImageProcessingRequest.processing_type, ImageProcessingRequest.request_time)
            .join(User)
            .where(User.telegram_id == telegram_id)
            .order_by(ImageProcessingRequest.request_time.desc())
        )
        return result.all()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)