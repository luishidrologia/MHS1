'''
MHS1 Realiza simulaciones del consumo de agua de una edificación
Copyright (C) 2016  Luis Martín Martínez

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation version 2
of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

MHS1 comes with ABSOLUTELY NO WARRANTY.
Contact info@hidrologiasostenible.com.
'''

import sys
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
#from scipy.interpolate import InterpolatedUnivariateSpline
from PyQt4 import QtCore, QtGui, uic
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from operator import itemgetter, attrgetter, methodcaller
# Cargar nuestro archivo .ui
mi_clase = uic.loadUiType("MHS1_15.ui")[0]



class MiFormulario(QtGui.QMainWindow, mi_clase):

    ruta = ""
    fichero_actual = ""

    def __init__(self, parent=None):
        global paletterojo; global paletteverde
        global numlam; global chd
        global tarifas;global tarifas_ext; global suelo;global meteorologia; global jardin
        global ntipoviviendas; global frec_limp ;global gasto_limpieza
        global liminf; global limsup; global lista_inicial;global recliminf; global reclimsup
        global in1_dep2; global in2_dep1; global in1_dep1; global in2_dep2
        global pluviales; global recogida


        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        picfile="logo.jpg"
        logo = os.getcwd() + "\\" + picfile
        pixmap = QtGui.QPixmap(logo)
        label = QtGui.QLabel(self.labelLogo)
        label.setPixmap(pixmap)

        picfile_peq="logo_peq.jpg"
        logo_peq = os.getcwd() + "\\" + picfile_peq
        pixmap_peq = QtGui.QPixmap(logo_peq)
        labeldatos1 = QtGui.QLabel(self.labelLogoDat1)
        labeldatos1.setPixmap(pixmap_peq)
        labeldatos2 = QtGui.QLabel(self.labelLogoDat2)
        labeldatos2.setPixmap(pixmap_peq)
        labelRes = QtGui.QLabel(self.labelLogoRes)
        labelRes.setPixmap(pixmap_peq)
        labelPlu = QtGui.QLabel(self.labelLogoPlu)
        labelPlu.setPixmap(pixmap_peq)

        picfile2="logoMHS1.jpg"
        logo2 = os.getcwd() + "\\" + picfile2
        pixmap2 = QtGui.QPixmap(logo2)
        label2 = QtGui.QLabel(self.labelLogo_2)
        label2.setPixmap(pixmap2)


        #Inicializo algunas variables
        numlam = 0; ntipoviviendas = 0;frec_limp = 0; gasto_limpieza = 0
        tarifas = False; suelo = False; meteorologia = False; jardin = False
        tarifas_ext =True
        liminf = True; limsup = False; balance = False
        recliminf = True;reclimsup = False
        in1_dep2 = False; in2_dep1 = False; in1_dep1 = True; in2_dep2 = True
        pluviales = False; recogida= False

        # Asigno los valores por defecto al consumo base y microcomponentes
        self.lineChd.setText("142")
        chd = int(self.lineChd.text())
        self.tableViv.setColumnCount(1)
        self.lineFreg.setText("19")
        freg = int(self.lineFreg.text())
        self.labelFreg.setText(str(chd * freg / 100) + " litros")
        self.lineLavavajillas.setText("0")
        lavavajillas = int(self.lineLavavajillas.text())
        self.labelLavavajillas.setText(str(chd * lavavajillas / 100) + " litros")
        self.lineDucha.setText("26")
        ducha = int(self.lineDucha.text())
        self.labelDucha.setText(str(chd * ducha / 100) + " litros")
        self.lineWc.setText("25")
        wc = int(self.lineWc.text())
        self.labelWc.setText(str(chd * wc / 100) + " litros")
        self.lineLavadero.setText("2")
        lavadero = int(self.lineLavadero.text())
        self.labelLavadero.setText(str(chd * lavadero / 100) + " litros")
        self.lineLavadora.setText("9")
        lavadora = int(self.lineLavadora.text())
        self.labelLavadora.setText(str(chd * lavadora / 100) + " litros")
        self.lineGrifos.setText("16")
        grifos = int(self.lineGrifos.text())
        self.labelGrifos.setText(str(chd * grifos / 100) + " litros")
        self.lineFugas.setText("3")
        fugas = int(self.lineFugas.text())
        self.labelFugas.setText(str(chd * fugas / 100) + " litros")
        total = freg + lavavajillas + ducha + wc + lavadero + lavadora + grifos + fugas
        self.lineTotal.setText(str(total))
        self.labelTotal.setText(str(chd * total / 100) + " litros")
        self.toolTarifasExt.setEnabled(False)
        self.labelTarifasExt.setEnabled(False)
        self.lineTviv.setText("0")
        self.lineTamDep.setText("0")
        self.lineLimpFrec.setText("0")
        self.lineLimpExt.setText("0")
        self.lineNumLam.setText("0")
        self.lineSrecogida.setText("0")
        self.labelSupRecogida.setText("Superficie de recogida (m<sup>2</sup>)")
        self.lineTmin.setText("0")
        self.lineSrecogidaMin.setText("0")
        self.checkBarras.setVisible(False)
        self.dialGrupo.setVisible(False)
        self.pushReset.setVisible(False)
        self.verticalWidgetToolbar.setVisible(False)
        self.verticalWidgetToolbar2.setVisible(False)
        self.labelDirectorio.setText("")

#        Paletas de colores para archivos cargados/nocargados
        # No cargados -> Rojo
        paletterojo = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 15, 15))
        brush.setStyle(QtCore.Qt.SolidPattern)
        paletterojo.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 15, 15))
        brush.setStyle(QtCore.Qt.SolidPattern)
        paletterojo.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        # Cargados -> Verde
        paletteverde = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(6, 190, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        paletteverde.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(6, 190, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        paletteverde.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)

        self.labelCosteElec.setText("Coste de la energía (€/kWh)")
        self.labelIntEnergetica.setText("- Intensidad energética (kWh/m<sup>3</sup>)")
        self.labelCo2GastElec.setText("- Asociadas al gasto eléctrico(Kg CO<sub>2</sub>/kWh)")
        self.labelCo2Cia.setText("- Emisiones totales (Kg CO<sub>2</sub>/m<sup>3</sup>)")
        self.labelCo2GastElecBomb.setText("Asociadas al gasto eléctrico de las bombas (Kg CO<sub>2</sub>/kWh)")

        #lista de gráficas a mostrar
        lista_inicial = ['Consumo mensual en volumen', 'Consumo mensual en €', 'Nivel del depósito de pluviales', 'Ahorro por medida en volumen', 'Ahorro por medida en €']

         # Creo los widgets para pintar las gráficas de resultados

        self.figure = plt.figure()
        self.figure.patch.set_color('white') #color de alrededor de los ejes
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.verticalLayout_grafica.addWidget(self.canvas)
        self.verticalLayoutToolbar.addWidget(self.toolbar)

        self.figure2 = plt.figure()
        self.figure2.patch.set_color('white') #color de alrededor de los ejes
        self.canvas2 = FigureCanvas(self.figure2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)
        self.verticalLayoutGraficas2.addWidget(self.canvas2)
        self.verticalLayoutToolbar_2.addWidget(self.toolbar2)
        #Para las graficas del dimensionamiento de pluviales
        self.figure3 = plt.figure()
        self.figure3.patch.set_color('white') #color de alrededor de los ejes

        self.canvas3 = FigureCanvas(self.figure3)
        self.toolbar3 = NavigationToolbar(self.canvas3, self)
        self.verticalGrafPluviales.addWidget(self.canvas3)
        self.verticalGrafPluviales.addWidget(self.toolbar3)



        # Señales
        QtCore.QObject.connect(self.lineChd, QtCore.SIGNAL('editingFinished()'), self.reset)
        QtCore.QObject.connect(self.lineFreg, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineLavavajillas, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineDucha, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineWc, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineLavadero, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineLavadora, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineGrifos, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.lineFugas, QtCore.SIGNAL('editingFinished()'), self.microcomp)
        QtCore.QObject.connect(self.pushReset, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.checkReduct, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.checkFont, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.checkLava, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.checkWc, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.checkAcs, QtCore.SIGNAL('clicked()'), self.reset)
        QtCore.QObject.connect(self.radioCont, QtCore.SIGNAL('clicked()'), self.contadores)

        #Comprueba que los datos introducidos son correctos
        QtCore.QObject.connect(self.lineChd, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineTviv, QtCore.SIGNAL('editingFinished()'), self.tipoviviendas)
        QtCore.QObject.connect(self.lineNumLam, QtCore.SIGNAL('editingFinished()'), self.numerolaminas)
        QtCore.QObject.connect(self.lineLimpExt, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineLimpFrec, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineTamDep, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.linePotConsumo, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCauConsumo, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.linePotRiego, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCauRiego, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCosteElec, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineIntEnergetica, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCo2Cia, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCo2GastElec, QtCore.SIGNAL('editingFinished()'), self.comprobar)
        QtCore.QObject.connect(self.lineCo2GastElecBomb, QtCore.SIGNAL('editingFinished()'), self.comprobar)


        QtCore.QObject.connect(self.toolDirectorio, QtCore.SIGNAL('clicked()'), self.abrirdirectorio)
        QtCore.QObject.connect(self.toolDatVeg, QtCore.SIGNAL('clicked()'), self.archivojardin)
        QtCore.QObject.connect(self.toolDatMet, QtCore.SIGNAL('clicked()'), self.archivomet)
        QtCore.QObject.connect(self.toolDatSuelo, QtCore.SIGNAL('clicked()'), self.archivosuelo)
        QtCore.QObject.connect(self.toolTarifas, QtCore.SIGNAL('clicked()'), self.archivotarifas)
        QtCore.QObject.connect(self.toolTarifasExt, QtCore.SIGNAL('clicked()'), self.archivotarifas_exterior)
        QtCore.QObject.connect(self.toolDatElecCo2, QtCore.SIGNAL('clicked()'), self.datoselecco2)

        QtCore.QObject.connect(self.pushCalcular, QtCore.SIGNAL('clicked()'), self.calcular)
        QtCore.QObject.connect(self.checkEtiqMes, QtCore.SIGNAL('clicked()'), self.cambiar_ejes)
        QtCore.QObject.connect(self.checkBarras, QtCore.SIGNAL('clicked()'), self.cambiar_ejes)
        QtCore.QObject.connect(self.dial, QtCore.SIGNAL('valueChanged(int)'), self.cambiar_ejes)
        #Simular depósito de pluviales
        QtCore.QObject.connect(self.lineTmin, QtCore.SIGNAL('editingFinished()'), self.pluviales)
        QtCore.QObject.connect(self.lineTmax, QtCore.SIGNAL('editingFinished()'), self.pluviales)
        QtCore.QObject.connect(self.lineTamDepPluFijo, QtCore.SIGNAL('editingFinished()'), self.pluviales)

        QtCore.QObject.connect(self.lineSrecogidaMin, QtCore.SIGNAL('editingFinished()'), self.recogida)
        QtCore.QObject.connect(self.lineSrecogidaMax, QtCore.SIGNAL('editingFinished()'), self.recogida)
        QtCore.QObject.connect(self.lineTamSuRecFija, QtCore.SIGNAL('editingFinished()'), self.recogida)


        QtCore.QObject.connect(self.radioPluFijo, QtCore.SIGNAL('clicked()'), self.visibletamvar)
        QtCore.QObject.connect(self.radioPluVar, QtCore.SIGNAL('clicked()'), self.visibletamvar)
        QtCore.QObject.connect(self.radioPluFijo, QtCore.SIGNAL('clicked()'), self.pluviales)
        QtCore.QObject.connect(self.radioPluVar, QtCore.SIGNAL('clicked()'), self.pluviales)
        QtCore.QObject.connect(self.radioSrecogidaFijo, QtCore.SIGNAL('clicked()'), self.visibletamvar)
        QtCore.QObject.connect(self.radioSrecogidaVar, QtCore.SIGNAL('clicked()'), self.visibletamvar)
        QtCore.QObject.connect(self.radioSrecogidaFijo, QtCore.SIGNAL('clicked()'), self.recogida)

        QtCore.QObject.connect(self.radioSrecogidaVar, QtCore.SIGNAL('clicked()'), self.recogida)
        QtCore.QObject.connect(self.pushCalcular, QtCore.SIGNAL('clicked()'), self.visibletamvar)
        QtCore.QObject.connect(self.horizontalNumCurvas, QtCore.SIGNAL('valueChanged(int)'), self.numerocurvas)
        QtCore.QObject.connect(self.pushSimular, QtCore.SIGNAL('clicked()'), self.simularpluviales)

        QtCore.QObject.connect(self.pushSimular, QtCore.SIGNAL('clicked()'), self.calcular)

        #Si hago cambios en los datos de entrada deshabilito los resultados
        QtCore.QObject.connect(self.lineChd, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineFreg, QtCore.SIGNAL('editingFinishedtextChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineLavavajillas, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineDucha, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineWc, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineLavadero, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineLavadora, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineGrifos, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineFugas, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.pushReset, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkReduct, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkFont, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkLava, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkWc, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkAcs, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.radioCont, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.toolDatVeg, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.toolDatMet, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.toolDatSuelo, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.toolTarifas, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.toolDatElecCo2, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkRiego, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkLluvRiego, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkLluvWc, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkLluvLext, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkLluvLint, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkGrisLint, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkGrisRiego, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.checkGrisWc, QtCore.SIGNAL('clicked()'), self.simoff)
        QtCore.QObject.connect(self.lineSrecogida, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineTamDep, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineTviv, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineNumLam, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineLimpExt, QtCore.SIGNAL('textChanged()'), self.simoff)
        QtCore.QObject.connect(self.lineLimpFrec, QtCore.SIGNAL('textChanged()'), self.simoff)


        QtCore.QObject.connect(self.comboGrafica, QtCore.SIGNAL('activated(QString)'), self.dibujargraficas)

    # Si varío los porcentajes de algún microcomponente
    def microcomp(self):
        chd = float(self.lineChd.text())
        freg = int(self.lineFreg.text())
        self.labelFreg.setText(str(chd * freg / 100) + " litros")
        lavavajillas = float(self.lineLavavajillas.text())
        self.labelLavavajillas.setText(str(chd * lavavajillas / 100) + " litros")
        ducha = float(self.lineDucha.text())
        self.labelDucha.setText(str(chd * ducha / 100) + " litros")
        wc = float(self.lineWc.text())
        self.labelWc.setText(str(chd * wc / 100) + " litros")
        lavadero = float(self.lineLavadero.text())
        self.labelLavadero.setText(str(chd * lavadero / 100) + " litros")
        lavadora = float(self.lineLavadora.text())
        self.labelLavadora.setText(str(chd * lavadora / 100) + " litros")
        grifos = float(self.lineGrifos.text())
        self.labelGrifos.setText(str(chd * grifos / 100) + " litros")
        fugas = float(self.lineFugas.text())
        self.labelFugas.setText(str(chd * fugas / 100) + " litros")
        total = freg + lavavajillas + ducha + wc + lavadero + lavadora + grifos + fugas
        self.lineTotal.setText(str(total))
        self.labelTotal.setText(str(chd * total / 100) + " litros")

# Si pulsamos el botón reset los porcentajes de los microcomponentes
# vuelven a sus valores originales
    def reset(self):
        global chd
        #MICROCOMPONENTES##-------------------------------------------------------
        # Consumo base
        chd = float(self.lineChd.text())
        #Fregadero
        if self.checkLava.isChecked() & self.checkReduct.isChecked():
            freg = 8
        elif self.checkLava.isChecked() & ~self.checkReduct.isChecked():
            freg = 10
        elif ~self.checkLava.isChecked() & self.checkReduct.isChecked():
            freg = 16
        elif ~self.checkLava.isChecked() & ~self.checkReduct.isChecked():
            freg = 19
        if ~self.checkLava.isChecked() & self.checkAcs.isChecked():
            freg = (chd *freg / 100 - 5) * 100/chd
        #Lavavajillas
        if self.checkLava.isChecked():
            lavavajillas = 1
        else:
            lavavajillas = 0
        #WC
        if self.checkWc.isChecked():
            wc = 19
        else:
            wc = 25
        #Lavadora
        lavadora = 9
        #Duchas
        if self.checkReduct.isChecked():
            ducha = 22
        else:
            ducha = 26
        if self.checkAcs.isChecked():
            ducha = (chd *ducha / 100 - 10) * 100/chd
        # Grifos
        if self.checkReduct.isChecked():
            grifos = 13
        else:
            grifos = 16
        if self.checkAcs.isChecked():
            grifos = (chd *grifos / 100 - 5) * 100/chd
        # Fugas
        if self.checkFont.isChecked():
            fugas = 0
        else:
            fugas = 3
        # Lavadero
        lavadero = 2

        self.lineFreg.setText(str(round(freg)))
        self.labelFreg.setText(str(round(chd * freg / 100, 1)) + " litros")
        self.lineLavavajillas.setText(str(round(lavavajillas, 1)))
        self.labelLavavajillas.setText(str(round(chd * lavavajillas / 100, 1)) + " litros")
        self.lineDucha.setText(str(round(ducha, 1)))
        self.labelDucha.setText(str(round(chd * ducha / 100, 1)) + " litros")
        self.lineWc.setText(str(round(wc, 1)))
        self.labelWc.setText(str(round(chd * wc / 100, 1)) + " litros")
        self.lineLavadero.setText(str(round(lavadero, 1)))
        self.labelLavadero.setText(str(round(chd * lavadero / 100,1)) + " litros")
        self.lineLavadora.setText(str(round(lavadora, 1)))
        self.labelLavadora.setText(str(round(chd * lavadora / 100, 1)) + " litros")
        self.lineGrifos.setText(str(round(grifos, 1)))
        self.labelGrifos.setText(str(round(chd * grifos / 100, 1)) + " litros")
        self.lineFugas.setText(str(round(fugas, 1)))
        self.labelFugas.setText(str(round(chd * fugas / 100, 1)) + " litros")
        total = freg + lavavajillas + ducha + wc + lavadero + lavadora + grifos + fugas
        self.lineTotal.setText(str(round(total, 1)))
        self.labelTotal.setText(str(round(chd * total / 100, 1)) + " litros")

    def contadores(self):
        if self.radioCont.isChecked():
            self.toolTarifasExt.setEnabled(True)
            self.labelTarifasExt.setEnabled(True)
            tarifas_ext ==False
        else:
            self.toolTarifasExt.setEnabled(False)
            self.labelTarifasExt.setEnabled(False)
            tarifas_ext ==True


    def tipoviviendas(self):
        global ntipoviviendas
        try:
            ntipoviviendas = int(self.lineTviv.text())
            if ntipoviviendas<0:
                ntipoviviendas = "no es un numero"
            ntipoviviendas = int(ntipoviviendas)
            self.tableViv.setColumnCount(int(ntipoviviendas))
            self.tableViv.setEnabled(True)
        except ValueError:
            self.lineTviv.setText("0")

    def numerolaminas(self):
        global numlam
        try:
            numlam = int(self.lineNumLam.text())
            if numlam<0:
                numlam = "no es un numero"
            numlam = int(numlam)
            self.tableLamAgua.setColumnCount(int(numlam))
            self.tableLamAgua.setEnabled(True)
        except ValueError:
            self.lineNumLam.setText("0")

    #Comprueba que el tipo dedato introducido es correcto
    def comprobar(self):
        try:
            frec = int(self.lineChd.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineChd.setText("142")
        try:
            consumo = int(self.lineLimpExt.text())
            if consumo<0:
                consumo = "no es un numero"
            consumo = int(consumo)

        except ValueError:
            self.lineLimpExt.setText("0")
        try:
            frec = int(self.lineLimpFrec.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineLimpFrec.setText("0")
        try:
            frec = int(self.lineTamDep.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineTamDep.setText("0")
        try:
            frec = int(self.lineSrecogida.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineSrecogida.setText("0")
        try:
            frec = int(self.linePotConsumo.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.linePotConsumo.setText("0")
        try:
            frec = int(self.linePotRiego.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.linePotRiego.setText("0")
        try:
            frec = int(self.lineCauConsumo.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCauConsumo.setText("0")
        try:
            frec = int(self.lineCauRiego.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCauRiego.setText("0")
        try:
            frec = float(self.lineCosteElec.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCosteElec.setText("0")
        try:
            frec = float(self.lineIntEnergetica.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineIntEnergetica.setText("0")
        try:
            frec = float(self.lineCo2Cia.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCo2Cia.setText("0")
        try:
            frec = float(self.lineCo2GastElec.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCo2GastElec.setText("0")
        try:
            frec = float(self.lineCo2GastElecBomb.text())
            if frec<0:
                frec = "no es un numero"
            frec = int(frec)

        except ValueError:
            self.lineCo2GastElecBomb.setText("0")

    def abrirdirectorio(self):
        global kj; global jardin; global linea; global ind; global datjardin
        global sup; global suprelativa
        global pp; global num_dias; global et0; global evap; global meteorologia
        global djuliano;global mes;global year; global num_meses;global precip
        global vas_max; global suelo
        global iva_ext; global cv_sinbloques_ext; global bloques1_ext; global bloques2_ext; global bloques3_ext
        global cf_ext
        global desc_consumo1_ext;global desc_consumo2_ext; global desc_consumo3_ext
        global cv_bloques1_ext; global cv_bloques2_ext; global cv_bloques3_ext;
        global tarifas_ext; global num_bloques1_ext; global num_bloques2_ext; global num_bloques3_ext
        global inc_cv_bloque1_ext; global inc_cv_bloque2_ext; global inc_cv_bloque3_ext
        global iva; global cv_sinbloques; global bloques1; global bloques2; global bloques3
        global cf; global bloquesxhab1; global bloquesxhab2; global bloquesxhab3
        global desc_consumo1;global desc_consumo2; global desc_consumo3
        global cv_bloques1; global cv_bloques2; global cv_bloques3;
        global tarifas; global num_bloques1; global num_bloques2; global num_bloques3
        global inc_cv_bloque1; global inc_cv_bloque2; global inc_cv_bloque3
        directorio = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.labelDirectorio.setText(directorio)
           # Leo los datos del jardín
        self.toolDatVeg.setPalette(paletteverde) #pongo el texto verde por defecto
        try:
            archivo = directorio + "\Zonas_verdes.txt"
            datjardin = np.loadtxt (archivo ,skiprows=2)
            datjardin = np.matrix(datjardin)
            filas, columnas = datjardin.shape
            linea = np.array(datjardin[:,0])
            linea = linea.astype(int)
            linea = linea.flatten()   #Lo necesito como una array
            ind = np.array([0,1,2])
            ind = ind.astype(int)
            ind = ind.flatten()   #Lo necesito como una array
            kj = datjardin[:,1]                 #Coeficiente de jardin
            sup = datjardin[:,2]                #Sup de las plantas
            srjar = datjardin[:,3]                #Superficie de recogida del jardin
            if sup[0] !=0:
                suprelativa = sup/srjar    #Para multiplicar por pp
            else:
                suprelativa = np.zeros(1)
            jardin = True
            if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                self.pushCalcular.setEnabled(True)
        except :
            self.toolDatVeg.setPalette(paletterojo) #Si hay error lo pongo rojo

        #Datos meteorológicos
        self.toolDatMet.setPalette(paletteverde) #pongo el texto verde por defecto
        try:
            archivo = directorio + "\Meteorologia.txt"
            datmet = np.loadtxt (archivo, delimiter=None, skiprows=2,)
            datmet = np.matrix(datmet)
            diames = np.array(datmet [:,0])
            diames=diames.astype(int)
            mes = np.array(datmet [:,1])
            mes = mes.astype(int)
            year =np.array(datmet [:,2])
            year=year.astype(int)
            precip = datmet [:,3]
            coef_escorrentia = 0.9
            pp = precip * coef_escorrentia
            et0 = datmet[:,4]
            evap = datmet[:,5]
            num_dias = len(diames)
            num_meses = round(num_dias/365.25 * 12)
            djuliano = np.zeros(num_dias)
            fmt = '%d.%m.%Y'
            for i in range(num_dias):
                fecha = str(diames[i][0]) +'.'+ str(mes[i][0]) +'.'+ str(year[i][0])
                dt = datetime.datetime.strptime(fecha, fmt)
                tt = dt.timetuple()
                djuliano[i] = tt.tm_yday
            djuliano = djuliano.astype(int)
            meteorologia = True
            if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                self.pushCalcular.setEnabled(True)
        except :
            self.toolDatMet.setPalette(paletterojo) #Si hay error lo pongo rojo

        ## Datos del suelo
        self.toolDatSuelo.setPalette(paletteverde) #pongo el texto verde por defecto
        try:
            archivo = directorio + "\Suelo.txt"
            datsuelo = np.loadtxt (archivo,delimiter=None, skiprows=2)
            datsuelo = np.matrix(datsuelo)
            filas, columnas = datsuelo.shape
            psuelo = datsuelo[:,1]
            cc = datsuelo[:,2]
            pmp = datsuelo[:,3]
            n_util = cc - pmp
            vas_max = np.multiply(psuelo, n_util)
            suelo = True
            if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                self.pushCalcular.setEnabled(True)
        except :
            self.toolDatSuelo.setPalette(paletterojo) #Si hay error lo pongo rojo


        ## Tarifas de agua
        self.toolTarifas.setPalette(paletteverde) #pongo el texto verde por defecto
        try:
            archivo = directorio + "\Tarifas.txt"
            precios = np.loadtxt(archivo,delimiter=None, skiprows=2)
            precios2 = np.matrix(precios)
            cf = precios[0,0]
            cv_sinbloques = precios[0,1]
            bloques1 = precios[:,2]
            bloquesxhab1 = precios[0,3]
            desc_consumo1 = precios[1,3]
            bloques2 = precios[:,4]
            bloquesxhab2 = precios[0,5]
            desc_consumo2 = precios[1,5]
            bloques3 = precios[:,6]
            bloquesxhab3 = precios[0,7]
            desc_consumo3 = precios[1,7]
            cv_bloques1 = precios[:,8]
            cv_bloques2 = precios[:,9]
            cv_bloques3 = precios[:,10]
            iva = precios [0,11]
            tarifas = True
            # Contabilizo los bloques de consumo que hay e inicializo las variables
            num_bloques1 = len(cv_bloques1) -  np.count_nonzero(np.isnan(cv_bloques1))
            inc_cv_bloque1 = np.zeros(num_bloques1)

            num_bloques2 = len(cv_bloques2) - np.count_nonzero(np.isnan(cv_bloques2))
            inc_cv_bloque2 = np.zeros(num_bloques2)

            num_bloques3 = len(cv_bloques3) - np.count_nonzero(np.isnan(cv_bloques3))
            inc_cv_bloque3 = np.zeros(num_bloques3)
            #Calculo losincrementos de precio de un bloque con el anterior
            if num_bloques1 != 0:
                inc_cv_bloque1[0] = cv_bloques1[0]
                for i in range(num_bloques1-1):
                    inc_cv_bloque1[i+1] = cv_bloques1[i+1] - cv_bloques1[i]

            if num_bloques2 !=0:
                inc_cv_bloque2[0] = cv_bloques2[0]
                for i in range(num_bloques2-1):
                    inc_cv_bloque2[i+1] = cv_bloques2[i+1] - cv_bloques2[i]

            if num_bloques3 !=0:
                inc_cv_bloque3[0] = cv_bloques3[0]
                for i in range(num_bloques3-1):
                    inc_cv_bloque3[i+1] = cv_bloques3[i+1] - cv_bloques3[i]


            if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                self.pushCalcular.setEnabled(True)
        except :
            self.toolTarifas.setPalette(paletterojo) #Si hay error lo pongo rojo

   ## Tarifas de agua de exterior
        self.toolTarifasExt.setPalette(paletteverde) #pongo el texto verde por defecto
        try:
            archivo = directorio + "\Tarifas_exterior.txt"
            precios_ext = np.loadtxt(archivo,delimiter=None, skiprows=2)
            precios2_ext = np.matrix(precios_ext)
            cf_ext = precios_ext[0,0]
            cv_sinbloques_ext = precios_ext[0,1]
            bloques1_ext = precios_ext[:,2]
            bloquesxhab1_ext = precios_ext[0,3]
            desc_consumo1_ext = precios_ext[1,3]
            bloques2_ext = precios_ext[:,4]
            bloquesxhab2_ext = precios_ext[0,5]
            desc_consumo2_ext = precios_ext[1,5]
            bloques3_ext = precios_ext[:,6]
            bloquesxhab3_ext = precios_ext[0,7]
            desc_consumo3_ext = precios_ext[1,7]
            cv_bloques1_ext = precios_ext[:,8]
            cv_bloques2_ext = precios_ext[:,9]
            cv_bloques3_ext = precios_ext[:,10]
            iva_ext = precios_ext [0,11]
            tarifas_ext = True
            # Contabilizo los bloques de consumo que hay e inicializo las variables
            num_bloques1_ext = len(cv_bloques1_ext) -  np.count_nonzero(np.isnan(cv_bloques1_ext))
            inc_cv_bloque1_ext = np.zeros(num_bloques1_ext)

            num_bloques2_ext = len(cv_bloques2_ext) - np.count_nonzero(np.isnan(cv_bloques2_ext))
            inc_cv_bloque2_ext = np.zeros(num_bloques2_ext)

            num_bloques3_ext = len(cv_bloques3_ext) - np.count_nonzero(np.isnan(cv_bloques3_ext))
            inc_cv_bloque3_ext = np.zeros(num_bloques3_ext)
            #Calculo losincrementos de precio de un bloque con el anterior
            if num_bloques1_ext != 0:
                inc_cv_bloque1_ext[0] = cv_bloques1_ext[0]
                for i in range(num_bloques1_ext-1):
                    inc_cv_bloque1_ext[i+1] = cv_bloques1_ext[i+1] - cv_bloques1_ext[i]
            if num_bloques2_ext !=0:
                inc_cv_bloque2_ext[0] = cv_bloques2_ext[0]
                for i in range(num_bloques2-1):
                    inc_cv_bloque2_ext[i+1] = cv_bloques2_ext[i+1] - cv_bloques2_ext[i]
            if num_bloques3_ext !=0:
                inc_cv_bloque3_ext[0] = cv_bloques3_ext[0]
                for i in range(num_bloques3_ext-1):
                    inc_cv_bloque3_ext[i+1] = cv_bloques3_ext[i+1] - cv_bloques3_ext[i]

            if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                self.pushCalcular.setEnabled(True)
        except :
            self.toolTarifasExt.setPalette(paletterojo) #Si hay error lo pongo rojo

#        Leo los datos de electricidad en un archivo por defecto
        self.toolDatElecCo2.setPalette(paletteverde) #Si hay error lo pongo rojo
        try:
            archivo = directorio + "\Electricidad_y_CO2.txt"
            datos = np.genfromtxt (archivo,delimiter=',', skiprows=1)
            datos = np.matrix(datos)
            filas, columnas = datos.shape
            potConsumo = datos[0,1]
            cauConsumo= datos[1,1]
            potRiego= datos[2,1]
            cauRiego= datos[3,1]
            costeElec= datos[4,1]
            intEnergetica= datos[5,1]
            emision_co2_cia= datos[6,1]
            emision_co2_elec= datos[7,1]
            emision_co2_bomba= datos[8,1]

            self.linePotConsumo.setText(str(int(potConsumo)))
            self.linePotRiego.setText(str(int(potRiego)))
            self.lineCauConsumo.setText(str(int(cauConsumo)))
            self.lineCauRiego.setText(str(int(cauRiego)))
            self.lineCosteElec.setText(str(costeElec))
            self.lineIntEnergetica.setText(str(intEnergetica))
            self.lineCo2GastElec.setText(str(emision_co2_elec))
            self.lineCo2Cia.setText(str(emision_co2_cia))
            self.lineCo2GastElecBomb.setText(str(emision_co2_bomba))

        except:
            self.toolDatElecCo2.setPalette(paletterojo) #Si hay error lo pongo rojo

    #Si decido incluir un archivo auxiliar en otra ubicación
    def archivojardin(self):
        global kj; global jardin; global linea; global ind; global datjardin
        global sup; global suprelativa
        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolDatVeg.setPalette(paletteverde) #pongo el texto verde por defecto
            try:
                datjardin = np.loadtxt (nombre_fichero ,skiprows=2)
                datjardin = np.matrix(datjardin)
                filas, columnas = datjardin.shape
                linea = np.array(datjardin[:,0])
                linea = linea.astype(int)
                linea = linea.flatten()   #Lo necesito como una array
                ind = np.linspace(0,len(linea)-1,len(linea))
                ind = ind.astype(int)
                kj = datjardin[:,1]                 #Coeficiente de jardin
                sup = datjardin[:,2]                #Sup de las plantas
                srjar = datjardin[:,3]                #Superficie de recogida del jardin
                if sup[0] !=0:
                    suprelativa = sup/srjar    #Para multiplicar por pp
                else:
                    suprelativa = np.zeros(1)
                jardin = True
                if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                    self.pushCalcular.setEnabled(True)
            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolDatVeg.setPalette(paletterojo) #Si hay error lo pongo rojo

        ## Datos meteorológicos
    def archivomet(self):
        global pp; global num_dias; global et0; global evap; global meteorologia
        global djuliano;global mes;global year; global num_meses;global precip
        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolDatMet.setPalette(paletteverde) #pongo el texto verde por defecto
            try:
                datmet = np.loadtxt (nombre_fichero, delimiter=None, skiprows=2,)
                datmet = np.matrix(datmet)
                diames = np.array(datmet [:,0])
                diames=diames.astype(int)
                mes = np.array(datmet [:,1])
                mes = mes.astype(int)
                year =np.array(datmet [:,2])
                year=year.astype(int)
                precip = datmet [:,3]
                coef_escorrentia = 0.9
                pp = precip * coef_escorrentia
                et0 = datmet[:,4]
                evap = datmet[:,5]
                num_dias = len(diames)
                num_meses = round(num_dias/365.25 * 12)
                djuliano = np.zeros(num_dias)
                fmt = '%d.%m.%Y'
                for i in range(num_dias):
                    fecha = str(diames[i][0]) +'.'+ str(mes[i][0]) +'.'+ str(year[i][0])
                    dt = datetime.datetime.strptime(fecha, fmt)
                    tt = dt.timetuple()
                    djuliano[i] = tt.tm_yday
                djuliano = djuliano.astype(int)
                meteorologia = True
                if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                    self.pushCalcular.setEnabled(True)
            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolDatMet.setPalette(paletterojo) #Si hay error lo pongo rojo

    ## Datos del suelo
    def archivosuelo(self):
        global vas_max; global suelo
        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolDatSuelo.setPalette(paletteverde) #pongo el texto verde por defecto

            try:
                datsuelo = np.loadtxt (nombre_fichero,delimiter=None, skiprows=2)
                datsuelo = np.matrix(datsuelo)
                filas, columnas = datsuelo.shape
                psuelo = datsuelo[:,1]
                cc = datsuelo[:,2]
                pmp = datsuelo[:,3]
                n_util = cc - pmp
                vas_max = np.multiply(psuelo, n_util)
                suelo = True
                if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                    self.pushCalcular.setEnabled(True)
            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolDatSuelo.setPalette(paletterojo) #Si hay error lo pongo rojo

    ## Tarifas de agua
    def archivotarifas(self):
        global iva; global cv_sinbloques; global bloques1; global bloques2; global bloques3
        global cf; global bloquesxhab1; global bloquesxhab2; global bloquesxhab3
        global desc_consumo1;global desc_consumo2; global desc_consumo3
        global cv_bloques1; global cv_bloques2; global cv_bloques3;
        global tarifas; global num_bloques1; global num_bloques2; global num_bloques3
        global inc_cv_bloque1; global inc_cv_bloque2; global inc_cv_bloque3
        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolTarifas.setPalette(paletteverde) #pongo el texto verde por defecto
            try:
                precios = np.loadtxt(nombre_fichero,delimiter=None, skiprows=2)
                precios2 = np.matrix(precios)
                cf = precios[0,0]
                cv_sinbloques = precios[0,1]
                bloques1 = precios[:,2]
                bloquesxhab1 = precios[0,3]
                desc_consumo1 = precios[1,3]
                bloques2 = precios[:,4]
                bloquesxhab2 = precios[0,5]
                desc_consumo2 = precios[1,5]
                bloques3 = precios[:,6]
                bloquesxhab3 = precios[0,7]
                desc_consumo3 = precios[1,7]
                cv_bloques1 = precios[:,8]
                cv_bloques2 = precios[:,9]
                cv_bloques3 = precios[:,10]
                iva = precios [0,11]
                tarifas = True
                # Contabilizo los bloques de consumo que hay e inicializo las variables
                num_bloques1 = len(cv_bloques1) -  np.count_nonzero(np.isnan(cv_bloques1))
                inc_cv_bloque1 = np.zeros(num_bloques1)

                num_bloques2 = len(cv_bloques2) - np.count_nonzero(np.isnan(cv_bloques2))
                inc_cv_bloque2 = np.zeros(num_bloques2)

                num_bloques3 = len(cv_bloques3) - np.count_nonzero(np.isnan(cv_bloques3))
                inc_cv_bloque3 = np.zeros(num_bloques3)


                #Calculo losincrementos de precio de un bloque con el anterior
                if num_bloques1 != 0:
                    inc_cv_bloque1[0] = cv_bloques1[0]
                    for i in range(num_bloques1-1):
                        inc_cv_bloque1[i+1] = cv_bloques1[i+1] - cv_bloques1[i]

                if num_bloques2 !=0:
                    inc_cv_bloque2[0] = cv_bloques2[0]
                    for i in range(num_bloques2-1):
                        inc_cv_bloque2[i+1] = cv_bloques2[i+1] - cv_bloques2[i]

                if num_bloques3 !=0:
                    inc_cv_bloque3[0] = cv_bloques3[0]
                    for i in range(num_bloques3-1):
                        inc_cv_bloque3[i+1] = cv_bloques3[i+1] - cv_bloques3[i]


                if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                    self.pushCalcular.setEnabled(True)
            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolTarifas.setPalette(paletterojo) #Si hay error lo pongo rojo

    ## Tarifas de agua
    def archivotarifas_exterior(self):
        global iva_ext; global cv_sinbloques_ext; global bloques1_ext; global bloques2_ext; global bloques3_ext
        global cf_ext
        global desc_consumo1_ext;global desc_consumo2_ext; global desc_consumo3_ext
        global cv_bloques1_ext; global cv_bloques2_ext; global cv_bloques3_ext;
        global tarifas_ext; global num_bloques1_ext; global num_bloques2_ext; global num_bloques3_ext
        global inc_cv_bloque1_ext; global inc_cv_bloque2_ext; global inc_cv_bloque3_ext
        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolTarifasExt.setPalette(paletteverde) #pongo el texto verde por defecto
            try:
                precios_ext = np.loadtxt(nombre_fichero,delimiter=None, skiprows=2)
                precios2_ext = np.matrix(precios_ext)
                cf_ext = precios_ext[0,0]
                cv_sinbloques_ext = precios_ext[0,1]
                bloques1_ext = precios_ext[:,2]
                bloquesxhab1_ext = precios_ext[0,3]
                desc_consumo1_ext = precios_ext[1,3]
                bloques2_ext = precios_ext[:,4]
                bloquesxhab2_ext = precios_ext[0,5]
                desc_consumo2_ext = precios_ext[1,5]
                bloques3_ext = precios_ext[:,6]
                bloquesxhab3_ext = precios_ext[0,7]
                desc_consumo3_ext = precios_ext[1,7]
                cv_bloques1_ext = precios_ext[:,8]
                cv_bloques2_ext = precios_ext[:,9]
                cv_bloques3_ext = precios_ext[:,10]
                iva_ext = precios_ext [0,11]
                tarifas_ext = True
                # Contabilizo los bloques de consumo que hay e inicializo las variables
                num_bloques1_ext = len(cv_bloques1_ext) -  np.count_nonzero(np.isnan(cv_bloques1_ext))
                inc_cv_bloque1_ext = np.zeros(num_bloques1_ext)

                num_bloques2_ext = len(cv_bloques2_ext) - np.count_nonzero(np.isnan(cv_bloques2_ext))
                inc_cv_bloque2_ext = np.zeros(num_bloques2_ext)

                num_bloques3_ext = len(cv_bloques3_ext) - np.count_nonzero(np.isnan(cv_bloques3_ext))
                inc_cv_bloque3_ext = np.zeros(num_bloques3_ext)


                #Calculo losincrementos de precio de un bloque con el anterior
                if num_bloques1_ext != 0:
                    inc_cv_bloque1_ext[0] = cv_bloques1_ext[0]
                    for i in range(num_bloques1_ext-1):
                        inc_cv_bloque1_ext[i+1] = cv_bloques1_ext[i+1] - cv_bloques1_ext[i]

                if num_bloques2_ext !=0:
                    inc_cv_bloque2_ext[0] = cv_bloques2_ext[0]
                    for i in range(num_bloques2-1):
                        inc_cv_bloque2_ext[i+1] = cv_bloques2_ext[i+1] - cv_bloques2_ext[i]

                if num_bloques3_ext !=0:
                    inc_cv_bloque3_ext[0] = cv_bloques3_ext[0]
                    for i in range(num_bloques3_ext-1):
                        inc_cv_bloque3_ext[i+1] = cv_bloques3_ext[i+1] - cv_bloques3_ext[i]


                if tarifas == True and suelo == True and meteorologia == True and jardin == True and tarifas_ext ==True:
                    self.pushCalcular.setEnabled(True)
            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolTarifasExt.setPalette(paletterojo) #Si hay error lo pongo rojo

    ## Datos del suelo
    def datoselecco2(self):

        nombre_fichero = QtGui.QFileDialog.getOpenFileName(self, "Abrir fichero", self.ruta)
        if nombre_fichero:
            self.fichero_actual = nombre_fichero
            self.rutaJardin = QtCore.QFileInfo(nombre_fichero).path()
            self.toolDatElecCo2.setPalette(paletteverde) #pongo el texto verde por defecto
            try:
                datos = np.genfromtxt (nombre_fichero, delimiter=',', skiprows=1)
                datos = np.matrix(datos)
                filas, columnas = datos.shape
                potConsumo = datos[0,1]
                cauConsumo= datos[1,1]
                potRiego= datos[2,1]
                cauRiego= datos[3,1]
                costeElec= datos[4,1]
                intEnergetica= datos[5,1]
                emision_co2_cia= datos[6,1]
                emision_co2_elec= datos[7,1]
                emision_co2_bomba= datos[8,1]

                self.linePotConsumo.setText(str(int(potConsumo)))
                self.linePotRiego.setText(str(int(potRiego)))
                self.lineCauConsumo.setText(str(int(cauConsumo)))
                self.lineCauRiego.setText(str(int(cauRiego)))
                self.lineCosteElec.setText(str(costeElec))
                self.lineIntEnergetica.setText(str(intEnergetica))
                self.lineCo2GastElec.setText(str(emision_co2_elec))
                self.lineCo2Cia.setText(str(emision_co2_cia))
                self.lineCo2GastElecBomb.setText(str(emision_co2_bomba))

            except :
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error de archivo")
                error.showMessage("El archivo introducido no es correcto. Por favor introduzca un archivo válido.")
                self.toolDatElecCo2.setPalette(paletterojo) #Si hay error lo pongo rojo
    # Si hago cambios en algun dato desactivo la opción de simular para que
    #haya que calcular todo otra vez
    def simoff(self):
        self.tabPluviales.setEnabled(False)
        self.tabGraficas.setEnabled(False)
    def cambiar_ejes(self):
        self.dibujargraficas(self.comboGrafica.currentText())

##-----------------------------------------------------------------------------
    #%% definimos la funcion que realizara el balance
    def hacer_balance(self, cubierta_piscina,cubierta, consumo_opt, riegooptimizado, dep1_out1, dep1_out2, dep1_out3, dep2_out1,
        dep2_out2, in1_dep1, in1_dep2, in2_dep1, in2_dep2,dep1_out4, dep2_out3, dep2_out4, dep1_out5, dep1_out6, cont_separados, c_limpext, lavavajillas, reductores, wc_efic, recir_acs, inst_nueva, porc, limres, sup_rec_pis, nivel_pisc_max,
        inverano, finverano, vad_pluviales_max, vriego, vriego_unitario,kj_max, vas, chd_base, srecogida, spiscina, hab,
        vas_max, num_dias, evap, et0, pp, djuliano, mes, year):


        ##MICROCOMPONENTES##-------------------------------------------------------
        if consumo_opt:
            pass
        else:
            lavavajillas, reductores, recir_acs, wc_efic, inst_nueva = False, False, False, False, False

        #Fregadero
        if lavavajillas & reductores:
            c_freg = chd_base * 0.08
        elif lavavajillas & ~reductores:
            c_freg = chd_base * 0.10
        elif ~lavavajillas & reductores:
            c_freg = chd_base * 0.16
        elif ~lavavajillas & ~reductores:
            c_freg = chd_base * 0.19

        if recir_acs:
            c_freg = c_freg - 5

        #Lavavajillas
        if lavavajillas:
            c_lavavajillas = chd_base * 0.01
        else:
            c_lavavajillas = chd_base * 0

        #WC
        if wc_efic:
            c_wc = chd_base * 0.19
        else:
            c_wc = chd_base * 0.25

        #Lavadora
        c_lavadora = chd_base * 0.09

        #Duchas
        if reductores:
            c_ducha = chd_base * 0.22
        else:
            c_ducha = chd_base * 0.26

        if recir_acs:
            c_ducha = c_ducha - 10

        # Grifos
        if reductores:
            c_grifo = chd_base * 0.13
        else:
            c_grifo = chd_base * 0.16
        if recir_acs:
            c_grifo = c_grifo - 5

        # Fugas
        if inst_nueva:
            c_fuga = chd_base *  0
        else:
            c_fuga = chd_base * 0.03

        # Lavadero
        c_lavadero = chd_base * 0.02


        microcomp = [c_freg, c_wc, c_lavadora, c_lavadero, c_ducha, c_grifo, c_lavavajillas, c_fuga]

        #----------------------------------------------------------------------
        grises = c_lavadora + c_lavadero + c_ducha + c_grifo
        negras = c_wc + c_freg + c_lavavajillas
        vad_residuales_max = round(sum(grises) * 2 / 100) * 100 # Volumen del depósito de almacenamiento de grises para otros usos

        ##Inicializamos las variables
        vad_pluviales = np.zeros(num_dias)
        vad_pluviales[0] = vad_pluviales_max/2  #Volumen del deposito, comenzamos a la mitad

        vriegototal = np.zeros((num_dias, int(max(linea))))    #Volumen de riego acumulado
        nivel_pisc = np.zeros([num_dias, numlam])         #nivel de la piscina 0 llena a su nivel óptimo
        riegototal = np.zeros(num_dias)
        riego_red = np.zeros(num_dias)
        riego_pisc = np.zeros([num_dias, numlam])
        vol_desbord_pisc = np.zeros([num_dias, numlam])
        R1 = np.zeros(num_dias)
        R2 = np.zeros(num_dias)
        negras_red1 = np.zeros(num_dias)
        negras_red2 = np.zeros(num_dias)
        riego_red1 = np.zeros(num_dias)
        riego_red2 = np.zeros(num_dias)
        limpieza_red = np.zeros(num_dias)
        limpieza_red2 = np.zeros(num_dias)
        limpext_red = np.zeros(num_dias)
        limpext_red2 = np.zeros(num_dias)
        cdomestico_diario = np.zeros(num_dias)
        cexteriores = np.zeros(num_dias)
        duchaygrifos_red = np.zeros(num_dias)
        piscina_red = np.zeros(num_dias)

        vol_bombeado_consumo =np.zeros(num_dias)
        vol_bombeado_riego =np.zeros(num_dias)

        if cont_separados:
            consumo_diario = np.zeros([num_dias, ntipoviviendas+1], dtype=float)
            consumo_mensual = np.zeros([round(num_dias/365.25 * 12), ntipoviviendas+1], dtype=float)
            consumo_mensual_e = np.zeros([round(num_dias/365.25 * 12), ntipoviviendas+1], dtype=float)
        else:
            consumo_diario = np.zeros(num_dias)
            consumo_mensual = np.zeros((round(num_dias/365.25 * 12), 1))
            consumo_mensual_e = np.zeros((round(num_dias/365.25 * 12), 1))

        mes_actual = 0

        ## Cálculos generales dia a dia
        for i in range(1, num_dias):

            ## RIEGO #########################################################
            ## Balance de agua en el SUELO
            for j in range(int(max(linea))):
                # Condición de infiltración profunda
                if vas[j,i-1] <= 0.1 * vas_max[j]:
                    ip = 0                   #Infiltración profunda
                else:
                    ip = 0.01 * vas[j, i-1]

                # volumen acumulado en el suelo
                vas [j,i]= vas [j,i-1] + pp [i] *suprelativa[j] - ip - et0 [i] * kj_max[j]
                vriegototal[i,j] = 0             # No se riega, a menos que entre en el caso 2 del siguiente if

                if vas [j,i] > vas_max [j]:        #Supera su capacida máxima
                    vas [j,i] = vas_max [j]        #El volumnen del suelo no puede pasar de la capacidad de campo

                elif vas [j,i] < limres:          # Si hay muy poca agua en el suelo, riego con el vol�men prefijado
                    vas [j,i] = vriego_unitario[j]
                    ind1 = ind[np.where(linea == j+1)]   #Selecciono solo la linea actual (varias zonas)
                    vriegototal[i,j] = vriego[j]    #volumen de riego total


                riegototal[i] = sum (vriegototal [i, :])       #acumulo el riego de todas las líneas en cada dia
                riegototal[i] += riegototal[i] * (0.3 * (1 - riegooptimizado)) #Controla si el riego está o no optimizado, si no lo está se incrementa en un 25#
                riego_red[i] = riegototal[i]                 #Que parte del riego se hace desde la red

            ## PISCINA #################################################################################################
            ## Cálculo del nivel de la piscina, en función de si hay cubierta o no
            if cubierta == False:
                cubierta_piscina2 = np.zeros(len(cubierta_piscina)).astype(bool) #La que tenga cubierta se la quito
            else:
                cubierta_piscina2 = cubierta_piscina
            if numlam != 0:    #Si existe piscina
                for z in range(numlam):
                    if cubierta_piscina2[z]:     # Si hay cubierta

                        if djuliano[i] < inverano or djuliano[i] > finverano:   #si no es verano
                            nivel_pisc[i, z] = nivel_pisc[i-1, z] + precip[i]

                            if nivel_pisc[i, z] > nivel_pisc_max:
                                nivel_pisc[i, z] = nivel_pisc_max

                        else:
                            nivel_pisc [i, z] = nivel_pisc[i-1, z] - evap[i] + precip[i] * sup_rec_pis[z]/spiscina[z]  #Si es verano

                    else:  # Si no hay cubierta
                        nivel_pisc[i, z] = nivel_pisc[i-1, z] - evap[i] + precip[i] * sup_rec_pis[z] / spiscina[z]


                    if nivel_pisc [i, z] > nivel_pisc_max:     #nivel m�ximo de la piscina
                        vol_desbord_pisc[i, z] = (nivel_pisc[i, z] - nivel_pisc_max) * spiscina[z] #Volumen que no se aprovecha de la piscina por desbordamiento o filtraci�n de la parte superior de la piscina mal impermeabilizada
                        nivel_pisc [i, z] = nivel_pisc_max


                    #Condición para el relleno de la piscina
                    if nivel_pisc [i, z] <= -100: #La piscina se rellena cuando baje el nivel m�s de 100 mm
                        riego_pisc[i, z] = abs(nivel_pisc [i, z]) * spiscina[z]
                        nivel_pisc[i, z] = 0
                    else:
                        riego_pisc [i, z] = 0


            ## BAlANCES DEPÓSITOS ###########################################
            ## Balances de los depósitos y cálculo del gasto desde la red.
            R1[0] = 0
            R2[0] = 0  #inicializamos los depósitos
            V1 = [srecogida * pp.item(i), sum(grises), sum(negras), riegototal[i]]  #MAtrices de variables de entrada y salida a los depÓsitos
            V2 = [srecogida * pp.item(i), sum(grises), sum(negras), riegototal[i]]


            #Matriz de decisiones
            D1 = np.matrix([in1_dep1, in2_dep1, -dep1_out1, -dep1_out2])    #Depósito pluviales
            D2 = np.matrix([in1_dep2, in2_dep2, -dep2_out1, -dep2_out2])   #Depósito aguas grises

            ### Entradas a los depósitos
            D1_trans = D1.T
            inplu = V1 [:2] * D1_trans[:2]        #Lo que entra
            inplu = inplu.item(0)
            R1[i] = R1.item(i-1) + inplu
            R2[i] = R2.item(i-1) + sum(grises)

            if R1[i] > vad_pluviales_max:
                R1[i] = vad_pluviales_max

            if R2 [i] > vad_residuales_max:
                R2 [i] = vad_residuales_max

            ## GRISES ##-----------------------------------------------------------
            # Grises - WC
            if dep2_out1:
              R2[i] = R2 [i] - sum(c_wc)
              if R2 [i] < 0:
                  negras_red1[i] = abs(R2[i])
                  R2[i] = 0
              else:
                  negras_red1[i] = 0

            else:
                  negras_red1[i] = sum(c_wc)

              # Grises - Limpieza interior (lavadero+lavadora)
            if dep2_out4:
                R2[i] = R2[i] - (sum(c_lavadero) + sum(c_lavadora))
                if R2[i] < 0:
                    limpieza_red[i] = abs(R2[i])
                    R2[i] = 0
                else:
                    limpieza_red[i] = 0
            else:
              limpieza_red[i] = sum(c_lavadero) + sum(c_lavadora)

            #Grises - limpieza exterior
            if dep2_out3:
                R2[i] = R2[i] - c_limpext[i]
                if R2[i] < 0:
                    limpext_red[i] = abs(R2[i])
                    R2[i] = 0
                else:
                  limpext_red[i] = 0

            else:
              limpext_red[i] = c_limpext[i]

            # Grises - Riego
            if dep2_out2:
              R2 [i] = R2 [i] - riegototal[i]
              if R2[i] < 0:
                  riego_red1[i] = abs(R2 [i])
                  R2[i] = 0
              else:
                  riego_red1[i] = 0

            else:
              riego_red1[i] = riegototal[i]


            ## Pluviales ##--------------------------------------------------

            # Pluviales - Riego
            if dep1_out2:
              R1[i] = R1[i] - riego_red1[i]
              if R1[i] < 0:
                  riego_red2[i] = abs(R1[i])
                  R1[i] = 0
              else:
                  riego_red2[i] = 0

            else:
              riego_red2[i] = riego_red1[i]

            # Pluviales - WC
            if dep1_out1:
              R1[i] = R1[i] - negras_red1[i]
              if R1[i] < 0:
                  negras_red2[i] = abs(R1[i])
                  R1[i] = 0
              else:
                  negras_red2[i] = 0

            else:
              negras_red2[i] = negras_red1[i]

              # Pluviales - Limpieza interior (lavadero+lavadora)
            if dep1_out3:
                R1[i] = R1[i] - limpieza_red[i]
                if R1[i] < 0:
                    limpieza_red2[i] = abs(R1[i])
                    R1[i] = 0
                else:
                    limpieza_red[i] = 0

            else:
              limpieza_red2[i] = limpieza_red[i]

             #Lluvia - limpieza exterior
            if dep1_out4:
              R1[i] = R1[i] - limpext_red[i]
              if R1[i] < 0:
                  limpext_red2[i] = abs(R1[i])
                  R1[i] = 0
              else:
                  limpext_red2[i] = 0

            else:
              limpext_red2[i] = limpext_red[i]

             #Luvia para duchas y grifos
            if dep1_out5:
              R1[i] = R1[i] - (sum(c_lavavajillas)+sum(c_freg)+sum(c_ducha)+sum(c_grifo))
              if R1[i] < 0:
                  duchaygrifos_red[i] = abs(R1[i])
                  R1[i] = 0
              else:
                  duchaygrifos_red[i] = 0

            else:
              duchaygrifos_red[i] = sum(c_lavavajillas)+sum(c_freg)+sum(c_ducha)+sum(c_grifo)

             #Luvia para rellenar la piscina
            if dep1_out6:
              R1[i] = R1[i] - sum(riego_pisc[i,:])
              if R1[i] < 0:
                  piscina_red[i] = abs(R1[i])
                  R1[i] = 0
              else:
                  piscina_red[i] = 0

            else:
              piscina_red[i] = sum(riego_pisc[i,:])

            ## CONSUMO DIARIO TOTAL
            cdomestico_diario[i] = (duchaygrifos_red[i] + sum(c_fuga) + negras_red2[i]
            + limpieza_red2[i])

            cexteriores[i] = riego_red2[i] + limpext_red2[i] + piscina_red[i]


            vol_bombeado_consumo[i]= ((sum(c_wc)+ sum(c_lavadora)+ sum(c_lavadero)
            +sum(c_lavavajillas)+sum(c_freg)+sum(c_ducha)+sum(c_grifo)+sum(riego_pisc[i,:]))
            -( limpext_red2[i] + limpieza_red2[i] + negras_red2[i] + duchaygrifos_red[i] + piscina_red[i]))

            vol_bombeado_riego[i] = riegototal[i] - riego_red2[i]


            #Si los contadores son individuales y hay otro por vivienda
            if cont_separados:
                for j in range(len(habitantes[1])):
                    consumo_diario[i][j] = cdomestico_diario[i] / hab * habitantes[1][j]
                consumo_diario[i][len(habitantes[1])] = cexteriores[i]
            else:
                consumo_diario[i] = cdomestico_diario[i] + cexteriores[i]


            ##    Agrupamos los consumos por meses

            if mes.item(i) == mes.item(i-1):
                consumo_mensual[mes_actual] = consumo_mensual[mes_actual] + consumo_diario[i]

            else:
                mes_actual += 1

                consumo_mensual[mes_actual] = consumo_diario[i]

        # Sumas totales por tipo de gasto
        suma_riego_red = sum(riego_red2 )
        suma_riegototal = sum(riegototal )
        sum_volbomb_consumo = sum(vol_bombeado_consumo)
        sum_volbomb_riego = sum(vol_bombeado_riego)


        suma_riegopisc = sum(riego_pisc / 1000)
        suma_limpieza =  sum(limpieza_red / 1000)
        consumo_diario = consumo_diario.T
        consumo_mensual = consumo_mensual / 1000


        ## CONSUMO MENSUAL EN EUROS
        if cont_separados:
            z = range(ntipoviviendas)

            #Calculo los precios para el consumo de EXTERIORES
            for t in range(len(consumo_mensual)):

                #Multiplico todo el consumo por los costes fijos y los variables del
                #primer bloque, luego le añado para cada bloque el consumo multiplicado
                #por la diferencia de precio con respecto al bloque anterior  [el
                #sobrecoste]

                consumo_mensual_e[t, -1] = cf + consumo_mensual [t, -1] * cv_sinbloques

                #Bloques 1
                if len(bloques1_ext) != sum(np.isnan(bloques1_ext)):
                    if consumo_mensual [t, -1] - desc_consumo1_ext > 0:
                        consumo_mensual_e [t, -1] += (consumo_mensual [t, -1] - desc_consumo1_ext) * cv_bloques1_ext[0]
                        for j in range(1, len(cv_bloques1_ext) - sum(np.isnan(bloques1_ext))):
                            if  (consumo_mensual[t, -1] - desc_consumo1_ext) > bloques1_ext[j]:
                                consumo_mensual_e[t, -1] += (consumo_mensual[t, -1] - desc_consumo1_ext - bloques1_ext[j]) * inc_cv_bloque1_ext[j]

                #Bloques 2
                if len(bloques2_ext) != sum(np.isnan(bloques2_ext)):
                    if consumo_mensual [t, -1] - desc_consumo2_ext > 0:
                        consumo_mensual_e [t, -1] += (consumo_mensual [t, -1] - desc_consumo2_ext) * cv_bloques2_ext[0]
                        for j in range(1, len(cv_bloques2_ext) - sum(np.isnan(bloques2_ext))):
                            if  (consumo_mensual[t, -1] - desc_consumo2_ext) > bloques2_ext[j]:
                                consumo_mensual_e[t, -1] += (consumo_mensual[t, -1] - desc_consumo2_ext - bloques2_ext[j]) * inc_cv_bloque2_ext[j]

                #Bloques 3
                if len(bloques3_ext) != sum(np.isnan(bloques3_ext)):
                    if consumo_mensual [t, -1] - desc_consumo3_ext > 0:
                        consumo_mensual_e [t, -1] += (consumo_mensual [t, -1] - desc_consumo3_ext) * cv_bloques3_ext[0]
                        for j in range(1, len(cv_bloques3_ext) - sum(np.isnan(bloques3_ext))):
                            if  (consumo_mensual[t, -1] - desc_consumo3_ext) > bloques3_ext[j]:
                                consumo_mensual_e[t, -1] += (consumo_mensual[t, -1] - desc_consumo3_ext - bloques3_ext[j]) * inc_cv_bloque3_ext[j]
        else:
            z = np.zeros(1)
       #Calculo el precio de los consumos

        for k in range(ntipoviviendas):

            #Calculo el CONSUMO DOMÉSTICO
            for t in range(len(consumo_mensual)):

                #Multiplico todo el consumo por los costes fijos y los variables del
                #primer bloque, luego le añado para cada bloque el consumo multiplicado
                #por la diferencia de precio con respecto al bloque anterior  [el
                #sobrecoste]

                consumo_mensual_e[t, k] = cf + consumo_mensual [t, k] * cv_sinbloques

                #Bloques 1
                if len(bloques1) != sum(np.isnan(bloques1)):
                    if consumo_mensual [t, k] - desc_consumo1 > 0:
                        consumo_mensual_e [t, k] += (consumo_mensual [t, k] - desc_consumo1) * cv_bloques1[0]
                        for j in range(1, len(cv_bloques1) - sum(np.isnan(bloques1))):
                            if  (consumo_mensual[t, k] - desc_consumo1) > bloques1b[j][k]:
                                consumo_mensual_e[t, k] += (consumo_mensual[t, k] - desc_consumo1 - bloques1b[j][k]) * inc_cv_bloque1[j]

                #Bloques 2
                if len(bloques2) != sum(np.isnan(bloques2)):
                    if consumo_mensual [t, k] - desc_consumo2 > 0:
                        consumo_mensual_e [t, k] += (consumo_mensual [t, k] - desc_consumo2) * cv_bloques2[0]
                        for j in range(1, len(cv_bloques2) - sum(np.isnan(bloques2))):
                            if  (consumo_mensual[t, k] - desc_consumo2) > bloques2b[j][k]:
                                consumo_mensual_e[t, k] += (consumo_mensual[t, k] - desc_consumo2 - bloques2b[j][k]) * inc_cv_bloque2[j]

                #Bloques 3
                if len(bloques3) != sum(np.isnan(bloques3)):
                    if consumo_mensual [t, k] - desc_consumo3 > 0:
                        consumo_mensual_e [t, k] += (consumo_mensual [t, k] - desc_consumo3) * cv_bloques3[0]
                        for j in range(1, len(cv_bloques3) - sum(np.isnan(bloques3))):
                            if  (consumo_mensual[t, k] - desc_consumo3) > bloques3b[j][k]:
                                consumo_mensual_e[t, k] += (consumo_mensual[t, k] - desc_consumo3 - bloques3b[j][k]) * inc_cv_bloque3[j]



        # Le aplico el IVA
        consumo_mensual_e = consumo_mensual_e  * (1 + iva/100)

        if cont_separados:
            consumo_mensual[:,:-1] =  consumo_mensual[:,:-1] * habitantes [0]
            consumo_mensual_total = sum(consumo_mensual.T)
            consumo_total_litros = sum(consumo_mensual_total)*1000

            consumo_mensual_e[:,:-1] =  consumo_mensual_e[:,:-1] * habitantes [0]
            consumo_mensuale_total = sum(consumo_mensual_e.T)
            consumo_total_euros = sum(consumo_mensuale_total)
        else:
            consumo_mensual_total = consumo_mensual
            consumo_total_litros = sum(consumo_mensual_total)*1000

            consumo_mensuale_total = consumo_mensual_e
            consumo_total_euros = sum(consumo_mensuale_total)




        consumodomestico_total = consumo_total_litros - suma_riegototal - suma_riegopisc

        consumotipos = [consumodomestico_total, suma_riegototal, suma_riegopisc,
            sum_volbomb_consumo, sum_volbomb_riego]


        return (consumo_mensual_total, consumo_mensuale_total, consumodomestico_total, consumotipos,
                consumo_total_litros, consumo_total_euros, suma_limpieza, R1, microcomp, consumo_diario, cdomestico_diario)


##----------------------------------------------------------------------------
    def calcular(self):
        global medidas; global ntipoviviendas; global balance;global kj_max;global habitantes
        global cubierta_piscina;global cubierta; global consumo_opt;global riegooptimizado;global dep1_out1
        global dep1_out2;global dep1_out3;global dep2_out1; global dep2_out2;global in1_dep1
        global in1_dep2;global in2_dep1;global in2_dep2;global dep1_out4;global dep2_out3
        global cont_separados;global c_limpext;global lavavajillas;global reductores
        global wc_efic;global recir_acs;global inst_nueva;global porc;global limres
        global sup_rec_pis;global nivel_pisc_max;global inverano;global finverano;global vad_pluviales_max
        global vriego;global vriego_unitario;global vas;global chd_base;global srecogida
        global spiscina;global hab; global inc_cv_bloque1;global inc_cv_bloque2
        global inc_cv_bloque3;global cf;global cv_sinbloques;global cv_bloques1;global cv_bloques2
        global cv_bloques3;global iva;global vas_max;global num_dias;global evap
        global et0;global pp;global djuliano;global mes;global year; global linea
        global bloques1b; global bloques2b; global bloques3b; global lista;global nocero

        global R1; global medidas_elegidas;global ahorro_total_pesos
        global ahorro_total_pesose; global consumo_mensualantes; global consumo_mensualeantes
        global consumo_mensual; global consumo_mensuale
        global consumo_total_sumadoe; global consumo_total_litros; global consumo_total_euros
        global consumo_total_litrosantes; global consumo_total_eurosantes
        global atp_medidas_elegidas; global atpe_medidas_elegidas
        global ahorro_total_pesos_descendente; global atp_descendente_medidas
        global ahorro_total_pesose_descendente; global atpe_descendente_medidas
        global ind2;global ind1; global maximo; global cjardin; global datprov

        self.tabGraficas.setEnabled(True)
        self.tabPluviales.setEnabled(True)

        ##%% Datos de entrada del proyecto a entrar por pantalla
        balance = True
        ##MICROCOMPONENTES del consumo doméstico--------------------------------------

        habitantes = np.zeros([2, ntipoviviendas], dtype=int)
        for q in range(2):
            for w in range(ntipoviviendas):
                habitantes[q][w] = int(self.tableViv.item(q, w).text())    #viviendas


        hab = sum(habitantes[0] * habitantes[1])    #numero total de personas
        viv = sum(habitantes[0])    #numero total de habitantes

        chd_base = chd
        chd_base = chd_base * habitantes[0] * habitantes[1]

        #Contadores separados por vivienda y otro para zonas comunes
        if self.radioCont.isChecked():
            cont_separados = True
        else:
            cont_separados = False

        if cont_separados:
            dim=ntipoviviendas
        else:
            dim = 1

        bloques1b =np.zeros((len(bloques1),dim))
        bloques2b =np.zeros((len(bloques2),dim))
        bloques3b =np.zeros((len(bloques3),dim))

        for k in range(dim):
            #Si los bloques son en función del numero de habitantes
            if bloquesxhab1:
                bloques1b[:,k] = bloques1 * habitantes[1][k]
            else:
                bloques1b[:,k] = bloques1
            if bloquesxhab2:
                bloques2b[:,k] = bloques2 * habitantes[1][k]
            else:
                bloques2b[:,k] = bloques2
            if bloquesxhab3:
                bloques3b[:,k] = bloques3 * habitantes[1][k]
            else:
                bloques3b[:,k] = bloques3

        ###EXTERIOR##------------------------------------------------------------------
        ##Jardín
        #Láminas de agua

        if numlam != 0:
            spiscina = np.zeros(numlam, dtype=int)
            sup_rec_pis = np.zeros(numlam, dtype=int)
            cubiertasn = np.zeros(numlam, dtype=str)
            cubierta_piscina = np.zeros(numlam, dtype=int)
            for w in range(numlam):
                spiscina[w] = int(self.tableLamAgua.item(0, w).text())
                sup_rec_pis[w] = int(self.tableLamAgua.item(1, w).text())
                cubiertasn[w] = self.tableLamAgua.item(2, w).text()
                if cubiertasn[w]=="S" or cubiertasn[w]=="s":
                    cubierta_piscina[w] = True
                elif cubiertasn[w]=="N" or cubiertasn[w]=="n":
                    cubierta_piscina[w] = False
        else:
             spiscina = np.zeros(1, dtype=int)
             sup_rec_pis = np.zeros(1, dtype=int)
             cubierta_piscina = np.zeros(1, dtype=bool)



        inverano = 166          # Día que destapamos la piscina 166=15 Junio
        finverano = 253         # Día que la volvemos a tapar 253 = 10 septiembre
        nivel_pisc_max = 100    # Nivel máximo de la piscina para que no haya pérdidas [0 = nivel de funcionamiento habitual]


        #Otros consumos (puede ser cualquier cosa pero se usa en el codigo como
        #si fuese para limieza de exteriores
        frec_limp =  int(self.lineLimpFrec.text())
        gasto_limpieza = int(self.lineLimpExt.text())
        #Gastos limpieza exteriores
        if gasto_limpieza !=0:
            c_limpext = np.zeros(frec_limp-1)
            c_limpext  = list(c_limpext )
            c_limpext .append(gasto_limpieza)
            c_limpext  = c_limpext  * (round(num_dias / frec_limp) + 1)
            c_limpext = np.array(c_limpext)
        else:
            c_limpext = np.zeros(num_dias)



        #Datos de energía y CO2
        potConsumo = int(self.linePotConsumo.text())
        potRiego = int(self.linePotRiego.text())
        cauConsumo = int(self.lineCauConsumo.text())
        cauRiego = int(self.lineCauRiego.text())
        costeElec = float(self.lineCosteElec.text())
        intEnergetica = float(self.lineIntEnergetica.text())
        emision_co2_elec = float(self.lineCo2GastElec.text())
        emision_co2_cia = float(self.lineCo2Cia.text())
        emision_co2_bomba = float(self.lineCo2GastElecBomb.text())


        porc = 50               # Tanto por ciento de la capacidad de campo a la que queremos regar [#]
        limres = 2              # Límite de la reserva en el suelo a partir de la cual deber�amos regar [mm]


        vad_pluviales_max = int(self.lineTamDep.text())       #volumen del deposito de pluviales
        srecogida = int(self.lineSrecogida.text())
        #TARIFAS
        #Si las tarifas van en funcion del número de habitantes modifico los bloques





        ## Eleccion del tipo de riego

        #Los volumenes referidos al suelo sera todos en l/m2 (mm)
        #los volumenes del deposito son en litros
        #elegimos que zona tiene un mayor kj para calcular el tiempo de riego de referencia
        #ind2 = np.matlib.zeros((15, 15))
        vriego = np.zeros(max(linea))
        vriego_unitario = np.zeros(max(linea))
        vas = np.zeros((max(linea), num_dias))
        kj_max = np.zeros(max(linea))

        for j in range(int(max(linea))):
            try:
                del datprov, datprov2
            except NameError:
                pass
            ind1 = ind[np.where(linea == j+1)]
            datprov = datjardin[ind1,:]              #Datos de la linea j
            indprov = ind[ind1]

            #Kj Máximo
            maximo = max(datprov[:,1])
            maximo = np.array(maximo).flatten()[0]
            #ind2 = linea[np.where( datprov < maximo + 0.1 and datprov > maximo - 0.1 )]
            cjardin = np.array(datprov[:,1]).flatten()
#            ind2 = datprov[np.where( np.isclose(cjardin, maximo,  0.01 )), 0]
            ind2 = indprov[np.where(cjardin == maximo) ]
            ind2 = np.array(ind2).flatten().astype(int)

            #ind2 = np.searchsorted(datprov, max(datprov))    #Datos de las zonas con el kj m�s alto
            datprov2 = datjardin[ind2]
            id_actual = ind[ind2[0]]
                                          #Escogemos de referencia la primera zona de las que cumplan
            kj_max[j] = datjardin[id_actual, 1]    #El id de la zona escogida

            #calculamos el tiempo de riego necesario para llevar el suelo a un # capacidad de campo

            vriego_unitario[j] = vas_max[j] * porc/100                      #volumen de agua (l) por m2 en cada riego
            vriego[j] = vriego_unitario[j] * sup[id_actual]          #Tiempo (h) de riego para que se llegue al vol�men requerido la zona con m�s consumo



            vas[j,0] = vas_max.item(j)


        # MEDÍDAS A APLICAR

        #Consumo domestico
        lavavajillas = self.checkLava.isChecked()
        reductores = self.checkReduct.isChecked()
        wc_efic = self.checkWc.isChecked()
        recir_acs = self.checkAcs.isChecked()
        inst_nueva = self.checkFont.isChecked()
        decisiones_domestico = [lavavajillas, reductores, wc_efic, recir_acs, inst_nueva]
        if any(decisiones_domestico):
            consumo_opt = True         #consumo doméstico optimizado
        else:
            consumo_opt = False

        #in1_dep1 = True        #Recogemos aguas lluvia

        dep1_out2 = self.checkLluvRiego.isChecked()       #Regamos con agua de lluvia
        dep1_out1 = self.checkLluvWc.isChecked()       #Usamos lluvia para WC
        dep1_out3 = self.checkLluvLint.isChecked()       #Lluvia para la limpieza interior
        dep1_out4 = self.checkLluvLext.isChecked()       #Lluvia para la limpieza exterior
        dep1_out5 = self.checkLluvDucha.isChecked()       #Lluvia para la limpieza exterior
        dep1_out6 = self.checkLluvPiscina.isChecked()       #Lluvia para la limpieza exterior


        dep2_out1 = self.checkGrisWc.isChecked()       #Aguas grises para WC
        dep2_out2 = self.checkGrisRiego.isChecked()       #Usamos grises para riego
        dep2_out3 = self.checkGrisLext.isChecked()       #Usamos grises para limpieza exterior
        dep2_out4 = self.checkGrisLint.isChecked()       #Usamos grises para limpieza interior


        #Si alguna de las láminas de agua tiene cubierta
        if all(v== False for v in cubierta_piscina):
            cubierta = False
        else:
            cubierta = True

        riegooptimizado = self.checkRiego.isChecked()     #La red de riego está optimizada

        medidas = [cubierta, consumo_opt, riegooptimizado,
        dep2_out2, dep2_out1, dep1_out2, dep1_out1, dep1_out3, dep1_out4, dep2_out3, dep2_out4, dep1_out5, dep1_out6]
        #medidas = np.array(medidas)
        nocero = np.where(medidas)
        #Si hay menos de dos medidasnomuestralas graficas de medidas (tarta o barras)
        if len(nocero[0])<2:
            lista = lista_inicial[:3]
        else:
            lista = lista_inicial
        self.comboGrafica.clear()
        self.comboGrafica.addItems(lista)
        medidas_nombre = ['Cubierta-piscina','Consumo doméstico ','Riego optimizado ','Grises-Riego ','Grises-WC ',
            'Pluviales-riego ','Pluviales-WC ', 'Lluvia-limpieza', 'Lluvia-otros',
            'Grises-otros', 'Grises-limpieza', 'Lluvia-grifos', 'Lluvia-piscina']
        medidas_elegidas =  [None] * len(nocero[0])
        for i in range(len(nocero[0])):
            medidas_elegidas[i] = medidas_nombre[nocero[0][i]]


        medidas2 = np.zeros(len(medidas)).astype(bool)
        consumo_total_pesos = np.zeros((len(nocero[0]),2))


        ##%% Hago el balance para las medidas propuestas
        (consumo_mensual, consumo_mensuale, consumodomestico_total, consumotipos, consumo_total_litros, consumo_total_euros, suma_limpieza,R1, microcomp, consumo_diario, cdomestico_diario) = self.hacer_balance(cubierta_piscina,cubierta, consumo_opt, riegooptimizado, dep1_out1, dep1_out2, dep1_out3, dep2_out1,
                      dep2_out2, in1_dep1, in1_dep2,  in2_dep1, in2_dep2, dep1_out4, dep2_out3, dep2_out4, dep1_out5, dep1_out6, cont_separados, c_limpext, lavavajillas, reductores, wc_efic, recir_acs, inst_nueva, porc, limres, sup_rec_pis, nivel_pisc_max,
                      inverano, finverano, vad_pluviales_max, vriego, vriego_unitario,kj_max, vas, chd_base, srecogida, spiscina, hab,
                      vas_max, num_dias, evap, et0, pp, djuliano, mes, year)


        #%% Balance sin medidas

        (consumo_mensualantes, consumo_mensualeantes, consumodomestico_totalantes, consumotiposantes,
        consumo_total_litrosantes, consumo_total_eurosantes, suma_limpiezaantes, R1antes, microcomp_antes, consumo_diario_antes,
        cdomestico_diario_antes) = self.hacer_balance(cubierta_piscina,False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, cont_separados,
        c_limpext, False, False, False, False, False, porc, limres, sup_rec_pis, nivel_pisc_max, inverano, finverano, vad_pluviales_max, vriego, vriego_unitario,
        kj_max, vas, chd_base, srecogida, spiscina, hab, vas_max, num_dias, evap, et0, pp, djuliano, mes, year)



        del R1antes
        consumo_total_pesos = np.zeros(len(nocero[0]))
        consumo_total_pesose = np.zeros(len(nocero[0]))
        ahorro_total_pesose = np.zeros(len(nocero[0]))
        ahorro_total_pesos = np.zeros(len(nocero[0]))


        #%%  Balance por medidas
        for s in range(len(nocero[0])):

            medidas2[:] = medidas[:] #medidas originales
            medidas2[nocero[0][s]] = False #Va eliminando las medidas que no son cero

            cubierta = medidas2[0]
            consumo_opt = medidas2[1]
            riegooptimizado = medidas2[2]
            dep2_out2 = medidas2[3]
            dep2_out1 = medidas2[4]
            dep1_out2 = medidas2[5]
            dep1_out1 = medidas2[6]
            dep1_out3 = medidas2[7]
            dep1_out4 = medidas2[8]
            dep2_out3 = medidas2[9]
            dep2_out4 = medidas2[10]
            dep1_out5 = medidas2[11]
            dep1_out6 = medidas2[12]

            #microcomponentes
            if consumo_opt == False:
                lavavajillas_p = False
                reductores_p = False
                wc_efic_p = False
                recir_acs_p = False
                inst_nueva_p = False
            else:
                lavavajillas_p = lavavajillas
                reductores_p = reductores
                wc_efic_p = wc_efic
                recir_acs_p = recir_acs
                inst_nueva_p = inst_nueva


            (consumo_mensual_p, consumo_mensuale_p, consumodomestico_total_p, consumotipos_p, consumo_total_litros_p, consumo_total_euros_p, suma_limpieza_p, R1_p,microcomp_p,  consumo_diario_p, cdomestico_diario_p) = self.hacer_balance(cubierta_piscina, cubierta, consumo_opt, riegooptimizado, dep1_out1, dep1_out2, dep1_out3, dep2_out1,
                      dep2_out2, in1_dep1, in1_dep2,  in2_dep1, in2_dep2, dep1_out4, dep2_out3, dep2_out4, dep1_out5, dep1_out6, cont_separados, c_limpext, lavavajillas_p, reductores_p, wc_efic_p, recir_acs_p, inst_nueva_p, porc, limres, sup_rec_pis, nivel_pisc_max,
                      inverano, finverano, vad_pluviales_max, vriego, vriego_unitario, kj_max, vas, chd_base, srecogida, spiscina, hab,
                      vas_max, num_dias, evap, et0, pp, djuliano, mes, year)

            consumo_total_pesos[s] = consumo_total_litros_p
            consumo_total_pesose[s] = consumo_total_euros_p

        ahorrom3 = (- consumo_total_litros + consumo_total_litrosantes)/1000
        ahorroeur = - consumo_total_euros + consumo_total_eurosantes

        # Reducimos las dimensiones de los vectores resultado para poder dibujarlos bien
        consumo_mensual = consumo_mensual.flatten()
        consumo_mensuale = consumo_mensuale.flatten()
        consumo_mensualantes = consumo_mensualantes.flatten()
        consumo_mensualeantes = consumo_mensualeantes.flatten()

        costeElec = float(self.lineCosteElec.text())
        intEnergetica = float(self.lineIntEnergetica.text())
        co2_elec = float(self.lineCo2GastElec.text())
        co2_cia = float(self.lineCo2Cia.text())
        co2_bomba = float(self.lineCo2GastElecBomb.text())

        sum_volbomb_consumo = consumotipos[3]
        sum_volbomb_riego = consumotipos [4]
        elec_consumo = potConsumo/1000 * sum_volbomb_consumo/cauConsumo
        elec_riego = potRiego/1000 * sum_volbomb_riego/cauRiego
        total_elec = elec_consumo + elec_riego
        gasto_elec = total_elec * costeElec
        emision_co2_cia = ahorrom3 * co2_cia
        emision_co2_elec = ahorrom3* intEnergetica * co2_elec
        emision_co2_bomba = total_elec * co2_bomba
        ahorro_co2_cia = emision_co2_cia - emision_co2_bomba
        ahorro_co2_elec = emision_co2_elec - emision_co2_bomba


        # Muestro los resultados por pantalla

        self.labelPeriodoSim.setText("Periodo de simulación de "+ str(int(num_meses/12))+ " años" )
        self.labelConM3.setText(str(int(consumo_total_litros/1000))+ " m<sup>3" )
        self.labelSinM3.setText(str(int(consumo_total_litrosantes/1000))+ " m<sup>3")
        self.labelConEur.setText(str(int(consumo_total_euros))+ " €")
        self.labelSinEur.setText(str(int(consumo_total_eurosantes))+ " €")

        if consumo_total_litrosantes==0:
            porcm3 = 0
        else:
            porcm3 = ahorrom3 * 100/ (consumo_total_litrosantes/1000)
        if consumo_total_litrosantes==0:
            porceur = 0
        else:
            porceur = ahorroeur * 100/ consumo_total_eurosantes

        self.labelAhM3.setText(str(int(ahorrom3))+ " m<sup>3")
        self.labelAhEur.setText(str(int(ahorroeur))+ " €")
        self.labelPorcM3.setText(str(int(porcm3))+ " %")
        self.labelPorcEur.setText(str(int(porceur))+ " %")
        self.labelConsEnergetico.setText(str(round(total_elec,1))+ " kWh")
        self.labelCosteEnergetico.setText(str(round(gasto_elec,1))+ " €")
        self.labelAhCo2Elec.setText(str(int(ahorro_co2_elec))+ " Kg CO<sub>2")
        self.labelAhCo2CIA.setText(str(int(ahorro_co2_cia))+ " Kg CO<sub>2")

        #Ahorro de cada una delas medidas

        for s in range(len(nocero[0])):
            ahorro_total_pesos[s] = (consumo_total_pesos[s] - consumo_total_litros)/1000
            ahorro_total_pesose[s] = consumo_total_pesose[s] - consumo_total_euros

        #Los ordeno, intercalando uno de ahorro grande con uno de ahorro pequeño
        #para que no se solapen al hacer la gráfica de tarta
        if len(nocero[0])>1:
            unidos = list(zip(ahorro_total_pesos, medidas_elegidas))
            sort1 = sorted(unidos, key=itemgetter(0))
            sort2 = sorted( unidos, reverse=True)
            sort3 =sort1 *2
            z=0
            for s in range(len(medidas_elegidas)):
                sort3[z] = sort1[s]
                sort3[z+1] = sort2[s]
                z = z+ 2
            unidos2 = sort3[:len(medidas_elegidas)]
            ahorro_total_pesos, atp_medidas_elegidas = zip(*unidos2)

            unidose = list(zip(ahorro_total_pesose, medidas_elegidas))
            sorte1 = sorted(unidose, key=itemgetter(0))
            sorte2 = sorted(unidose, reverse=True)
            sorte3 =sorte1 *2
            z=0
            for s in range(len(medidas_elegidas)):
                sorte3[z] = sorte1[s]
                sorte3[z+1] = sorte2[s]
                z = z+ 2
            unidose2 = sorte3[:len(medidas_elegidas)]
            ahorro_total_pesose, atpe_medidas_elegidas = zip(*unidose2)


            unidos3 = sorted(unidos, key=itemgetter(0), reverse = True)
            ahorro_total_pesos_descendente, atp_descendente_medidas =zip(*unidos3)

            unidose4 = sorted(unidose, key=itemgetter(0), reverse = True)
            ahorro_total_pesose_descendente, atpe_descendente_medidas =zip(*unidose4)



        self.dibujargraficas(self.comboGrafica.currentText())
    def visibletamvar (self):
        global tamdepfijo; global tamrecfijo
        tamdepfijo = self.radioPluFijo.isChecked()
        tamrecfijo = self.radioSrecogidaFijo.isChecked()
        if tamdepfijo:
            self.groupTamDepVar.setEnabled(False)
            self.lineTamDepPluFijo.setEnabled(True)
            self.groupNumCurvas.setEnabled(False)

        else:
            self.groupTamDepVar.setEnabled(True)
            self.lineTamDepPluFijo.setEnabled(False)

        if tamrecfijo:
            self.groupSrecogidaVar.setEnabled(False)
            self.groupNumCurvas.setEnabled(False)
            self.lineTamSuRecFija.setEnabled(True)
        else:
            self.groupSrecogidaVar.setEnabled(True)
            self.lineTamSuRecFija.setEnabled(False)
            self.groupNumCurvas.setEnabled(True)
            if tamdepfijo:
                self.groupNumCurvas.setEnabled(False)

    def recogida(self):
        global reclimsup; global rec_limsup
        global recliminf;global rec_liminf
        global recogida

        if tamrecfijo:
            try:
                rec = int(self.lineTamSuRecFija.text())      #volumen minimo del dep pluviales para la simulacion
                if rec<0:
                    rec= "no es un numero"
                rec = int(rec)
                recogida = True
            except ValueError:
                recogida = False
                self.lineTamSuRecFija.clear()

            if recogida:
                self.pushSimular.setEnabled(True)
            else:
                self.pushSimular.setEnabled(False)
        else:
            try:
                rec_limsup = int(self.lineSrecogidaMax.text())      #volumen minimo del dep pluviales para la simulacion
                if rec_limsup<0:
                    rec_limsup = "no es un numero"
                rec_limsup = int(rec_limsup)
                reclimsup = True
            except ValueError:
                reclimsup = False
                self.lineSrecogidaMax.clear()

            try:
                rec_liminf = int(self.lineSrecogidaMin.text())      #volumen minimo del dep pluviales para la simulacion
                if rec_liminf<0:
                    rec_liminf = "no es un numero"
                rec_liminf = int(rec_liminf)
                recliminf = True
            except ValueError:
                recliminf = False
                self.lineSrecogidaMin.clear()
            if recliminf and reclimsup:
                recogida = True
            else:
                recogida = False
        self.botonsimular()

    def pluviales(self):
        global plu_liminf; global liminf
        global plu_limsup; global limsup
        global pluviales

        if tamdepfijo:
            try:
                plu_tam = int(self.lineTamDepPluFijo.text())      #volumen minimo del dep pluviales para la simulacion
                if plu_tam<0:
                    plu_tam = "no es un numero"
                plu_tam = int(plu_tam)
                pluviales = True
            except ValueError:
                pluviales = False
                self.lineTamDepPluFijo.clear()

        else:

            try:
                plu_liminf = int(self.lineTmin.text())      #volumen minimo del dep pluviales para la simulacion
                if plu_liminf<0:
                    plu_liminf = "no es un numero"
                plu_liminf = int(plu_liminf)
                liminf = True
            except ValueError:
                liminf = False
                self.lineTmin.clear()

            try:
                plu_limsup = int(self.lineTmax.text())      #volumen minimo del dep pluviales para la simulacion
                if plu_limsup<0:
                    plu_limsup = "no es un numero"
                plu_limsup = int(plu_limsup)
                limsup = True
            except ValueError:
                limsup = False
                self.lineTmax.clear()

            if liminf and limsup:
                pluviales = True
            else:
                pluviales = False

        self.botonsimular()

    def botonsimular(self):
        if pluviales and recogida:
            self.pushSimular.setEnabled(True)
        else:
            self.pushSimular.setEnabled(False)

    # line del tamaño mínimo de pluviales

    def numerocurvas(self):
        global numcurv
        numcurv = int(self.horizontalNumCurvas.value())
        self.labelNumCurvas.setText(str(numcurv))

    def simularpluviales(self):
        global medidas;
        global cubierta_piscina; global consumo_opt;global riegooptimizado;global dep1_out1
        global dep1_out2;global dep1_out3;global dep2_out1; global dep2_out2;global in1_dep1
        global in1_dep2;global in2_dep1;global in2_dep2;global dep1_out4;global dep2_out3
        global cont_separados;global c_limpext;global lavavajillas;global reductores
        global wc_efic;global recir_acs;global inst_nueva;global porc;global limres
        global sup_rec_pis;global nivel_pisc_max;global inverano;
        global vriego;global vriego_unitario;global vas;global chd_base;global srecogida
        global spiscina;global hab; global inc_cv_bloque1;global inc_cv_bloque2
        global inc_cv_bloque3;global cf;global cv_sinbloques;global cv_bloques1;global cv_bloques2
        global cv_bloques3;global iva;global vas_max;global num_dias;global evap
        global et0;global pp;global djuliano;global mes;global year
        global plu_limsup; global plu_liminf; global consumo_var
        global ysp; global yspe; global consumo_varan; global consumo_evaran
        global consumo_varan2; global consumo_evaran2; global srecogida_var2
        #Limpio las graficas de dimensionamiento de pluviales
        plt.close()
        a = self.figure3
        a.clear()
        self.canvas3.draw()

        numcurv = int(self.horizontalNumCurvas.value())
        tamdepfijo = self.radioPluFijo.isChecked()
        tamrecfijo = self.radioSrecogidaFijo.isChecked()
        if tamrecfijo:
            num_depositos = 10
        else:
            num_depositos = 5

        try:
            if tamdepfijo:
                vad_pluviales_max_var = np.zeros(1) + int(self.lineTamDepPluFijo.text())
                srecogida_var = np.linspace(rec_liminf,rec_limsup, 10)
                len_srecogida_var = 10
                len_vad_pluviales_max_var = 1
            else:
                if plu_limsup - plu_liminf <0:
                    condicion = "Limites del tamaño de depósto incorrectos"
                else:
                    condicion = 1
                condicion = int(condicion) #nos dará un error si los límites del depósito
                #no están bien
                vad_pluviales_max_var = np.linspace(plu_liminf, plu_limsup, num_depositos)
                len_vad_pluviales_max_var = num_depositos
            if tamrecfijo:
                srecogida_var = np.zeros(1) + int(self.lineTamSuRecFija.text())
                len_srecogida_var = 1
            else:
                if rec_limsup - rec_liminf <0:
                    condicion2 = "Limites del tamaño de depósto incorrectos"
                else:
                    condicion2 = 1

                    if tamdepfijo:
                        pass
                    else:
                        srecogida_var = np.linspace(rec_liminf,rec_limsup, numcurv)
                        len_srecogida_var = numcurv

                condicion2 = int(condicion2) #nos dará un error si los límites del depósito
                #no están bien puestos
            # Construimos un vector con diferentes tamaños de depósito

            consumo_var = np.zeros((len_vad_pluviales_max_var,len_srecogida_var))
            consumo_varan = np.zeros((len_vad_pluviales_max_var,len_srecogida_var))
            consumo_evar = np.zeros((len_vad_pluviales_max_var,len_srecogida_var))
            consumo_evaran = np.zeros((len_vad_pluviales_max_var,len_srecogida_var))

            cubierta = medidas[0]
            consumo_opt = medidas[1]          #***********************
            riegooptimizado = medidas[2]
            dep2_out2 = medidas[3]
            dep2_out1 = medidas[4]
            dep1_out2 = medidas[5]
            dep1_out1 = medidas[6]
            dep1_out3 = medidas[7]
            dep1_out4 = medidas[8]
            dep2_out3 = medidas[9]
            dep2_out4 = medidas[10]
            dep1_out5 = medidas[11]
            dep1_out6 = medidas[12]


            for s in range(len_vad_pluviales_max_var):
                vad_pluviales_max = vad_pluviales_max_var[s]
                for r in range (len_srecogida_var):
                    srecogida = srecogida_var[r]
                    #%% Hago el balance para las medidas propuestas
                    (consumo_mensual_v, consumo_mensual_ev, consumodomestico_total_v, consumotipos_v, consumo_total_litros_v, consumo_total_euros_v, suma_limpieza_v,R1_v, microcomp_v, consumo_diario_v, cdomestico_diario_v) = self.hacer_balance(cubierta_piscina,cubierta, consumo_opt, riegooptimizado, dep1_out1, dep1_out2, dep1_out3, dep2_out1,
                              dep2_out2, in1_dep1, in1_dep2,  in2_dep1, in2_dep2, dep1_out4, dep2_out3, dep2_out4, dep1_out5, dep1_out6, cont_separados, c_limpext, lavavajillas, reductores, wc_efic, recir_acs, inst_nueva, porc, limres, sup_rec_pis, nivel_pisc_max,
                              inverano, finverano, vad_pluviales_max, vriego, vriego_unitario,kj_max, vas, chd_base, srecogida, spiscina, hab,
                              vas_max, num_dias, evap, et0, pp, djuliano, mes, year)


                    # Consumo total para cada tamaño de depósito
                    consumo_var[s,r] = consumo_total_litros_v/1000
                    consumo_varan[s,r] = consumo_var[s,r] / round(num_dias / 365) # Consumo anual


                    # Consumo total para cada tamaño de depósito
                    consumo_evar[s,r] = consumo_total_euros_v
                    consumo_evaran[s,r] = consumo_evar[s,r] / round(num_dias / 365) # Consumo anual
            if tamdepfijo:
                x = np.linspace(rec_liminf, rec_limsup, 100)

    #            ysp = InterpolatedUnivariateSpline(srecogida_var, consumo_varan)(x)  # Llamamos a la clase con x
    #            yspe = InterpolatedUnivariateSpline(srecogida_var, consumo_evaran)(x)  # Llamamos a la clase con x

                ysp = np.interp(x, srecogida_var, consumo_varan[0])
                yspe = np.interp(x, srecogida_var, consumo_evaran[0])

                ahorro_plu = ysp[0] - ysp
                ahorroe_plu = yspe[0] - yspe

                if ahorro_plu[1] < 0.001:
                    ahorro_plu = np.round(ahorro_plu)
                if ahorroe_plu[1]<0.001:
                    ahorroe_plu = np.round(ahorroe_plu)

            else:
                x = np.linspace(plu_liminf, plu_limsup, 100)
                ysp = np.zeros((len(x),len_srecogida_var))
                yspe = np.zeros((len(x),len_srecogida_var))
                ahorro_plu = np.zeros((len(x),len_srecogida_var))
                ahorroe_plu = np.zeros((len(x),len_srecogida_var))
                for r in range (len_srecogida_var):
    #                ysp[:,r] = InterpolatedUnivariateSpline(vad_pluviales_max_var, consumo_varan[:,r])(x)  # Llamamos a la clase con x
    #                yspe[:,r] = InterpolatedUnivariateSpline(vad_pluviales_max_var, consumo_evaran[:,r])(x)  # Llamamos a la clase con x

                    consumo_varan2 = consumo_varan.T
                    consumo_evaran2 = consumo_evaran.T

                    ysp[:,r] = np.interp(x, vad_pluviales_max_var, consumo_varan2[r])
                    yspe[:,r] = np.interp(x, vad_pluviales_max_var, consumo_evaran2[r])

                    ahorroe_plu[:,r] = yspe[0,r] - yspe[:,r]
                    ahorro_plu[:,r] = ysp[0,r] - ysp[:,r]

                    if ahorro_plu[1,r] < 0.001:
                        ahorro_plu[r] = np.round(ahorro_plu[r])
                    if ahorroe_plu[1,r]<0.001:
                        ahorroe_plu[r] = np.round(ahorroe_plu[r])


            #dibujo los resultados de ahorro vs. tamaño de depósito
            # create an axis
            self.figure3.suptitle('Ahorro anual')
            ax2 = self.figure3.add_subplot(211)
            ax3 = self.figure3.add_subplot(212)

            ax2.hold(False);ax3.hold(False)

            # plot data
            ax2.plot(x,ahorro_plu)
            ax3.plot(x,ahorroe_plu)
            ax2.grid();ax3.grid()
            if tamdepfijo:
                ax2.set_ylabel('$m^3$')


                ax3.set_xlabel('Superficie de recogida en $m^2$')
                ax3.set_ylabel('€')

            else:
                ax2.set_ylabel('$m^3$')
                leyenda = np.array(srecogida_var, dtype=int)
                leyenda = list(leyenda)
                box2 = ax2.get_position()
                box3 = ax3.get_position()
                ax2.set_position([box2.x0, box2.y0, box2.width * 0.9, box2.height])
                ax3.set_position([box3.x0, box3.y0, box3.width * 0.9, box3.height])

                ax2.legend(leyenda, loc='center left',bbox_to_anchor=(1, 0.5),
                    fancybox=True, fontsize=10)

                ax3.set_xlabel('Tamaño del depósito en litros')
                ax3.set_ylabel('€')

            self.canvas3.draw()
        except ValueError:
                error = QtGui.QErrorMessage(self)
                error.setWindowTitle("Error en los valores")
                error.showMessage("El tamaño mínimo del depósito no puede ser más grande que el máximo")

    def dibujargraficas(self, text):
        global lista; global consumo_mensual_total; global consumo_mensual_totale
        global num_meses; global R1;global x_meses
        plt.close()
        mostrar_mes = self.checkEtiqMes.isChecked()       #Aguas grises para WC
        self.dialGrupo.setVisible(False)
        self.checkBarras.setVisible(False)
        self.checkEtiqMes.setVisible(False)
        self.verticalWidgetToolbar.setVisible(False)
        self.verticalWidgetToolbar2.setVisible(False)

        x = range(num_meses)
        x_meses = ['E', 'F','M', 'A', 'My','J','Jl','Ag','S','O','N','D']
        x_meses = x_meses * int(num_meses/12)
        x_meses = np.array(x_meses)
        y = range(num_dias)
        z = np.array(range(num_meses))
        posicion = np.array(range(len(medidas_elegidas))) + 1
        # create an axis
        ax = self.figure.add_subplot(111)
        ax2 = self.figure2.add_subplot(111)
        ax.clear(); ax2.clear()

        ax.axis('auto'); ax2.axis('equal')


        if text == lista[0]:
            self.checkEtiqMes.setVisible(True)
            ax.bar(x, consumo_mensualantes, color=(1,0,0),align='center')
            ax.bar(x, consumo_mensual,color='b', alpha = 0.5,align='center' )
            ax.grid()

            if mostrar_mes:
                ax.set_xticks(z)
                ax.set_xticklabels(x_meses)
                ax.set_xlabel('Mes')
            else:
                ax.set_xticks(np.array(range(int(num_meses/12)))*12)
                ax.set_xticklabels(np.array(range(int(num_meses/12)))+1)
                ax.set_xlabel('Año')
            ax.set_ylabel('$m^3$')
            ax.set_xlim([0, num_meses - 1])
            ax.set_title('Consumo mensual')
            self.verticalWidgetToolbar.setVisible(True)
            self.figure.tight_layout()
            self.canvas.draw()


        if text == lista[1]:
            self.checkEtiqMes.setVisible(True)
            ax.grid()
            ax.bar(x, consumo_mensualeantes, color='r',align='center')
            ax.bar(x, consumo_mensuale,color='b', alpha=0.5,align='center' )
            if mostrar_mes:
                ax.set_xticks(z)
                ax.set_xticklabels(x_meses)
                ax.set_xlabel('Mes')
            else:
                ax.set_xticks(np.array(range(int(num_meses/12)))*12)
                ax.set_xticklabels(np.array(range(int(num_meses/12)))+1)
                ax.set_xlabel('Año')
            ax.set_ylabel('€')
            ax.set_xlim([0, num_meses - 1])
            ax.set_title('Consumo mensual')
            self.verticalWidgetToolbar.setVisible(True)
            self.figure.tight_layout()
            self.canvas.draw()

        if text == lista[2]:
            self.checkEtiqMes.setVisible(True)
            ax.grid()
            ax.plot(y, R1,color =(0.04,0.45,0.59))
            ax.fill_between(y, 0, R1, facecolor=(0.04,0.45,0.59))

            ax.set_ylabel('Litros')
            ax.set_xlim([0, num_dias - 1])

            if mostrar_mes:
                ax.set_xticks(np.linspace(0,num_dias, num_meses))
                ax.set_xticklabels(x_meses)
                ax.set_xlabel('Mes')
            else:
                ax.set_xticks(np.array(range(int(num_meses/12)))*365)
                ax.set_xticklabels(np.array(range(int(num_meses/12)))+1)
                ax.set_xlabel('Año')
            self.verticalWidgetToolbar.setVisible(True)
            self.figure.tight_layout()
            self.canvas.draw()

        if len(nocero[0])>1:
            if text == lista[3]:
                self.checkBarras.setVisible(True)
                barras = self.checkBarras.isChecked()
                if barras:
                    ax.grid()
                    ax.bar(posicion, ahorro_total_pesos_descendente, align = 'center',color =(0.04,0.45,0.59))
                    ax.set_xticklabels(atp_descendente_medidas, rotation=30)
                    ax.set_xticks(posicion)
                    ax.set_ylabel('$m^3$')
                    self.verticalWidgetToolbar.setVisible(True)
                    self.figure.tight_layout()
                    self.canvas.draw()

                else:
                    self.dialGrupo.setVisible(True)
                    angulocero = self.dial.value()-90
                    number = len(medidas_elegidas)
                    cmap = plt.get_cmap('Blues')

                    colores = [cmap(i) for i in np.linspace(0.25, 0.6, number)]

                    edge, t1, t2 = ax2.pie(ahorro_total_pesos, labels = atp_medidas_elegidas, colors=colores,
                            autopct='%1.1f%%', shadow=False, startangle=angulocero)
                    for w in edge:
                        w.set_linewidth( 0.5 )
                        w.set_edgecolor( 'gray' )
                    self.verticalWidgetToolbar2.setVisible(True)
                    self.figure2.tight_layout()
                    self.canvas2.draw()


            if text == lista[4]:
                self.checkBarras.setVisible(True)
                barras = self.checkBarras.isChecked()
                if barras:
                    ax.grid()
                    ax.bar(posicion, ahorro_total_pesose_descendente, align = 'center', color =(0.04,0.45,0.59))
                    ax.set_xticklabels(atp_descendente_medidas, rotation=30)
                    ax.set_xticks(posicion)
                    ax.set_ylabel('€')
                    self.verticalWidgetToolbar.setVisible(True)
                    self.figure.tight_layout()
                    self.canvas.draw()
                else:
                    self.dialGrupo.setVisible(True)
                    angulocero = self.dial.value()-90
                    number = len(medidas_elegidas)
                    cmap = plt.get_cmap('Blues')

                    colores = [cmap(i) for i in np.linspace(0.25, 0.6, number)]

                    edge, t1, t2 = ax2.pie(ahorro_total_pesose, labels = atpe_medidas_elegidas, colors=colores,
                            autopct='%1.1f%%', shadow=False, startangle=angulocero)
                    for w in edge:
                        w.set_linewidth( 0.5 )
                        w.set_edgecolor( 'gray' )
                    self.verticalWidgetToolbar2.setVisible(True)
                    self.figure2.tight_layout()
                    self.canvas2.draw()


app = QtGui.QApplication(sys.argv)
MiVentana = MiFormulario(None)
MiVentana.setWindowTitle("MHS1")
MiVentana.show()
sys.exit(app.exec_())
