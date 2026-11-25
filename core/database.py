from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

db_engine = create_async_engine('postgresql+asyncpg://postgres:8262@localhost:5432/e-commerce')
db_session = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

