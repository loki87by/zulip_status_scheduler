```bash
.venv/bin/pip install zulip python-dotenv requests # in project folder
sudo nano /etc/systemd/system/zulip-status.service
```

content:
```text
[Unit]
Description=Zulip Status Scheduler
After=network.target

[Service]
Type=simple
User=<userName>
WorkingDirectory=/<full_path_to_folder>
ExecStart=/<full_path_to_folder>/.venv/bin/python main.py daemon
EnvironmentFile=/<full_path_to_folder>/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable zulip-status.service
sudo systemctl start zulip-status.service
sudo systemctl status zulip-status.service
# проверка логов
sudo journalctl -u zulip-status.service -f
```