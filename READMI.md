docker volume prune -f
docker container prune -f
docker image prune -f
docker images -a -q | % { docker image rm $_ -f }

docker compose --env-file ./app/.env down
docker compose --env-file ./app/.env up -d --build --force-recreat

export DATABASE_URL=postgresql+asyncpg://alchemy_user:strong_password_123@localhost:5432/alchemy_crm
poetry run alembic revision --autogenerate -m "init"
poetry run alembic upgrade head

http://localhost:8089/ KafkaUI
http://localhost:8080/browser/ PGAdminUI

Чисто по фану тестовое звучало примерно так

Мы пишем внутренний процессинг для начисления бонусов и переводов между сотрудниками. Твоя задача — реализовать отказоустойчивое ядро транзакций.
Задача 1: API Транзакций 
Реализовать модель Wallet (Кошелек) и Transaction (Транзакция). Сделать эндпоинт POST /api/transfer, который переводит валюту с кошелька А на кошелек Б.
Условия со звездочкой:
    1. Race Condition Check: Представь, что на этот эндпоинт приходит 100 запросов в секунду от одного юзера с целью списать баланс в минус. Реализуй защиту от Double Spending (двойного списания). Подсказка: Просто if balance > amount недостаточно.
    2. Комиссия системы: Если сумма перевода > 1000 u., система берет комиссию 10%. Комиссия должна зачисляться на специальный технический кошелек admin. Все три операции (списание, зачисление, комиссия) должны пройти атомарно (либо все, либо ничего).
Задача 2: Асинхронность 
После успешной транзакции нужно отправить "уведомление" получателю (в реальности это Telegram, но тут упростим).
    1. Создай задачу в Celery.
    2. Внутри задачи сделай имитацию долгого запроса (time.sleep(5)).
    3. Важно: Если "отправка" упала (симуляция ошибки), задача должна автоматически перезапуститься (Retry) через 3 секунды, но не более 3-х раз.
 
