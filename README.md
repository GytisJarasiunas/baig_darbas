Ši programa yra transporto priemonių valdymo sistema, kuri padeda stebėti ir tvarkyti transporto priemonių, priekabų, vairuotojų ir kitų susijusių įrašų duomenis. Programoje naudojama PyQt5 grafinė vartotojo sąsaja (GUI) ir SQLAlchemy duomenų bazės valdymui.
Funkcionalumas

    Transporto priemonių valdymas: Galimybė pridėti, redaguoti ir ištrinti transporto priemonių įrašus. Programa taip pat stebi techninės apžiūros ir kelių mokesčio datas bei informuoja, jei šių įrašų galiojimas greitai baigsis.

    Kuro įrašai: Naudotojai gali pridėti, redaguoti ir ištrinti kuro įrašus, įskaitant informaciją apie įpilto kuro kiekį, kainą, datą ir transporto priemonės ridą.

    Priekabų valdymas: Galimybė pridėti, redaguoti ir ištrinti priekabų įrašus. Programa taip pat stebi priekabų techninės apžiūros datas.

    Vairuotojų valdymas: Galimybė pridėti, redaguoti ir ištrinti vairuotojų įrašus, įskaitant vardą, pavardę, telefono numerį ir priskirtą transporto priemonę.

    Markės ir modelio valdymas: Galimybė pridėti, redaguoti ir ištrinti transporto priemonių markės ir modelio įrašus.

    Sąsaja: Pagrindinis langas turi mygtukus, skirtus įvairioms funkcijoms atlikti, įskaitant transporto priemonės, kuro įrašo, priekabos, vairuotojo ir markės/modelio pridėjimą, redagavimą bei ištrynimą.

    Programa ir jos grafinė vartotojo sąsaja lengvai modifikuojama, dėka QT Designer .ui failu.


Repositorijoje taip pat kartu ikeltas failas, pavadinimu "TransportoValdymasInstall1_0.exe". Failas skirtas programai 
instaliuoti ir konfiguruoti.
Susisiekti: gytisje@gmail.com

Pasileisti is kodo: persisiuntus visa direktorija, reikia susiimportuoti requirements(pip install -r /path/to/requirements.txt)
. Atsidarius pycharme pasirinkti main ir spausti run. UI failu redagavimui naudojama QT Designer:
https://www.pythonguis.com/installation/install-qt-designer-standalone/ 