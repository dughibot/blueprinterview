from typing import List, Dict
from sqlalchemy import Integer, String, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship, attribute_keyed_dict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from uuid import uuid4


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Screener(Base):
    __tablename__ = "screener"
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String())
    disorder: Mapped[str] = mapped_column(String())
    full_name: Mapped[str] = mapped_column(String())
    display_name: Mapped[str] = mapped_column(String())

    sections: Mapped[List["ScreenerSection"]] = relationship()

    @property
    def questions(self) -> Dict[str, "Question"]:
        if not hasattr(self, "_questions"):
            self._questions = {
                q.id: q for sect in self.sections for q in sect.questions
            }
        return self._questions

    @classmethod
    def from_dict(cls, screener_dict: dict) -> "Screener":
        content = screener_dict.pop("content")
        screener_dict["display_name"] = content.pop("display_name")
        screener = cls(**screener_dict)
        for section in content["sections"]:
            section_id = str(uuid4())
            answers = section.pop("answers")
            questions = section.pop("questions")
            db_section = ScreenerSection(id=section_id, **section)
            for answer in answers:
                db_section.answers.append(AnswerOption(**answer))
            for question in questions:
                db_section.questions.append(
                    Question(id=question["question_id"], title=question["title"])
                )
            screener.sections.append(db_section)
        return screener


section_to_question_table = Table(
    "section_to_question",
    Base.metadata,
    Column("section_id", ForeignKey("screener_section.id"), primary_key=True),
    Column("question_id", ForeignKey("question.id"), primary_key=True),
)


class ScreenerSection(Base):
    __tablename__ = "screener_section"
    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String())
    title: Mapped[str] = mapped_column(String())
    screener_id = mapped_column(ForeignKey("screener.id"))

    answers: Mapped[List["AnswerOption"]] = relationship()
    questions: Mapped[List["Question"]] = relationship(
        secondary=section_to_question_table
    )


class AnswerOption(Base):
    __tablename__ = "answer_option"
    title: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(Integer())
    screener_section_id = mapped_column(ForeignKey("screener_section.id"))


class Domain(Base):
    __tablename__ = "domain"
    name: Mapped[str] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"Domain(name={self.name})"


class Question(Base):
    __tablename__ = "question"

    id: Mapped[str] = mapped_column(primary_key=True)
    domain = mapped_column(ForeignKey("domain.name"))
    title: Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return f'Question(id={self.id}, domain={self.domain}, title="{self.title}")'
