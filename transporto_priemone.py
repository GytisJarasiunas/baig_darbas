import re
from PyQt5 import uic, QtWidgets
from datetime import date
from PyQt5.QtWidgets import QMessageBox
from prid_marke import MarkModelIrasas
from PyQt5.QtGui import QValidator, QIcon
from sqlalchemy.orm import sessionmaker
from prid_priekab import PriekabaIrasas
from models import engine, TransportoPriemone, MarkeModelis, Priekaba

#cia viskas susyje su tp redagavimu ir pridejimu
# validatorius valstybiniam numeriui
class ValsybNum(QValidator):
    def validate(self, string, index):
        # paternas netikrina ilgio ar formos, nes gali but ivairiu saliu valstyb. nr kuriu formatai skirias
        pattern = re.compile(r'^[A-Za-z0-9]+')
        #patikrina ar ka rasom atitinka, jei ne nedisplayina
        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index

#pagrindine klase kuri prideda irasa
class TPIrasas(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        #cia tas pats kas maine
        uic.loadUi('userinterfaces/t_p_irasas.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        self.val_nr.setValidator(ValsybNum())
        self.pridet_marke.clicked.connect(self.marke_add)
        self.prid_priekab.clicked.connect(self.priekaba_add)
        self.refresh.clicked.connect(self.load_data)
        self.pagam_data.setDate(date.today())
        self.kel_mokestis.setDate(date.today())
        self.tech.setDate(date.today())
        self.load_data()
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    # tikrinam kad nr butu bent 6 skaitmenu nr ir kad toks nr jau neegzistuotu
    # kodel turim validatoriu ir sita? nes validatorius netikrina galutinio produkto, jis tikrina tik kiekviena zenkla
    def validate_record(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        #cia paziurm ar ner tuscias ir ar nera per trumpas
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 6:
            self.msg.setText('Neįrašėte kažkurio lauko! arba irašėte neteisingai')
            return
        #cia praiteruojam per visus irasus ir patikrinam ar nera jau tp tokiu numeriu
        for irasas in tr_priemones:
            if self.val_nr.text().upper() == irasas.valstyb_nr:
                self.msg.setText('T.P. tokiu valstyb. nr jau egzistuoja, gal suklydote?')
                return
        #try exept nes qtablewidget nesvarbu ar pasirinkta ar ne grazina atsakyma, ko pasekoje suhandlint pavyko tik taip
        try:
            self.tp_save()
        except:
            self.msg.setText('Nepasirinkote markės/modelio arba priekabos')


#funkcija kuri issaugo duomenis
    def tp_save(self):
        #sukuriam sesija
        Session = sessionmaker(bind=engine)
        session = Session()
        #parasom kintamuosius, kad butu paprasciau
        eile_m = self.marke.currentItem().row()
        mark = self.marke.item(eile_m, 0).text()
        eile_p = self.priekaba.currentItem().row()
        priekab = self.priekaba.item(eile_p, 0).text()
        technikine = self.tech.date().toPyDate()
        pdata = self.pagam_data.date().toPyDate()
        kmokestis = self.kel_mokestis.date().toPyDate()
        vnum = self.val_nr.text().upper()
        tpirasas = TransportoPriemone(valstyb_nr=vnum, tech=technikine, pagam_data=pdata, keliu_mokestis=kmokestis,
                                      marke=mark, priekaba_id=priekab)
        session.add(tpirasas)
        session.commit()
        self.msg.setText('Įrašas pridėtas')
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.val_nr.clear()


#datos krovimas i qtableview taspats kaip main window
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        modeliai = session.query(MarkeModelis).all()
        priekabos = session.query(Priekaba).all()
        tablerow_modeliai = 0
        tablerow_priekabos = 0
        self.marke.setRowCount(len(modeliai))
        self.priekaba.setRowCount(len(priekabos))
        for x in modeliai:
            self.marke.setItem(tablerow_modeliai, 0, QtWidgets.QTableWidgetItem(str(x.id)))
            self.marke.setItem(tablerow_modeliai, 1, QtWidgets.QTableWidgetItem(x.marke))
            self.marke.setItem(tablerow_modeliai, 2, QtWidgets.QTableWidgetItem(x.modelis))
            tablerow_modeliai += 1
        for y in priekabos:
            self.priekaba.setItem(tablerow_priekabos, 0, QtWidgets.QTableWidgetItem(str(y.id)))
            self.priekaba.setItem(tablerow_priekabos, 1, QtWidgets.QTableWidgetItem(y.valstyb_nr))
            self.priekaba.setItem(tablerow_priekabos, 2, QtWidgets.QTableWidgetItem(y.pavadinimas))
            tablerow_priekabos += 1

    # funkcijoms dviems pridejimo mygtukams
    def marke_add(self):
        self.dialog = MarkModelIrasas()

    def priekaba_add(self):
        self.dialog = PriekabaIrasas()

#cia editas, einantis tiesiai, is pagrindinio lango. kiti irašai dar turi direct edit,
#kuo skiriasi direct edit nuo paprasto tai kad cia edita gauname per tp id
#o direct edit eina tiesiai per iraso id numeri
class TPIrasasEdit(QtWidgets.QDialog):
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
        uic.loadUi('userinterfaces/t_p_irasas.ui', self)
        self.setWindowTitle('Transporto priemonės įrašo redagavimas')
        self.val_nr.setValidator(ValsybNum())
        self.pridet_marke.clicked.connect(self.marke_add)
        self.prid_priekab.clicked.connect(self.priekaba_add)
        self.refresh.clicked.connect(self.rerun)
        self.pagam_data.setDate(date.today())
        self.kel_mokestis.setDate(date.today())
        self.tech.setDate(date.today())
        self.load_data(self.select)
        self.show()
        self.issaugot.clicked.connect(self.validate_record)

    def rerun(self):
        self.load_data(self.select)

    # tikrinam kad nr butu bent 6 skaitmenu nr ir kad toks nr jau neegzistuotu
    def validate_record(self):
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 6:
            self.msg.setText('Neįrašėte kažkurio lauko! arba irašėte neteisingai')
            return

        self.tp_save()





    def tp_save(self):
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
            eile_m = self.marke.currentItem().row()
            mark = self.marke.item(eile_m, 0).text()
            eile_p = self.priekaba.currentItem().row()
            priekab = self.priekaba.item(eile_p, 0).text()
            technikine = self.tech.date().toPyDate()
            pdata = self.pagam_data.date().toPyDate()
            kmokestis = self.kel_mokestis.date().toPyDate()
            vnum = self.val_nr.text().upper()
            tpirasas = session.get(TransportoPriemone, self.select)
            tpirasas.marke = mark
            tpirasas.priekaba_id = priekab
            tpirasas.tech = technikine
            tpirasas.pagam_data = pdata
            tpirasas.keliu_mokestis = kmokestis
            tpirasas.valstyb_nr = vnum
            session.add(tpirasas)
            session.commit()
            self.msg.setText('Įrašas atnaujintas')
     # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint


        # uzkrauna duomenis i dropdown menu

    def load_data(self, select):
        Session = sessionmaker(bind=engine)
        session = Session()
        modeliai = session.query(MarkeModelis).all()
        priekabos = session.query(Priekaba).all()
        tablerow_modeliai = 0
        tablerow_priekabos = 0
        self.marke.setRowCount(len(modeliai))
        self.priekaba.setRowCount(len(priekabos))
        for x in modeliai:
            self.marke.setItem(tablerow_modeliai, 0, QtWidgets.QTableWidgetItem(str(x.id)))
            self.marke.setItem(tablerow_modeliai, 1, QtWidgets.QTableWidgetItem(x.marke))
            self.marke.setItem(tablerow_modeliai, 2, QtWidgets.QTableWidgetItem(x.modelis))
            tablerow_modeliai += 1
        for y in priekabos:
            self.priekaba.setItem(tablerow_priekabos, 0, QtWidgets.QTableWidgetItem(str(y.id)))
            self.priekaba.setItem(tablerow_priekabos, 1, QtWidgets.QTableWidgetItem(y.valstyb_nr))
            self.priekaba.setItem(tablerow_priekabos, 2, QtWidgets.QTableWidgetItem(y.pavadinimas))
            tablerow_priekabos += 1
        self.val_nr.setText(session.query(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == select)
                            .first()[0])
        self.tech.setDate(session.query(TransportoPriemone.tech).where(TransportoPriemone.id == select).first()[0])
        self.pagam_data.setDate(session.query(TransportoPriemone.pagam_data)
                                .where(TransportoPriemone.id == select).first()[0])
        self.kel_mokestis.setDate(session.query(TransportoPriemone.keliu_mokestis)
                                  .where(TransportoPriemone.id == select).first()[0])
        self.marke.setCurrentCell(session.query(TransportoPriemone.marke)
                                .where(TransportoPriemone.id == select).first()[0],0)
        self.priekaba.setCurrentCell(session.query(TransportoPriemone.priekaba_id)
                                           .where(TransportoPriemone.id == select).first()[0],0)

    def marke_add(self):
        self.dialog = MarkModelIrasas()

    def priekaba_add(self):
        self.dialog = PriekabaIrasas()
#funkcija delete, kuri is tikro neistrina iraso, tik ji overridina(beveik soft delete)
#stack overflow radau pavyzdi jog butu galbut geriau daryt su deletestate bet tada susiduriam su beda del pasirinkimu
#gaunamu is qcombobox
class TransportasDelete(QtWidgets.QDialog):

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
            #turim atskira inteface istrinimui
            uic.loadUi('userinterfaces/istrinti.ui', self)
            self.atsaukti.clicked.connect(self.close)
            self.istrinti.clicked.connect(self.delete)
            self.show()
            self.load_data()

        def load_data(self):
            Session = sessionmaker(bind=engine)
            session = Session()
        #kai paspaudziamas mygtukas istrinti popupina naujas langas kuriame ira info apie trinama objekta
            #tai kad netycia neistrint iraso
            pavadinimas = session.query(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == self.iraso_id).first()[0]
            self.irasas.setText(f'T.P. irašas:{self.iraso_id}. {pavadinimas}')
#ir overridinam
        def delete(self):
            Session = sessionmaker(bind=engine)
            session = Session()
            trinamas = session.get(TransportoPriemone, self.iraso_id)
            trinamas.valstyb_nr = '000000'
            trinamas.marke = '0'
            trinamas.priekaba_id = '0'
            session.add(trinamas)
            session.commit()
            self.close()




if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = TPIrasas()
    app.exec()
