from PyQt5 import QtWidgets, uic
from sqlalchemy.orm import sessionmaker

from models import engine, MarkeModelis, TransportoPriemone


class MarkModelIrasas(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi("marke_modelis.ui", self)
        self.show()
        self.issaugot.clicked.connect(self.mm_save)

    def mm_save(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        mark = self.marke.text()
        model = self.modelis.text()
        markeirasas = MarkeModelis(marke=mark, modelis=model)
        session.add(markeirasas)
        session.commit()
        self.msg.setText("Įrašas pridėtas")
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint
        self.marke.clear()
        self.modelis.clear()

class MarkModelEdit(QtWidgets.QDialog):

    def __init__(self, selection):
        super().__init__()
        self.select = selection
        print(self.select)

        uic.loadUi("marke_modelis.ui", self)
        self.setWindowTitle("Markės/modelio redagavimas")
        self.load_data()
        self.show()
        self.issaugot.clicked.connect(self.mm_save)
    def load_data(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        marke_modelis_id = session.query(TransportoPriemone.marke).where(TransportoPriemone.id == self.select).first()[
            0]
        print(marke_modelis_id)
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
        self.msg.setText("Įrašas Atnaujintas")
        # issaugojus isvalo langelius kad netycia nepridet dar karta, ar kad norint pridet dar viena irasa nereiktu trint


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = MarkModelEdit(2)
    app.exec()

