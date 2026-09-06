# Docker

Guia operacional de Docker para os pipelines.

## Build

```bash
docker build -f docker/Dockerfile.pipelines -t financial_pipelines .
docker compose -f docker/docker-compose.yml build
```

A configuracao comum do Compose monta `pipelines/data`, `pipelines/logs`, `pipelines/checkpoints` e `pipelines/historical_data`. O limite e `7g` de memoria, com reserva de `4g`.

## Compose

```bash
docker compose -f docker/docker-compose.yml run --rm \
  -e PIPELINE_ENV=dev \
  <servico-compose>
```

Os servicos e nomes de pipeline estao definidos em `docker/docker-compose.yml`.

## Execucao direta

```bash
docker run --rm -it \
  -e PIPELINE_NAME=<pipeline_name> \
  -e PIPELINE_ENV=dev \
  -v "$PWD/pipelines/data:/app/pipelines/data" \
  -v "$PWD/pipelines/logs:/app/pipelines/logs" \
  -v "$PWD/pipelines/checkpoints:/app/pipelines/checkpoints" \
  -v "$PWD/pipelines/historical_data:/app/pipelines/historical_data" \
  financial_pipelines
```

## Monitoramento

```bash
docker ps
docker stats
docker compose -f docker/docker-compose.yml images
```
