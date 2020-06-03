# -*- coding:utf-8 -*-
# Copyright (C) 2020 Rui Fontes <rui.fontes@tiflotecnia.com> with code from palavras-master from Python.pro.br
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import globalPluginHandler
import os
import api
import textInfos
from textInfos import offsets
import collections
import string
import wx
from wx.lib.expando import ExpandoTextCtrl
import gui
from gui import guiHelper
from ui import message
from time import sleep
import globalVars
from keyboardHandler import KeyboardInputGesture
import codecs
import re
from globalCommands import SCRCAT_CONFIG
import time
import addonHandler
addonHandler.initTranslation()

#filepath = os.path.join (os.path.dirname(__file__), "palavras_pt_PT.txt")
#filepath = os.path.join (os.path.dirname(__file__), "palavras_br.txt")
filepath = os.path.join (os.path.dirname(__file__), "words_alpha.txt")
letters = 'aáàãâbcçdeéêfghiíjklmnoóõôpqrstuúvwxyz'
allText = ""
wordsList = []
vocabulary = []
misspelled = ""
msParagraph = ""
x = 0
y = 0
candidates = []
misspelledWord = ""

def vocabularyCreation():
	# Creating the global and personal vocabulary.
	global vocabulary
	with open(filepath, "r", encoding = "UTF-8") as f:
		vocabulary = f.read().split()
	# Creating personal dictionary if exists, or ignore if not exisxts.
	if os.path.exists (os.path.join (os.path.dirname(__file__), "personal.txt")) == False:
		checkVocabulary()
		return
	else:
		with open (os.path.join (os.path.dirname(__file__), "personal.txt"), "r", encoding = "UTF-8") as g:
			pVocabulary = g.read().split()
		# Join personal dictionary to global
		vocabulary += pVocabulary
	checkVocabulary()

def checkVocabulary():
	# Check wich words are not present in the dictionary
	global wordsList, misspelled, vocabulary
	for x in range(len(wordsList)):
		# Removing words with numbers...
		if wordsList[x].isdigit() == True:
			pass
		elif any(i.isdigit() for i in wordsList[x]) == True:
			pass
		# Word present in dictionary, so skip it
		elif wordsList[x] in vocabulary:
			pass
		else:
			# Possible misspelled word since it is not part of dictionary...
			# Check if exists in lowercase
			if wordsList[x].lower() in vocabulary:
				pass
			else:
				misspelled = wordsList[x]
				# Forcing the next llop to start where this stopped.
				wordsList = wordsList[x+1:]
				break
	# No possible misspelled words, and reached the end of list... So, inform that spell checking is finished...
	if misspelled == "":
		spellCheckerDialog.Destroy(spellCheckerDialog)
	else:
		getSentence()

def getSentence():
	global misspelled, msParagraph, x, y, allText, letters, misspelledWord
	# Ensure that variables are cleaned...
	msParagraph = ""
	indexIn = 0
	indexEnd = 0
 # Find position of misspelled in original string
	for x in range(len(allText[y:])):
		y = allText.find(misspelled, y, -1)
		# Check if we have find a string in a word or the whole word
		if allText[y-1] not in letters and allText[y+len(misspelled)] not in letters:
			# Considere the word and the character before and after to ensure that when replacing we do not replace part of other word...
			misspelledWord = allText[y-1:y+len(misspelled)+1]
			indexMisspelled = y
			break
	# Find position of sentence beginning
	# Clear the variable...
	index = []
	# Look backward for the first position of ".", ":", ";", "?", "!", "\r" and "\n" as end of previous sentence...
	index.append(allText.rfind(".", 0, indexMisspelled))
	index.append(allText.rfind(":", 0, indexMisspelled))
	index.append(allText.rfind(";", 0, indexMisspelled))
	index.append(allText.rfind("?", 0, indexMisspelled))
	index.append(allText.rfind("!", 0, indexMisspelled))
	index.append(allText.rfind("\n", 0, indexMisspelled))
	index.append(allText.rfind("\r", 0, indexMisspelled))
	# If none is present we must start from begining of the file...
	if max(index) == -1:
		indexIn == 0
	else:
		indexIn = max(index)
	# Find of sentence end
	# Clear the variable...
	index = []
	# Look forward for the first position of ".", ":", ";", "?", "!", "\r" and "\n" as end of the sentence...
	index.append(allText.find(".", indexMisspelled, -1))
	index.append(allText.find(":", indexMisspelled, -1))
	index.append(allText.find(";", indexMisspelled, -1))
	index.append(allText.find("?", indexMisspelled, -1))
	index.append(allText.find("!", indexMisspelled, -1))
	index.append(allText.find("\r", indexMisspelled, -1))
	index.append(allText.find("\n", indexMisspelled, -1))
	index.append(allText.find("\n", indexMisspelled, -1))
	index.append(allText.find("\r", indexMisspelled, -1))
	# Must remove all values of -1 except if all of them are -1, meaning we must go untill end of file...
	while min(index) == -1:
		index.remove(-1)
		if len(index) == 1:
			break
	indexEnd = min(index)
	# Define sentence
	# If = 0 we start from begining of file. If different, we start in the first character after the end of prior sentence...
	if indexIn != 0:
		indexIn += 1
	msParagraph = allText[indexIn:indexEnd+1]
	candidatesList()

def candidatesList():
	# Code of this function is from palavras-master from Python.pro.br
	# Returns all possibilities of words (known and unknown)
	# with up to two mistakes.
	# :param misspelled Set of words.
	global misspelled
	# Not necessary since is declared as global in line 30
	# letters = 'aáàãâbcçdeéêfghiíjklmnoóõôpqrstuúvwxyz'
	deletes = [misspelled[:i]+misspelled[i+1:] for i in range(len(misspelled))]
	splits = [(misspelled[:i], misspelled[i:]) for i in range(len(misspelled) + 1)]
	switchs = [L+R[1]+R[0]+R[2:] for L, R in splits if len(R)>1]
	replaces = [L + letter + R[1:] for L, R in splits for letter in letters]
	adds = [L + letter + R for L, R in splits for letter in letters]
	unigrams = list(set(deletes + switchs + replaces + adds))
	global candidates, vocabulary
	setUnigrams = set(word for word in unigrams)
	setVocabulary = set(word for word in vocabulary)
	candidates = list(setUnigrams.intersection(setVocabulary))
	gui.mainFrame._popupSettingsDialog(spellCheckerDialog)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()

	__gestures={
		"kb:Control+f7": "spellCheck",
	}

	def script_spellCheck(self, gesture):
		# For translators: Message announcing the start of works...
		message(_("Processing... Please wait... This operation can takes some seconds..."))

		# Create the list of words present in the text
		obj = api.getFocusObject()
		treeInterceptor = obj.treeInterceptor
		if hasattr (treeInterceptor, 'TextInfo') and not treeInterceptor.passThrough:
			obj = treeInterceptor
		try:
			info = obj.makeTextInfo (textInfos.POSITION_ALL)
		except (RuntimeError, NotImplementedError):
			info = None
		if not info or info.isCollapsed:
			message (_("Error"))
		else:
			# save allText as the original string...
			global allText
			allText = info.text
			allText1 = str(allText)

			# Removing all punctuations except hyphen, "-", and apostroph, "'", between words.
			toRemove = string.punctuation.replace("\'", "").replace("-", "").replace("@", "").replace(" ", "")+"“"+"”"+"—"+"…"+"«"+"»"
			for z in range(len(toRemove)):
				X = toRemove[z]
				allText1 = allText1.translate(str.maketrans(X, " "))
				allText1 = allText1.replace("- ", " ")

			# Now, create the list...
			global wordsList
			wordsList = allText1.split()

		# Starts the process of spellchecking...
		vocabularyCreation()

class spellCheckerDialog(wx.Dialog):
	# A dialog  to show spellchecker
	_instance = None
	def __new__(cls, *args, **kwargs):
		if spellCheckerDialog._instance is None:
			return wx.Dialog.__new__(cls)
		return spellCheckerDialog._instance

	def __init__ (self, parent):
		spellCheckerDialog._instance = self
		# Translators: Title of the dialog.
		super (spellCheckerDialog, self).__init__(parent, wx.ID_ANY, title = _("Spell checker"))
		title = _("Spell checker")
		self.title = title
		self.makeSettings()

	def makeSettings(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		tasksSizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: A label for the the Not in dictionary field
		NotInDictionLabel = _("&Not in dictionary")
		notDictBox = wx.StaticBox(self, label = NotInDictionLabel)
		self.misspelledCtrl = ExpandoTextCtrl(self, size = (250, -1), value = misspelled, style=wx.TE_READONLY)

		# Translators: A label for the paragraph field
		NotInDiction1Label = _("in the following paragraph:")
		notDict1Box = wx.StaticBox(self, label = NotInDiction1Label)
		self.msParagraphCtrl = ExpandoTextCtrl(self, size = (250, -1), value = msParagraph, style=wx.TE_READONLY)
		# Translators: The label for the list of suggestions.
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		entriesLabelText=_("&Suggestions")
		self.dictList = sHelper.addLabeledControl(entriesLabelText, wx.ListBox, id = wx.ID_ANY, choices = candidates, style = wx.LB_SINGLE, size = (700,580))
		#self.editingIndex=-1

		# Create buttons.
		# Buttons are in a horizontal row
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)

		addButtonID = wx.Window.NewControlId()
		# Translators: Label of button to add the misspelled word to the personal dictionary.
		self.addButton = wx.Button(self, addButtonID, _('&Add'))
		buttonsSizer.Add (self.addButton)

		ignoreButtonID = wx.Window.NewControlId()
		# Translators: Label of button to ignore the misspelled word once.
		self.ignoreButton = wx.Button (self, ignoreButtonID, _('Ignore &once'))
		buttonsSizer.Add(self.ignoreButton)

		ignoreAllButtonID = wx.Window.NewControlId()
		# Translators: Label of button to ignore all cases of the misspelled word.
		self.ignoreAllButton = wx.Button(self, ignoreAllButtonID, _('&Ignore all'))
		buttonsSizer.Add (self.ignoreAllButton)

		substituteButtonID = wx.Window.NewControlId()
		# Translators: Label of button to replace the misspelled word by the suggestion.
		self.substituteButton = wx.Button(self, substituteButtonID, _('&Substitute'))
		buttonsSizer.Add (self.substituteButton)

		substituteAllButtonID = wx.Window.NewControlId()
		# Translators: Label of button to replace all occurrences of the misspelled word by the suggestion.
		self.substituteAllButton = wx.Button(self, substituteAllButtonID, _('Su&bstitute all'))
		buttonsSizer.Add (self.substituteAllButton)

		editButtonID = wx.Window.NewControlId()
		# Translators: Label of button to allow edition of the text.
		self.editButton = wx.Button (self, editButtonID, _('&Edit'))
		buttonsSizer.Add (self.editButton)

		cancelButtonID = wx.Window.NewControlId()
		# Translators: Button Label that closes the add-on.
		self.cancelButton = wx.Button(self, cancelButtonID, _('&Close'))
		buttonsSizer.Add(self.cancelButton)

		tasksSizer.Add(buttonsSizer)
		mainSizer.Add(tasksSizer)

		# Bind the buttons.
		self.Bind(wx.EVT_BUTTON, self.onAdd, id = addButtonID)
		self.Bind (wx.EVT_BUTTON, self.onIgnoreOnce, id = ignoreButtonID )
		self.Bind(wx.EVT_BUTTON, self.onIgnoreAll, id = ignoreAllButtonID)
		self.Bind(wx.EVT_BUTTON, self.onSubstitute, id = substituteButtonID)
		self.Bind(wx.EVT_BUTTON, self.onSubstituteAll, id = substituteAllButtonID)
		self.Bind(wx.EVT_BUTTON, self.onEdit, id = editButtonID)
		self.cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.dictList.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
		self.misspelledCtrl.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
		self.msParagraphCtrl.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Show the window if it is hidden
		if not self.IsShown():
			gui.mainFrame.prePopup()
			self.Show()
			gui.mainFrame.postPopup()

	def onAdd(self,evt):
		global vocabulary, misspelled
		# Create or open a personal dictionary to add our words or words not in main dictionary...
		with open (os.path.join (os.path.dirname(__file__), "personal.txt"), "a", encoding = "UTF-8") as g:
			g.write(misspelled +"\n")
			g.close()
		# Temporarily add this word to Vocabulary to allow the added word to be considered as correct...
		vocabulary.append(misspelled)
		# Clean the variable...
		misspelled = ""
		# Close the dialog...
		self.Close()
		# Resume the spellchecking...
		checkVocabulary()

	def onIgnoreOnce(self,evt):
		global misspelled
		# Just clean the variable and do nothing since the process restart on next word...
		misspelled = ""
		self.Close()
		checkVocabulary()

	def onIgnoreAll(self,evt):
		global vocabulary, misspelled
		# Temporarily add the word to the dictionary to make it considered correct...
		vocabulary.append(misspelled)
		misspelled = ""
		self.Close()
		checkVocabulary()

	def onSubstitute(self,evt):
		global allText, misspelled, candidates, misspelledWord
		# Get the selected word from the candidates list...
		index = self.dictList.GetSelection()
		# Add to replacement word the character before and after the misspelled word to maintain possible punctuations...
		replacementWord = misspelledWord[0]+str (candidates[index])+misspelledWord[-1]
		# Replace the misspelled by the candidate word selected...
		allText = allText.replace (str(misspelledWord), replacementWord, 1)
		misspelled = ""
		self.Close()
		checkVocabulary()

	def onSubstituteAll(self,evt):
		global allText, misspelled, candidates, misspelledWord, wordsList
		# Get the selected word from the candidates list...
		index = self.dictList.GetSelection()
		# Add to replacement word the character before and after the misspelled word to maintain possible punctuations...
		replacementWord = misspelledWord[0]+str (candidates[index])+misspelledWord[-1]
		# Replace the misspelled by the candidate word selected...
		allText = allText.replace (str(misspelledWord), replacementWord)
		# Remove the misspelled word from the list of words...
		wordsList = list(filter(lambda a: a != misspelled, wordsList))
		misspelled = ""
		self.Close()
		checkVocabulary()

	def onEdit(self,evt):
		global allText, msParagraph
		# Translators: Message dialog box to change a block of text.
		dlg = wx.TextEntryDialog(gui.mainFrame, _("Enter the new block of text or press Enter to confirm"), self.title, style = wx.OK | wx.CANCEL | wx.TE_MULTILINE)
		dlg.SetValue(msParagraph)
		if dlg.ShowModal() == wx.ID_OK:
			corParagraph = dlg.GetValue()
			allText = allText.replace(msParagraph, corParagraph)
			misspelled = ""
		else:
			dlg.Destroy()
			return
		misspelled = ""
		self.Close()
		checkVocabulary()

	def onKeyPress(self, evt):
		# Sets enter key  to replace the misspelled word by the suggestion and Escape to close.
		evt.Skip()
		keycode = evt.GetKeyCode()
		if keycode == wx.WXK_RETURN and self.dictList.GetSelection():
			self.onSubstitute(evt)
		elif keycode == wx.WXK_ESCAPE:
			self.Destroy()

	def Destroy(self):
		self = spellCheckerDialog._instance
		if gui.messageBox(_("Do you want to apply the changes?"), _("Spell checker"), style=wx.ICON_QUESTION|wx.YES_NO) == wx.YES:
			self.applyCorrections()

		spellCheckerDialog._instance = None
		super (spellCheckerDialog, self).Destroy()

	def applyCorrections(self):
		self.Close()
		KeyboardInputGesture.fromName("Control+home").send()
		KeyboardInputGesture.fromName("Control+Shift+end").send()
		api.copyToClip(str(allText))
		time.sleep(2.0)
		KeyboardInputGesture.fromName("Control+v").send()

		spellCheckerDialog._instance = None
		super (spellCheckerDialog, self).Destroy()

