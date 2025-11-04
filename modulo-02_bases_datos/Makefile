SHELL := /bin/bash

# Carga las variables del .env si existe
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: up stop down restart logs inspect ip psql seed status

up: ## Levanta Postgres y PGAdmin en segundo plano
	docker compose up -d

stop: ## Detiene los contenedores sin borrarlos
	docker compose stop

down: ## Detiene y elimina contenedores y redes
	docker compose down

restart: ## Reinicia el entorno completo
	$(MAKE) down
	$(MAKE) up

logs: ## Muestra logs de los servicios
	docker compose logs -f

inspect: ## Inspecciona la configuración de docker-compose
	docker compose config

ip: ## Muestra la IP del contenedor de Postgres
	@docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(POSTGRES_CONTAINER_NAME)

psql: ## Abre psql dentro del contenedor de Postgres
	docker exec -it $(POSTGRES_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

seed: ## Ejecuta scripts .sql en ./initdb dentro del contenedor
	docker exec -it $(POSTGRES_CONTAINER_NAME) bash -lc "for f in /docker-entrypoint-initdb.d/*.sql; do [ -f $$f ] && echo '>> Ejecutando' $$f && psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f $$f; done"

status: ## Lista contenedores relevantes
	docker ps --filter "name=$(POSTGRES_CONTAINER_NAME)" --filter "name=$(PGADMIN_CONTAINER_NAME)"
