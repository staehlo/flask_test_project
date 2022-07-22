"""
Generation of classes to map the tables in the database.

This script produces an object-relational mapping class for each of the tables
in the database.
The code was produced with sqlacodegen.
see: https://pypi.org/project/sqlacodegen/
[bash or cmd]>sqlacodegen --outfile models.py sqlite:///data.db
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Company(Base):
    __tablename__ = 'Company'

    name = Column(String, primary_key=True)


class Developer(Base):
    __tablename__ = 'Developer'

    name = Column(String, primary_key=True)


class Language(Base):
    __tablename__ = 'Language'

    lang_id = Column(String, primary_key=True)
    name = Column(String)
    year = Column(Integer, nullable=False)


class Affiliation(Base):
    __tablename__ = 'Affiliation'

    affi_id = Column(Integer, primary_key=True)
    lang_id = Column(ForeignKey('Language.lang_id'))
    company = Column(ForeignKey('Company.name'))

    Company = relationship('Company')
    lang = relationship('Language')


class Succession(Base):
    __tablename__ = 'Succession'

    succ_id = Column(Integer, primary_key=True)
    predecessor = Column(ForeignKey('Language.lang_id'))
    successor = Column(ForeignKey('Language.lang_id'))

    Language = relationship('Language', primaryjoin='Succession.predecessor == Language.lang_id')
    Language1 = relationship('Language', primaryjoin='Succession.successor == Language.lang_id')


class Team(Base):
    __tablename__ = 'Team'

    team_id = Column(Integer, primary_key=True)
    lang_id = Column(ForeignKey('Language.lang_id'))
    developer = Column(ForeignKey('Developer.name'))

    Developer = relationship('Developer')
    lang = relationship('Language')
