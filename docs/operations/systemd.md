# Systemd

Guia operacional dos timers e services dos pipelines agendados.

| Pipeline | Timer | Frequencia |
|---|---|---|
| CVM ITR | `kairos-trap-cvm-itr.timer` | Diaria, 08:30 |
| CVM DFP | `kairos-trap-cvm-dfp.timer` | Diaria, 08:00 |
| CVM CAD | `kairos-trap-cvm-cad.timer` | Diaria, 09:10 |
| CVM FRE | `kairos-trap-cvm-fre.timer` | Diaria, 19:00 |
| B3 CAD | — | Manual |
| B3 indices | — | Manual |

## Consultar

```bash
systemctl list-timers --all | grep kairos-trap-
systemctl status <nome>.timer
journalctl -u <nome>.service -n 200 --no-pager
```

## Operar timer

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now <nome>.timer
sudo systemctl restart <nome>.timer
sudo systemctl start <nome>.service
```

Timers de execucao unica ou descontinuados devem ser desabilitados com `sudo systemctl disable --now <nome>.timer`.

## Adicionar novo timer

Modelo universal para criar service + timer de um novo pipeline. Substitua `<nome-pipeline>` (ex.: `cvm-itr`), `<Descricao>` (ex.: `CVM ITR`), `<servico-docker-compose>` (nome do serviço no `docker-compose.yml`) e `<HH:MM:SS>` pelo horario desejado.

### 1. Criar service

```bash
sudo tee /etc/systemd/system/kairos-trap-<nome-pipeline>.service > /dev/null <<'EOF'
[Unit]
Description=Kairos Trap - <Descricao>
Wants=network-online.target
After=network-online.target docker.service
Requires=docker.service

[Service]
Type=oneshot
User=rian
WorkingDirectory=/home/rian/kairos-trap/docker
ExecStart=/usr/bin/docker compose -f /home/rian/kairos-trap/docker/docker-compose.yml run --rm <servico-docker-compose>
EOF
```

### 2. Criar timer

```bash
sudo tee /etc/systemd/system/kairos-trap-<nome-pipeline>.timer > /dev/null <<'EOF'
[Unit]
Description=Timer - <Descricao>

[Timer]
OnCalendar=*-*-* <HH:MM:SS>
Persistent=true
Unit=kairos-trap-<nome-pipeline>.service

[Install]
WantedBy=timers.target
EOF
```

### 3. Ativar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kairos-trap-<nome-pipeline>.timer
```

### 4. Verificar

```bash
systemctl status kairos-trap-<nome-pipeline>.timer
systemctl list-timers --all | grep kairos-trap-<nome-pipeline>
journalctl -u kairos-trap-<nome-pipeline>.service -n 200 --no-pager
```

Depois de validar, adicione a nova entrada na tabela no topo deste documento.
