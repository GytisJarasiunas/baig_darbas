import re

from PyQt5 import uic, QtWidgets
from datetime import date
from prid_marke import MarkModelIrasas
from PyQt5.QtGui import QValidator
from sqlalchemy.orm import sessionmaker

from models import engine, Priekaba

#tikrinam numeri
class ValsybNum(QValidator):
    def validate(self, string, index):
        pattern = re.compile(r"^[A-Za-z0-9]+")

        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index

class PriekabaIrasas(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi("priek_irasas.ui", self)
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
            self.msg.setText("Neįrašėte kažkurio lauko! arba irašėte neteisingai")
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
        self.msg.setText("Įrašas pridėtas")
        #issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.val_nr.clear()
        self.pavadinimas.clear()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = PriekabaIrasas()
    app.exec()

