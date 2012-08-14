# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
from gettext import gettext as _
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from gi.repository import Gtk, Gdk
import gi
from netzob.Common.Type.UnitSize import UnitSize
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.UI.Vocabulary.Views.Partitioning.NewSimplePartitioningView import NewSimplePartitioningView
from netzob.Common.Threads.Job import Job


class NewSimplePartitioningController(object):
    '''
    classdocs
    '''

    def __init__(self, vocabularyController):
        self.vocabularyController = vocabularyController
        self._view = NewSimplePartitioningView(self)
        self.log = logging.getLogger(__name__)

    @property
    def view(self):
        return self._view

    def simple_cancel_clicked_cb(self, widget):
        self._view.simpleDialog.destroy()

    def simple_execute_clicked_cb(self, widget):
        # update widget
        self._view.simple_cancel.set_sensitive(False)
        self._view.simple_execute.set_sensitive(False)
        self._view.radiobutton8bits.set_sensitive(False)
        self._view.radiobutton16bits.set_sensitive(False)
        self._view.radiobutton32bits.set_sensitive(False)
        self._view.radiobutton64bits.set_sensitive(False)

        #extract chosen value
        symbolList = self.vocabularyController.view.getCheckedSymbolList()
        formatBits = UnitSize.BITS8

        if self._view.radiobutton16bits.get_active():
            formatBits = UnitSize.BITS16
        elif self._view.radiobutton32bits.get_active():
            formatBits = UnitSize.BITS32
        elif self._view.radiobutton64bits.get_active():
            formatBits = UnitSize.BITS64

        # create a job to execute the partitioning
        Job(self.startSimplePartitioning(symbolList, formatBits))

    def startSimplePartitioning(self, symbols, unitSize):
        if len(symbols) > 0:
            self.log.debug("Start to simple partitioning the selected symbols")
            try:
                (yield ThreadedTask(self.simplePartitioning, symbols, unitSize))
            except TaskError, e:
                self.log.error(_("Error while proceeding to the simple partitioning of symbols: {0}").format(str(e)))
        else:
            self.log.debug("No symbol selected")

        self.vocabularyController.restart()

        #update button
        self._view.simple_stop.set_sensitive(True)

        #close dialog box
        self._view.simpleDialog.destroy()

    def simplePartitioning(self, symbols, unitSize):
        """Simple partitioning the provided symbols"""
        step = float(100) / float(len(symbols))
        total = float(0)
        for symbol in symbols:
            GObject.idle_add(self._view.simple_progressbar.set_text, _("Simple partitioning symbol {0}".format(symbol.getName())))
            if self.flagStop:
                return
            symbol.simplePartitioning(unitSize)
            total = total + step
            rtotal = float(total) / float(100)
            time.sleep(0.01)
            GObject.idle_add(self._view.simple_progressbar.set_fraction, rtotal)
        GObject.idle_add(self._view.simple_progressbar.set_text, _("Simple partitioning finished !"))

    def simple_stop_clicked_cb(self, widget):
        # update button
        self._view.simple_stop.set_sensitive(False)

        # ++CODE HERE++
        # STOP THE THREAD OF simple PARTITIONING

        # update widget
        self._view.simple_execute.set_sensitive(True)
        self._view.simple_cancel.set_sensitive(True)
        self._view.radiobutton8bits.set_sensitive(True)
        self._view.radiobutton16bits.set_sensitive(True)
        self._view.radiobutton32bits.set_sensitive(True)
        self._view.radiobutton64bits.set_sensitive(True)

    def run(self):
        self._view.simple_stop.set_sensitive(False)
        self._view.radiobutton8bits.set_active(True)
        self._view.run()