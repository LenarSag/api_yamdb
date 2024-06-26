# api_yamdb

## Содержание

- [Описание](#описание)
- [Технологии](#технологии)
- [Как запустить проект](#как-запустить-проект)
- [Ресурсы API YaMDb](#ресурсы-api-yamdb)
- [Пользовательские роли и права доступа](#пользовательские-роли-и-права-доступа)
- [Примеры запросов](#примеры-запросов)
- [Команда проекта](#команда-проекта)

### Описание:

Проект YaMDb собирает отзывы пользователей на произведения.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен жанр из списка предустановленных. Новые жанры может создавать только администратор.

Документация доступна локально на localhost/redoc/

### Технологии:

- python3.10
- Django
- Django REST framework

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/vvvolokitin/api_yamdb
```

```
cd API_YAMBD
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
для Windows:
venv\Scripts\activate.bat 

для Linux и MacOS:
source venv/bin/activate 
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
### Ресурсы API YaMDb:

- Ресурс auth: аутентификация.
- Ресурс users: пользователи.
- Ресурс titles: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
- Ресурс categories: категории (типы) произведений («Фильмы», «Книги», «Музыка»). Одно произведение может быть привязано только к одной категории.
- Ресурс genres: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс reviews: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс comments: комментарии к отзывам. Комментарий привязан к определённому отзыву.

### Пользовательские роли и права доступа:

- Аноним — может просматривать описания произведений, читать отзывы и комментарии.
- Аутентифицированный пользователь (user) — может читать всё, как и Аноним, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
- Модератор (moderator) — те же права, что и у Аутентифицированного пользователя, плюс право удалять и редактировать любые отзывы и комментарии.
Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
- Суперпользователь Django должен всегда обладать правами администратора, пользователя с правами admin. Даже если изменить пользовательскую роль суперпользователя — это не лишит его прав администратора. Суперпользователь — всегда администратор, но администратор — не обязательно суперпользователь.

### Примеры запросов:

Получение списка всех категорий
```
Запрос:

GET http://127.0.0.1:8000/api/v1/categories/

Ответ:

{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "^-$"
    }
  ]
}
```

Получить список всех объектов. Права доступа: Доступно без токена
```
Запрос:

GET http://127.0.0.1:8000/api/v1/titles/

Ответ:

{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "^-$"
        }
      ],
      "category": {
        "name": "string",
        "slug": "^-$"
      }
    }
  ]
}
```

Добавить новый отзыв. Пользователь может оставить только один отзыв на произведение. Права доступа: Аутентифицированные пользователи.
```
Запрос:

GET http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/

Ответ:

{
  "text": "string",
  "score": 1
}
```

### Команда проекта:

- [Волокитин Никита](https://github.com/vvvolokitin) — team leader/backend developer
- [Сагындыков Ленар](https://github.com/LenarSag) — backend developer
- [Фоминых Андрей](https://github.com/AndreyFominykh) — backend developer
