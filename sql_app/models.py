from sql_app.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
# from datetime import datetime
from sqlalchemy.orm import relationship


class User(Base):
    """
     Клас модели пользователя.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, unique=True)
    fam = Column(String)
    name = Column(String)
    otc = Column(String)
    phone = Column(String, index=True, unique=True)

    pass_add = relationship("Pass", back_populates="users")


class Coord(Base):
    """
     Клас модели географических координат:
     Широта
     Долгота
     Высота
    """
    __tablename__ = "coords"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    height = Column(Integer)
    pass_add = relationship("Pass", back_populates="coord")


class Image(Base):
    """
    Клас модели картинок/фото перевала.
    """
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    title = Column(String)
    id_pass = Column(Integer, ForeignKey("passes.id"))

    # Организация связи таблиц
    owner = relationship("Pass", back_populates="images")

    def __repr__(self):
        return f"id={self.id} image_url={self.image_url} title={self.title} id_pass={self.id_pass}"


class Pass(Base):
    """
     Клас модели перевалов.
    """
    __tablename__ = "passes"

    id = Column(Integer, primary_key=True, index=True)
    beautyTitle = Column(String)
    title = Column(String)
    other_titles = Column(String)
    connect = Column(String)
    add_time = Column(DateTime)
    winter = Column(String)
    summer = Column(String)
    autumn = Column(String)
    spring = Column(String)
    user = Column(Integer, ForeignKey("users.id"))
    coords = Column(Integer, ForeignKey("coords.id"))
    status = Column(String)

    users = relationship("User", back_populates="pass_add")
    coord = relationship("Coord", back_populates="pass_add")
    images = relationship("Image", back_populates="owner")
