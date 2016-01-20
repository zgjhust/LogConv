#! /usr/bin/python
# -*- encoding:utf-8 -*-
import re
from Tkinter import *
from ttk import *
# from Tix import *
import tkFileDialog

YEAR = 0x1CAE8C13E000000
DAY = 0x00141DD76000000
HOUR = 0x0000D693A400000
MIN = 0x000003938700000
SEC = 0x0000000F4240000
MSEC = 0x0000000003E8000
BASE_YEAR = 1900
DAYS_YEAR = 365
DAYS_LEAPYEAR = 366
FEB = 2
days = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

# Convert a stck date to human readable and a Julian date


def stckToDate(stck):
	if len(stck) == 0: raise ValueError('wrong length of stck value!')
	if not isValidHex(stck): raise ValueError('stck not a valid hex string!')

	# The last 15 bits of very large numbers in Javascript
	# are suspect and there precision may not be maintained.
	# Thus we chop off the last 16 bits and will add it back
	# in at the end of the conversion.
	# import pdb; pdb.set_trace()
	stckVal = int(stck,16)
	dytt = 0

	while stckVal >= YEAR:
		stckVal = stckVal - YEAR
		if isLeapYear(dytt + BASE_YEAR):
			stckVal = stckVal - DAY
		dytt = dytt + 1

	# the clock started in 1900 so we add on the base year
	# import pdb; pdb.set_trace()
	dytt = dytt + BASE_YEAR

	# get the Julian date...we are on the day after
	# the number of full days that have passed
	dtjd = int(stckVal/DAY + 1)
	stckVal = stckVal % DAY
	dthr = int(stckVal/HOUR)
	stckVal = stckVal % HOUR
	dtmin = int(stckVal/MIN)
	stckVal = stckVal % MIN
	dtsec = int(stckVal/SEC)
	stckVal = stckVal % SEC
	dtmsec = int(stckVal/MSEC)
	# get the month
	dtmm = 1
	dtot = 0
	daysNextMonth = days[0]
	while dtot + daysNextMonth < dtjd:
		dtot = dtot + daysNextMonth
		daysNextMonth = days[dtmm] 
		if (dtmm + 1) == FEB & isLeapYear(dytt):
			daysNextMonth = daysNextMonth + 1
		dtmm = dtmm + 1
	return "%s-%s-%s %s:%s:%s.%s" %(str(dytt), str(dtmm).zfill(2), str(dtjd-dtot).zfill(2),
				str(dthr).zfill(2), str(dtmin).zfill(2), str(dtsec).zfill(2), str(dtmsec).zfill(2))

def isValidHex(val):
	for i in val:
		if i not in 'abcdefABCDEF0123456789':
			return False
	return True


def isLeapYear(year):
	if (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
		return True
	return False

class LogRec(object):
	# rex_W = re.compile(r"\n")
	rex_URID = re.compile(r".*URID[(](.*?)[)]")
	rex_LRSN = re.compile(r".*LRSN[(](.*?)[)]")
	rex_TYPE = re.compile(r".*?TYPE[(](.*?)[)]")
	rex_SUBTYPE = re.compile(r".*SUBTYPE[(](.*?)[)]")

	def __init__(self, head, content):
		self.head = head
		self.content = content

	def get_urid(self):
		m = LogRec.rex_URID.match(self.head.replace('\n',''))
		if m:
			return m.group(1).strip()
		else:
			return ""

	def get_lrsn(self):
		m = LogRec.rex_LRSN.match(self.head.replace('\n',''))
		if m:
			return stckToDate(m.group(1).strip() + '0000')
		else:
			return ""

	def get_type(self):
		m = LogRec.rex_TYPE.match(self.head.replace('\n',''))
		if m:
			return m.group(1).strip()
		else:
			return ""

	def get_subtype(self):
		m = LogRec.rex_SUBTYPE.match(self.head.replace('\n',''))
		if m:
			return m.group(1).strip()
		else:
			return ""

class LogAnalyzeGUI(Frame):
	def __init__(self, master):
		self.logrecs = []
		self.master = master
		master.title("DB2z日志分析小工具v0.2")
		master.wm_state("zoomed")
		master.minsize(1072,836)
		self.create_gui()
		
	def do_open(self):
		fn = tkFileDialog.askopenfilename(filetypes=(("Log files","*.log"),("Text files","*.txt"),("All files","*.*")))
		if fn:
			self.open_logfile(fn)
			self.resetWidget()
			for i, rec in enumerate(self.logrecs):
				self.tvWidget.insert('', 'end', text=str(i), values=(rec.get_urid(), rec.get_lrsn(), rec.get_type(), rec.get_subtype()))

	def resetWidget(self):
		# import pdb;pdb.set_trace()
		children = self.tvWidget.get_children()
		for child in children:	
			self.tvWidget.delete(child)
		self.scrollTextCont.delete("1.0", END)
		self.scrollTextHead.delete("1.0", END)

	def showAbout(self):
		pass

	def open_logfile(self, filename):
		if self.logrecs:
			for i in self.logrecs:
				del i
		self.logrecs = []
		with open(filename) as fr:
			fall = fr.read()
			rex = re.compile(r"(\W{0,2}[0-9A-Fa-f]{12}.*MEMBER.*\n(?:.*\n){0,4}\W+)(\W*\*LRH\*(?:.*[*].*\n)+\W+)", re.MULTILINE)
			for match in rex.finditer(fall):
				hd, content = match.groups()
				# the rex removed the beginning blanks, add them back
				self.logrecs.append(LogRec(hd, '      '+content))
	def create_gui(self):

		# the menu
		self.mnuBar = Menu(self.master)
		fileMnu = Menu(self.mnuBar, tearoff=0)
		fileMnu.add_command(label="Open", command=self.do_open)
		fileMnu.add_separator()
		fileMnu.add_command(label="Exit", command=self.master.quit)
		self.mnuBar.add_cascade(label="File", menu=fileMnu)

		hlpMnu = Menu(self.mnuBar, tearoff=0)
		hlpMnu.add_command(label="About", command=self.showAbout)
		self.mnuBar.add_cascade(label="Help", menu=hlpMnu)
		self.master.config(menu=self.mnuBar)


		# the treeview
		self.lblSeq = Label(text='DB2操作时序')
		self.lblSeq.grid(sticky=E+W)

		self.tvWidget = Treeview(self.master, height=15)
		self.tvWidget['columns'] = ('URID', 'LRSN', 'Type', 'SubType')
		self.tvWidget.heading("#0", text='Sequence', anchor='center')
		self.tvWidget.column('#0', anchor='w')
		self.tvWidget.heading('URID', text='URID')
		self.tvWidget.column('URID', anchor='center')
		self.tvWidget.heading('LRSN', text='LRSN')
		self.tvWidget.column('LRSN', anchor='center')
		self.tvWidget.heading('Type', text='Type')
		self.tvWidget.column('Type', anchor='center')
		self.tvWidget.heading('SubType', text='SubType')
		self.tvWidget.column('SubType', anchor='center')
		self.tvWidget.grid(sticky=E+W)
		self.tvWidget.bind("<<TreeviewSelect>>", self.on_item_select)
		# the head info
		self.lblHead = Label(text='日志头信息')
		self.lblHead.grid(sticky=E+W)
		self.scrollTextHead = Text(self.master, height=10)
		self.scrollTextHead.grid(sticky=E+W)

		# the content
		self.lblCont = Label(text='日志内容')
		self.lblCont.grid(sticky=E+W)
		self.scrollTextCont = Text(self.master,height=23)
		self.scrollTextCont.grid(sticky=E+W)

		#copy right
		self.lblCopyright = Label(text = 'Copyright 2016 @ 数据中心系统处 系统一组     ', \
			 						anchor=E, foreground="#BBBBBB", font="微软黑体")
		self.lblCopyright.grid(sticky=E+W)
		self.master.columnconfigure(0, weight=1)
		self.master.rowconfigure(1,weight=1)
		self.master.rowconfigure(3,weight=1)
		self.master.rowconfigure(5,weight=1)

	def on_item_select(self, event):
		item = event.widget.selection()
		if item:
			i = self.tvWidget.item(item)
			self.scrollTextHead.delete('1.0', END)
			self.scrollTextHead.insert(END, self.logrecs[int(i["text"])].head)
			self.scrollTextCont.delete('1.0', END)
			self.scrollTextCont.insert(END, self.logrecs[int(i["text"])].content)


if __name__ == '__main__':

	root = Tk()
	app = LogAnalyzeGUI(root)
	root.mainloop()
