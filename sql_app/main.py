from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sql_app import crud, schemas, models
from sql_app.database import SessionLocal, engine
from sql_app.errors import ErrorConnectionServer, get_json_response
from fastapi.encoders import jsonable_encoder
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/submitData/', response_model=schemas.Pass)
def post_pass(item: schemas.PassCreate, db: Session = Depends(get_db)):
    """
    Вызов функции создания записи о перевале, пользователе, координат и информации о фотографиях.
    :param item: Схема создания Перевала.
    :param db: сессия подключения бд.
    :return: ответ в JSON.
    """
    try:  # Проверка на подключение к базе
        db.execute('SELECT * FROM users')
    except Exception as error:
        raise ErrorConnectionServer(f'Ошибка соединения: {error}')

    news_user = crud.create_user(db=db, user=item.user)  # Создание пользователя

    if news_user is None:
        return get_json_response(422, "Ошибка при создании пользователя")
    else:
        new_coords = crud.create_coord(db=db, coord=item.coords)  # Создание координат

    if new_coords is None:
        return get_json_response(422, "Ошибка при создании координат")
    else:
        item.user = news_user
        item.coords = new_coords

        new_pass = crud.create_pass(db=db, item=item)  # Создание перевала

        if new_pass is None:
            return get_json_response(422, "Ошибка при создании перевала")
        else:
            crud.search_pass(db=db, new_pass=new_pass, image=item.images)

            return get_json_response(200, "Перевал создан", new_pass)


@app.get('/submitData/{id}', response_model=schemas.PassCreate)
def search_pass(id: int, db: Session = Depends(get_db)):
    """
    Запрос на получение информации о перевале по id.
    :param id: id перевала.
    :param db: сессия подключения бд.
    :return: ответ в формате JSON.
    """
    item = crud.get_pass(db=db, id=id)
    if item is None:
        return get_json_response(422, f'Перевал с id {id} отсутствует')
    else:
        return get_json_response(200, 'Объект получен', jsonable_encoder(item))


@app.get('/submitDate/{email}', response_model=List[schemas.PassBase])
def read_pass(email: str, db: Session = Depends(get_db)):
    """
    Запрос о перевалах созданных пользователем с фильтром по email.
    :param email: email пользователя.
    :param db: сессия подключения.
    :return: сообщение в JSON.
    """
    pass_all = crud.search_all(db=db, email=email)
    if pass_all is None:
        return get_json_response(422, "По этому email записей не найдено")
    else:
        return pass_all


@app.patch("/submitData/{id}", response_model=schemas.PassCreate, response_model_exclude_none=True)
def patch_submit_data_id(id: int, item: schemas.PassAddedUpdate, db: Session = Depends(get_db)):
    """
    Вызов функции получения информации о перевале.
    :param id: Параметр id записи перевала.
    :param item: класс схемы.
    :param db: сессия подключения дб.
    :return: сообщение в JSON.
    """
    # pending — если модератор взял в работу;
    # accepted — модерация прошла успешно;
    # rejected — модерация прошла, информация не принята.

    statuses = [
        'pending',
        'accepted',
        'rejected',
    ]

    db_pass_info = crud.get_pass(db, id)

    if db_pass_info is None:
        return get_json_response(422, f'Перевал с id {id} отсутствует', {"state": 0})

    if db_pass_info['status'] in statuses:
        return get_json_response(422, f'Перевал с id {id} на модерации', {"state": 0})
    else:
        crud.update_pass(id, db, item)
        return get_json_response(200, 'Запись обновлена', {"state": 1})
