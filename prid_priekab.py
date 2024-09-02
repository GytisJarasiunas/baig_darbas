import re
from PyQt5 import uic, QtWidgets
from datetime import date
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtGui import QValidator, QIcon
from sqlalchemy.orm import sessionmaker
from models import engine, Priekaba, TransportoPriemone


#tikrinam numeri
class ValsybNum(QValidator):
    def validate(self, string, index):
        pattern = re.compile(r'^[A-Za-z0-9]+')

        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index

class PriekabaIrasas(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('userinterfaces/priek_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.val_nr.setValidator(ValsybNum())
        self.pagam_data.setDate(date.today())
        self.tech.setDate(date.today())
        self.show()
        self.issaugot.clicked.connect(self.validate_record)
    def validate_record(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        priekabos = session.query(Priekaba).all()
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 5:
            self.msg.setText('Neįrašėte kažkurio lauko! arba irašėte neteisingai')
            return
        for irasas in priekabos:
            if self.val_nr.text().upper() == irasas.valstyb_nr:
                self.msg.setText('T.P. tokiu valstyb. nr jau egzistuoja, gal suklydote?')
                return

        self.priekaba_save()


    def priekaba_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        technikine = self.tech.date().toPyDate()
        pdata = self.pagam_data.date().toPyDate()
        vnum = self.val_nr.text().upper()
        pavad = self.pavadinimas.text()
        tpirasas = Priekaba(valstyb_nr=vnum, tech=technikine, pagam_metai=pdata, pavadinimas=pavad)
        print( pavad, technikine, pdata, vnum)
        print(type(pavad), type(technikine), type(pdata), type(vnum))
        session.add(tpirasas)
        session.commit()
        self.msg.setText('Įrašas pridėtas')
        #issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.val_nr.clear()
        self.pavadinimas.clear()


class PriekabaEdit(QtWidgets.QDialog):

    def __init__(self, selection):
        super().__init__()
        self.select = selection
        if int(self.select) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo redaguoti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            return
        uic.loadUi('userinterfaces/priek_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.setWindowTitle('Priekabos įrašo redagavimas')
        self.val_nr.setValidator(ValsybNum())
        self.load_data()
        self.show()
        self.issaugot.clicked.connect(self.validate_record)
    def validate_record(self):
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 5:
            self.msg.setText('Neįrašėte kažkurio lauko! arba irašėte neteisingai')
            return
        self.priekaba_save()

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        #pajamam is tp stulpelio priekabos id
        priekaba_id = session.query(TransportoPriemone.priekaba_id).where(TransportoPriemone.id == self.select).first()[
            0]
        #i pasirinkimu langelius uzkraunam pasirinkto iraso kintamuosius
        try:
            self.val_nr.setText(session.query(Priekaba.valstyb_nr).where(Priekaba.id == priekaba_id)
                            .first()[0])
        except TypeError:
            self.val_nr.setText('xx000')

        try:
            self.pavadinimas.setText(session.query(Priekaba.pavadinimas).where(Priekaba.id == priekaba_id)
                                .first()[0])
        except TypeError:
            self.pavadinimas.setText('DEFAULT')

        try:
            self.pagam_data.setDate(session.query(Priekaba.pagam_metai).where(Priekaba.id == priekaba_id)
                                 .first()[0])
        except TypeError:
            self.pagam_data.setDate('2001-01-01')

        try:
            self.tech.setDate(session.query(Priekaba.tech).where(Priekaba.id == priekaba_id)
                                   .first()[0])
        except TypeError:
            self.tech.setDate('2001-01-01')

    def priekaba_save(self):
        #sukuriam sesija
        Session = sessionmaker(bind=engine)
        session = Session()
        #priskiriam  langeliu reiksmes kintamiesiems
        technikine = self.tech.date().toPyDate()
        pdata = self.pagam_data.date().toPyDate()
        vnum = self.val_nr.text().upper()
        pavad = self.pavadinimas.text()
        # is db getinam iraša ir pakeiciam senus irasus naujais
        priekaba_id = session.query(TransportoPriemone.priekaba_id).where(TransportoPriemone.id == self.select).first()[
            0]
        priekaba = session.get(Priekaba, priekaba_id)
        priekaba.tech = technikine
        priekaba.pagam_metai = pdata
        priekaba.pavadinimas = pavad
        priekaba.valstyb_nr = vnum
        session.add(priekaba)
        session.commit()
        self.msg.setText('Įrašas atnaujintas')

class PriekabaDirectEdit(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        if int(self.select) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo redaguoti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            return
        uic.loadUi('userinterfaces/priek_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.setWindowTitle('Priekabos įrašo redagavimas')
        self.val_nr.setValidator(ValsybNum())
        self.load_data(self.select)
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    def validate_record(self):
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 5:
            self.msg.setText('Neįrašėte kažkurio lauko! arba irašėte neteisingai')
            return
        self.priekaba_save()

    def load_data(self, priekaba_id):
        Session = sessionmaker(bind=engine)
        session = Session()
        #pajamam is tp stulpelio priekabos id
        try:
            self.val_nr.setText(session.query(Priekaba.valstyb_nr).where(Priekaba.id == priekaba_id)
                            .first()[0])
        except TypeError:
            pass

        try:
            self.pavadinimas.setText(session.query(Priekaba.pavadinimas).where(Priekaba.id == priekaba_id)
                                .first()[0])
        except TypeError:
            pass

        try:
            self.pagam_data.setDate(session.query(Priekaba.pagam_metai).where(Priekaba.id == priekaba_id)
                                 .first()[0])
        except TypeError:
            pass

        try:
            self.tech.setDate(session.query(Priekaba.tech).where(Priekaba.id == priekaba_id)
                                   .first()[0])
        except TypeError:
            pass

    def priekaba_save(self):
        #sukuriam sesija
        Session = sessionmaker(bind=engine)
        session = Session()
        #priskiriam  langeliu reiksmes kintamiesiems
        technikine = self.tech.date().toPyDate()
        pdata = self.pagam_data.date().toPyDate()
        vnum = self.val_nr.text().upper()
        pavad = self.pavadinimas.text()
        # is db getinam iraša ir pakeiciam senus irasus naujais
        priekaba = session.get(Priekaba, self.select)
        priekaba.tech = technikine
        priekaba.pagam_metai = pdata
        priekaba.pavadinimas = pavad
        priekaba.valstyb_nr = vnum
        session.add(priekaba)
        session.commit()
        self.msg.setText('Įrašas atnaujintas')

class PriekabaDelete(QtWidgets.QDialog):

    def __init__(self, iraso_id):
        super().__init__()
        self.iraso_id = iraso_id
        if int(self.iraso_id) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo ištrinti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            return
        uic.loadUi('userinterfaces/istrinti.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.atsaukti.clicked.connect(self.close)
        self.istrinti.clicked.connect(self.delete)
        self.show()
        self.load_data()

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        pavadinimas = session.query(Priekaba.pavadinimas).where(Priekaba.id == self.iraso_id).first()[0]
        val_nr = session.query(Priekaba.valstyb_nr).where(Priekaba.id == self.iraso_id).first()[0]
        self.irasas.setText(f'Priekabos irašas:{self.iraso_id}. {pavadinimas} {val_nr} ')

    def delete(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        trinamas = session.get(Priekaba, self.iraso_id)
        trinamas.valstyb_nr = '00000'
        trinamas.pavadinimas = 'irasas istrintas'
        session.add(trinamas)
        session.commit()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = PriekabaDelete(7)
    app.exec()

