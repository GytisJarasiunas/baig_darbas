from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Date, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os
#sukurta Database
Base = declarative_base()
engine = create_engine('sqlite:///duomenu_baze.db')

class MarkeModelis(Base):
    __tablename__ = "marke_modelis"
    id = Column(Integer, primary_key=True)
    marke = Column("Markė", String)
    modelis = Column("Modelis", String)

#DB saugoti ivairius transporto priemoniu parametrus(T.A), keliu mokestis ir pns
#turi relationshipus su keliomis lentelemis(one to many

class TransportoPriemone(Base):
    __tablename__ = "transportas"
    id = Column(Integer, primary_key=True)
    valstyb_nr = Column("Valstybinis numeris", String, nullable=False)
    tech = Column("Techninė apžiura(iki)", Date)
    pagam_data = Column('Pagaminimo data', Date)
    keliu_mokestis = Column("Kelių mokestis(iki)", Date)
    marke = Column(Integer,ForeignKey("marke_modelis.id"))
    priekaba_id = Column(Integer, ForeignKey("priekaba.id"))

    def __repr__(self):
        return f"{self.id}: {self.valstyb_nr} {self.tech}, {self.keliu_mokestis}, {self.pagam_data}"

class Priekaba(Base):
    __tablename__ = "priekaba"
    id = Column(Integer, primary_key=True)
    pavadinimas = Column("pavadinimas", String, nullable=False)
    valstyb_nr = Column("valstybinis_numeris", String)
    pagam_metai = Column("pagaminimo-metai", Date)
    tech = Column("technikinė_apžiura(iki)", Date)

    def __repr__(self):
        return f"{self.id}: {self.pavadinimas}, {self.valstyb_nr}, {self.pagam_metai}, {self.tech}"

class Vairuotojas(Base):
    __tablename__ = "vairuotojas"
    id = Column(Integer, primary_key=True)
    vardas = Column("vardas", String)
    pavarde = Column("pavarde", String)
    telef_nr = Column("tel.nr", Integer)
    transp_priemon = Column(Integer, ForeignKey('transportas.id'))

    def __repr__(self):
        return (f"Vairuotojas ID:{self.id} Vardas: {self.vardas} Pavardė: {self.pavarde}")


class KurasIrasas(Base):
    __tablename__= "kuro_duomenys"
    id = Column(Integer, primary_key=True)
    data = Column("data", Date)
    kilometrazas = Column("kilometrazas", Integer)
    kiekis = Column("kiekis", Float)
    kaina = Column("kaina", Float)
    tp_id = Column(Integer, ForeignKey("transportas.id"))


Base.metadata.create_all(engine, checkfirst=True)

