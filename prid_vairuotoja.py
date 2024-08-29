import re
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QValidator, QIcon
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy.orm import sessionmaker
from models import TransportoPriemone, engine, Vairuotojas

#sukurtas validatorius kad patikrintu ka dedame ivestyje, kad nerasytu visokiu raidziu ar zenklu
class NumOnly(QValidator):
    def validate(self, string, index):
        #regex pattern pagal kuri tikrina
        pattern = re.compile('[0-9]+')

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
        pattern = re.compile('[A-Za-zĄ-Žą-ž]+')

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
        uic.loadUi('userinterfaces/vairuotojas_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
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
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.vairuotojas_save()

    #funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def vairuotojas_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = self.tp_pasirinkimas.currentIndex()
        tel_num = int(self.tel_nr.text())
        vardas = self.vardas.text()
        pavarde = self.pavarde.text()
        vairuotojas = Vairuotojas(vardas=vardas, pavarde=pavarde, telef_nr=tel_num,  transp_priemon=sunk)
        session.add(vairuotojas)
        session.commit()
        #paraso i  mgbox jog viskas pavyko sekmingai
        self.msg.setText('Įrašas pridėtas')
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


# noinspection PyTypeChecker
class VairuotojasEdit(QtWidgets.QDialog):
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
        uic.loadUi('userinterfaces/vairuotojas_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.tel_nr.setValidator(NumOnly())
        self.vardas.setValidator(LettersOnly())
        self.pavarde.setValidator(LettersOnly())
        self.setWindowTitle('Vairuotojo įrašo redagavimas')

        self.issaugot.clicked.connect(self.validate_record)
        #iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data()
        self.show()


    #funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.tel_nr.text() == "" or self.vardas.text() == "" or self.pavarde.text() == "":
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.vairuotojas_save()

    #funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def vairuotojas_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        sunk = self.tp_pasirinkimas.currentIndex()
        tel_num = int(self.tel_nr.text())
        vardas = self.vardas.text()
        pavarde = self.pavarde.text()
        vair_id = session.query(Vairuotojas.id).where(Vairuotojas.transp_priemon == self.select).first()[0]
        vairuotojas = session.get(Vairuotojas, vair_id)
        vairuotojas.vardas = vardas
        vairuotojas.pavarde = pavarde
        vairuotojas.transp_priemon = sunk
        vairuotojas.telef_nr = tel_num
        session.add(vairuotojas)
        session.commit()
        #paraso i  mgbox jog viskas pavyko sekmingai
        self.msg.setText('Įrašas atnaujintas')

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
            msg.setInformativeText('Šiai T.P. nėra priskirtas vairuotojas!'
                                   '\nJei šiai t.p. nori priskirti vairuotoja, eik: Visi įrašai> Visi vairuotojo įrašai>'
                                   'Redaguoti.\nArba pridėk nauja vairuotoja ir jam priskirk šia t.p.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            self.vardas.setReadOnly(True)
            self.pavarde.setReadOnly(True)
            self.tel_nr.setReadOnly(True)
            self.msg.setText('Pirmiausia priskirk TP!')


class VairuotojasDirectEdit(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        if int(self.select) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo ištrinti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            return
        uic.loadUi('userinterfaces/vairuotojas_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.tel_nr.setValidator(NumOnly())
        self.vardas.setValidator(LettersOnly())
        self.pavarde.setValidator(LettersOnly())
        self.setWindowTitle('Vairuotojo įrašo redagavimas')
        self.issaugot.clicked.connect(self.validate_record)
        #iskvieciama funkcija kad uzpildytu drop down menu
        self.load_data()
        self.show()


    #funkcija kuri patikrina ar yra suvesti visi laukeliai
    def validate_record(self):
        if self.tel_nr.text() == "" or self.vardas.text() == "" or self.pavarde.text() == "":
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.vairuotojas_save()

    #funkcija kuri paima lenteles duomenis ir juos issaugo i database
    def vairuotojas_save(self):
        if int(self.select) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo redaguoti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
        else:
            Session = sessionmaker(bind=engine)
            session = Session()
            sunk = self.tp_pasirinkimas.currentIndex()
            tel_num = int(self.tel_nr.text())
            vardas = self.vardas.text()
            pavarde = self.pavarde.text()
            vairuotojas = session.get(Vairuotojas, self.select)
            vairuotojas.vardas = vardas
            vairuotojas.pavarde = pavarde
            vairuotojas.transp_priemon = sunk
            vairuotojas.telef_nr = tel_num
            session.add(vairuotojas)
            session.commit()
            #paraso i  mgbox jog viskas pavyko sekmingai
            self.msg.setText('Įrašas atnaujintas')

    #Funkcija kuri prideda pasirinkimus i dropdown menu
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        for x in tr_priemones:
            self.tp_pasirinkimas.addItem(f'{x.id}. {x.valstyb_nr}')
        try:
            self.vardas.setText(session.query(Vairuotojas.vardas).where(Vairuotojas.id == self.select)
                                    .first()[0])
            self.pavarde.setText(session.query(Vairuotojas.pavarde).where(Vairuotojas.id == self.select)
                                .first()[0])
            self.tel_nr.setText(str(session.query(Vairuotojas.telef_nr).where(Vairuotojas.id == self.select)
                                .first()[0]))
            self.vardas.setText(session.query(Vairuotojas.vardas).where(Vairuotojas.id == self.select)
                                .first()[0])
            self.tp_pasirinkimas.setCurrentIndex((session.query(Vairuotojas.transp_priemon)
                                               .where(Vairuotojas.id == self.select).first()[0]))
        except TypeError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Šiai T.P. nėra priskirtas vairuotojas!'
                                   '\nnJei šiai t.p. nori priskirti vairuotoja, eik: Visi įrašai> Visi vairuotojo įrašai>'
                                   'Redaguoti.\nArba pridėk nauja vairuotoja ir jam priskirk šia t.p.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            self.vardas.setReadOnly(True)
            self.pavarde.setReadOnly(True)
            self.tel_nr.setReadOnly(True)
            self.msg.setText('Pirmiausia priskirk TP!')

class VairuotojasDelete(QtWidgets.QDialog):

    def __init__(self, iraso_id):
        super().__init__()
        self.iraso_id = iraso_id
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
        vardas = session.query(Vairuotojas.vardas).where(Vairuotojas.id == self.iraso_id).first()[0]
        pavarde = session.query(Vairuotojas.pavarde).where(Vairuotojas.id == self.iraso_id).first()[0]
        self.irasas.setText(f'Vairuotojo irašas:{self.iraso_id}. {vardas} {pavarde} ')

    def delete(self):
        if self.iraso_id == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. jo ištrinti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
        else:
            Session = sessionmaker(bind=engine)
            session = Session()
            trinamas = session.get(Vairuotojas, self.iraso_id)
            trinamas.vardas = 'irasas'
            trinamas.pavarde = 'istrintas'
            trinamas.telef_nr = '00000'
            trinamas.transp_priemon = 0
            session.add(trinamas)
            session.commit()
            self.close()

#jei kodas leidziamas tiesiogiai ivykdo kas yra po if, jei ne tai to nevykdo.
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = VairuotojasEdit(19)
    app.exec()