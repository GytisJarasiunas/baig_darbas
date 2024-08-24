import re
from PyQt5 import uic, QtWidgets
from datetime import date
from prid_marke import MarkModelIrasas
from PyQt5.QtGui import QValidator
from sqlalchemy.orm import sessionmaker
from prid_priekab import PriekabaIrasas
from models import engine, TransportoPriemone, MarkeModelis, Priekaba


# validatorius valstybiniam numeriui
class ValsybNum(QValidator):
    def validate(self, string, index):
        # paternas netikrina ilgio ar formos, nes gali but ivairiu saliu valstyb. nr kuriu formatai skirias
        pattern = re.compile(r"^[A-Za-z0-9]+")

        if string == "":
            return QValidator.State.Acceptable, string, index

        if pattern.fullmatch(string):
            return QValidator.State.Acceptable, string, index

        else:
            return QValidator.State.Invalid, string, index


class TPIrasas(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("t_p_irasas.ui", self)
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
    def validate_record(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        tr_priemones = session.query(TransportoPriemone).all()
        if self.val_nr.text() == "" or len(self.val_nr.text()) < 6:
            self.msg.setText("Neįrašėte kažkurio lauko! arba irašėte neteisingai")
            return
        for irasas in tr_priemones:
            if self.val_nr.text().upper() == irasas.valstyb_nr:
                self.msg.setText('T.P. tokiu valstyb. nr jau egzistuoja, gal suklydote?')
                return

        self.tp_save()

    def tp_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        mark = (self.marke_modelis.currentIndex()) + 1
        priekab = (self.priekaba.currentIndex()) + 1
        technikine = self.tech.date().toPyDate()
        pdata = self.pagam_data.date().toPyDate()
        kmokestis = self.kel_mokestis.date().toPyDate()
        vnum = self.val_nr.text().upper()
        tpirasas = TransportoPriemone(valstyb_nr=vnum, tech=technikine, pagam_data=pdata, keliu_mokestis=kmokestis,
                                      marke=mark, priekaba_id=priekab)
        session.add(tpirasas)
        session.commit()
        self.msg.setText("Įrašas pridėtas")
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.val_nr.clear()

        # uzkrauna duomenis i dropdown menu

    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        modeliai = session.query(MarkeModelis).all()
        priekabos = session.query(Priekaba).all()
        for x in modeliai:
            self.marke_modelis.addItem(f'{x.id}. {x.marke} {x.modelis}')
        for y in priekabos:
            self.priekaba.addItem(f'{y.id}. {y.valstyb_nr}, {y.pavadinimas}')

    # funkcijoms dviems pridejimo mygtukams
    def marke_add(self):
        self.dialog = MarkModelIrasas()

    def priekaba_add(self):
        self.dialog = PriekabaIrasas()


class TPIrasasEdit(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        uic.loadUi("t_p_irasas.ui", self)
        self.setWindowTitle("Transporto priemonės įrašo redagavimas")
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
            self.msg.setText("Neįrašėte kažkurio lauko! arba irašėte neteisingai")
            return


        self.tp_save()

    def tp_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        mark = (self.marke_modelis.currentIndex())
        priekab = (self.priekaba.currentIndex()) + 1
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
        self.msg.setText("Įrašas pridėtas")
     # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint


        # uzkrauna duomenis i dropdown menu

    def load_data(self, select):
        Session = sessionmaker(bind=engine)
        session = Session()
        modeliai = session.query(MarkeModelis).all()
        priekabos = session.query(Priekaba).all()
        self.marke_modelis.clear()
        self.priekaba.clear()
        for x in modeliai:
            self.marke_modelis.addItem(f'{x.id}. {x.marke} {x.modelis}')
        for y in priekabos:
            self.priekaba.addItem(f'{y.id}. {y.valstyb_nr}, {y.pavadinimas}')
        self.val_nr.setText(session.query(TransportoPriemone.valstyb_nr).where(TransportoPriemone.id == select)
                            .first()[0])
        self.tech.setDate(session.query(TransportoPriemone.tech).where(TransportoPriemone.id == select).first()[0])
        self.pagam_data.setDate(session.query(TransportoPriemone.pagam_data)
                                .where(TransportoPriemone.id == select).first()[0])
        self.kel_mokestis.setDate(session.query(TransportoPriemone.keliu_mokestis)
                                  .where(TransportoPriemone.id == select).first()[0])
        self.marke_modelis.setCurrentIndex(session.query(TransportoPriemone.marke)
                                           .where(TransportoPriemone.id == select).first()[0])
        self.priekaba.setCurrentIndex(session.query(TransportoPriemone.priekaba_id)
                                           .where(TransportoPriemone.id == select).first()[0]-1)



    # funkcijoms dviems pridejimo mygtukams
    def marke_add(self):
        self.dialog = MarkModelIrasas()

    def priekaba_add(self):
        self.dialog = PriekabaIrasas()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = TPIrasasEdit(9)
    app.exec()
