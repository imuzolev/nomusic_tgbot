# DEPLOY.md — вход, обновление `bot.py`, проверка статуса

## 1) Вход на сервер (Windows PowerShell)

```powershell
ssh root@2.56.240.119

zwaHQ1*xv7YJ
```

## 2) Перезаписать `bot.py` с Windows (залить новый файл на сервер)

В папке проекта на Windows (`C:\bot`):

```powershell
scp .\bot.py root@2.56.240.119:/root/bot/bot.py
```

## 3) Проверка/перезапуск/логи на сервере

### Проверить, что файл на месте

```bash
ls -la /root/bot/bot.py
stat /root/bot/bot.py
```

### Проверить синтаксис (чтобы не “уронить” сервис)

```bash
/root/bot/venv/bin/python -m py_compile /root/bot/bot.py
```

### Перезапустить сервис

```bash
systemctl restart telegram-bot.service
```

### Проверить статус

```bash
systemctl status telegram-bot.service --no-pager
```

### Посмотреть логи

```bash
journalctl -u telegram-bot.service -n 200 --no-pager
journalctl -u telegram-bot.service -f
```

