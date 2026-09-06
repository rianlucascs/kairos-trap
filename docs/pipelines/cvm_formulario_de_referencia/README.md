# CVM Formulario de Referencia

## Objetivo

Extrair e organizar os dados do Formulario de Referencia da CVM.

## Status e execucao

- Status: `active`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/cvm_formulario_de_referencia/stage/pipeline.py`
- Agendamento: diario, 19:00, via `kairos-trap-cvm-fre.timer`.

## Stages

`extract` -> `to_interim` -> `to_processed` -> `compare` -> `retention`.

## Dados

Consulte [data-catalog.md](data-catalog.md) para identificadores, campos e granularidade.

## Validacao

Confira checkpoints e a comparacao entre snapshots antes de consumir os dados.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Systemd](../../operations/systemd.md)
- [Troubleshooting](../../operations/troubleshooting.md)
