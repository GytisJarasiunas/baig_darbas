import re
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy.orm import sessionmaker
from models import TransportoPriemone, engine, Vairuotojas

#sukurtas validatorius kad patikrintu ka dedame ivestyje, kad nerasytu visokiu raidziu ar zenklu
class NumOnly(QValidator):
    def validate(self, string, index):
        #regex pattern pagal kuri tikrina
        pattern = re.compile("[0-9]+")

        #tikrina ar atitinka regex paterna
        if string == "":
            #nustato state
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index
#tikrintojas kad leistu rašyt tik raides
class LettersOnly(QValidator):
    def validate(self, string, index):
        pattern = re.compile("[A-Za-z]+")

        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index


#sukuriama lango klase, kuri uzkrauna ui faila, panaudoja validatoriu eilutems
class VairuotojoIrasas(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("vairuotojas_irasas.ui", self)
        self.tel_nr.setValidator(NumOnly())
        self.vardas.setValidator(LettersOnly())
        self.pavarde.setValidator(LettersOnly())
        self.issaugot.clicked.connect(self.validate_record)
        #iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data()
        self.show()


    #funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.tel_nr.text() == "" or self.vardas.text() == "" or self.pavarde.text() == "":
            self.msg.setText("Neįrašėte kažkurio lauko!")
            return

        self.vairuotojas_save()

    #funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def vairuotojas_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = (self.tp_pasirinkimas.currentIndex()) + 1
        tel_num = int(self.tel_nr.text())
        vardas = self.vardas.text()
        pavarde = self.pavarde.text()
        vairuotojas = Vairuotojas(vardas=vardas, pavarde=pavarde, telef_nr=tel_num,  transp_priemon=sunk)
        session.add(vairuotojas)
        session.commit()
        #paraso i  mgbox jog viskas pavyko sekmingai
        self.msg.setText("Įrašas pridėtas")
        #issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.vardas.clear()
        self.pavarde.clear()
        self.tel_nr.clear()

    #Funkcija kuri prideda pasirinkimus i dropdown menu
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        for x in tr_priemones:
            self.tp_pasirinkimas.addItem(f'{x.id}. {x.valstyb_nr}')

class VairuotojasEdit(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        uic.loadUi("vairuotojas_irasas.ui", self)
        self.tel_nr.setValidator(NumOnly())
        self.vardas.setValidator(LettersOnly())
        self.pavarde.setValidator(LettersOnly())
        self.setWindowTitle("Vairuotojo įrašo redagavimas")

        self.issaugot.clicked.connect(self.validate_record)
        #iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data()
        self.show()


    #funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.tel_nr.text() == "" or self.vardas.text() == "" or self.pavarde.text() == "":
            self.msg.setText("Neįrašėte kažkurio lauko!")
            return

        self.vairuotojas_save()

    #funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def vairuotojas_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = (self.tp_pasirinkimas.currentIndex()) + 1
        tel_num = int(self.tel_nr.text())
        vardas = self.vardas.text()
        pavarde = self.pavarde.text()
        vair_id = session.query(select(Vairuotojas.id).where(Vairuotojas.transp_priemon == self.select))
        vairuotojas = session.get(Vairuotojas, vair_id)
        vairuotojas.vardas = vardas
        vairuotojas.pavarde = pavarde
        vairuotojas.transp_priemon = sunk
        vairuotojas.telef_nr = tel_num
        session.add(vairuotojas)
        session.commit()
        #paraso i  mgbox jog viskas pavyko sekmingai
        self.msg.setText("Įrašas atnaujintas")

    #Funkcija kuri prideda pasirinkimus i dropdown menu
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        for x in tr_priemones:
            self.tp_pasirinkimas.addItem(f'{x.id}. {x.valstyb_nr}')
        try:
            self.vardas.setText(session.query(Vairuotojas.vardas).where(Vairuotojas.transp_priemon == self.select)
                                    .first()[0])
            self.pavarde.setText(session.query(Vairuotojas.pavarde).where(Vairuotojas.transp_priemon == self.select)
                                .first()[0])
            self.tel_nr.setText(str(session.query(Vairuotojas.telef_nr).where(Vairuotojas.transp_priemon == self.select)
                                .first()[0]))
            self.vardas.setText(session.query(Vairuotojas.vardas).where(Vairuotojas.transp_priemon == self.select)
                                .first()[0])
            self.tp_pasirinkimas.setCurrentIndex(session.query(Vairuotojas.transp_priemon)
                                               .where(Vairuotojas.transp_priemon == self.select).first()[0])
        except TypeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Klaida")
            msg.setInformativeText('Šiai T.P. nėra priskirtas vairuotojas! ')
            msg.setWindowTitle("Klaida")
            msg.exec_()
            self.vardas.setReadOnly(True)
            self.pavarde.setReadOnly(True)
            self.tel_nr.setReadOnly(True)
            self.msg.setText("Pirmiausia priskirk TP!")




#jei kodas leidziamas tiesiogiai ivykdo kas yra po if, jei ne tai to nevykdo.
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = VairuotojasEdit(3)
    app.exec()