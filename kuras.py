import re
from datetime import date
from transporto_priemone import TPIrasas
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QValidator
from sqlalchemy.orm import sessionmaker
from models import TransportoPriemone, engine, KurasIrasas


# sukurtas validatorius kad patikrintu ka dedame ivestyje, kad nerasytu visokiu raidziu ar zenklu
class NumOnly(QValidator):
    def validate(self, string, index):
        pattern = re.compile("[0-9]+")

        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index


# sukuriama lango klase, kuri uzkrauna ui faila, panaudoja validatoriu eilutems
class KuroIrasas(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("kuro_forma.ui", self)
        self.kuro_kiekis.setValidator(NumOnly())
        self.kilometrazas.setValidator(NumOnly())
        # data jog date selector automatiskai butu sios dienos data o ne 2000-01-01
        self.data.setDate(date.today())
        # mygtuko sujungimas su funkcija
        self.refresh.clicked.connect(self.load_data)
        self.pridet_sunk.clicked.connect(self.mygtukas)
        self.issaugot.clicked.connect(self.validate_record)
        # iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data()
        self.show()

    # funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.kuro_kiekis.text() == "" or self.kilometrazas.text() == "":
            self.msg.setText("Neįrašėte kažkurio lauko!")
            return

        self.kuras_save()

    # funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def kuras_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = (self.sunk_pas.currentIndex()) + 1
        kiek = float(self.kuro_kiekis.text())
        dat = self.data.date().toPyDate()
        kms = int(self.kilometrazas.text())
        kain = self.kaina.value()
        kuras = KurasIrasas(data=dat, kilometrazas=kms, kiekis=kiek, kaina=kain, tp_id=sunk)
        session.add(kuras)
        session.commit()
        self.msg.setText("Įrašas pridėtas")
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.kilometrazas.clear()
        self.kuro_kiekis.clear()

    # Funkcija kuri prideda pasirinkimus i dropdown menu
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        for x in tr_priemones:
            self.sunk_pas.addItem(f'{x.id}.{x.valstyb_nr}')

    def mygtukas(self):
        self.langas = TPIrasas()


class KuroIrasasEdit(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        uic.loadUi("kuro_forma.ui", self)
        self.kuro_kiekis.setValidator(NumOnly())
        self.label.setText("Pasirink kuri iraša redaguoti")
        self.kilometrazas.setValidator(NumOnly())
        self.pridet_sunk.setText("Pridėti nauja įraša")
        # self.kuro_kiekis.setText()
        # data jog date selector automatiskai butu sios dienos data o ne 2000-01-01
        # self.data.setDate()
        # mygtuko sujungimas su funkcija
        self.refresh.setText("jei pakeistas įrašo pasirinkimas spausk čia")
        self.refresh.clicked.connect(self.rerun)
        self.pridet_sunk.clicked.connect(self.mygtukas)
        self.issaugot.clicked.connect(self.validate_record)
        # iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data(self.select)
        self.show()

    def rerun(self):
        self.load_data(self.select)
    # funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.kuro_kiekis.text() == "" or self.kilometrazas.text() == "":
            self.msg.setText("Neįrašėte kažkurio lauko!")
            return

        self.kuras_save()

    # funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def kuras_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = self.sunk_pas.currentText()[:-10]
        kiek = float(self.kuro_kiekis.text())
        dat = self.data.date().toPyDate()
        kms = int(self.kilometrazas.text())
        kain = self.kaina.value()
        kuras = session.get(KurasIrasas, sunk)
        kuras.kiekis = kiek
        kuras.data = dat
        kuras.kilometrazas = kms
        kuras.kaina = kain
        session.add(kuras)
        session.commit()
        self.msg.setText("Įrašas atnaujintas!")

    # Funkcija kuri prideda pasirinkimus i dropdown menu
    def load_data(self, selection):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(KurasIrasas).where(KurasIrasas.tp_id == selection).all()
        tp = session.query(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == selection).first()[0]
        # print(len(tr_priemones))
        self.dabartinis.setText(f'Dabartinis: {tp}')
        if tr_priemones:
            if len(tr_priemones) != len(self.sunk_pas):
                self.sunk_pas.clear()
                for x in tr_priemones:
                    self.sunk_pas.addItem(f'{x.id} {x.data}')
        # print(len(self.sunk_pas))

        if selection and not tr_priemones:
            self.sunk_pas.addItem("Pasirinktam sunkvežimiui nera kuro įrašu.")
            return

        pasirinkimas = self.sunk_pas.currentText()[:-10]

        print(session.query(KurasIrasas.kiekis).where(KurasIrasas.id == pasirinkimas).first())
        self.kuro_kiekis.setText(
            str(session.query(KurasIrasas.kiekis).where(KurasIrasas.id == pasirinkimas).first()[0]))
        self.data.setDate(session.query(KurasIrasas.data).where(KurasIrasas.id == pasirinkimas).first()[0])
        self.kaina.setValue(session.query(KurasIrasas.kaina).where(KurasIrasas.id == pasirinkimas).first()[0])
        self.kilometrazas.setText(
            str(session.query(KurasIrasas.kilometrazas).where(KurasIrasas.id == pasirinkimas).first()[0]))




    def mygtukas(self):
        self.langas = KuroIrasas()


# jei kodas leidziamas tiesiogiai ivykdo kas yra po if, jei ne tai to nevykdo.
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = KuroIrasasEdit(1)
    app.exec()
