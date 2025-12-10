need create .env file with data:

```text
ZULIP_EMAIL=<user_email>
ZULIP_API_KEY=<api_key>
ZULIP_SITE=https://<sub_domain>.zulipchat.com
START_WORK_TIME=10 #your_start_work_time
END_WORK_TIME=18 #your_end_work_time
TIMEZONE=Europe/Moscow #or other tz
```

need create statuses.py file with data:

**example**

```python
# список статусов из которых рандомно будет выбираться самый первый статус ежедневно
FIRST_STATUSES = [
    {"text": "Солнце взошло, пора работать", "emoji": "sunrise"},
]

# список остальных статусов
STATUSES = [
    {"text": "Я устал", "emoji": "brain"},
]
```


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
Environment="PYTHONPATH=<full_path_to_folder>"
EnvironmentFile=/<full_path_to_folder>/.env
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

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
