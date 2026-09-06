# CVM Informacoes Trimestrais

## Objetivo

Extrair e transformar informacoes financeiras trimestrais da CVM.

## Status e execucao

- Status: `active`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/cvm_formulario_informacoes_trimestrais/stage/pipeline.py`
- Agendamento: diario, 08:30, via `kairos-trap-cvm-itr.timer`.

## Stages

`extract` -> `to_interim` -> `to_processed` -> `compare` -> `retention`.

## Dados

Consulte [data-catalog.md](data-catalog.md) para demonstracoes, campos e granularidade.

## Validacao

Confira checkpoints, periodos de referencia e comparacoes entre snapshots.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Systemd](../../operations/systemd.md)
- [Troubleshooting](../../operations/troubleshooting.md)
