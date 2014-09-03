#===============================================================================
# Copyright (C) 2014 Ryan Holmes
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.    If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import wx
import bitmapLoader
import service
from gui.utils.clipboard import toClipboard, fromClipboard

class ResistsEditorDlg (wx.Dialog):

    DAMAGE_TYPES = ("em", "thermal", "kinetic", "explosive")

    def __init__(self, parent):
        wx.Dialog.__init__ (self, parent, id = wx.ID_ANY, title = u"Target Resists Editor", size = wx.Size( 350,240 ))

        self.block = False
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.headerSizer = headerSizer = wx.BoxSizer(wx.HORIZONTAL)

        sTR = service.TargetResists.getInstance()

        self.choices = sTR.getTargetResistsList()

        # Sort the remaining list and continue on
        self.choices.sort(key=lambda p: p.name)
        self.ccResists = wx.Choice(self, choices=map(lambda p: p.name, self.choices))
        self.ccResists.Bind(wx.EVT_CHOICE, self.patternChanged)
        self.ccResists.SetSelection(0)

        self.namePicker = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.namePicker.Bind(wx.EVT_TEXT_ENTER, self.processRename)
        self.namePicker.Hide()

        self.btnSave = wx.Button(self, wx.ID_SAVE)
        self.btnSave.Hide()
        self.btnSave.Bind(wx.EVT_BUTTON, self.processRename)

        size = None
        headerSizer.Add(self.ccResists, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT|wx.LEFT, 3)

        buttons = (("new", wx.ART_NEW),
                   ("rename", bitmapLoader.getBitmap("rename", "icons")),
                   ("copy", wx.ART_COPY),
                   ("delete", wx.ART_DELETE))
        for name, art in buttons:
                bitmap = wx.ArtProvider.GetBitmap(art, wx.ART_BUTTON) if name != "rename" else art
                btn = wx.BitmapButton(self, wx.ID_ANY, bitmap)
                if size is None:
                    size = btn.GetSize()

                btn.SetMinSize(size)
                btn.SetMaxSize(size)

                btn.Layout()
                setattr(self, name, btn)
                btn.Enable(True)
                btn.SetToolTipString("%s resist profile" % name.capitalize())
                headerSizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)

        mainSizer.Add(headerSizer, 0, wx.EXPAND | wx.ALL, 2)

        self.sl = wx.StaticLine(self)
        mainSizer.Add(self.sl, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)

        contentSizer = wx.BoxSizer(wx.VERTICAL)

        resistEditSizer = wx.FlexGridSizer(2, 6, 0, 2)
        resistEditSizer.AddGrowableCol(0)
        resistEditSizer.AddGrowableCol(5)
        resistEditSizer.SetFlexibleDirection(wx.BOTH)
        resistEditSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        width = -1
        defSize = wx.Size(50,-1)

        for i, type in enumerate(self.DAMAGE_TYPES):
            if i%2:
                style = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx. LEFT
                border = 25
            else:
                style = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT
                border = 5

            bmp = wx.StaticBitmap(self, wx.ID_ANY, bitmapLoader.getBitmap("%s_big"%type, "icons"))
            resistEditSizer.Add(bmp, 0, style, border)
            # set text edit
            setattr(self, "%sEdit"%type, wx.TextCtrl(self, wx.ID_ANY, "", wx.DefaultPosition, defSize))
            editObj = getattr(self, "%sEdit"%type)
            resistEditSizer.Add(editObj, 0, wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER_VERTICAL, 5)
            resistEditSizer.Add(wx.StaticText( self, wx.ID_ANY, u"%", wx.DefaultPosition, wx.DefaultSize, 0 ), 0, wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER_VERTICAL, 5)
            editObj.Bind(wx.EVT_TEXT, self.ValuesUpdated)

        contentSizer.Add(resistEditSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.slfooter = wx.StaticLine(self)
        contentSizer.Add(self.slfooter, 0, wx.EXPAND | wx.TOP, 5)

        footerSizer = wx.BoxSizer(wx.HORIZONTAL)
        perSizer = wx.BoxSizer(wx.VERTICAL)

        self.stNotice = wx.StaticText(self, wx.ID_ANY, u"")
        self.stNotice.Wrap(-1)
        perSizer.Add(self.stNotice, 0, wx.BOTTOM | wx.TOP | wx.LEFT, 5)

        footerSizer.Add(perSizer, 1,  wx.ALIGN_CENTER_VERTICAL, 5)

        self.totSizer = wx.BoxSizer(wx.VERTICAL)

        contentSizer.Add(footerSizer, 0, wx.EXPAND, 5)

        mainSizer.Add(contentSizer, 1, wx.EXPAND, 0)

        if "wxGTK" in wx.PlatformInfo:
            self.closeBtn = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
            mainSizer.Add( self.closeBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
            self.closeBtn.Bind(wx.EVT_BUTTON, self.closeEvent)

        self.SetSizer(mainSizer)

        importExport = (("Import", wx.ART_FILE_OPEN, "from"),
                        ("Export", wx.ART_FILE_SAVE_AS, "to"))

        for name, art, direction in importExport:
                bitmap = wx.ArtProvider.GetBitmap(art, wx.ART_BUTTON)
                btn = wx.BitmapButton(self, wx.ID_ANY, bitmap)

                btn.SetMinSize( btn.GetSize() )
                btn.SetMaxSize( btn.GetSize() )

                btn.Layout()
                setattr(self, name, btn)
                btn.Enable(True)
                btn.SetToolTipString("%s patterns %s clipboard" % (name, direction) )
                footerSizer.Add(btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_RIGHT)

        self.Layout()
        bsize = self.GetBestSize()
        self.SetSize((-1,bsize.height))

        self.new.Bind(wx.EVT_BUTTON, self.newPattern)
        self.rename.Bind(wx.EVT_BUTTON, self.renamePattern)
        self.copy.Bind(wx.EVT_BUTTON, self.copyPattern)
        self.delete.Bind(wx.EVT_BUTTON, self.deletePattern)
        self.Import.Bind(wx.EVT_BUTTON, self.importPatterns)
        self.Export.Bind(wx.EVT_BUTTON, self.exportPatterns)

        self.patternChanged()

    def closeEvent(self, event):
        self.Destroy()

    def ValuesUpdated(self, event=None):
        if self.block:
            return
        if event is not None:
             print event.GetString()

        try:
            p = self.getActivePattern()

            for type in self.DAMAGE_TYPES:
                editObj = getattr(self, "%sEdit"%type)

                if editObj.GetValue() == "":
                    # if we are blank, overwrite with 0
                    editObj.ChangeValue("0")
                    editObj.SetInsertionPointEnd()

                value = float(editObj.GetValue())

                # assertion, because they're easy
                assert 0 <= value <= 100

                # if everything checks out, set resist attribute
                setattr(p, "%sAmount"%type, value/100)

            self.stNotice.SetLabel("")
            self.totSizer.Layout()

            if event is not None:
                # If we get here, everything is normal. Reset color
                event.EventObject.SetForegroundColour(wx.NullColor)
                event.Skip()

            service.TargetResists.getInstance().saveChanges(p)

        except ValueError:
            event.EventObject.SetForegroundColour(wx.RED)
            self.stNotice.SetLabel("Incorrect Formatting (decimals only)")
        except AssertionError:
            event.EventObject.SetForegroundColour(wx.RED)
            self.stNotice.SetLabel("Incorrect Range (must be 0-100)")
        finally:
            self.Refresh()  # Refresh for color changes to take effect immediately

    def restrict(self):
        for type in self.DAMAGE_TYPES:
            editObj = getattr(self, "%sEdit"%type)
            editObj.Enable(False)
        self.rename.Enable(False)
        self.delete.Enable(False)

    def unrestrict(self):
        for type in self.DAMAGE_TYPES:
            editObj = getattr(self, "%sEdit"%type)
            editObj.Enable()
        self.rename.Enable()
        self.delete.Enable()

    def getActivePattern(self):
        if len(self.choices) == 0:
            return None

        return self.choices[self.ccResists.GetSelection()]

    def patternChanged(self, event=None):
        p = self.getActivePattern()
        if p is None:
            return

        self.block = True
        for field in self.DAMAGE_TYPES:
            edit = getattr(self, "%sEdit" % field)
            amount = getattr(p, "%sAmount" % field)*100
            edit.ChangeValue(str(amount))

        self.block = False
        self.ValuesUpdated()

    def newPattern(self,event):
        sTR = service.TargetResists.getInstance()
        p = sTR.newPattern()
        self.choices.append(p)
        id = self.ccResists.Append(p.name)
        self.ccResists.SetSelection(id)
        self.btnSave.SetLabel("Create")

        # reset values
        for type in self.DAMAGE_TYPES:
            editObj = getattr(self, "%sEdit"%type)
            editObj.ChangeValue("0")
            editObj.SetForegroundColour(wx.NullColor)

        self.Refresh()
        self.renamePattern()

    def renamePattern(self,event=None):
        if event is not None:
            self.btnSave.SetLabel("Rename")

        self.ccResists.Hide()
        self.namePicker.Show()
        self.headerSizer.Replace(self.ccResists, self.namePicker)
        self.namePicker.SetFocus()
        self.namePicker.SetValue(self.getActivePattern().name)

        for btn in (self.new, self.rename, self.delete, self.copy):
            btn.Hide()
            self.headerSizer.Remove(btn)

        self.headerSizer.Add(self.btnSave, 0, wx.ALIGN_CENTER)
        self.btnSave.Show()
        self.headerSizer.Layout()
        if event is not None:
            event.Skip()

    def processRename(self, event):
        newName = self.namePicker.GetLineText(0)
        self.stNotice.SetLabel("")

        p = self.getActivePattern()
        for pattern in self.choices:
            if pattern.name == newName and p != pattern:
                self.stNotice.SetLabel("Name already used, please pick another")
                return

        if newName == "":
            self.stNotice.SetLabel("Invalid name")
            return

        sTR = service.TargetResists.getInstance()
        sTR.renamePattern(p, newName)

        self.headerSizer.Replace(self.namePicker, self.ccResists)
        self.ccResists.Show()
        self.namePicker.Hide()
        self.btnSave.Hide()
        self.headerSizer.Remove(self.btnSave)
        for btn in (self.new, self.rename, self.delete, self.copy):
            self.headerSizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)
            btn.Show()

        sel = self.ccResists.GetSelection()
        self.ccResists.Delete(sel)
        self.ccResists.Insert(newName, sel)
        self.ccResists.SetSelection(sel)
        self.ValuesUpdated()
        self.unrestrict()

    def copyPattern(self,event):
        sTR = service.TargetResists.getInstance()
        p = sTR.copyPattern(self.getActivePattern())
        self.choices.append(p)
        id = self.ccResists.Append(p.name)
        self.ccResists.SetSelection(id)
        self.btnSave.SetLabel("Copy")
        self.renamePattern()
        self.patternChanged()

    def deletePattern(self,event):
        sTR = service.TargetResists.getInstance()
        sel = self.ccResists.GetSelection()
        sTR.deletePattern(self.getActivePattern())
        self.ccResists.Delete(sel)
        self.ccResists.SetSelection(max(0, sel - 1))
        del self.choices[sel]
        self.patternChanged()

    def __del__( self ):
        pass

    def importPatterns(self, event):
        text = fromClipboard()
        if text:
            sTR = service.TargetResists.getInstance()
            # @todo: fix return value and use that to determine label
            sTR.importPatterns(text)
            self.stNotice.SetLabel("Patterns imported from clipboard")
        else:
            self.stNotice.SetLabel("Could not import from clipboard")

    def exportPatterns(self, event):
        sTR = service.TargetResists.getInstance()
        toClipboard( sTR.exportPatterns() )
        self.stNotice.SetLabel("Patterns exported to clipboard")
