import os
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import select
from datetime import datetime, timedelta
from dialog_window import Selections, EditSelection
from models import engine, TransportoPriemone, Priekaba, Vairuotojas, MarkeModelis
from sqlalchemy.orm import sessionmaker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("pagrindinis.ui", self)
        self.show()
        self.prideti.clicked.connect(self.pridejimas)
        self.redaguoti.clicked.connect(self.redagavimas)
        self.load_data()
        self.atnaujinti.clicked.connect(self.load_data)

    def redagavimas(self):

        pasirinkimas = self.visi_auto.currentRow() + 1
        if pasirinkimas:
            self.dialog = EditSelection(pasirinkimas)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Klaida")
            msg.setInformativeText('Nepasirinkote irašo kurį redaguoti.'
                                   '\nPirma pasirinkite iš lentelės, tada spauskite redaguoti')
            msg.setWindowTitle("Klaida")
            msg.exec_()

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        priekabos = session.query(Priekaba).all()
        reik_demesio =[]
        demesio_priekabos = []
        print(tr_priemones)

        for irasas in tr_priemones:
            if (irasas.tech <= (datetime.now().date() + timedelta(days=30))
                    or irasas.keliu_mokestis <= datetime.now().date() + timedelta(days=30)):
                reik_demesio.append(irasas)

        for irasas in priekabos:
            try:
                if irasas.tech <= datetime.now().date() + timedelta(days=30):
                    demesio_priekabos.append(irasas)
            except TypeError:
                pass

        self.populate(self.visi_auto, tr_priemones)
        self.populate(self.reik_dem, reik_demesio)
        print(reik_demesio)



    def populate(self, table, tr_priemones):
        Session = sessionmaker(bind=engine)
        session = Session()
        table.setRowCount(len(tr_priemones))
        tablerow = 0
        for row in tr_priemones:
            print(row.id)
            table.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            table.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row.valstyb_nr))
            table.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(str(row.tech)))
            table.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row.keliu_mokestis)))
            table.setItem(tablerow, 4, QtWidgets.QTableWidgetItem
            (str(session.execute(select(Priekaba.valstyb_nr).where(Priekaba.id == row.priekaba_id)).first()[0])))
            table.setItem(tablerow, 5, QtWidgets.QTableWidgetItem
            (str(session.execute(select(Priekaba.tech).where(Priekaba.id == row.priekaba_id)).first()[0])))

            try:
                table.setItem(tablerow, 6, QtWidgets.QTableWidgetItem
                (str(session.execute(select(Vairuotojas.vardas).where(Vairuotojas.transp_priemon == row.id))
                     .first()[0])))
            except TypeError:
                table.setItem(tablerow, 6, QtWidgets.QTableWidgetItem("Vair. nepriskirtas"))
            try:
                table.setItem(tablerow, 7, QtWidgets.QTableWidgetItem
                (str(session.execute(select(Vairuotojas.pavarde).where(Vairuotojas.transp_priemon == row.id))
                     .first()[0])))
            except TypeError:
                table.setItem(tablerow, 7, QtWidgets.QTableWidgetItem("Vair. nepriskirtas"))

            table.setItem(tablerow, 8, QtWidgets.QTableWidgetItem(session.execute(
                select(MarkeModelis.marke).where(MarkeModelis.id == row.marke)).first()[0]))
            table.setItem(tablerow, 9, QtWidgets.QTableWidgetItem(session.execute(
                select(MarkeModelis.modelis).where(MarkeModelis.id == row.marke)).first()[0]))
            tablerow += 1







    def pridejimas(self):
        self.dialog = Selections()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    first = MainWindow()
    app.exec()