''' 
Flickr Export Plugin for Acorn
Copyright (c) 2008 Coding Robots, Dmitry Chestnykh 
http://www.codingrobots.com

ISC/OpenBSD License, see AcornFlickrLicense.txt.

'''

import objc
from Foundation import *
from AppKit import *
import os, sys

pluginPath = os.path.expanduser('~/Library/Application Support/Acorn/Plug-Ins')
sys.path.append(pluginPath)

import flickrapi

ACScriptSuperMenuTitle = None
ACScriptMenuTitle = "Export to Flickr..."
ACIsAction = True


class FlickrExportController(NSObject):
    # Outlets
    exportPanel = objc.IBOutlet('exportPanel')
    loginButton = objc.IBOutlet('loginButton')
    authField = objc.IBOutlet('authField')
    titleField = objc.IBOutlet('titleField')
    descriptionField = objc.IBOutlet('descriptionField')
    tagsField = objc.IBOutlet('tagsField')
    privateRadio = objc.IBOutlet('privateRadio')
    familyCheckbox = objc.IBOutlet('familyCheckbox')
    friendsCheckbox = objc.IBOutlet('friendsCheckbox')
    publicRadio = objc.IBOutlet('publicRadio')
    exportButton = objc.IBOutlet('exportButton')
    infoPanel = objc.IBOutlet('infoPanel')
    
    loginStep = 1
    token = None
    frob = None

    def do_login_first_step(self):
        api_key = 'd112ba8e82f4d975c2e90f3a07997ddf'
        api_secret = '3ac72279792c6117'

        self.flickr = flickrapi.FlickrAPI(api_key, api_secret)

        NSLog('FlickrExport: authenticating...')
        (self.token, self.frob) = self.flickr.get_token_part_one(perms='write')
        NSLog('FlickrExport: done...')
        if not self.token: 
            return False
        else:
            return True

    # Actions
    def login_(self, sender):
        logged = False
        if self.loginStep == 1:
            if self.do_login_first_step():
                logged = True
                self.loginStep = 3
            else:
                self.authField.setStringValue_('Click Login again after you finish authorization.')
                self.loginStep = 2
        
        if self.loginStep == 2:
            NSLog("FlickrExport: Login, part two...")
            self.flickr.get_token_part_two((self.token, self.frob))
            logged = True
            self.loginStep = 3
            
        if logged:
            self.authField.setStringValue_('Logged as ' + self.flickr.username)
            self.loginButton.setEnabled_(False)
            self.exportButton.setEnabled_(True)
        
        
    def export_(self, sender):
            	
    	isPublic = 0
    	isFamily = 0
    	isFriend = 0
    	if self.publicRadio.state() == NSOnState:
    	    isPublic = 1
    	if self.familyCheckbox.state() == NSOnState: 
    	    isFamily = 1
    	if self.friendsCheckbox.state() == NSOnState:
    	    isFriend = 1
    	
    	#def export_callback(progress, done):
        #    if done:
        #        # Remove temp file
        #    	#os.remove(self.filePath)
        #    	NSLog("Done!")
        #    else:
        #        NSLog(str(progress) + "%")

        
        self.flickr.upload(
            filename = self.filePath,
            title = self.titleField.stringValue().encode('utf-8'),
            description = self.descriptionField.stringValue().encode('utf-8'),
            tags = self.tagsField.stringValue().encode('utf-8'),
            is_public = isPublic,
            is_family = isFamily,
            is_friend = isFriend,
            callback = None #export_callback #callback doesn't work :(
        )
        NSLog("FlickrExport: Photo uploaded!")
        os.remove(self.filePath)
        NSApplication.sharedApplication().stopModal()
        self.exportPanel.orderOut_(self)
        
    def cancel_(self, sender):
        NSApplication.sharedApplication().stopModal()
        self.exportPanel.orderOut_(self)

    def radioClicked_(self, sender):
        if sender != self.privateRadio: self.privateRadio.setState_(NSOffState)
        if sender != self.publicRadio: self.publicRadio.setState_(NSOffState)
        
    def checkboxClicked_(self, sender):
        self.privateRadio.setState_(NSOnState)
        self.publicRadio.setState_(NSOffState)
        
    def windowWillClose_(self, notification):
        NSApplication.sharedApplication().stopModal()
        if notification.object() == self.infoPanel:
            self.infoPanel.orderOut_(self)
        elif notification.object() == self.exportPanel:
            self.exportPanel.orderOut_(self)
    
    def showInfo_(self, sender):
        self.infoPanel.orderFront_(self)
        NSApplication.sharedApplication().runModalForWindow_(self.infoPanel)
        

flickrExportController = None

def main(image):
    # Load nib on first use
    global flickrExportController
    if not flickrExportController:
        flickrExportController = FlickrExportController.new()

        # Prepare temp file
        doc = NSDocumentController.sharedDocumentController().currentDocument()
        data = doc.dataRepresentationOfType_("public.jpeg")
        flickrExportController.filePath = "/tmp/" + doc.fileName().lastPathComponent().stringByDeletingPathExtension() + ".jpg"
        data.writeToFile_atomically_(flickrExportController.filePath, True)

        nibUrl = NSURL.fileURLWithPath_(os.path.join(pluginPath, 'AcornFlickr.nib'))
        nib = NSNib.alloc().initWithContentsOfURL_(nibUrl)
        nib.instantiateNibWithOwner_topLevelObjects_(flickrExportController, None)

    # Ask user for search terms
    flickrExportController.exportPanel.orderFront_(flickrExportController)
    NSApplication.sharedApplication().runModalForWindow_(flickrExportController.exportPanel)
    #if not getString.result:
    #  return None

    ##
    ## Can't find a way to make windows modal for current document in Acorn :-(
    ##
    #NSApp.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
    #    flickrExportController.exportPanel,
    #    #NSDocumentController.sharedDocumentController().currentDocument().windowForSheet(),
    #    NSApp.keyWindow(), # modalForWindow
    #    self, # modalDelegate
    #    nil, # didEndSelector
    #    nil # contextInfo
    #)
    
    return None
