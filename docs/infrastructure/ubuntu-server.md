# Ubuntu Server

Procedimentos basicos de operacao do servidor que executa os pipelines.

```bash
timedatectl
uptime
htop
df -h
du -sh pipelines/data pipelines/logs pipelines/checkpoints
```

O servidor deve manter o fuso horario esperado pelos timers Systemd e espaco suficiente para snapshots, logs e checkpoints.
