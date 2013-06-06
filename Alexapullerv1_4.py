#!/usr/bin/env python

import wx
import os
import re
import glob
import threading


class MyFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self,parent, title=title, size=(750,300), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
		self.panel = wx.Panel(self,-1)
		
		self.sourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,65))
		
		self.twosourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,115))
		
		self.destinationprint = wx.StaticText(self.panel, -1, "Awaiting Destination Directory",(400,165))
		
		self.openprint = wx.StaticText(self.panel, -1, "Awaiting EDL/TXT/XML File",(400,20))
		
		self.oncopy = wx.StaticText(self.panel, -1, "",(400,215))
		
		openButton = wx.Button(self.panel, -1, 'Open', (250,15),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.OnOpen, openButton)
		
		self.rushesSource = wx.Button(self.panel, -1, '1st Source', (250,60),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.FindSource, self.rushesSource)
		self.rushesSource.Enable(False)
		
		self.tworushesSource = wx.Button(self.panel, -1, '2nd Source', (250,110),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.twoFindSource, self.tworushesSource)
		self.tworushesSource.Enable(False)
		
		self.rushesDestination = wx.Button(self.panel, -1, 'Destination', (250,160), (130,-1))
		self.Bind(wx.EVT_BUTTON, self.SetDest, self.rushesDestination)
		self.rushesDestination.Enable(False)
		
		"""
		PrintCheckedButton = wx.Button(self.panel, -1, 'Print Checked', (250,150))
		self.Bind(wx.EVT_BUTTON, self.PrintChecked, PrintCheckedButton)
		"""
		
		self.DoTheCopyButton = wx.Button(self.panel, -1, 'Pull Files', (250,210),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.DoCopy, self.DoTheCopyButton)
		self.DoTheCopyButton.Enable(False)
		
		self.selectAllButton = wx.Button(self.panel, -1, "All", (15,210), (50,-1))
		self.Bind(wx.EVT_BUTTON, self.SelectAll, self.selectAllButton)
		self.selectAllButton.Enable(False)
		
		self.selectNoneButton = wx.Button(self.panel, -1, "None", (80,210), (50,-1))
		self.Bind(wx.EVT_BUTTON, self.SelectNone, self.selectNoneButton)
		self.selectNoneButton.Enable(False)
		
		self.listBox = wx.CheckListBox(self.panel, -1, (20, 6), (220, 195), "", wx.LB_SINGLE)
		self.inlistDisplay = wx.StaticText(self.panel, -1, "",(160,215))
		self.listBox.Bind(wx.EVT_PAINT, self.on_list_update)
		
		"""
		self.makefiles = wx.Button(self.panel, -1, "Make Files", (270,210))
		self.Bind(wx.EVT_BUTTON, self.makefilesfunction, self.makefiles)
		"""
		filemenu = wx.Menu()
		
		menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit", "Terminate the program")
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		
		
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Centre()
		self.Show(True)
		
	def on_list_update(self, event):
		event.Skip()
		self.filecount = self.listBox.GetCount()
		self.findchecked = self.listBox.GetChecked()
		self.filecountdisplay = str(len(self.findchecked)) + "/" + str(self.filecount) + " Found"
		self.inlistDisplay.SetLabel(self.filecountdisplay)
		self.Refresh()

	def SetDest(self,e):
		self.Destname = ''
		checkedinlist = self.listBox.GetCheckedStrings()
		DestDlg = wx.DirDialog(self, "Choose Your Destination Directory:",self.Destname, wx.DD_DIR_MUST_EXIST, (50,50), (50,50))
		if DestDlg.ShowModal() == wx.ID_OK:
			self.DirDest = DestDlg.GetPath()
			self.destinationprint.SetLabel(str(self.DirDest))
			for r, d, f in os.walk(self.DirDest):
				for file in f:
					f_name, f_ext = os.path.splitext(file)
					if ".mov" == f_ext:
						if f_name in checkedinlist:
							checkedindex = self.output.index(f_name)
							
							self.listBox.Check(checkedindex, False)
							
						
			self.DoTheCopyButton.Enable(True)
			
			
			
		DestDlg.Destroy()
	
	def FindSource(self,e):
		self.SourceDictionary = {}
		self.dirDirname = ''
		dirDlg = wx.DirDialog(self, "Choose Your 1st Rushes Directory:",self.dirDirname, wx.DD_DIR_MUST_EXIST, (50,50), (50,50))
		if dirDlg.ShowModal() == wx.ID_OK:
			self.DirFilename = dirDlg.GetPath()
			self.sourceprint.SetLabel(str(self.DirFilename))
			self.rushesDestination.Enable(True)
			self.firstPass = list(self.output)
			for r, d, f in os.walk(self.DirFilename):
				for file in f:
					f_name, f_ext = os.path.splitext(file)
					if ".mov" == f_ext:
					
					
						if f_name in self.output:
						
							src_abs_path = os.path.join(r, file)
							self.SourceDictionary[f_name] = src_abs_path
							
							SourceIndexOne = self.output.index(f_name)
							self.listBox.Check(SourceIndexOne, True)
						
							if f_name in self.firstPass:
								self.firstPass.remove(f_name)
							else:
								pass
			
			self.firstsourcelist = self.listBox.GetCheckedStrings()				
			self.tworushesSource.Enable(True)
			self.twoDirFilename = ''
			
			
		dirDlg.Destroy()	
		
	def twoFindSource(self,e):
		self.secondsourcelist = []
		self.dirDlg = wx.DirDialog(self, "Choose Your 2nd Rushes Directory:",self.dirDirname, wx.DD_DIR_MUST_EXIST, (50,50), (50,50))
		if self.dirDlg.ShowModal() == wx.ID_OK:
			self.twoDirFilename = self.dirDlg.GetPath()
			self.twosourceprint.SetLabel(str(self.twoDirFilename))
		
			for r, d, f in os.walk(self.twoDirFilename):
				for file in f:
					
					f_name, f_ext = os.path.splitext(file)
					
					if ".mov" == f_ext:
						if f_name in self.firstPass:
							
							src_abs_path = os.path.join(r, file)
							self.SourceDictionary[f_name] = src_abs_path
							

							self.secondsourcelist.append(f_name)
							SourceIndexOne = self.output.index(f_name)
							self.listBox.Check(SourceIndexOne, True)
						
		self.dirDlg.Destroy()
		
	def OnOpen(self,e):
		"""Open a File"""
		self.dirname = ''
		dlg = wx.FileDialog(self, "Choose a File:",self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			r = open(os.path.join(self.dirname, self.filename), 'r+')
			self.edlfile = os.path.join(self.dirname, self.filename)
			self.openprint.SetLabel(str(self.edlfile)) 
			line = r.readline()
			foundList = list()
			for line in r:
				matchObj = re.search( r'\w\d\d\d\w\d\d\d_([^\s]+)', line, re.M|re.I)
				if matchObj:
					foundAlexaRoll = matchObj.group()
					foundList.append(foundAlexaRoll)
				else:
					pass
			self.output = []
			def removeDupe(foundList):
				for x in foundList:
					if x not in self.output:
						self.output.append(x)
					else:
						pass
			removeDupe(foundList)
			self.output.sort()
			self.listBox.Set(self.output)
			self.inthelist = self.output
			self.selectAllButton.Enable(True)
			self.selectNoneButton.Enable(True)
			self.rushesSource.Enable(True)
			
			r.close()
		dlg.Destroy()
		
	def SelectAll(self, e):
		self.listBox.SetChecked(range(0,len(self.output)))
		
	def SelectNone(self, e):
		self.listBox.SetChecked(range(0,0))
		
	def PrintChecked(self,e):
		self.PrintChecked = self.listBox.GetCheckedStrings()
		print self.PrintChecked
		
	def DoCopy(self,e):
		
		self.worker = PullFiles()
		self.worker.start()
		
		
		"""
	def makefilesfunction(self,e):
		for i in self.output:
			temp_path = "/Users/gavinhinfey/Desktop/" + i + ".mov"
			file = open(temp_path, "w")
			file.write("")
			file.close	
		"""
		
	def OnExit(self,e):
		self.Close(True)
	
class PullFiles(threading.Thread):
		
	def __init__(self):
		
		threading.Thread.__init__(self)
		
	def run(self):
		
		report = open("port.txt", "w")
		selectedList = []
		selectedList = frame.listBox.GetCheckedStrings()
		
				
		self.counter = 0
		self.counterText = "Files Copied: "
		self.listlength = len(selectedList)
		print frame.SourceDictionary
		
		for alexa in selectedList:
			
			src_abs_path = frame.SourceDictionary[alexa]
			src_relative_path = os.path.relpath(src_abs_path, frame.DirFilename)
			dst_abs_path = os.path.join(frame.DirDest, src_relative_path)
			dst_dir = os.path.dirname(dst_abs_path)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)
			ret = os.system("""cp "%s" "%s"  """ % (src_abs_path, dst_abs_path))
			if ret != 0:
				putFoundOnNewLine = src_abs_path + "\n"
				report.write(putFoundOnNewLine)
			else:
				self.counter += 1
				self.toPrint = self.counterText + str(self.counter) + "/" + str(self.listlength)
				wx.CallAfter(frame.oncopy.SetLabel, self.toPrint)


		report.close()
		
		
		
	
app = wx.App(True)
frame = MyFrame(None,"Alexa Puller v1.4")
app.MainLoop()
