from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy.orm import sessionmaker

from models import engine, MarkeModelis, TransportoPriemone


class MarkModelIrasas(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('userinterfaces/marke_modelis.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    def validate_record(self):
        if self.marke.text() == "" or self.modelis.text() == "":
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.mm_save()

    def mm_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        mark = self.marke.text()
        model = self.modelis.text()
        markeirasas = MarkeModelis(marke=mark, modelis=model)
        session.add(markeirasas)
        session.commit()
        self.msg.setText('Įrašas pridėtas')
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.marke.clear()
        self.modelis.clear()


class MarkModelEdit(QtWidgets.QDialog):

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
        uic.loadUi('userinterfaces/marke_modelis.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.setWindowTitle('Markės/modelio redagavimas')
        self.load_data()
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    def validate_record(self):
        if self.marke.text() == "" or self.modelis.text() == "":
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.mm_save()

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        marke_modelis_id = session.query(TransportoPriemone.marke).where(TransportoPriemone.id == self.select).first()[
            0]

        self.marke.setText(session.query(MarkeModelis.marke).where(MarkeModelis.id == marke_modelis_id)
                           .first()[0])
        self.modelis.setText(session.query(MarkeModelis.modelis).where(MarkeModelis.id == marke_modelis_id)
                             .first()[0])

    def mm_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        marke_modelis_id = session.query(TransportoPriemone.marke).where(TransportoPriemone.id == self.select).first()[
            0]
        mark = self.marke.text()
        model = self.modelis.text()
        markeirasas = session.get(MarkeModelis, marke_modelis_id)
        markeirasas.marke = mark
        markeirasas.modelis = model
        session.add(markeirasas)
        session.commit()
        self.msg.setText('Įrašas atnaujintas')


class MarkModelDirectEdit(QtWidgets.QDialog):

    def __init__(self, irasas_id):
        super().__init__()
        self.irasas = irasas_id
        if int(self.irasas) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText('Klaida')
            msg.setInformativeText('Įrašas yra numatytasis. Jo redaguoti negalima.')
            msg.setWindowTitle('Klaida')
            msg.exec_()
            return
        uic.loadUi('userinterfaces/marke_modelis.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.setWindowTitle('Markės/modelio redagavimas')
        self.load_data()
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    def validate_record(self):
        if self.marke.text() == "" or self.modelis.text() == "":
            self.msg.setText('Neįrašėte kažkurio lauko!')
            return

        self.mm_save()

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        self.marke.setText(session.query(MarkeModelis.marke).where(MarkeModelis.id == self.irasas)
                           .first()[0])
        self.modelis.setText(session.query(MarkeModelis.modelis).where(MarkeModelis.id == self.irasas)
                             .first()[0])

    def mm_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        mark = self.marke.text()
        model = self.modelis.text()
        markeirasas = session.get(MarkeModelis, self.irasas)
        markeirasas.marke = mark
        markeirasas.modelis = model
        session.add(markeirasas)
        session.commit()
        self.msg.setText('Įrašas atnaujintas')
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint


class MarkeDelete(QtWidgets.QDialog):

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
        marke = session.query(MarkeModelis.modelis).where(MarkeModelis.id == self.iraso_id).first()[0]
        modelis = session.query(MarkeModelis.marke).where(MarkeModelis.id == self.iraso_id).first()[0]
        self.irasas.setText(f'Markės/modelio irašas:{self.iraso_id}. {marke} {modelis} ')

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
            trinamas = session.get(MarkeModelis, self.iraso_id)
            trinamas.marke = 'irašas'
            trinamas.modelis = 'ištrintas'
            session.add(trinamas)
            session.commit()
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = MarkModelEdit(2)
    app.exec()
