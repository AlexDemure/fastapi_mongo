# FastApi, React, Mongo
Прототип для сервиса со статистикой. <br>

В Данном прототипе реализовано:
- Линейная диаграмма
- Таблицы
- Работа с xlsx-файлами

Линейная диаграмма.
![line_diagram](https://www.fsight.ru/wp-content/uploads/2018/10/2graf.png)

## Развертывание

```sh
https://github.com/AlexDemure/fastapi_mongo
cd fastapi_mongo

cd ./frontend
npm install  # add node_modules

cd ..
docker-compose up -d --build
```
Бекенд адрес
```
localhost:7040 
localhost:7040/docs  # api docs
```
Фронтенд адрес
```
localhost:3000
```
### Работа с MongoDB
#### Скачивание
Для работы с данной БД необходимо установить MongoDB Compass
Ссылка для скачивания: https://www.mongodb.com/try/download/compass

#### Подключение
- Запустите приложение Mongo Compass
- Перейдите во вкладку "New connection"
- В поле ввода введите строку адреса подключения (Как получить строку подключения описано ниже).
![mongodb_compass_connection](https://habrastorage.org/webt/nv/p-/og/nvp-ogdn3bq-tj2e_e2cd-jnmpw.png)
- Нажмите "connect"

#### БД и таблицы
- После успешного подключения появится список для более понятного описания "Базы данных".
Нас интересует dashboards нажимаем на него.
![mongodb_tables](https://habrastorage.org/webt/jx/0l/sw/jx0lsw7r1o7dd_iyhufwcnenrxs.png)
- Далее появится список коллекций данной "БД". Коллекции будем считать как "Таблицы". 
Нас интересует statistics. В данной таблице находятся все записи за все дни со статистикой клиентов.

##### Получение строки адреса подключения
Обязательный шаг: Необходимо развернуть приложение с помощью docker-compose и убедиться что все контейнеры запущены.<br>
В терминале:
```
docker logs statistics
```
В логах будет строка "Connect to MongoDB" необходимо скопировать значение у параметра "uri:".
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:7040 (Press CTRL+C to quit)
Connect to MongoDB: db:dashboards, collection:statistics, uri:mongodb://****:*****@****:27017/
```
```
uri:mongodb://test:testpassword@localhost:27017/
```

### Как загружать данные в MongoDB?
Данные загружаются в MongoDB автоматический при запуске приложения. Данные загружаются только 1 раз за 1 день.
При повторном перезапуске приложения файлы загружены не будут.

#### Загрузка данных в MongoDB за определенный день.
В .env файле в backend папке вы может установить значение в переменную DAYS (числовое значение)
 тем самым будет установлен другой день недели за счет переопределения даты.. 

#### Файлы со статистикой
В backend части лежат два файла со статистикой.<br>
Файлы находятся в директории: backend/src/apps/xlsx/static/

