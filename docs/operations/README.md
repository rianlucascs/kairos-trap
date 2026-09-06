# Operacoes

Documentacao transversal para executar, agendar e diagnosticar pipelines.

- [Docker](docker.md): build, Compose, `docker run` e volumes.
- [Systemd](systemd.md): timers ativos e operacao dos services.
- [Troubleshooting](troubleshooting.md): verificacoes comuns e recuperacao.
- [Agenda estruturada](../pipelines/pipeline_execution_schedule.json): fonte de verdade para frequencia e status.

O metodo de execucao oficial de cada pipeline deve ser confirmado no README do proprio pipeline. Pipelines B3 sao executados sob demanda via `stage/pipeline.py`; Compose e uma alternativa de isolamento.
