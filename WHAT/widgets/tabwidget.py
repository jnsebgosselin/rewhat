# -*- coding: utf-8 -*-
"""
Copyright 2014-2017 Jean-Sebastien Gosselin
email: jean-sebastien.gosselin@ete.inrs.ca

WHAT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# ---- Standard library imports

import copy

# ---- Third parties imports

from PyQt5.QtCore import pyqtSignal as QSignal
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QTabBar,
                             QDesktopWidget)

# ---- Local imports

from WHAT.widgets.about import AboutWhat
from WHAT.common import IconDB, QToolButtonBase


class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent=None)

        self.aboutwhat = AboutWhat(parent=parent)

        self.about_btn = QToolButtonBase(IconDB().info)
        self.about_btn.setIconSize(QSize(20, 20))
        self.about_btn.setFixedSize(32, 32)
        self.about_btn.setToolTip('About WHAT...')
        self.about_btn.setParent(self)
        self.about_btn.clicked.connect(self.aboutwhat.show)

        tab_bar = TabBar(self, parent)
        self.setTabBar(tab_bar)
        tab_bar.sig_resized.connect(self.moveAboutButton)
        tab_bar.sig_tab_layout_changed.connect(self.moveAboutButton)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.moveAboutButton()

    def moveAboutButton(self):
        """
        Move the buton to show the About dialog window to the right side of the
        tab bar.
        """
        x = 0
        for i in range(self.count()):
            x += self.tabBar().tabRect(i).width()
        self.about_btn.move(x, 0)


class TabBar(QTabBar):

    sig_resized = QSignal()
    sig_tab_layout_changed = QSignal()

    def __init__(self, tab_widget, parent=None):
        super(TabBar, self).__init__(parent=None)

        self.__tab_widget = tab_widget

        self.__oldIndex = -1
        self.__newIndex = -1
        self.currentChanged.connect(self.storeIndex)

    def tabWidget(self):
        return self.__tab_widget

    def tabSizeHint(self, index):
        width = QTabBar.tabSizeHint(self, index).width()
        return QSize(width, 32)

    def sizeHint(self):
        sizeHint = QTabBar.sizeHint(self)
        w = sizeHint.width() + self.tabWidget().about_btn.size().width()
        return QSize(w, 32)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sig_resized.emit()

    def tabLayoutChange(self):
        super().tabLayoutChange()
        self.sig_resized.emit()

    def storeIndex(self, index):
        self.__oldIndex = copy.copy(self.__newIndex)
        self.__newIndex = index

    def previousIndex(self):
        return self.__oldIndex


if __name__ == '__main__':                                   # pragma: no cover
    import sys

    app = QApplication(sys.argv)
    tabwidget = TabWidget()
    tabwidget.addTab(QWidget(), 'Tab#1')
    tabwidget.addTab(QWidget(), 'Tab#2')
    tabwidget.addTab(QWidget(), 'Tab#3')
    tabwidget.show()

    qr = tabwidget.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    tabwidget.move(qr.topLeft())

    sys.exit(app.exec_())