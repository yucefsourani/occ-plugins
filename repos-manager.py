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
import os
from gi.repository import Gtk
from OjubaControlCenter.pluginsClass import PluginsClass
from OjubaControlCenter.widgets import  error, info


## NOTE: these global vars is loader validators
category = 'install'
caption = _('Manager repos')
description = _("Manager Repos")
priority = 100



class occPlugin(PluginsClass):
    def __init__(self,ccw):
        PluginsClass.__init__(self, ccw, caption, category, priority)
        self.__reposdirs=["/etc/yum.repos.d/","/etc/distro.repos.d/"]
        self.__reposinformations=None
        self.__refresh_repos_informations()
        
        
        self.hbox=Gtk.HBox(spacing=20)
        self.add(self.hbox)
        self.vbox1=Gtk.VBox(spacing=5)
        self.vbox2=Gtk.VBox(spacing=5,homogeneous=True)
        self.hbox.pack_start(self.vbox1,True,True,0)
        self.hbox.pack_start(self.vbox2,True,True,0)
        self.name_label=Gtk.Label(_("<b>Name</b>"),use_markup=True)
        self.execute_label=Gtk.Label(_("<b>Switch</b>"),use_markup=True)
        self.vbox1.pack_start(self.name_label,True,True,0)
        self.vbox2.pack_start(self.execute_label,True,True,0)
        
        for k,v in self.__reposinformations.items():
			self.name=Gtk.Label(k)
			self.switch=Gtk.Switch()
			if v=="Disabled":
				self.switch.set_active(False)
			else:
				self.switch.set_active(True)
			self.switch.connect("notify::active",self.__enable_or_disable,k)

			self.vbox1.pack_start(self.name,True,True,0)
			self.vbox2.pack_start(self.switch,True,True,0)
			
    def __refresh_repos_informations(self):
        self.__reposinformations=self.__get_information_from_location()
    
    def __enable_or_disable(self,b,s,data):
        if  b.get_active():
            check=self.ccw.mechanism('run','system',"dnf config-manager --set-enable %s -y"%data)
            if check!='0':
                return error(_("unexpected return code, possible an error had occurred"), self.ccw)
            
        else:
            check=self.ccw.mechanism('run','system',"dnf config-manager --set-disable %s -y"%data)
            if check!='0':
                return error(_("unexpected return code, possible an error had occurred"), self.ccw)
            
        
        info(_('Done.'), self.ccw)
    
    def __get_information_from_repofile(self,repo_file):
        result={}
        key=""
        try:
            with open(repo_file,"r") as repofile:
                for line in repofile:
                    line=line.strip()
                    if line.startswith("["):
                        result.setdefault(line[1:-1],None)
                        key=line[1:-1]
                    if line.startswith("enable"):
                        result[key]=line[8:]
                        if line[8:]=="0" or line[8:]=="false" or line[8:]=="False":
                            result[key]="Disabled"
                        else:
                            result[key]="Enabled"
        except:
            return None
        
        return result
    
    def __get_information_from_location(self):
        result={}
        locations=self.__reposdirs
        for location in locations:
            if os.path.isdir(location):
                for f in os.listdir(location):
                    if f.endswith(".repo"):
                        informations=self.__get_information_from_repofile("%s%s"%(location,f))
                        if informations!=None:
                            for k,v in informations.items():
                                result.setdefault(k,v)
        return result

