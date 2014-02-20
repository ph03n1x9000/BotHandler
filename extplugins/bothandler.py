# BotHandler Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2014 ph03n1x
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

__version__ = '1.0.1'
__author__  = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin
import shutil
import os
    
class BothandlerPlugin(b3.plugin.Plugin):
    _allBots = []
    _botstart = True # Is adding bots enabled at startup?
    _botminplayers = 4 # Amount of bots
    _clients = 0 # Clients number
    _bots = 0 # bots number
    _i = 0 # Used in secondary functions
    _adding = False
    _first = True
    _more = 0
    _mb = 0 # used to help forcing of extra bots
    _more_bots = []
    
    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_STOP)
        self._adminPlugin = self.console.getPlugin('admin')
     
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return
        
        # Register commands
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
    
    def onEvent(self, event):
        if event.type == b3.events.EVT_CLIENT_AUTH:
            sclient = event.client
            if self._botstart:
                self.addBots()
            elif self._clients == 0:
                for c in self.console.clients.getClientsByLevel(): # Get players
                    self._clients += 1                    
            elif 'BOT' not in sclient.guid:
                if self._botstart:
                    self.addBots()
            else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): # Get players
                        self._clients += 1                    
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            sclient = event.client
            if 'BOT' not in sclient.guid:
                if self._botstart:
                    self.addBots() 
                else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): # Get players
                        self._clients += 1
        elif event.type == b3.events.EVT_STOP:
            self.console.write("kick allbots")
            
    def onLoadConfig(self):
        self.loadBotstuff() # Get settings from config
        
    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
        
    def loadBotstuff(self):
        for bot in self.config.get('bots/bot'):
            nameBot = bot.find('name').text
            charBot = bot.find('character').text
            lvlBot = bot.find('skill').text
            teamBot = bot.find('team').text
            pingBot = bot.find('ping').text
            self._allBots.insert(1, [charBot, lvlBot, teamBot, pingBot, nameBot])
            self.debug('Bot added: %s %s %s %s %s' % (nameBot, charBot, lvlBot, teamBot, pingBot))
            self._botminplayers = self.config.getint('settings', 'bot_minplayers')
            moreBot1 = self.config.get('more_bots', 'bot1')
            moreBot2 = self.config.get('more_bots', 'bot2')
            self._more_bots.insert(1, [moreBot2, moreBot1])
                    
                    
    def addBots(self):
        self._bots = 0
        self._clients = 0
        if self._botstart: 
            self.console.write("bot_enable 1")
            for c in self.console.clients.getClientsByLevel(): # Get players
                self._clients += 1
                
                if 'BOT' in c.guid:
                    self._clients -= 1
                    self._bots += 1
            
            clients = self._clients
            bots = self._bots
            extrabots = self._botminplayers + self._mb
            bclients = extrabots - clients - bots
            if bclients == 0 or ((self._clients - self._bots) > self._botminplayers):
                self.debug('bclients = %s, stopping check' % bclients)
            
            if bclients > 0: # Check if we need to add bots
                self.debug('adding bots')
                if self._adding:
                    self._i += 1

                while bclients > 0: # Add all the necessary bots
                    bclients -= 1
                    if self._i == len(self._allBots):
                        break
                    self.console.write('addbot %s %s %s %s %s' % (self._allBots[self._i][0], self._allBots[self._i][1], self._allBots[self._i][2], self._allBots[self._i][3], self._allBots[self._i][4]))
                    self._bots += 1
                    if self._i < (len(self._allBots)):
                        self._i += 1

                self._adding = True
                if self._i > 0:
                    self._i -= 1
                    
            elif bclients < 0: # Check if we need to kick bots
                self.debug('kicking bots')
                while bclients < 0:
                
                    self._bots -= 1
                    bclients += 1
                    self.console.write('kick %s' % self._allBots[self._i][4])
                    self._i -= 1

                self._adding = True
            
    def enableBots(self):
        self.console.say('Bots on the way, brace yourself...')
        self._botstart = True
        self.addBots()

    def disableBots(self):
        self._botstart = False
        self._bots = 0
        self._clients = 0
        self._i = 0
        self._adding = False
        self.console.write("kick allbots")
        
    def moreBots(self):
        if self._more > 2:
            self._more = 2
            client.message('Warning: Extra bots limit is 2...auto-changed to 2')
            self._mb += 1
            
        more = self._more
        while more > 0:
            more -= 1
            self.console.write('addbot %s' % (self._more_bots[0][more]))

    def cmd_kickbots(self, data, client, cmd=None):
        input = self._adminPlugin.parseUserCmd(data)
        self.disableBots()
        if not input:
            client.message('^7You ^1kicked ^7all bots in the server')
            client.message('^7Use ^2!ab ^7to add them')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            time = int(match.group('number'))
            t = threading.Timer((time * 60), self.enableBots)
            t.start()
            client.message('^7You ^1kicked ^7all bots  for ^5%s ^7minutes' % time)
            client.message('^7Use ^2!ab ^7to add them')
        
    def cmd_addbots(self, data, client, cmd=None):
        input = self._adminPlugin.parseUserCmd(data)
        if not input:
            self._botstart = True
            self.addBots()
            client.message('^7Bots ^2added^7.')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            self._more = int(match.group('number'))
            self.moreBots()
            client.message('^2Extra bots added. They will be kicked on next map start')

            
