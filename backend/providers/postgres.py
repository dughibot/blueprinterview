from typing import List, Dict
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Screener(db.Model):
    __tablename__ = "screener"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    disorder: Mapped[str] = mapped_column(String())
    full_name: Mapped[str] = mapped_column(String())
    display_name: Mapped[str] = mapped_column(String())

    sections: Mapped[List["ScreenerSection"]] = relationship()

    questions: Mapped[Dict[str, "Question"]] = relationship(
        collection_class=attribute_keyed_dict("id")
    )


class ScreenerSection(db.Model):
    __tablename__ = "screener_section"
    id: Mapped[str] = mapped_column(primary_key=True)
    type = mapped_column(ForeignKey())
    title: Mapped[str] = mapped_column(String())

    answers: Mapped[List["AnswerOption"]] = relationship()
    questions: Mapped[List["Question"]] = relationship()


class AnswerOption(db.Model):
    __tablename__ = "answer_option"
    title: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(Integer())
    screener_section_id = mapped_column(ForeignKey("screener_section.id"))


class Domain(db.Model):
    __tablename__ = "domain"
    name: Mapped[str] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"Domain(name={self.name})"


class Question(db.Model):
    __tablename__ = "question"

    id: Mapped[str] = mapped_column(primary_key=True)
    domain = mapped_column(ForeignKey("domain.name"))
    title = Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return f'Question(id={self.id}, domain={self.domain}, text="{self.text}")'
