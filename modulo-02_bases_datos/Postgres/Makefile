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

down: ## Detiene y elimina contenedores y volumen de datos
	docker compose down -v

restart: ## Reinicia todo el entorno
	$(MAKE) down
	$(MAKE) up

logs: ## Muestra logs de Postgres
	docker compose logs -f postgres

inspect: ## Inspecciona la configuración de docker-compose
	docker compose config

ip: ## Muestra la IP del contenedor de Postgres
	@docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(POSTGRES_CONTAINER_NAME)

psql: ## Abre psql dentro del contenedor de Postgres (se conecta a $(POSTGRES_DB))
	docker exec -it $(POSTGRES_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

seed: ## Ejecuta los scripts .sql en ./initdb dentro del contenedor (sobre $(POSTGRES_DB))
	docker exec -it $(POSTGRES_CONTAINER_NAME) bash -lc 'for f in /docker-entrypoint-initdb.d/*.sql; do echo "Ejecutando $$f"; psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f $$f; done'

status: ## Lista contenedores de Postgres y PGAdmin
	docker ps --filter "name=$(POSTGRES_CONTAINER_NAME)" --filter "name=$(PGADMIN_CONTAINER_NAME)"
