# B3 Enriquecimento Cadastral de Ativos

## Objetivo

Enriquecer informacoes cadastrais de ativos e companhias com dados retornados pela B3.

## Status e execucao

- Status: `manual`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/b3_enriquecimento_cadastral_ativos/stage/pipeline.py`
- Agendamento: sob demanda; sem timer Systemd ativo.
- Alternativa: servico Compose `b3-cad-pipeline`.

## Stages

`extract` -> `to_interim` -> `retention`.

## Dados

Os dados brutos e intermediarios sao armazenados em `pipelines/data/b3_enriquecimento_cadastral_ativos/<snapshot>/`. Consulte [data-catalog.md](data-catalog.md) para datasets e campos.

## Validacao

Confira logs e checkpoints em `pipelines/logs/b3_enriquecimento_cadastral_ativos` e `pipelines/checkpoints/b3_enriquecimento_cadastral_ativos`.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Troubleshooting](../../operations/troubleshooting.md)
