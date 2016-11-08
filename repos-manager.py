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
        self.count=0
        self.hbox=Gtk.HBox()
        self.add(self.hbox)
        self.vbox1=Gtk.VBox()
        self.vbox2=Gtk.VBox()
        self.grid=Gtk.Grid(row_homogeneous=True)
        self.vbox2.pack_start(self.grid,True,True,0)
        self.hbox.pack_start(self.vbox1,True,True,0)
        self.hbox.pack_start(self.vbox2,True,True,0)
        self.name_label=Gtk.Label(_("<b>Name</b>"),use_markup=True)
        self.vbox1.pack_start(self.name_label,True,True,0)
        self.execute_label=Gtk.Label(_("<b>Switch</b>"),use_markup=True)
        self.grid.attach(self.execute_label,0,self.count,1,1)
        self.count+=1
        
        
        
        
        for k,v in self.__reposinformations.items():
            self.name=Gtk.Label(k)
            
            if v=="Disabled":
                self.switch=Gtk.Switch()
            else:
                self.switch=Gtk.Switch()
                self.switch.set_active(True)
            
            self.switch.connect("state-set",self.__enable_or_disable,[k,v])
            self.vbox1.pack_start(self.name,True,True,0)
            self.grid.attach(self.switch,0,self.count,1,1)
            self.count+=1
			
			
    def __refresh_repos_informations(self):
        self.__reposinformations=self.__get_information_from_location()
    
    def __enable_or_disable(self,b,s,data):
        if not b.get_state():
            check=self.ccw.mechanism('run','system',"dnf config-manager --set-enable %s -y"%data[0])
            if check!='0':
                error(_("unexpected return code, possible an error had occurred"), self.ccw)
                b.set_state(False)
                b.set_active(False)
                return True
                
            
        else:
            check=self.ccw.mechanism('run','system',"dnf config-manager --set-disable %s -y"%data[0])
            if check!='0':
                error(_("unexpected return code, possible an error had occurred"), self.ccw)
                b.set_state(True)
                b.set_active(True)
                return True
            
        
        #info(_('Done.'), self.ccw)
    
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

