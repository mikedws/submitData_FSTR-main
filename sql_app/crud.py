from sqlalchemy.orm import Session
from sql_app import models, schemas
import datetime
from fastapi.encoders import jsonable_encoder


def get_user(db: Session, user_id: int):
    """
    Запрос по id.
    :param db: сессия подключения.
    :param user_id: id пользователя.
    :return: возврат модели с фильтром по id.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """
    Запрос пользователя по email.
    :param db: сессия подключения.
    :param email: email пользователя.
    :return: возврат модели с фильтром по email.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):

    """
    Лимит на запросы.
    :param db: сессия подключения.
    :param skip: пропуск по id.
    :param limit: лимит выборки по количеству записей.
    :return:
    """
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Запрос на создание пользователя.
    :param db: сессия подключения.
    :param user: пользователь.
    :return: возврат id пользователя.
    """
    db_user = get_user_by_email(db, email=user.email)
    if db_user is None:
        db_users = models.User(**user.dict())
        db.add(db_users)
        db.commit()
        db.refresh(db_users)
        return db_users.id
    else:
        db_users = db_user
        return db_users.id


def create_coord(db: Session, coord: schemas.CoordCreate) -> int:
    """
    Запрос на создание координат.
    :param db: сессия подключения.
    :param coord: схема.
    :return: Возврат id координат.
    """
    db_coord = models.Coord(**coord.dict())
    db.add(db_coord)
    db.commit()
    db.refresh(db_coord)
    return db_coord.id


def create_pass(db: Session, item: schemas.PassCreate) -> object:
    """
    Запрос на создание перевала.
    :param db: сессия подключения.
    :param item: схема.
    :return: возврат id перевала.
    """
    db_pass = models.Pass(
        beautyTitle=item.beautyTitle,
        title=item.title,
        other_titles=item.other_titles,
        connect=item.connect,
        add_time=item.add_time,
        user=item.user,
        coords=item.coords,
        winter=item.winter,
        summer=item.summer,
        autumn=item.autumn,
        spring=item.spring,
    )

    db_pass.status = 'new'
    db_pass.date_added = datetime.datetime.now()

    db.add(db_pass)
    db.commit()
    db.refresh(db_pass)

    return db_pass.id


def search_pass(db: Session, new_pass: int, image: schemas.ImageCreate):
    """
    Запрос на поиск перевала и создание запроса на добавление картинок.
    :param db: сессия подключения.
    :param new_pass: id перевала.
    :param image: схема.
    :return:
    """
    for i in image:
        db_image = models.Image(**i.dict())
        db_image.id_pass = new_pass
        db.add(db_image)

    db.commit()


def get_pass(db: Session, id: int) -> dict:
    """
    Запрос на получение информации о перевале по id.
    :param db: сессия подключения.
    :param id: id пользователя.
    :return:
    """
    c_pass = db.query(models.Pass).filter(models.Pass.id == id).first()
    if c_pass is None:
        return None
    else:
        user = db.query(models.User).filter(models.User.id == c_pass.user).first()
        coords = db.query(models.Coord).filter(models.Coord.id == c_pass.coords).first()
        image = db.query(models.Image).filter(models.Image.id_pass == id).all()

        json_user = jsonable_encoder(user)
        json_coords = jsonable_encoder(coords)
        json_images = jsonable_encoder(image)
        dict_pass = jsonable_encoder(c_pass)

        dict_pass['user'] = json_user
        dict_pass['coords'] = json_coords
        dict_pass['images'] = json_images

        return dict_pass


def search_all(db: Session, email: str):
    """
    Поиск всех перевалов по email.
    :param db: сессия подключения.
    :param email: email пользователя.
    :return: список перевалов.
    """
    user_pass = get_user_by_email(db, email)
    if user_pass is None:
        return None
    else:
        q_pass = db.query(models.Pass).filter(models.Pass.user == user_pass.id).all()

        list_pass = jsonable_encoder(q_pass)
        json_user = jsonable_encoder(user_pass)

        index = -1
        for i in q_pass:
            index += 1

            json_coords = jsonable_encoder(db.query(models.Coord).filter(models.Coord.id == i.coords).first())
            json_images = jsonable_encoder(db.query(models.Image).filter(models.Image.id_pass == i.id).all())

            list_pass[index]['user'] = json_user
            list_pass[index]['coords'] = json_coords
            list_pass[index]['images'] = json_images

        return list_pass


def update_pass(pass_id: int, db: Session, item: schemas.PassAddedUpdate) -> object:
    """
    Запрос на обновление перевала.
    :param pass_id: id перевала.
    :param db: сессия подключения.
    :param item: схема.
    :return:
    """
    db_pass = db.query(models.Pass).filter(models.Pass.id == pass_id).first()

    db_pass.beauty_title = item.beauty_title
    db_pass.title = item.title
    db_pass.other_titles = item.other_titles
    db_pass.connect = item.connect
    db_pass.winter = item.winter
    db_pass.summer = item.summer
    db_pass.autumn = item.autumn
    db_pass.spring = item.spring

    if not db_pass.coords is None:
        db_coords = db.query(models.Coord).filter(models.Coord.id == db_pass.coords).first()

        db_coords.latitude = item.coords.latitude
        db_coords.longitude = item.coords.longitude
        db_coords.height = item.coords.height

        db.add(db_coords)
        db.commit()
        db.refresh(db_coords)
    else:
        db_coords = create_coord(db, item.coords)
        db_pass.coords_id = db_coords

    for img in item.images:
        id_img = img.id
        db_image = models.Image(**img.dict())

        db_amg = db.query(models.Image).filter(models.Image.id == id_img).first()

        db.is_modified(db_amg)
        db_amg.image_url = db_image.image_url
        db_amg.title = db_image.title
        db.is_modified(db_amg)

    db.add(db_pass)
    db.commit()
    db.refresh(db_pass)

    return db_pass.id
