from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon
from kuras import KuroIrasas, KuroIrasasEdit
from transporto_priemone import TPIrasas, TPIrasasEdit
from prid_marke import MarkModelIrasas, MarkModelEdit
from prid_priekab import PriekabaIrasas, PriekabaEdit
from prid_vairuotoja import VairuotojoIrasas, VairuotojasEdit

#nieko stebuklingo apie apie si langa, kai paspaudziamas mygtukas pridet ar redaguot pirmam lange ismetamas popup langas
#pasirinkti ka norime redaguoti, nes pagrindiniam is pasirinkimu galima redaguoti viska
# sukuriamas pasirinkimu langas

class Selections(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # užkraunamas ui failas
        uic.loadUi('userinterfaces/pasirinkimai.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        # sukuriami mygtuku rysiai
        self.add_kuras.clicked.connect(self.dialog_kuras)
        self.tp_iras.clicked.connect(self.dialog_tpirasas)
        self.priekaba.clicked.connect(self.dialog_priekaba)
        self.vair.clicked.connect(self.dialog_vairuotojas)
        self.marke.clicked.connect(self.dialog_marke)
        self.show()

    # sukurtos funkcijos kurios vykdomos nuspaudus mygtuka

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


class EditSelection(QtWidgets.QDialog):
    def __init__(self, selection):
        super().__init__()
        self.select = selection
        # užkraunamas ui failas
        uic.loadUi('userinterfaces/pasirinkimai.ui', self)
        app_icon = QIcon('resources/icon.png')
        self.setWindowIcon(app_icon)
        #pakeičiamas lango pavadinimas (kad nekurt naujo, ir nedidint projekto apimties)
        self.setWindowTitle('Redaguoti įraša')
        # sukuriami mygtuku rysiai
        self.add_kuras.clicked.connect(self.dialog_kuras)
        self.tp_iras.clicked.connect(self.dialog_tpirasas)
        self.priekaba.clicked.connect(self.dialog_priekaba)
        self.vair.clicked.connect(self.dialog_vairuotojas)
        self.marke.clicked.connect(self.dialog_marke)
        self.show()

    # sukurtos funkcijos kurios vykdomos nuspaudus mygtuka

    def dialog_kuras(self):
        self.dialog = KuroIrasasEdit(self.select)

    def dialog_tpirasas(self):
        self.dialog = TPIrasasEdit(self.select)

    def dialog_marke(self):
        self.dialog = MarkModelEdit(self.select)

    def dialog_priekaba(self):
        self.dialog = PriekabaEdit(self.select)

    def dialog_vairuotojas(self):
        self.dialog = VairuotojasEdit(self.select)


# jei kodas leidziamas tiesiogiai ivykdo kas yra po if, jei ne tai to nevykdo.
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    second = EditSelection(1)
    app.exec()
