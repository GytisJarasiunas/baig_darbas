from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import select
from datetime import datetime, timedelta
from kuras import KurasEditDirect, KurasDelete, KuroIrasas
from dialog_window import EditSelection, Selections
from models import engine, TransportoPriemone, Priekaba, Vairuotojas, MarkeModelis, KurasIrasas
from sqlalchemy.orm import sessionmaker
from prid_marke import MarkModelIrasas, MarkModelDirectEdit, MarkeDelete
from prid_priekab import PriekabaIrasas, PriekabaDirectEdit, PriekabaDelete
from prid_vairuotoja import VairuotojoIrasas, VairuotojasDirectEdit, VairuotojasDelete
from transporto_priemone import TPIrasas, TransportasDelete


#sukuriamas main window
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #paleidžiam funkcija sukurt d-base ir ten irasyt default duomenis
        self.populate_initial_data()
        #loadinam user-interface faila
        uic.loadUi('userinterfaces/pagrindinis.ui', self)
        #kairiame kampe pridedame icona
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        #inicijuojam lango rodyma
        self.show()
        #Sujungiam mygtukus su funkcijomis
        self.prideti.clicked.connect(self.pridejimas)
        self.redaguoti.clicked.connect(self.redagavimas_reik_demesio)
        self.redaguoti_2.clicked.connect(self.redagavimas)
        self.prideti_kuras.clicked.connect(self.dialog_kuras)
        self.prideti_marke.clicked.connect(self.dialog_marke)
        self.prideti_priekaba.clicked.connect(self.dialog_priekaba)
        self.prideti_vairuotojas.clicked.connect(self.dialog_vairuotojas)
        self.redaguoti_kuras.clicked.connect(self.edit_kuras)
        self.redaguoti_marke.clicked.connect(self.edit_marke)
        self.redaguoti_priekaba.clicked.connect(self.edit_priekaba)
        self.redaguoti_vairuotojas.clicked.connect(self.edit_vairuotojas)
        self.istrinti_kuras.clicked.connect(self.delete_kuras)
        self.istrinti_marke.clicked.connect(self.delete_marke)
        self.istrinti_priekaba.clicked.connect(self.delete_priekaba)
        self.istrinti_vairuotojas.clicked.connect(self.delete_vairuotojas)
        self.istrinti.clicked.connect(self.delete_t_p)
        self.atnaujinti.clicked.connect(self.load_data)
        self.atnaujinti_lenteles.clicked.connect(self.populate_tab_2)
        #i tablewidget langus uzkraunam duomenis
        self.load_data()
        self.populate_tab_2()


    #Funkcija kuri patikrina ar yra default irasai o jei ju nera tada juo sukuria
    def populate_initial_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        #kintamieji grazinantis bool
        tp_empty = session.query(TransportoPriemone).count() == 0
        priekaba_empty = session.query(Priekaba).count() == 0
        vairuotojas_empty = session.query(Vairuotojas).count() == 0
        marke_modelis_empty = session.query(MarkeModelis).count() == 0
        default_date = datetime(2001, 1, 1).date()


        #patikrinam ar tuscia ir jei tuscia pridedam irasa
        if tp_empty:
            default_tp = TransportoPriemone(id=0, valstyb_nr="xxx000", tech=default_date, pagam_data=default_date, keliu_mokestis=default_date,
                                            priekaba_id=0, marke=0)
            session.add(default_tp)

        if priekaba_empty:
            default_priekaba = Priekaba(id=0, pavadinimas="DEFAULT", valstyb_nr="xx000",
                                        pagam_metai=default_date, tech=default_date)
            session.add(default_priekaba)

        if vairuotojas_empty:
            default_vairuotojas = Vairuotojas(id=0, vardas="DEFAULT", pavarde="DEFAULT", telef_nr=0,
                                              transp_priemon=0)
            session.add(default_vairuotojas)

        if marke_modelis_empty:
            default_marke_modelis = MarkeModelis(id=0, marke="Nežinomas", modelis="Modelis")
            session.add(default_marke_modelis)

        #issaugom, uzdarom
        session.commit()
        session.close()

#funkcija iskviest antros korteles langu uzpildyma
    def populate_tab_2(self):
        self.populate_kuro_irasai()
        self.populate_marke()
        self.populate_priekaba()
        self.populate_vairuotojas()

    # dvi atskiros funkcijos atskiru langu redagavimui
    def redagavimas_reik_demesio(self):
        try:
            eile = self.reik_dem.currentItem().row()
            tp_id = self.reik_dem.item(eile, 0).text()
            print(tp_id)
            self.dialog = EditSelection(tp_id)
            return
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                   '\nPirma pasirinkite iš reikia dėmesio lentelės, tada spauskite redaguoti')

    # redaguoti visu tp irašus
    def redagavimas(self):
        try:
            eile = self.visi_auto.currentItem().row()
            tp_id = self.visi_auto.item(eile, 0).text()
            self.dialog = EditSelection(tp_id)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                   '\nPirma pasirinkite iš Visu T.P. lentelės, tada spauskite redaguoti')

#funkcija kuri patikrina ir irasus del tech ar keliu mokescio ir duoda uzklausa uzpildyt langus
    def load_data(self):
        #sukuriam sesija
        Session = sessionmaker(bind=engine)
        session = Session()
        #gaunam visas tp
        tr_priemones = session.query(TransportoPriemone).all()
        #gaunam visas priekabas
        priekabos = session.query(Priekaba).all()
        #du dicts i kuriuos keliauja irasai kurie turi besibaigiancia tech ar keliu mokesti
        reik_demesio = []
        demesio_priekabos = []

        for irasas in tr_priemones:
            if irasas.id == 0: #praleidziam index 0 tikrinima nes tai yra default irasas
                pass
            #patikrinam ar tech data patenka i bracketus, jei patenka ja appendinam i listus
            else:
                if (irasas.tech <= (datetime.now().date() + timedelta(days=30))
                        or irasas.keliu_mokestis <= datetime.now().date() + timedelta(days=30)):
                    reik_demesio.append(irasas)

        for irasas in priekabos:
            if irasas.id == 0:
                pass
            else:
                try:
                    if irasas.tech <= datetime.now().date() + timedelta(days=30):
                        demesio_priekabos.append(irasas)
                except TypeError:
                    pass
        for x in demesio_priekabos:
            t_p = session.query(TransportoPriemone).where(TransportoPriemone.priekaba_id == x.id).first()
            reik_demesio.append(t_p)


        #siunciam uzklausa funkcijai paduodami dictus ir self.visi_auto(lenteles pavadinimas)
        self.populate(self.visi_auto, tr_priemones)
        self.populate(self.reik_dem, reik_demesio)

    def populate(self, table, tr_priemones):
        Session = sessionmaker(bind=engine)
        session = Session()
        #nustatom lenteles eiluciu skaiciu pagal dict ilgi
        table.setRowCount(len(tr_priemones))
        tablerow = 0
        for row in tr_priemones:
            #i table vieta iklijuojam lenteles pavadinima ir iteruojam per irasus
            table.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            #Qtable view kazkodel pyksta ant intergers todel idedant interger pakeiciam str
            table.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row.valstyb_nr))
            table.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(str(row.tech)))
            table.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row.keliu_mokestis)))
            table.setItem(tablerow, 4, QtWidgets.QTableWidgetItem
            (str(session.execute(select(Priekaba.valstyb_nr).where(Priekaba.id == row.priekaba_id)).first()[0])))
            table.setItem(tablerow, 5, QtWidgets.QTableWidgetItem
            (str(session.execute(select(Priekaba.tech).where(Priekaba.id == row.priekaba_id)).first()[0])))
            #try exept pridedam nes priskirimas vairuotojui tik kuriant vairuotoja, tai kad galetume be jo :
            try:
                table.setItem(tablerow, 6, QtWidgets.QTableWidgetItem
                (str(session.execute(select(Vairuotojas.vardas).where(Vairuotojas.transp_priemon == row.id))
                     .first()[0])))
            except TypeError:
                table.setItem(tablerow, 6, QtWidgets.QTableWidgetItem('Vair. nepriskirtas'))
            try:
                table.setItem(tablerow, 7, QtWidgets.QTableWidgetItem
                (str(session.execute(select(Vairuotojas.pavarde).where(Vairuotojas.transp_priemon == row.id))
                     .first()[0])))
            except TypeError:
                table.setItem(tablerow, 7, QtWidgets.QTableWidgetItem('Vair. nepriskirtas'))

            table.setItem(tablerow, 8, QtWidgets.QTableWidgetItem(session.execute(
                select(MarkeModelis.marke).where(MarkeModelis.id == row.marke)).first()[0]))
            table.setItem(tablerow, 9, QtWidgets.QTableWidgetItem(session.execute(
                select(MarkeModelis.modelis).where(MarkeModelis.id == row.marke)).first()[0]))
            tablerow += 1
#kodel buvo sukurtas dar kelios funkcijos, tai todel kad visi langai turi skirtinga stulpeliu skaiciu.
    def populate_kuro_irasai(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        irasai = session.query(KurasIrasas).all()
        self.kuro_irasai.setRowCount(len(irasai))
        tablerow = 0
        for row in irasai:
            self.kuro_irasai.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            self.kuro_irasai.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(str(row.data)))
            self.kuro_irasai.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(str(row.kilometrazas)))
            self.kuro_irasai.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row.kiekis)))
            self.kuro_irasai.setItem(tablerow, 4, QtWidgets.QTableWidgetItem(str(row.kaina)))
            self.kuro_irasai.setItem(tablerow, 5, QtWidgets.QTableWidgetItem(session.execute(
                select(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == row.tp_id)).first()[0]))

            tablerow += 1

    def populate_marke(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        irasai = session.query(MarkeModelis).all()
        self.markes_irasai.setRowCount(len(irasai) - 1)
        tablerow = 0
        for row in irasai:
            if row.id == 0:
                pass
            else:
                self.markes_irasai.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
                self.markes_irasai.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row.marke))
                self.markes_irasai.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row.modelis))
                tablerow += 1

    def populate_priekaba(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        irasai = session.query(Priekaba).all()
        self.priekabos_irasai.setRowCount(len(irasai))
        tablerow = 0
        for row in irasai:
            self.priekabos_irasai.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            self.priekabos_irasai.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row.pavadinimas))
            self.priekabos_irasai.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row.valstyb_nr))
            self.priekabos_irasai.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row.pagam_metai)))
            self.priekabos_irasai.setItem(tablerow, 4, QtWidgets.QTableWidgetItem(str(row.tech)))
            tablerow += 1

    def populate_vairuotojas(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        irasai = session.query(Vairuotojas).all()
        self.vair_irasai.setRowCount(len(irasai))
        tablerow = 0
        for row in irasai:
            self.vair_irasai.setItem(tablerow, 0, QtWidgets.QTableWidgetItem(str(row.id)))
            self.vair_irasai.setItem(tablerow, 1, QtWidgets.QTableWidgetItem(row.vardas))
            self.vair_irasai.setItem(tablerow, 2, QtWidgets.QTableWidgetItem(row.pavarde))
            self.vair_irasai.setItem(tablerow, 3, QtWidgets.QTableWidgetItem(str(row.telef_nr)))
            self.vair_irasai.setItem(tablerow, 4, QtWidgets.QTableWidgetItem(session.execute(
                select(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == row.transp_priemon)).first()[0]))
            tablerow += 1
#connectinant mygtukus su funkcijomis jei prie connect idedi funkcija kaip pvz
    # (self.mygtukas.clicked.connect(Selections()) neivykodma funkcija, ir nevyksta niekas todel i buttonconectus dedas
    # tik funkcijos pavadinimas, ko pasekoje reikejo sukurti funkcijas kurios iskviecia funkcijas
    def pridejimas(self):
        self.dialog = Selections()

    def dialog_kuras(self):
        self.dialog = KuroIrasas()

    def dialog_tpirasas(self):
        self.dialog = TPIrasas()

    def dialog_marke(self):
        self.dialog = MarkModelIrasas()

    def dialog_priekaba(self):
        self.dialog = PriekabaIrasas()

    def dialog_vairuotojas(self):
        self.dialog = VairuotojoIrasas()
#cia tas pats bet su jomis dar kartu pasiduoda pasirinkimas, kuri editint
    def edit_kuras(self):
        try:
            eile = self.kuro_irasai.currentItem().row()
            selection = self.kuro_irasai.item(eile, 0).text()
            self.dialog = KurasEditDirect(selection)
        #exceptas be TypeError ar pns nes PYQT daugeliu atveju neduoda eror o tiesiog uzsidaro su visiskai neaiskiu
        #process finish, ir jei irasius type error tada nepagauna jog ivyko klaida,
        # bandziau suzinot kas per kodas bet tokiu kodu nelabai yra
        except:
            #jei nepavyko ismetamas langelis su paaiskinimu
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu Kuro '
                                    'įrašų lentelės, tada spauskite redaguoti.')

    def edit_marke(self):
        try:
            eile = self.markes_irasai.currentItem().row()
            selection = self.markes_irasai.item(eile, 0).text()
            self.dialog = MarkModelDirectEdit(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu markės/modelio įrašų lentelės, '
                                    'tada spauskite redaguoti.')


    def edit_priekaba(self):
        try:
            eile = self.priekabos_irasai.currentItem().row()
            selection = self.priekabos_irasai.item(eile, 0).text()
            self.dialog = PriekabaDirectEdit(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu priekabos įrašų lentelės, tada spauskite redaguoti.')

    def edit_vairuotojas(self):
        try:
            eile = self.vair_irasai.currentItem().row()
            selection = self.vair_irasai.item(eile, 0).text()
            self.dialog = VairuotojasDirectEdit(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu vairuotoju įrašų lentelės, tada spauskite redaguoti.')
#funkcijos detele, viskas tas pats
    def delete_t_p(self):
        try:
            eile = self.visi_auto.currentItem().row()
            selection = self.visi_auto.item(eile, 0).text()
            self.dialog = TransportasDelete(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu transporto priemonės įrašu lentelės,'
                                    ' tada spauskite ištrinti')

    def delete_kuras(self):
        try:
            eile = self.kuro_irasai.currentItem().row()
            selection = self.kuro_irasai.item(eile, 0).text()
            self.dialog = KurasDelete(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu kuro įrašu lentelės, tada spauskite ištrinti')

    def delete_marke(self):
        try:
            eile = self.markes_irasai.currentItem().row()
            selection = self.markes_irasai.item(eile, 0).text()
            self.dialog = MarkeDelete(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu markės/modelio įrašu lentelės, '
                                    'tada spauskite ištrinti')

    def delete_priekaba(self):
        try:
            eile = self.priekabos_irasai.currentItem().row()
            selection = self.priekabos_irasai.item(eile, 0).text()
            self.dialog = PriekabaDelete(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                    '\nPirma pasirinkite iš visu priekabos įrašu lentelės, tada spauskite ištrinti')

    def delete_vairuotojas(self):
        try:
            eile = self.vair_irasai.currentItem().row()
            selection = self.vair_irasai.item(eile, 0).text()
            self.dialog = VairuotojasDelete(selection)
        except:
            self.show_error_message('Nepasirinkote irašo kurį redaguoti.'
                                   '\nPirma pasirinkite iš visu vairuotojo įrašu lentelės, tada spauskite ištrinti')


#error message laukelis, be uii failo, ateina is pyqt defaultu su pilnu funkcionalumu
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText('Klaida')
        msg.setInformativeText(message)
        msg.setWindowTitle('Klaida')
        msg.exec_()



# jei kodas leidziamas tiesiogiai ivykdo kas yra po if, jei ne tai to nevykdo.
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    first = MainWindow()
    app.exec()
