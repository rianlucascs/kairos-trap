# Troubleshooting

## Pipeline nao inicia

1. Confirme o nome do pipeline e o ambiente.
2. Verifique o log em `pipelines/logs/<pipeline>`.
3. Consulte o checkpoint em `pipelines/checkpoints/<pipeline>`.
4. Execute novamente com um `run_id` novo.

## Compose

```bash
docker compose -f docker/docker-compose.yml config
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs <servico-compose>
```

## Systemd

```bash
systemctl status <nome>.service
journalctl -u <nome>.service -n 200 --no-pager
systemctl list-timers --all | grep kairos-trap-
```

## Dados intermediarios

Confira os arquivos em `pipelines/data/<pipeline>/<snapshot>/transform/to_interim/` e compare o checkpoint do stage com o schema esperado no `data-catalog.md` do pipeline.
