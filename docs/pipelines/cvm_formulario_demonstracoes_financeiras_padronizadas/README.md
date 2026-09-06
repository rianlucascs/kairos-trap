# CVM Demonstracoes Financeiras Padronizadas

## Objetivo

Extrair e transformar demonstracoes financeiras padronizadas da CVM.

## Status e execucao

- Status: `active`
- Comando: `.venv/bin/python pipelines/scripts/pipelines/cvm_formulario_demonstracoes_financeiras_padronizadas/stage/pipeline.py`
- Agendamento: diario, 08:00, via `kairos-trap-cvm-dfp.timer`.

## Stages

`extract` -> `to_interim` -> `to_processed` -> `compare` -> `retention`.

## Dados

Consulte [data-catalog.md](data-catalog.md) para as demonstracoes, campos e tipos.

## Validacao

Confira checkpoints de extracao, transformacao e comparacao antes de publicar os dados.

## Operacao relacionada

- [Docker](../../operations/docker.md)
- [Systemd](../../operations/systemd.md)
- [Troubleshooting](../../operations/troubleshooting.md)
