# B3 Indices de Segmentos Setoriais

## Objetivo

Extrair e organizar a composicao dos indices de segmentos e setores da B3.

## Status e execucao

- Status: `manual`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/b3_indices_segmentos_setoriais/stage/pipeline.py`
- Agendamento: sob demanda; sem timer Systemd ativo.
- Alternativa: servico Compose `b3-indi-seg-set-pipeline`.

## Stages

`extract` -> `to_interim` -> `retention`.

## Dados

Os dados brutos sao JSON por indice. A transformacao produz `indices.parquet` e `composicao.parquet` em `transform/to_interim/parquet/`. Consulte [data-catalog.md](data-catalog.md).

## Validacao

Confira logs e checkpoints em `pipelines/logs/b3_indices_segmentos_setoriais` e `pipelines/checkpoints/b3_indices_segmentos_setoriais`.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Troubleshooting](../../operations/troubleshooting.md)
