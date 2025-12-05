 docker volume prune -f 
 docker container prune -f


docker compose --env-file ./app/.env up -d
docker compose --env-file ./app/.env down