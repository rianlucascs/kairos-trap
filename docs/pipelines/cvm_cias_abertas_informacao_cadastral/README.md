# CVM Cadastro de Companhias Abertas

## Objetivo

Extrair e preparar informacoes cadastrais de companhias abertas publicadas pela CVM.

## Status e execucao

- Status: `active`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/cvm_cias_abertas_informacao_cadastral/stage/pipeline.py`
- Agendamento: diario, 09:10, via `kairos-trap-cvm-cad.timer`.

## Stages

`extract` -> `to_interim` -> `retention`.

## Dados

Consulte [data-catalog.md](data-catalog.md) para formato, campos e granularidade.

## Validacao

Confira logs e checkpoints do pipeline antes de consumir novos snapshots.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Systemd](../../operations/systemd.md)
- [Troubleshooting](../../operations/troubleshooting.md)
