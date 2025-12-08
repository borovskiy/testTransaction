 docker volume prune -f 
 docker container prune -f


docker compose --env-file ./app/.env up -d
docker compose --env-file ./app/.env down


export DATABASE_URL=postgresql+asyncpg://alchemy_user:strong_password_123@localhost:5432/alchemy_crm
poetry run alembic revision --autogenerate -m "init"
poetry run alembic upgrade head
