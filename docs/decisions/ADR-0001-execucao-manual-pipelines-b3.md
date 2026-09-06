# ADR-0001: Execucao sob demanda dos pipelines B3

- Status: Aceita
- Escopo: `b3_enriquecimento_cadastral_ativos` e `b3_indices_segmentos_setoriais`

## Contexto

Os dois pipelines B3 podem ser executados em momentos variaveis e nao possuem uma janela recorrente definida.

## Decisao

A execucao oficial sera manual e sob demanda pelo respectivo `stage/pipeline.py`. Docker Compose e `docker run` permanecem como alternativas de isolamento, mas nao existe timer Systemd ativo para esses pipelines.

## Consequencias

A operacao nao depende de timers B3. Cada execucao deve ser registrada por logs, checkpoints e identificador de snapshot. Uma futura necessidade de recorrencia deve alterar esta decisao e a agenda centralizada.
