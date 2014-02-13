#!/usr/bin/env python
from __future__ import division
import wx
import os
import re
import glob
import threading
import subprocess
import time
import shutil
import shlex


class MyFrame(wx.Frame):
	
	def __init__(self, parent, title):
		wx.Frame.__init__(self,parent, title=title, size=(750,330), style = wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
		self.panel = wx.Panel(self,-1)
		
		self.sourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,65))
		
		self.twosourceprint = wx.StaticText(self.panel, -1, "Awaiting Source Directory", (400,115))
		
		self.destinationprint = wx.StaticText(self.panel, -1, "Awaiting Destination Directory",(400,165))
		
		self.openprint = wx.StaticText(self.panel, -1, "Awaiting EDL",(400,20))
		
		self.oncopy = wx.StaticText(self.panel, -1, "",(400,215))
		
		self.getsize = wx.StaticText(self.panel, -1, "",(400,235))

		self.getspeed = wx.StaticText(self.panel, -1, "",(400,255))
		
		openButton = wx.Button(self.panel, -1, 'Open', (250,15),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.OnOpen, openButton)
		
		self.rushesSource = wx.Button(self.panel, -1, '1st Source', (250,60),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.FindSource, self.rushesSource)
		self.rushesSource.Enable(False)
		
		self.tworushesSource = wx.Button(self.panel, -1, '2nd Source', (250,110),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.FindSource, self.tworushesSource)
		self.tworushesSource.Enable(False)
		
		self.rushesDestination = wx.Button(self.panel, -1, 'Destination', (250,160), (130,-1))
		self.Bind(wx.EVT_BUTTON, self.SetDest, self.rushesDestination)
		self.rushesDestination.Enable(False)
		
		self.DoTheCopyButton = wx.Button(self.panel, -1, 'Pull Files', (250,210),(130,-1))
		self.Bind(wx.EVT_BUTTON, self.DoCopy, self.DoTheCopyButton)
		self.DoTheCopyButton.Enable(False)
		
		self.fileformats = wx.TextCtrl(self.panel, -1, pos=(25,250), size=(200,-1))
		self.fileformats.SetValue('.mov .R3D .MXF')
		
		self.selectAllButton = wx.Button(self.panel, -1, "All", (15,210), (50,-1))
		self.Bind(wx.EVT_BUTTON, self.SelectAll, self.selectAllButton)
		self.selectAllButton.Enable(False)
		
		self.selectNoneButton = wx.Button(self.panel, -1, "None", (80,210), (50,-1))
		self.Bind(wx.EVT_BUTTON, self.SelectNone, self.selectNoneButton)
		self.selectNoneButton.Enable(False)
		
		self.listBox = wx.CheckListBox(self.panel, -1, (15, 15), (220, 181), "", wx.LB_SINGLE)
		self.inlistDisplay = wx.StaticText(self.panel, -1, "",(160,215))
		self.listBox.Bind(wx.EVT_PAINT, self.on_list_update)
		
		filemenu = wx.Menu()
		
		menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit", "Terminate the program")
		
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		
		self.SourceDictionary = {}
		
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
		
		inputformats = frame.fileformats.GetValue()
		inputformatslist = shlex.split(inputformats)
		
		self.Destname = ''
		checkedinlist = self.listBox.GetCheckedStrings()
		DestDlg = wx.DirDialog(self, "Choose Your Destination Directory:",self.Destname, wx.DD_DIR_MUST_EXIST, (50,50), (50,50))
		if DestDlg.ShowModal() == wx.ID_OK:
			self.DirDest = DestDlg.GetPath()
			self.destinationprint.SetLabel(str(self.DirDest))
			for r, d, f in os.walk(self.DirDest):
				for file in f:
					f_name, f_ext = os.path.splitext(file)
					
					for i in inputformatslist:
					
						if str(i) == f_ext:
					
							if f_name in checkedinlist:
								checkedindex = self.output.index(f_name)
							
								self.listBox.Check(checkedindex, False)
							
			self.DoTheCopyButton.Enable(True)
			
		DestDlg.Destroy()
	
	def FindSource(self,e):
		
		
		inputformats = frame.fileformats.GetValue()
		inputformatslist = inputformats.split(" ")
		
		dirDirname = ''
		
		dirDlg = wx.DirDialog(self, "Choose Your Rushes Directory:",dirDirname, wx.DD_DIR_MUST_EXIST, (50,50), (50,50))
		
		if dirDlg.ShowModal() == wx.ID_OK:
			DirFilename = dirDlg.GetPath()
			
			for r, d, f in os.walk(DirFilename):
				
				for file in f:
					f_name, f_ext = os.path.splitext(file)
					f_name = f_name.upper()
					
					for i in inputformatslist:
						
						if str(i) == f_ext:
					
							if f_name in self.output:
						
								SourceIndexOne = self.output.index(f_name)
							
								src_abs_path = os.path.join(r, file)
								self.SourceDictionary[f_name] = [src_abs_path, DirFilename]
								self.listBox.Check(SourceIndexOne, True)	
						
			
			if self.sourceprint.GetLabel() == "Awaiting Source Directory":
				self.sourceprint.SetLabel(str(DirFilename))
			else:
				self.twosourceprint.SetLabel(str(DirFilename))
				
			self.rushesDestination.Enable(True)
		
		dirDlg.Destroy()	
		
	def OnOpen(self,e):
		
		"""Open a File"""
		self.dirname = ''
		dlg = wx.FileDialog(self, "Choose a File:",self.dirname, "", "*.*", wx.OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetFilename()
			self.dirname = dlg.GetDirectory()
			r = open(os.path.join(self.dirname, self.filename), 'r+')
			self.edlfile = os.path.join(self.dirname, self.filename)
			self.openprint.SetLabel(str(self.filename)) 
			line = r.readline()
			foundList = list()
			
			for line in r:
			
				splitline = shlex.split(line)
				firstinline = splitline[0]
				matchitem = re.search('\d\d\d\d\d\d', firstinline)
				if matchitem:
					foundAlexaRoll = splitline[1]
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
			self.tworushesSource.Enable(True)
			frame.fileformats.Enable(False)
			
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
		
	def OnExit(self,e):
		self.Close(True)
	
class PullFiles(threading.Thread):
		
	def __init__(self):
		
		threading.Thread.__init__(self)
		
	def run(self):
		
		self.finishedPrint = "Copy Started."
		wx.CallAfter(frame.oncopy.SetLabel, self.finishedPrint)
		
		self.calc = CalSizeTime()
		self.calc.start()
		
		self.toPrint = ""
		
		selectedList = []
		selectedList = frame.listBox.GetCheckedStrings()
		
		self.counter = 0
		self.counterText = "Files Copied: "
		self.listlength = len(selectedList)
		
		for alexa in selectedList:
			
			if frame.SourceDictionary.get(alexa):
				
				src_abs_path = frame.SourceDictionary[alexa][0]
				DirFilename = frame.SourceDictionary[alexa][1]
				src_relative_path = os.path.relpath(src_abs_path, DirFilename)
				dst_abs_path = os.path.join(frame.DirDest, src_relative_path)
			
				dst_dir = os.path.dirname(dst_abs_path)
			
				if not os.path.exists(dst_dir):
					os.makedirs(dst_dir)

				self.dst_abs_path = dst_abs_path

				self.dogs = True
				
				self.speed = CalSpeed()
				self.speed.start()

				self.dogs = True

				ret = shutil.copy(src_abs_path, dst_abs_path)
				"""
				self.dogs = False

				if ret != 0:
					pass
				
				else:
				"""
				self.counter += 1
				self.toPrint = self.counterText + str(self.counter) + "/" + str(self.listlength)
				wx.CallAfter(frame.oncopy.SetLabel, self.toPrint)
				
			else:
				pass
				
		self.finishedPrint = "Copy Complete. " + self.toPrint
		wx.CallAfter(frame.oncopy.SetLabel, self.finishedPrint)
		


class CalSpeed(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)

		
	def run(self):

		time.sleep(2)

		self.x = 0
		def work():  

			if frame.worker.dogs:
				y = self.x
				
				threading.Timer(1,work).start();
				self.x = os.path.getsize(frame.worker.dst_abs_path)

				growth = self.x - y
				
				kbs = growth / 1048576
				places = int(kbs * 10**1) / 10**1
				wx.CallAfter(frame.getspeed.SetLabel, str(places) + " MBps")
			else:
				pass
			
		work()

class CalSizeTime(threading.Thread):
	
	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		
		selectedList = frame.listBox.GetCheckedStrings()
		TotalSize = 0
		self.feedback = "Calculating Size..."
		wx.CallAfter(frame.getsize.SetLabel, self.feedback)
		
		for alexa in selectedList:
			if frame.SourceDictionary.get(alexa):
			
				src_abs_path = frame.SourceDictionary[alexa][0]
				
				statinfo = os.stat(src_abs_path)
				TotalSize += statinfo.st_size
		
		CalString = int(TotalSize) / 1073741824
		places = int(CalString * 10**3) / 10**3
		CalStringWithTxt = str(places) + " Gigs In Total."
		self.feedback = CalStringWithTxt
		wx.CallAfter(frame.getsize.SetLabel, self.feedback)
		self.Close(True)
		
		
app = wx.App(True)
frame = MyFrame(None,"ReelID-Copier")
app.MainLoop()
