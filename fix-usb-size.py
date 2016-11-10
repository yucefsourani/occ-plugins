# -*- coding: utf-8 -*-
"""
Ojuba Control Center
Copyright © 2009, Ojuba Team <core@ojuba.org>
        Released under terms of Waqf Public License.
        This program is free software; you can redistribute it and/or modify
        it under the terms of the latest version Waqf Public License as
        published by Ojuba.org.
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
        The Latest version of the license can be found on
        "http://waqf.ojuba.org/license"
"""
import subprocess
import os
import time
from gi.repository import Gtk
from OjubaControlCenter.pluginsClass import PluginsClass
from OjubaControlCenter.widgets import  error, info, sure


## NOTE: these global vars is loader validators
category = 'hw'
caption = _('Fix flash memory size')
description = _("Fix USB Flash Memory Size")
priority = 100



class occPlugin(PluginsClass):
    def __init__(self,ccw):
        PluginsClass.__init__(self, ccw, caption, category, priority)
                
        vbox=Gtk.VBox(False,10)
        self.add(vbox)
        
        hbox=Gtk.HBox(False,2)
        vbox.pack_start(hbox,False,False,6)
        
        self.labeldescription=Gtk.Label(description)
        hbox.pack_start(self.labeldescription,False,False,0)
        
        hbox2=Gtk.HBox(False,5)
        vbox.pack_start(hbox2,False,False,0)
        
        self.labeltarget=Gtk.Label(_('Target Device:'))
        hbox2.pack_start(self.labeltarget, False,False,2)
        
        self.target_dev_ls=Gtk.ComboBoxText(tooltip_text=_("Select Device"))
	self.target_dev_ls.props.width_request=510
        hbox2.pack_start(self.target_dev_ls, False,False,2)
        
        buttonrefresh=Gtk.Button(stock=Gtk.STOCK_REFRESH,tooltip_text=_("Refresh Device"))
        buttonrefresh.connect('clicked', self.__refresh_target_dev)
        hbox2.pack_start(buttonrefresh, False,False,2)
        
        hbox3=Gtk.HBox(False,2)
        vbox.pack_start(hbox3,False,False,0)
        
        
        
        buttonfix=Gtk.Button(_('Run Fix'),tooltip_text=_("Run fix flash"))
        buttonfix.connect('clicked', self.__fix_flash_memory)
        buttonfix.set_size_request(110,30)
        hbox3.pack_start(buttonfix,False,False,315)
        
        self.__refresh_target_dev()

    
    
    def __refresh_target_dev(self, *args):
        self.target_dev_ls.get_model().clear()
        
        for f in  self.__get_flash_memory_directory():
            self.target_dev_ls.append_text(f)

            

    def __is_correct_directory(self,directory):
        if os.path.exists(directory):
            if directory[-1].isalpha() and directory.startswith("/dev/sd") and directory[-1]!="a":
                return True
			
            elif directory[-1].isalpha() and directory.startswith("/dev/mmcblk"):
                return True
			
            return False
		
        else:
            return False
		
		
    def __get_flash_memory_directory(self):
        result=[]
        flashs1= subprocess.Popen("ls /dev |grep sd",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].decode('utf-8').strip().split()
        flashs2= subprocess.Popen("ls /dev |grep mmcblk",stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].decode('utf-8').strip().split()
        
        for f in flashs1:
            if self.__is_correct_directory("/dev/%s"%f):
                result.append("/dev/%s"%f)
			
        for f in flashs2:
            if self.__is_correct_directory("/dev/%s"%f):
                result.append("/dev/%s"%f)
		
        return result


    def __fix_flash_memory(self,button):
        directory=self.target_dev_ls.get_active_text()        
        if directory==None:
            return error(_("Select Device"), self.ccw)
        

        
        info(_("WARNING! ALL DATA ON DRIVE %s WILL BE LOST!"%directory), self.ccw)
        if not sure(_("ALL DATA ON DRIVE %s WILL BE LOST! Are you sure you want to continue?"%directory), self.ccw):
            return
            
        if not os.path.exists(directory):
            self.__refresh_target_dev()
            return error(_("Select Device"), self.ccw)
            
        nn="100%"


        check=self.ccw.mechanism('run','system',"dd if=/dev/zero of=%s count=1 bs=1M"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.1"), self.ccw)
        
        check=self.ccw.mechanism('run','system',"eject %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.2"), self.ccw)
        check=self.ccw.mechanism('run','system',"eject -t %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.3"), self.ccw)
        
        check=self.ccw.mechanism('run','system',"parted %s mktable msdos -s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.4"), self.ccw)
    


        check=self.ccw.mechanism('run','system',"eject %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.5"), self.ccw)
        


        check=self.ccw.mechanism('run','system',"eject -t  %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.6"), self.ccw)

		
        check=self.ccw.mechanism('run','system',"parted %s mkpart primary fat32 1M %s -s"%(directory,nn))
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.7"), self.ccw)
            

		
        check=self.ccw.mechanism('run','system',"eject %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.8"), self.ccw)
            


        check=self.ccw.mechanism('run','system',"eject -t  %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.9"), self.ccw)
        
 
		
        time.sleep(2)
        self.ccw.mechanism('run','system',"umount $(findmnt %s1  -n -o TARGET)  &>/dev/null"%directory)
        

		

		
        check=self.ccw.mechanism('run','system',"mkfs.vfat -F 32 %s1 -n FLASH"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.10"), self.ccw)
		

        
		
        check=self.ccw.mechanism('run','system',"eject %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.11"), self.ccw)
            

        
        check=self.ccw.mechanism('run','system',"eject -t  %s"%directory)
        if check!='0':
            return error(_("unexpected return code, possible an error had occurred.12"), self.ccw)
        


        info(_('Done.'), self.ccw)
		
 
