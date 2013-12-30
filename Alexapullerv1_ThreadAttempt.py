#!/usr/bin/env python

import wx
import os
import re
import glob
from threading import *


# Button definitions
ID_START = wx.NewId()
ID_STOP = wx.NewId()

# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
	"""Define Result Event."""
	win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data


class WorkerThread(Thread):
	"""Worker Thread Class."""
	def __init__(self, notify_window):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self._notify_window = notify_window
		self._want_abort = 0
		# This starts the thread running on creation, but you could
		# also make the GUI thread responsible for calling this
		self.start()
		
	def run(self):
		"""Run Worker Thread."""
		# This is the code executing in the new thread. Simulation of
		# a long process (well, 10s here) as a simple loop - you will
		# need to structure your processing so that you periodically
		# peek at the abort variable

		report = open("report.txt", "w")
		selectedList = []
		selectedList = MyFrame.listBox.GetCheckedStrings()
		
		selectedfirstsource = []
		selectedsecondcource = []
		
		for i in selectedList:
			if i in MyFrame.firstsourcelist:
				selectedfirstsource.append(i)
			else:
				pass
				
		if MyFrame.twoDirFilename != "":
			for x in selectedList:
				if x in MyFrame.secondsourcelist:
					selectedsecondcource.append(x)
				else:
					pass
				
		MyFrame.counter = 0
		MyFrame.counterText = "Files Copied: "
		MyFrame.listlength = len(selectedfirstsource)
		
		for r, d, f in os.walk(MyFrame.DirFilename):
			for file in f:
				f_name, f_ext = os.path.splitext(file)
				if ".mov" == f_ext:
					if f_name in selectedfirstsource:
						MyFrame.counter += 1
						MyFrame.toPrint = MyFrame.counterText + str(MyFrame.counter) + "/" + str(MyFrame.listlength)
						MyFrame.oncopy.SetLabel(MyFrame.toPrint)
						src_abs_path = os.path.join(r, file)
						src_relative_path = os.path.relpath(src_abs_path, MyFrame.DirFilename)
						dst_abs_path = os.path.join(MyFrame.DirDest, src_relative_path)
						dst_dir = os.path.dirname(dst_abs_path)
						if not os.path.exists(dst_dir):
							os.makedirs(dst_dir)
						ret = os.system("""copy "%s" "%s"  """ % (src_abs_path, dst_abs_path))
						if ret != 0:
							putFoundOnNewLine = f_name + "\n"
							report.write(putFoundOnNewLine)
							
		totallistlength = MyFrame.listlength + len(selectedsecondcource)
		if MyFrame.twoDirFilename != "":
			for r, d, f in os.walk(MyFrame.twoDirFilename):
				for file in f:
					f_name, f_ext = os.path.splitext(file)
					if ".mov" == f_ext:
						if f_name in selectedsecondcource:
							MyFrame.counter += 1
							MyFrame.toPrint = MyFrame.counterText + str(MyFrame.counter) + "/" + str(len(selectedList))
							MyFrame.oncopy.SetLabel(MyFrame.toPrint)
							src_abs_path = os.path.join(r, file)
							src_relative_path = os.path.relpath(src_abs_path, MyFrame.twoDirFilename)
							dst_abs_path = os.path.join(MyFrame.DirDest, src_relative_path)
							dst_dir = os.path.dirname(dst_abs_path)
							if not os.path.exists(dst_dir):
								os.makedirs(dst_dir)
							ret = os.system("""copy "%s" "%s" """ % (src_abs_path, dst_abs_path))
							if ret != 0:
								putFoundOnNewLine = f_name + "\n"
								report.write(putFoundOnNewLine)
		else:
			pass

		report.close()

		
		# Here's where the result would be returned (this is an
		# example fixed result of the number 10, but it could be
		# any Python object)
		wx.PostEvent(self._notify_window, ResultEvent(10))
		
	def abort(self):
		"""abort worker thread."""
		# Method for use by main thread to signal an abort
		self._want_abort = 1
		
		
class MyFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self,parent, title=title, size=(750,300), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
		self.panel = wx.Panel(self,-1)
		
		self.sourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,65))
		
		self.twosourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,115))
		
		self.destinationprint = wx.StaticText(self.panel, -1, "Awaiting Destination Directory",(400,165))
		
		self.openprint = wx.StaticText(self.panel, -1, "Awaiting EDL/TXT/XML File",(400,20))
		
		self.status = wx.StaticText(self.panel, -1, "",(400,215))
		
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
		self.Bind(wx.EVT_BUTTON, self.OnStart, id=ID_START)
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
		
		"""wx.Button(self, ID_STOP, 'Stop', pos=(0,50))
		self.Bind(wx.EVT_BUTTON, self.OnStop, id=ID_STOP)
		"""



		# Set up event handler for any worker thread results
		EVT_RESULT(self,self.OnResult)

		# And indicate we don't have a worker thread yet
		self.worker = None

		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
		self.Centre()
		self.Show(True)
		
	def OnStart(self, event):
		"""Start Computation."""
		# Trigger the worker thread unless it's already busy
		if not self.worker:
			self.status.SetLabel('Starting computation')
			self.worker = WorkerThread(self)
			
	def OnStop(self, event):
		"""Stop Computation."""
		# Flag the worker thread to stop if running
		if self.worker:
			self.status.SetLabel('Trying to abort computation')
			self.worker.abort()
	
	def OnResult(self, event):
		"""Show Result status."""
		if event.data is None:
			# Thread aborted (using our convention of None return)
			self.status.SetLabel('Computation aborted')
		else:
			# Process results here
			self.status.SetLabel('Computation Result: %s' % event.data)
		# In either event, the worker is done
		self.worker = None
	
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
		
app = wx.App(True)
frame = MyFrame(None,"Alexa Puller v1.2")
app.MainLoop()
