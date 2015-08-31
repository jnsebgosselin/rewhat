# -*- coding: utf-8 -*-
"""
Copyright 2014-2015 Jean-Sebastien Gosselin

email: jnsebgosselin@gmail.com

This file is part of WHAT (Well Hydrograph Analysis Toolbox).

WHAT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

#---- STANDARD LIBRARY IMPORTS ----

import csv
import sys
import os
import copy

#---- THIRD PARTY IMPORTS ----

from PySide import QtGui, QtCore
from PySide.QtCore import QDate

import numpy as np
from xlrd.xldate import xldate_from_date_tuple
from xlrd import xldate_as_tuple
import xlwt

#---- PERSONAL IMPORTS ----

import HydroCalc
import database as db
import hydrograph3 as hydroprint
import mplFigViewer3 as mplFigViewer
import meteo
import MyQWidget

#==============================================================================
        
class HydroprintGUI(QtGui.QWidget):                           # HydroprintGUI #
    
#==============================================================================

    ConsoleSignal = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        super(HydroprintGUI, self).__init__(parent)
        
        self.workdir = os.getcwd()
        self.UpdateUI = True
        self.fwaterlvl = []
        self.waterlvl_data = hydroprint.WaterlvlData()
        self.meteo_data = meteo.MeteoObj()
        
        #---- memory path variable ----
        
        self.meteo_dir = self.workdir + '/Meteo/Output'
        self.waterlvl_dir = self.workdir + '/Water Levels'
        self.save_fig_dir = self.workdir
        
        self.initUI()
        
    def initUI(self): #============================================ initUI ====
    
        #-------------------------------------------------------- DATABASE ----
       
        styleDB = db.styleUI()
        iconDB = db.Icons()
        styleDB = db.styleUI()
        ttipDB = db.Tooltips('English')
        
        #----------------------------------------------------- Main Window ----
        
        self.setWindowIcon(iconDB.WHAT)
        
        #------------------------------------------ Weather Normals Widget ----
        
        self.weather_avg_graph = meteo.WeatherAvgGraph(self)
        
        #------------------------------------------------ HydroCalc Widget ----
        
        self.hydrocalc = HydroCalc.WLCalc()
        self.hydrocalc.hide()
        
        #----------------------------------------------- Page Setup Widget ----
               
        self.page_setup_win = PageSetupWin(self)        
        self.page_setup_win.newPageSetupSent.connect(self.layout_changed)

        #--------------------------------------------------------- Toolbar ----
       
        #---- Graph Title Section ----
        
        graph_title_widget = QtGui.QWidget()
        
        self.graph_title = QtGui.QLineEdit()
        self.graph_title.setMaxLength(65)
        self.graph_title.setEnabled(False)
        self.graph_title.setText('Add A Title To The Figure Here')
        self.graph_title.setToolTip(ttipDB.addTitle)
        self.graph_status = QtGui.QCheckBox() 
        
        graph_title_layout = QtGui.QGridLayout()
        graph_title_layout.addWidget(QtGui.QLabel('         '), 0, 0)
        graph_title_layout.addWidget(self.graph_title, 0, 1)
        graph_title_layout.addWidget(self.graph_status, 0, 2)
        graph_title_layout.setColumnStretch(1, 100)
        
        graph_title_widget.setLayout(graph_title_layout)        
        
        #---- Toolbar Buttons ----
        
        btn_loadConfig = QtGui.QToolButton()
        btn_loadConfig.setAutoRaise(True)
        btn_loadConfig.setIcon(iconDB.load_graph_config)
        btn_loadConfig.setToolTip(ttipDB.loadConfig)
        btn_loadConfig.setIconSize(styleDB.iconSize)        
                                  
        btn_saveConfig = QtGui.QToolButton()
        btn_saveConfig.setAutoRaise(True)
        btn_saveConfig.setIcon(iconDB.save_graph_config)
        btn_saveConfig.setToolTip(ttipDB.saveConfig)
        btn_saveConfig.setIconSize(styleDB.iconSize)
        
        btn_bestfit_waterlvl = QtGui.QToolButton()
        btn_bestfit_waterlvl.setAutoRaise(True)
        btn_bestfit_waterlvl.setIcon(iconDB.fit_y)        
        btn_bestfit_waterlvl.setToolTip(ttipDB.fit_y)
        btn_bestfit_waterlvl.setIconSize(styleDB.iconSize)
        
        btn_bestfit_time = QtGui.QToolButton()
        btn_bestfit_time.setAutoRaise(True)
        btn_bestfit_time.setIcon(iconDB.fit_x)
        btn_bestfit_time.setToolTip(ttipDB.fit_x)
        btn_bestfit_time.setIconSize(styleDB.iconSize)
        
        btn_closest_meteo = QtGui.QToolButton()
        btn_closest_meteo.setAutoRaise(True)
        btn_closest_meteo.setIcon(iconDB.closest_meteo)
        btn_closest_meteo.setToolTip(ttipDB.closest_meteo)
        btn_closest_meteo.setIconSize(styleDB.iconSize)
        
        btn_draw = QtGui.QToolButton()
        btn_draw.setAutoRaise(True)
        btn_draw.setIcon(iconDB.refresh)        
        btn_draw.setToolTip(ttipDB.draw_hydrograph)
        btn_draw.setIconSize(styleDB.iconSize)
        
        btn_weather_normals = QtGui.QToolButton()
        btn_weather_normals.setAutoRaise(True)
        btn_weather_normals.setIcon(iconDB.meteo)        
        btn_weather_normals.setToolTip(ttipDB.weather_normals)
        btn_weather_normals.setIconSize(styleDB.iconSize)
        
        self.btn_work_waterlvl = QtGui.QToolButton()
        self.btn_work_waterlvl.setAutoRaise(True)
        self.btn_work_waterlvl.setIcon(iconDB.toggleMode)        
        self.btn_work_waterlvl.setToolTip(ttipDB.work_waterlvl)
        self.btn_work_waterlvl.setIconSize(styleDB.iconSize)

        btn_save = QtGui.QToolButton()
        btn_save.setAutoRaise(True)
        btn_save.setIcon(iconDB.save)
        btn_save.setToolTip(ttipDB.save_hydrograph)
        btn_save.setIconSize(styleDB.iconSize)
        
        btn_page_setup = QtGui.QToolButton()
        btn_page_setup.setAutoRaise(True)
        btn_page_setup.setIcon(iconDB.page_setup)
        btn_page_setup.setToolTip(ttipDB.btn_page_setup)
        btn_page_setup.setIconSize(styleDB.iconSize)
        btn_page_setup.clicked.connect(self.page_setup_win.show)
        
        class VSep(QtGui.QFrame): # vertical separators for the toolbar
            def __init__(self, parent=None):
                super(VSep, self).__init__(parent)
                self.setFrameStyle(styleDB.VLine)
        
        #---- Layout ----
        
        btn_list = [self.btn_work_waterlvl, VSep(), btn_save, btn_draw,
                    btn_loadConfig, btn_saveConfig, VSep(), 
                    btn_bestfit_waterlvl, btn_bestfit_time, btn_closest_meteo,
                    VSep(), btn_weather_normals, btn_page_setup,
                    graph_title_widget]
        
        subgrid_toolbar = QtGui.QGridLayout()
        toolbar_widget = QtGui.QWidget()
           
        row = 0; col=0
        for btn in btn_list:
            subgrid_toolbar.addWidget(btn, row, col)
            col += 1
                       
        subgrid_toolbar.setSpacing(5)
        subgrid_toolbar.setContentsMargins(0, 0, 0, 0)
        
        toolbar_widget.setLayout(subgrid_toolbar)
        
        #----------------------------------------------------- LEFT PANEL ----
        
        #---- SubGrid Hydrograph Frame ----
        
        self.hydrograph = hydroprint.Hydrograph()
        self.hydrograph_scrollarea = mplFigViewer.ImageViewer()
        
        grid_hydrograph_widget = QtGui.QFrame()
        grid_hydrograph =  QtGui.QGridLayout() 
        
        grid_hydrograph.addWidget(self.hydrograph_scrollarea, 0, 0)
        
        grid_hydrograph.setRowStretch(0, 500)
        grid_hydrograph.setColumnStretch(0, 500)
        grid_hydrograph.setContentsMargins(0, 0, 0, 0) # (L, T, R, B) 
        
        grid_hydrograph_widget.setLayout(grid_hydrograph)
        
        #----- ASSEMBLING SubGrids -----
                
        grid_layout = QtGui.QGridLayout()
        self.grid_layout_widget = QtGui.QFrame()
        
        row = 0
        grid_layout.addWidget(toolbar_widget, row, 0)
        row += 1
        grid_layout.addWidget(grid_hydrograph_widget, row, 0)
        
        grid_layout.setContentsMargins(0, 0, 0, 0) # Left, Top, Right, Bottom 
        grid_layout.setSpacing(5)
        grid_layout.setColumnStretch(0, 500)
        grid_layout.setRowStretch(1, 500)
        
        self.grid_layout_widget.setLayout(grid_layout)
        
        def make_data_files_panel(self): #----------------- Data Files Panel --
            
            #---- widgets ----
                    
            btn_waterlvl_dir = QtGui.QPushButton(' Water Level Data File')
            btn_waterlvl_dir.setIcon(iconDB.openFile)
            btn_waterlvl_dir.setIconSize(styleDB.iconSize2)
            btn_waterlvl_dir.clicked.connect(self.select_waterlvl_file)
            
            self.well_info_widget = QtGui.QTextEdit()
            self.well_info_widget.setReadOnly(True)
            self.well_info_widget.setFixedHeight(150)
            
            btn_weather_dir = QtGui.QPushButton(' Weather Data File')
            btn_weather_dir.setIcon(iconDB.openFile)
            btn_weather_dir.setIconSize(styleDB.iconSize2)
            btn_weather_dir.clicked.connect(self.select_meteo_file)
            
            self.meteo_info_widget = QtGui.QTextEdit()
            self.meteo_info_widget.setReadOnly(True)
            self.meteo_info_widget.setFixedHeight(150)
            
            #---- layout ----
            
            self.data_files_panel = QtGui.QWidget()
            layout = QtGui.QGridLayout()
                                
            layout.addWidget(btn_waterlvl_dir, 0, 0)
            layout.addWidget(self.well_info_widget, 1, 0)
            layout.addWidget(btn_weather_dir, 2, 0)        
            layout.addWidget(self.meteo_info_widget, 3, 0)
            
            layout.setSpacing(5)
            layout.setContentsMargins(0, 0, 0, 0)
            
            self.data_files_panel.setLayout(layout)
            
        make_data_files_panel(self)
        
        def make_scales_tab_widget(self): #------------- Scales Tab Widget ----
        
            #---------------------------------------------------  TIME --------
            
            #---- widget ----
            
            self.date_start_widget = QtGui.QDateEdit()
            self.date_start_widget.setDisplayFormat('01 / MM / yyyy')
            self.date_start_widget.setAlignment(QtCore.Qt.AlignCenter)
        
            self.date_end_widget = QtGui.QDateEdit()
            self.date_end_widget.setDisplayFormat('01 / MM / yyyy')
            self.date_end_widget.setAlignment(QtCore.Qt.AlignCenter)
            
            self.time_scale_label = QtGui.QComboBox()
            self.time_scale_label.setEditable(False)
            self.time_scale_label.setInsertPolicy(QtGui.QComboBox.NoInsert)
            self.time_scale_label.addItems(['Month', 'Year'])
            self.time_scale_label.setCurrentIndex(0)
            
            #---- layout ----
            
            widget_time_scale = QtGui.QFrame()
            widget_time_scale.setFrameStyle(0)  # styleDB.frame 
            grid_time_scale = QtGui.QGridLayout()
            
            row = 0
            grid_time_scale.addWidget(QtGui.QLabel('Date Min :'), row, 1)
            grid_time_scale.addWidget(self.date_start_widget, row, 2)
            row +=1
            grid_time_scale.addWidget(QtGui.QLabel('Date Max :'), row, 1)  
            grid_time_scale.addWidget(self.date_end_widget, row, 2)
            row += 1
            grid_time_scale.addWidget(QtGui.QLabel('Date Scale :'), row, 1)  
            grid_time_scale.addWidget(self.time_scale_label, row, 2)
            
            grid_time_scale.setVerticalSpacing(5)
            grid_time_scale.setHorizontalSpacing(10)
            grid_time_scale.setContentsMargins(10, 10, 10, 10)
            grid_time_scale.setColumnStretch(2, 100)
            
            widget_time_scale.setLayout(grid_time_scale)
            
            #--------------------------------------------- WATER LEVEL --------
            
            label_waterlvl_scale = QtGui.QLabel('WL Scale :') 
            self.waterlvl_scale = QtGui.QDoubleSpinBox()
            self.waterlvl_scale.setSingleStep(0.05)
            self.waterlvl_scale.setMinimum(0.05)
            self.waterlvl_scale.setSuffix('  m')
            self.waterlvl_scale.setAlignment(QtCore.Qt.AlignCenter) 
            self.waterlvl_scale.setKeyboardTracking(False)
            
            label_waterlvl_max = QtGui.QLabel('WL Min :') 
            self.waterlvl_max = QtGui.QDoubleSpinBox()
            self.waterlvl_max.setSingleStep(0.1)
            self.waterlvl_max.setSuffix('  m')
            self.waterlvl_max.setAlignment(QtCore.Qt.AlignCenter)
            self.waterlvl_max.setMinimum(-1000)
            self.waterlvl_max.setMaximum(1000)
            self.waterlvl_max.setKeyboardTracking(False)
            
            label_datum = QtGui.QLabel('WL Datum :')
            self.datum_widget = QtGui.QComboBox()
            self.datum_widget.addItems(['Ground Surface', 'See Level'])
            
            self.subgrid_WLScale_widget = QtGui.QFrame()
            self.subgrid_WLScale_widget.setFrameStyle(0) # styleDB.frame
            subgrid_WLScale = QtGui.QGridLayout()
            
            row = 0
            subgrid_WLScale.addWidget(label_waterlvl_scale, row, 1)        
            subgrid_WLScale.addWidget(self.waterlvl_scale, row, 2)
            row += 1
            subgrid_WLScale.addWidget(label_waterlvl_max, row, 1)        
            subgrid_WLScale.addWidget(self.waterlvl_max, row, 2)
            row += 1
            subgrid_WLScale.addWidget(label_datum, row, 1)
            subgrid_WLScale.addWidget(self.datum_widget, row, 2)
            
            subgrid_WLScale.setVerticalSpacing(5)
            subgrid_WLScale.setHorizontalSpacing(10)
            subgrid_WLScale.setContentsMargins(10, 10, 10, 10) # (L, T, R, B)
            subgrid_WLScale.setColumnStretch(2, 100)
            
            self.subgrid_WLScale_widget.setLayout(subgrid_WLScale)
        
            #------------------------------------------------- WEATHER --------
            
            #---- widgets ----
            
            label_Ptot_scale = QtGui.QLabel('Precip. Scale :')
            self.Ptot_scale = QtGui.QSpinBox()
            self.Ptot_scale.setSingleStep(5)
            self.Ptot_scale.setMinimum(5)
            self.Ptot_scale.setMaximum(50)
            self.Ptot_scale.setValue(20)        
            self.Ptot_scale.setSuffix('  mm')
            self.Ptot_scale.setAlignment(QtCore.Qt.AlignCenter)
            
            self.qweather_bin = QtGui.QComboBox()
            self.qweather_bin.setEditable(False)
            self.qweather_bin.setInsertPolicy(QtGui.QComboBox.NoInsert)
            self.qweather_bin.addItems(['day', 'week', 'month'])
            self.qweather_bin.setCurrentIndex(1)
            
            #---- layout ----
            
            widget_weather_scale = QtGui.QFrame()
            widget_weather_scale.setFrameStyle(0)
            layout = QtGui.QGridLayout()
            #--
            row = 1
            layout.addWidget(label_Ptot_scale, row, 1)        
            layout.addWidget(self.Ptot_scale, row, 2)
            row += 1
            layout.addWidget(QtGui.QLabel('Resampling :'), row, 1)
            layout.addWidget(self.qweather_bin, row, 2)            
            #--
            layout.setVerticalSpacing(5)
            layout.setHorizontalSpacing(10)
            layout.setContentsMargins(10, 10, 10, 10) #(L, T, R, B)
            layout.setColumnStretch(2, 100)
            layout.setRowStretch(row+1, 100)
            layout.setRowStretch(0, 100)
            
            widget_weather_scale.setLayout(layout)
                    
            #----------------------------------------- ASSEMBLING TABS --------
            
            self.tabscales = QtGui.QTabWidget()
            self.tabscales.addTab(widget_time_scale, 'Time')
            self.tabscales.addTab(self.subgrid_WLScale_widget, 'Water Level')
            self.tabscales.addTab(widget_weather_scale, 'Weather')
        
        make_scales_tab_widget(self)
        
        def make_label_language_widget(self): #----- Label Language Widget ----
            
            #---- widgets ----
            
            self.language_box = QtGui.QComboBox()
            self.language_box.setEditable(False)
            self.language_box.setInsertPolicy(QtGui.QComboBox.NoInsert)
            self.language_box.addItems(['French', 'English'])
            self.language_box.setCurrentIndex(1)
            
            #---- layout ----
            
            self.qAxeLabelsLanguage = QtGui.QFrame()
            layout = QtGui.QGridLayout()
            #--
            layout.addWidget(QtGui.QLabel('Label Language:'), 0, 0)        
            layout.addWidget(self.language_box, 0, 1)
            #--
            layout.setSpacing(5)
            layout.setContentsMargins(5, 5, 5, 5) # (L, T, R, B)            
            self.qAxeLabelsLanguage.setLayout(layout)
        
        make_label_language_widget(self)
        
        def make_right_panel(self): #------------------------- Right Panel ----
        
            self.hydrocalc.widget_MRCparam.hide()
            
            RightPanel = QtGui.QFrame()            
            layout = QtGui.QGridLayout()
            #--
            row = 0
            layout.addWidget(self.data_files_panel, row, 0)
            row += 1
            layout.addWidget(self.tabscales, row, 0)
            layout.addWidget(self.hydrocalc.widget_MRCparam, row, 0)
            row += 1            
            layout.addWidget(self.qAxeLabelsLanguage, 2, 0)                        
            #--
            layout.setContentsMargins(0, 0, 0, 0) # (L, T, R, B)
            layout.setSpacing(15)
            layout.setRowStretch(row+1, 100)
            RightPanel.setLayout(layout)
            
            return RightPanel
        
        RightPanel = make_right_panel(self)
        
        #------------------------------------------------------- MAIN GRID ----
                
        vSep = QtGui.QFrame()
        vSep.setFrameStyle(styleDB.VLine)
        
        mainGrid = QtGui.QGridLayout()

        mainGrid.addWidget(self.grid_layout_widget, 0, 0)
        mainGrid.addWidget(self.hydrocalc, 0, 0)
        mainGrid.addWidget(vSep, 0, 1)
        mainGrid.addWidget(RightPanel, 0, 2)
        
        mainGrid.setContentsMargins(10, 10, 10, 10) # (L, T, R, B) 
        mainGrid.setSpacing(15)
        mainGrid.setColumnStretch(0, 500)
        
        self.setLayout(mainGrid)
        
        #--------------------------------------------------- MESSAGE BOXES ----
                                          
        self.msgBox = QtGui.QMessageBox()
        self.msgBox.setIcon(QtGui.QMessageBox.Question)
        self.msgBox.setStandardButtons(QtGui.QMessageBox.Yes |
                                       QtGui.QMessageBox.No)
        self.msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        self.msgBox.setWindowTitle('Save Graph Layout')
        self.msgBox.setWindowIcon(iconDB.WHAT)
                        
        self.msgError = MyQWidget.MyQErrorMessageBox()
        
        #---------------------------------------------------------- EVENTS ----
        
        #----- Toolbox Layout -----
        
        btn_loadConfig.clicked.connect(self.load_graph_layout)
        btn_saveConfig.clicked.connect(self.save_config_isClicked)
        btn_bestfit_waterlvl.clicked.connect(self.best_fit_waterlvl)
        btn_bestfit_time.clicked.connect(self.best_fit_time)
        btn_closest_meteo.clicked.connect(self.select_closest_meteo_file)
        btn_draw.clicked.connect(self.draw_hydrograph)
        btn_save.clicked.connect(self.select_save_path)
        btn_weather_normals.clicked.connect(self.show_weather_averages)
        
        #----- Toggle Mode -----
        
        self.btn_work_waterlvl.clicked.connect(self.toggle_computeMode)
        self.hydrocalc.btn_layout_mode.clicked.connect(self.toggle_layoutMode)
        
        #----- Hydrograph Layout -----
        
        self.datum_widget.currentIndexChanged.connect(self.layout_changed)
        self.language_box.currentIndexChanged.connect(self.layout_changed)
        self.waterlvl_max.valueChanged.connect(self.layout_changed)
        self.waterlvl_scale.valueChanged.connect(self.layout_changed)
        self.Ptot_scale.valueChanged.connect(self.layout_changed)
        self.date_start_widget.dateChanged.connect(self.layout_changed)
        self.graph_status.stateChanged.connect(self.layout_changed)
        self.graph_title.editingFinished.connect(self.layout_changed)        
        self.date_start_widget.dateChanged.connect(self.layout_changed)
        self.date_end_widget.dateChanged.connect(self.layout_changed)        
        self.qweather_bin.currentIndexChanged.connect(self.layout_changed)
        self.time_scale_label.currentIndexChanged.connect(self.layout_changed)
        
        #------------------------------------------------------ Init Image ----
        
        self.hydrograph_scrollarea.load_mpl_figure(self.hydrograph)
        
    def set_workdir(self, directory): #========================================
        
        self.workdir = directory 
                
        self.meteo_dir = directory + '/Meteo/Output'
        self.waterlvl_dir = directory + '/Water Levels'
        self.save_fig_dir = directory
        
    def check_files(self): #===================================================
        
        #---- System project folder organization ----
        if not os.path.exists(self.workdir + '/Water Levels'):
            os.makedirs(self.workdir + '/Water Levels')
        
        #---- waterlvl_manual_measurements.xls ----
        
        fname = self.workdir + '/waterlvl_manual_measurements.xls'
        if not os.path.exists(fname):
            
            msg = ('No "waterlvl_manual_measurements.xls" file found. ' +
                   'A new one has been created.')
            print(msg)
            
            # http://stackoverflow.com/questions/13437727
            book = xlwt.Workbook(encoding="utf-8")
            sheet1 = book.add_sheet("Sheet 1")
            sheet1.write(0, 0, 'Well_ID')
            sheet1.write(0, 1, 'Time (days)')
            sheet1.write(0, 2, 'Obs. (mbgs)')
            book.save(fname)
            
        #---- graph_layout.lst ----
        
        filename = self.workdir + '/graph_layout.lst'
        if not os.path.exists(filename):
            
            fcontent = db.FileHeaders().graph_layout
                        
            msg = ('No "graph_layout.lst" file found. ' +
                   'A new one has been created.')
            print(msg)

            with open(filename, 'wb') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(fcontent)
                
    def toggle_layoutMode(self): #=============================================
        
        self.hydrocalc.hide()        
        self.grid_layout_widget.show()
        
        #---- Right Panel Update ----
        
        self.hydrocalc.widget_MRCparam.hide()
        
        self.tabscales.show()
        self.qAxeLabelsLanguage.show()
        
    def toggle_computeMode(self): #====================== toggle_computeMode ==
        
        self.grid_layout_widget.hide()
        self.hydrocalc.show()
        
        #---- Right Panel Update ----
        
        self.hydrocalc.widget_MRCparam.show()
        
        self.tabscales.hide()
        self.qAxeLabelsLanguage.hide()
                    
    def show_weather_averages(self): #================ show_weather_averages ==
        
        filemeteo = copy.copy(self.hydrograph.fmeteo)

        if not filemeteo:
            
            self.ConsoleSignal.emit(
            '''<font color=red>No valid Weather Data File currently 
                 selected.</font>''')
                               
            self.emit_error_message(
            '''<b>Please select a valid Weather Data File first.</b>''')
            
            return
        
        self.weather_avg_graph.save_fig_dir = self.workdir
        self.weather_avg_graph.generate_graph(filemeteo)            
        self.weather_avg_graph.show()
        
    def emit_error_message(self, error_text): #========== emit_error_message ==
        
        self.msgError.setText(error_text)
        self.msgError.exec_()
        
    def select_waterlvl_file(self): #================== select_waterlvl_file ==
        
        '''
        This method is called by <btn_waterlvl_dir> is clicked. It prompts
        the user to select a valid Water Level Data file.        
        '''
    
        
        filename, _ = QtGui.QFileDialog.getOpenFileName(
                                  self, 'Select a valid water level data file', 
                                  self.waterlvl_dir, '*.xls')
        
        for i in range(5):
            QtCore.QCoreApplication.processEvents()
            
        self.load_waterlvl(filename)
        
                              
    def load_waterlvl(self, filename): #======================================
        
        '''
        If "filename" exists:
        
        The (1) water level time series, (2) observation well info and the
        (3) manual measures are loaded and saved in the class instance 
        "waterlvl_data".
        
        Then the code check if there is a layout already saved for this well
        and if yes, will prompt the user if he wants to load it.
        
        Depending if there is a lyout or not, a Weather Data File will be 
        loaded and the hydrograph will be automatically plotted.
        '''
        
        
        if not filename:
            print('Path is empty. Cannot load water level file.')
            return
            
        self.check_files()
            
        #----- Update UI Memory Variables -----
        
        self.waterlvl_dir = os.path.dirname(filename)
        self.fwaterlvl = filename
        
        #----- Load Data -----
        
        state = self.waterlvl_data.load(filename)
        if state == False:
            msg = ('WARNING: Waterlvl data file "%s" is not formatted ' +
                   ' correctly.') % os.path.basename(filename)
            print(msg)
            
            self.ConsoleSignal.emit('<font color=red>%s</font>' % msg)
            return False
            
        name_well = self.waterlvl_data.name_well
                
        #----- Load Manual Measures -----
        
        filename = self.workdir + '/waterlvl_manual_measurements.xls'        
        self.waterlvl_data.load_waterlvl_measures(filename, name_well)
        
        #----- Update Waterlvl Obj -----
        
        self.hydrograph.set_waterLvlObj(self.waterlvl_data)
        
        #----- Display Well Info in UI -----
        
        self.well_info_widget.setText(self.waterlvl_data.well_info)
        
        self.ConsoleSignal.emit(
        '''<font color=black>Water level data set loaded successfully for
             well %s.</font>''' % name_well)
             
        #---- Update "Compute" Mode Graph ----
        
        self.draw_computeMode_waterlvl()
        
        #---- Well Layout -----

        filename = self.workdir + '/graph_layout.lst'
        isLayoutExist = self.hydrograph.checkLayout(name_well, filename)
                        
        if isLayoutExist == True:
            
            self.ConsoleSignal.emit(
            '''<font color=black>A graph layout exists for well %s.
               </font>''' % name_well)
            
            self.msgBox.setText('<b>A graph layout already exists ' +
                                    'for well ' + name_well + '.<br><br> Do ' +
                                    'you want to load it?</b>')
            override = self.msgBox.exec_()

            if override == self.msgBox.Yes:
                self.load_graph_layout()
                return
        
        #---- Fit Water Level in Layout ----
        
        self.UpdateUI = False
        
        self.best_fit_waterlvl()
        self.best_fit_time()
        
        self.UpdateUI = True
        
        self.select_closest_meteo_file()
            
            
    def select_closest_meteo_file(self): #====================================
                
        meteo_folder = self.workdir + '/Meteo/Output'
        
        if os.path.exists(meteo_folder) and self.fwaterlvl:
            
            LAT1 = self.waterlvl_data.LAT
            LON1 = self.waterlvl_data.LON
            
            # Generate a list of data file paths.            
            fmeteo_paths = []
            for files in os.listdir(meteo_folder):
                if files.endswith(".out"):
                    fmeteo_paths.append(meteo_folder + '/' + files)
                    
            if len(fmeteo_paths) > 0:
            
                LAT2 = np.zeros(len(fmeteo_paths))
                LON2 = np.zeros(len(fmeteo_paths))
                DIST = np.zeros(len(fmeteo_paths))
                i = 0
                for fmeteo in fmeteo_paths:
                    
                    with open(fmeteo, 'rb') as f:
                        reader = list(csv.reader(f, delimiter='\t'))
               
                    LAT2[i] = float(reader[2][1])
                    LON2[i] = float(reader[3][1])
                    DIST[i] = hydroprint.LatLong2Dist(LAT1, LON1, LAT2[i], 
                                                      LON2[i])
                    
                    i += 1
                    
                index = np.where(DIST == np.min(DIST))[0][0]
                          
                self.load_meteo_file(fmeteo_paths[index])
                for i in range(5): QtCore.QCoreApplication.processEvents()
    
           
    def select_meteo_file(self): #============================================
       
        '''
        This method is called by <btn_weather_dir.clicked.connect>. It prompts
        the user to select a valid Weather Data file.        
        '''
    
         
        filename, _ = QtGui.QFileDialog.getOpenFileName(
                                      self, 'Select a valid weather data file', 
                                      self.meteo_dir, '*.out')       

        for i in range(5): QtCore.QCoreApplication.processEvents()
            
        self.load_meteo_file(filename)
    
           
    def load_meteo_file(self, filename): #====================================
        
        if not filename:
            print('Path is empty. Cannot load weather data file.')
            return
            
        self.meteo_dir = os.path.dirname(filename)
        self.hydrograph.fmeteo = filename
        self.hydrograph.finfo = filename[:-3] + 'log'
        
        self.meteo_data.load_and_format(filename)
        self.meteo_info_widget.setText(self.meteo_data.INFO)       
        self.ConsoleSignal.emit(
        '''<font color=black>Weather data set loaded successfully for
             station %s.</font>''' % self.meteo_data.STA)
        
        if self.fwaterlvl:
            QtCore.QCoreApplication.processEvents()
            self.draw_hydrograph()
    
    
    def update_graph_layout_parameter(self): #================================
    
        '''
        This method is called either by the methods <save_graph_layout>
        or by <draw_hydrograph>. It fetches the values that are currently 
        displayed in the UI and save them in the class instance 
        <hydrograph> of the class <Hydrograph>.
        '''    

        if self.UpdateUI == False:
            return
        
        #---- dates ----
        year = self.date_start_widget.date().year()
        month = self.date_start_widget.date().month()
        day = 1
        date = xldate_from_date_tuple((year, month, day),0)
        self.hydrograph.TIMEmin = date
        
        year = self.date_end_widget.date().year()
        month = self.date_end_widget.date().month()
        day = 1
        date = xldate_from_date_tuple((year, month, day),0)
        self.hydrograph.TIMEmax = date
        
        #---- scales ----
        
        self.hydrograph.WLscale = self.waterlvl_scale.value()
        self.hydrograph.WLmin = self.waterlvl_max.value()        
        self.hydrograph.RAINscale = self.Ptot_scale.value() 
        
        #---- graph title ----
        
        if self.graph_status.isChecked():
            self.hydrograph.title_state = 1
        else:
            self.hydrograph.title_state = 0            
        self.hydrograph.title_text = self.graph_title.text()
        
        #---- label language ----
        
        self.hydrograph.language = self.language_box.currentText()
        
        #---- figure size ----
        
        self.hydrograph.fwidth = self.page_setup_win.pageSize[0]
             
            
    def load_graph_layout(self): #============================================
    

        self.check_files()
        
        #----------------------------------- Check if Waterlvl Data Exist ----
        
        if not self.fwaterlvl:
            
            self.ConsoleSignal.emit(
            '''<font color=red>No valid water level data file currently 
                 selected. Cannot load graph layout.</font>''')
                               
            self.emit_error_message(
            '''<b>Please select a valid water level data file.</b>''')
            
            return
        
        #----------------------------------------- Check if Layout Exists ----
                
        filename = self.workdir + '/graph_layout.lst'
        name_well = self.waterlvl_data.name_well
        isLayoutExist = self.hydrograph.checkLayout(name_well, filename)
                    
        if isLayoutExist == False:
            
            self.ConsoleSignal.emit(
            '''<font color=red>No graph layout exists for well %s.
               </font>''' % name_well)
            
            self.emit_error_message('''<b>No graph layout exists 
                                         for well %s.</b>''' % name_well)
                                             
            return
        
        #---------------------------------------------------- Load Layout ----
                    
        self.hydrograph.load_layout(name_well, filename)
        
        #----------------------------------------------------- Update UI -----
        
        self.UpdateUI = False
                                         
        date = self.hydrograph.TIMEmin
        date = xldate_as_tuple(date, 0)
        self.date_start_widget.setDate(QDate(date[0], date[1], date[2]))
        
        date = self.hydrograph.TIMEmax
        date = xldate_as_tuple(date, 0)
        self.date_end_widget.setDate(QDate(date[0], date[1], date[2]))
                                    
        self.waterlvl_scale.setValue(self.hydrograph.WLscale)
        self.waterlvl_max.setValue(self.hydrograph.WLmin)
        self.datum_widget.setCurrentIndex (self.hydrograph.WLdatum)
        
        self.Ptot_scale.setValue(self.hydrograph.RAINscale)
         
        if self.hydrograph.title_state == 1:
            self.graph_status.setCheckState(QtCore.Qt.Checked)
        else:                    
            self.graph_status.setCheckState(QtCore.Qt.Unchecked)
            
        self.graph_title.setText(self.hydrograph.title_text)
        
        #----- Check if Weather Data File exists -----
        
        if os.path.exists(self.hydrograph.fmeteo):
            self.meteo_data.load_and_format(self.hydrograph.fmeteo)
            INFO = self.meteo_data.build_HTML_table()
            self.meteo_info_widget.setText(INFO)
            self.ConsoleSignal.emit(
            '''<font color=black>Graph layout loaded successfully for 
               well %s.</font>''' % name_well)
               
            QtCore.QCoreApplication.processEvents()
            
            self.draw_hydrograph()
        else:
            self.meteo_info_widget.setText('')
            self.ConsoleSignal.emit(
            '''<font color=red>Unable to read the weather data file. %s
               does not exist.</font>''' % self.hydrograph.fmeteo)
            self.emit_error_message(
            '''<b>Unable to read the weather data file.<br><br>
               %s does not exist.<br><br> Please select another weather
               data file.<b>''' % self.hydrograph.fmeteo)
            self.hydrograph.fmeteo = []
            self.hydrograph.finfo = []
            
        self.UpdateUI = True    
    
    def save_config_isClicked(self): #========================================
        
        if not self.fwaterlvl:
            
            self.ConsoleSignal.emit(
            '''<font color=red>No valid water level file currently selected.
                 Cannot save graph layout.
               </font>''')
            
            self.msgError.setText(
            '''<b>Please select valid water level data file.</b>''')
            
            self.msgError.exec_()
            
            return
            
        if not self.hydrograph.fmeteo:
            
            self.ConsoleSignal.emit(
            '''<font color=red>No valid weather data file currently selected. 
                 Cannot save graph layout.
               </font>''')
            
            self.msgError.setText(
                            '''<b>Please select valid weather data file.</b>''')
                            
            self.msgError.exec_()
            
            return
            
        #----------------------------------------- Check if Layout Exists ----
            
        filename = self.workdir + '/graph_layout.lst'
        if not os.path.exists(filename):
            # Force the creation of a new "graph_layout.lst" file
            self.check_files()
            
        name_well = self.waterlvl_data.name_well
        isLayoutExist = self.hydrograph.checkLayout(name_well, filename)
        
        #---------------------------------------------------- Save Layout ----
        
        if isLayoutExist == True:
            self.msgBox.setText(
            '''<b>A graph layout already exists for well %s.<br><br> Do 
                 you want to replace it?</b>''' % name_well)
            override = self.msgBox.exec_()

            if override == self.msgBox.Yes:
                self.save_graph_layout(name_well)
                            
            elif override == self.msgBox.No:
                self.ConsoleSignal.emit('''<font color=black>Graph layout 
                               not saved for well %s.</font>''' % name_well)
                
        else:            
            self.save_graph_layout(name_well)
              
    def save_graph_layout(self, name_well): #=================================
        
        self.update_graph_layout_parameter()
        filename = self.workdir + '/graph_layout.lst'
        self.hydrograph.save_layout(name_well, filename)
        self.ConsoleSignal.emit(
        '''<font color=black>Graph layout saved successfully
             for well %s.</font>''' % name_well)
            
    def best_fit_waterlvl(self): #============================================
        
        if len(self.waterlvl_data.lvl) != 0:
            
            WLscale, WLmin = self.hydrograph.best_fit_waterlvl()
            
            self.waterlvl_scale.setValue(WLscale)
            self.waterlvl_max.setValue(WLmin)
            
    def best_fit_time(self): #================================================
            
        if len(self.waterlvl_data.time) != 0:
            
            TIME = self.waterlvl_data.time 
            date0, date1 = self.hydrograph.best_fit_time(TIME)
            
            self.date_start_widget.setDate(QDate(date0[0], date0[1], date0[2]))                                                        
            self.date_end_widget.setDate(QDate(date1[0], date1[1], date1[2]))
            
    def select_save_path(self): #=============================================
       
        name_well = self.waterlvl_data.name_well
        dialog_dir = self.save_fig_dir + '/hydrograph_' + name_well
        
        dialog = QtGui.QFileDialog()
        dialog.setConfirmOverwrite(True)
        fname, ftype = dialog.getSaveFileName(
                                    caption="Save Figure", dir=dialog_dir,
                                    filter=('*.pdf;;*.svg'))
                                  
        if fname:         
            
            if fname[-4:] != ftype[1:]:
                # Add a file extension if there is none
                fname = fname + ftype[1:]
                
            self.save_fig_dir = os.path.dirname(fname)
            self.save_figure(fname)
            
    def save_figure(self, fname): #===========================================
        
        self.hydrograph.generate_hydrograph(self.meteo_data)
                                       
        self.hydrograph.savefig(fname)
        
    def draw_computeMode_waterlvl(self): #====================================
        
        self.hydrocalc.time = self.waterlvl_data.time
        self.hydrocalc.water_lvl = self.waterlvl_data.lvl
        self.hydrocalc.soilFilename = self.waterlvl_data.soilFilename
        
        self.hydrocalc.plot_water_levels() 
    
    def draw_hydrograph(self): #==============================================
        
        if not self.fwaterlvl:
            console_text = ('<font color=red>Please select a valid water ' +
                            'level data file</font>')
            self.ConsoleSignal.emit(console_text)
            self.emit_error_message(
            '<b>Please select a valid Water Level Data File first.</b>')
            
            return
            
        if not self.hydrograph.fmeteo:
            console_text = ('<font color=red>Please select a valid ' +
                            'weather data file</font>')
            self.ConsoleSignal.emit(console_text)
            self.emit_error_message(
            '<b>Please select a valid Weather Data File first.</b>')
            
            return
                    
        self.update_graph_layout_parameter()
        
        #----- Generate and Display Graph -----
        
        for i in range(5): QtCore.QCoreApplication.processEvents()
        
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.hydrograph.generate_hydrograph(self.meteo_data)        
        self.hydrograph_scrollarea.load_mpl_figure(self.hydrograph)
        QtGui.QApplication.restoreOverrideCursor()

        
    def layout_changed(self): #=========================== layout_changed ====
    
        sender = self.sender()
                
        if self.UpdateUI == False:
            return

        if not self.hydrograph.isHydrographExists:
            return
        
        if sender == self.language_box:
            self.hydrograph.language = self.language_box.currentText()

            self.hydrograph.draw_ylabels()
            self.hydrograph.draw_xlabels()
                
        elif sender in [self.waterlvl_max, self.waterlvl_scale]:
            
            self.hydrograph.WLmin = self.waterlvl_max.value()
            self.hydrograph.WLscale = self.waterlvl_scale.value()            

            self.hydrograph.update_waterlvl_scale()
            self.hydrograph.draw_ylabels()
                
        elif sender == self.Ptot_scale:
            self.hydrograph.RAINscale = self.Ptot_scale.value()

            self.hydrograph.update_precip_scale()
            self.hydrograph.draw_ylabels()
                
        elif sender == self.datum_widget:
            self.hydrograph.WLdatum = self.datum_widget.currentIndex()
            self.hydrograph.WLmin = (self.waterlvl_data.ALT - 
                                     self.hydrograph.WLmin)

            self.hydrograph.update_waterlvl_scale()            
            self.hydrograph.draw_waterlvl()
            self.hydrograph.draw_ylabels()
                
        elif sender in [self.date_start_widget, self.date_end_widget]:            
            year = self.date_start_widget.date().year()
            month = self.date_start_widget.date().month()
            day = 1
            date = xldate_from_date_tuple((year, month, day), 0)
            self.hydrograph.TIMEmin = date
            
            year = self.date_end_widget.date().year()
            month = self.date_end_widget.date().month()
            day = 1
            date = xldate_from_date_tuple((year, month, day),0)
            self.hydrograph.TIMEmax = date
            
            self.hydrograph.set_time_scale()
            self.hydrograph.draw_weather()
            self.hydrograph.draw_figure_title()
                
        elif sender == self.graph_title:
                
            #---- Update Instance Variables ----
            
            self.hydrograph.title_text = self.graph_title.text()
                
            #---- Update Graph if Exists ----
                
            self.hydrograph.draw_figure_title()
        
        elif sender == self.graph_status:        
            self.graph_title.setEnabled(self.graph_status.isChecked())
           
            if self.graph_status.isChecked():
                self.hydrograph.title_state = 1
                self.hydrograph.title_text = self.graph_title.text()
            else:
                self.hydrograph.title_state = 0
           
            self.hydrograph.set_margins()
            self.hydrograph.draw_figure_title()
                
        elif sender == self.page_setup_win:
            fwidth = self.page_setup_win.pageSize[0]
            self.hydrograph.set_fig_size(fwidth, 8.5)
        
        #---------------------------------------- Sampling of Weather Data ----
        
        elif sender == self.qweather_bin: 
            self.hydrograph.bwidth_indx = self.qweather_bin.currentIndex ()
            self.hydrograph.resample_bin()
            self.hydrograph.draw_weather()
            self.hydrograph.draw_ylabels()
        
        #-------------------------------------------- Scale of Data Labels ----
            
        elif sender == self.time_scale_label: 
            
            year = self.date_start_widget.date().year()
            month = self.date_start_widget.date().month()
            day = 1
            date = xldate_from_date_tuple((year, month, day), 0)
            self.hydrograph.TIMEmin = date
            
            year = self.date_end_widget.date().year()
            month = self.date_end_widget.date().month()
            day = 1
            date = xldate_from_date_tuple((year, month, day),0)
            self.hydrograph.TIMEmax = date
            
            self.hydrograph.datemode = self.time_scale_label.currentText()
            self.hydrograph.set_time_scale()
            self.hydrograph.draw_weather()
            
        else:
            print('No action for this widget yet.')
                
        # !!!! temporary fix until I can find a better solution !!!!
        
#        sender.blockSignals(True)
        if type(sender) in [QtGui.QDoubleSpinBox, QtGui.QSpinBox]:
            sender.setReadOnly(True)
        for i in range(10):
             QtCore.QCoreApplication.processEvents() 
        self.hydrograph_scrollarea.load_mpl_figure(self.hydrograph)
        for i in range(10):
             QtCore.QCoreApplication.processEvents()
        if type(sender) in [QtGui.QDoubleSpinBox, QtGui.QSpinBox]:
            sender.setReadOnly(False)
#        sender.blockSignals(False) 
        
        
#=============================================================================
        
class PageSetupWin(QtGui.QWidget):                             # PageSetupWin #

#=============================================================================
            
    newPageSetupSent = QtCore.Signal(bool)
    
    def __init__(self, parent=None):
        super(PageSetupWin, self).__init__(parent)
        
        self.setWindowTitle('Page Setup')
        self.setWindowFlags(QtCore.Qt.Window)
        
        #---- Default Values ----
        
        self.pageSize = (11., 8.5)
        
        #---- Toolbar ----
        
        toolbar_widget = QtGui.QWidget()
        
        btn_apply = QtGui.QPushButton('Apply')
        btn_apply.clicked.connect(self.btn_apply_isClicked)
        btn_cancel = QtGui.QPushButton('Cancel')
        btn_cancel.clicked.connect(self.close)
        btn_OK = QtGui.QPushButton('OK')
        btn_OK.clicked.connect(self.btn_OK_isClicked)
                        
        toolbar_layout = QtGui.QGridLayout()
        toolbar_layout.addWidget(btn_OK, 0, 1)
        toolbar_layout.addWidget(btn_cancel, 0, 2)
        toolbar_layout.addWidget(btn_apply, 0, 3)
        toolbar_layout.setColumnStretch(0, 100)
        
        toolbar_widget.setLayout(toolbar_layout)
        
        #---- Figure Size ----
        
        figSize_widget =  QtGui.QWidget()
        
        self.fwidth = QtGui.QDoubleSpinBox()
        self.fwidth.setSingleStep(0.05)
        self.fwidth.setMinimum(5.)
        self.fwidth.setValue(self.pageSize[0])
        self.fwidth.setSuffix('  in')
        self.fwidth.setAlignment(QtCore.Qt.AlignCenter)
        
        figSize_layout = QtGui.QGridLayout()
        figSize_layout.addWidget(QtGui.QLabel('Figure Size:'), 0, 0)
        figSize_layout.addWidget(self.fwidth, 0, 1)                
        figSize_layout.addWidget(QtGui.QLabel('x'), 0, 2)
        figSize_layout.addWidget(QtGui.QLabel('8.5 in'), 0, 3)
        figSize_layout.setColumnStretch(4, 100)
        
        figSize_widget.setLayout(figSize_layout)
        
        #---- Main Layout ----
        
        main_layout = QtGui.QGridLayout()
        main_layout.addWidget(figSize_widget, 0, 0)
        main_layout.addWidget(toolbar_widget, 1, 0)
        
        self.setLayout(main_layout)
        
    def btn_OK_isClicked(self):
        self.btn_apply_isClicked()
        self.close()
        
    def btn_apply_isClicked(self): #==================================
        
        self.pageSize = (self.fwidth.value(), 8.5)                
        self.newPageSetupSent.emit(True)
    
    def closeEvent(self, event): #====================================
        super(PageSetupWin, self).closeEvent(event)

        #---- Refresh UI ----
        
        # If cancel or X is clicked, the parameters will be reset to
        # the values they had the last time "Accept" button was
        # clicked.
        
        self.fwidth.setValue(self.pageSize[0])
        
    def show(self): #=================================================
        super(PageSetupWin, self).show()
        self.activateWindow()
        self.raise_()
        
        qr = self.frameGeometry()
        if self.parentWidget():
            parent = self.parentWidget()
            
            wp = parent.frameGeometry().width()
            hp = parent.frameGeometry().height()
            cp = parent.mapToGlobal(QtCore.QPoint(wp/2., hp/2.))
        else:
            cp = QtGui.QDesktopWidget().availableGeometry().center()
            
        qr.moveCenter(cp)                    
        self.move(qr.topLeft())           
        self.setFixedSize(self.size())
        
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    
    Hydroprint = HydroprintGUI()
    Hydroprint.set_workdir("../Projects/Project4Testing")
    Hydroprint.show()

    sys.exit(app.exec_())        
        
        
