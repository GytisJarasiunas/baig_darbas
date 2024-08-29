from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Date, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///duomenu_baze.db')


class MarkeModelis(Base):
    __tablename__ = "marke_modelis"
    id = Column(Integer, primary_key=True)
    marke = Column(String)
    modelis = Column(String)


# DB saugoti ivairius transporto priemoniu parametrus(T.A), keliu mokestis ir pns

class TransportoPriemone(Base):
    __tablename__ = "transportas"
    id = Column(Integer, primary_key=True)
    valstyb_nr = Column(String, nullable=False)
    tech = Column(Date)
    pagam_data = Column(Date)
    keliu_mokestis = Column(Date)
    marke = Column(Integer, ForeignKey("marke_modelis.id"))
    priekaba_id = Column(Integer, ForeignKey("priekaba.id"))

    def __repr__(self):
        return f"{self.id}: {self.valstyb_nr} {self.tech}, {self.keliu_mokestis}, {self.pagam_data}"


class Priekaba(Base):
    __tablename__ = "priekaba"
    id = Column(Integer, primary_key=True)
    pavadinimas = Column(String, nullable=False)
    valstyb_nr = Column(String)
    pagam_metai = Column(Date)
    tech = Column(Date)

    def __repr__(self):
        return f"{self.id}: {self.pavadinimas}, {self.valstyb_nr}, {self.pagam_metai}, {self.tech}"


class Vairuotojas(Base):
    __tablename__ = "vairuotojas"
    id = Column(Integer, primary_key=True)
    vardas = Column(String)
    pavarde = Column(String)
    telef_nr = Column(Integer)
    transp_priemon = Column(Integer, ForeignKey('transportas.id'))

    def __repr__(self):
        return (f"Vairuotojas ID:{self.id} Vardas: {self.vardas} Pavardė: {self.pavarde}")


class KurasIrasas(Base):
    __tablename__ = "kuro_duomenys"
    id = Column(Integer, primary_key=True)
    data = Column(Date)
    kilometrazas = Column(Integer)
    kiekis = Column(Float)
    kaina = Column(Float)
    tp_id = Column(Integer, ForeignKey("transportas.id"))


Base.metadata.create_all(engine, checkfirst=True)
