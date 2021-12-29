# ddns4regru
ddns на домене от reg.ru
## Установка и настройка
###### Склонируйте репозиторий в нужную папку
```bash
cd /usr/bin/
git clone https://github.com/dANkTild/ddns4regru
cd ddns4regru
```
###### Установите зависимости
```bash
sudo pip install -r requirements.txt
```
###### Создайте файл *"domains.txt"* в папке скрипта
Структура файла состоит из блоков, отделенных пустой строкой. В каждом блоке первая строка - имя домена, остальные несколько - поддомены.
[![File](https://i.ibb.co/4PY11cp/image.png "File")](https://ibb.co/hDZYYkV "File")

## Подготовка к запуску
###### Разрешите доступ к API вашему диапазону ip-адресов
[https://www.reg.ru/user/account/#/settings/api/](https://www.reg.ru/user/account/#/settings/api/)
[![Add ip](https://i.ibb.co/r5HgnwQ/image.png "Add ip")](https://i.ibb.co/r5HgnwQ/image.png "Add ip")

## Добавление в автозагрузку
###### Создайте файл *"/etc/systemd/system/ddns4regru.service"*
    [Unit]
    Description=DDNS4REGRU
    After=network.target

    [Service]
    Type=simple
    WorkingDirectory=/usr/bin/ddns4regru

    ExecStart=python3 ddns_updater.py <ЛОГИН> <ПАРОЛЬ>
    Restart=always

    [Install]
    WantedBy=multi-user.target

###### Запустите
```bash
sudo systemctl enable ddns4regru
sudo systemctl start ddns4regru
```
