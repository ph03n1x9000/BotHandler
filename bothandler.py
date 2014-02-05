__version__ = '1.0'

import b3, time, threading, re
import b3.events
import b3.plugin
import shutil
import os
    
class BotmapsurtPlugin(b3.plugin.Plugin):
    _allBots = []
    _custom_maps = {} # Maps to add
    _clients = 0 # Clients control at round_start
    _addmaps = False # Map where the plugin will copy the custom maps
    _putmap = False
    _remmaps = False # Map where the plugin will remove the custom maps
    _sourcepath = "" # Directory from where maps will be copied
    _destpath = "" # Directory where maps will be copied
    _newmapcycle = "" # Mapcycle with custom maps
    _oldmapcycle = "" # Mapcycle with bots
    _botstart = True # To control if the plugin has to to add bots or not
    _botstart2 = False
    _botminplayers = 4 # Bots control related with players
    _minmapplayers = 0
    _clients = 0 # Clients number
    _bots = 0 # bots number
    _mapbots = 0
    _i = 0
    _FFA = True
    _adding = False
    _first = True
    
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
        if event.type == b3.events.EVT_GAME_ROUND_START:
            if self._first:
                self.addMaps()
                self.console.write('bot_minplayers "0"')
                gametype = self.console.getCvar('g_gametype').getInt()
                if gametype == 0:
                    if self._botstart:
                        if self._FFA:
                            self._bots = 0
                            self._clients = 0
                            self._i = 0
                            self._adding = False
                            self.console.write("kick allbots")
                            self.addBots()
                            self._FFA = False
                else:
                    self._FFA = True
                self._first == False
                #t = threading.Timer(10, self.addMaps) # Add bots
                #t.start()
            else:
                self._first = True
                #self._botstart2 = True

        elif event.type == b3.events.EVT_GAME_EXIT:
            if self._first:
                self.addMaps()
                if self._botstart:
                    self._botstart = False
                    self._botstart2 = True
                    self._mapbots = self._bots
                self._first == False
                #if self._putmap:
                 #   self.console.write('map %s' % self.console.getNextMap())
                  #  self._putmap = False
            else:
                self._first = True
        elif event.type == b3.events.EVT_CLIENT_AUTH:
            sclient = event.client
            if self._mapbots != False:
                if self._botstart:
                    self.addBots()
                else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): # Get allplayers
                        self._clients += 1                    
            elif 'BOT' not in sclient.guid:
                if self._botstart:
                    self.addBots()
                else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): # Get allplayers
                        self._clients += 1                    
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            sclient = event.client
            if 'BOT' not in sclient.guid:
                if self._botstart:
                    self.addBots() 
                else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): # Get allplayers
                        self._clients += 1
        elif event.type == b3.events.EVT_STOP:
            self.console.write("kick allbots")
            
    def onLoadConfig(self):
        self.loadBotstuff() # Get stuff from the .xml
        
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
                    
                    
    def addBots(self):
        #self.debug('starting proceess to add/rem bots')
        #self.debug('self._i = %s' % self._i)
        self._bots = 0
        self._clients = 0
        if self._botstart: # if bots are enabled
            self.console.write("bot_enable 1")
            for c in self.console.clients.getClientsByLevel(): # Get allplayers
                self._clients += 1
                
                if 'BOT' in c.guid:
                    self._clients -= 1
                    self._bots += 1
                    #self.debug('loop bots = %s' % self._bots)
            
            clients = self._clients
            bots = self._bots
            bclients = self._botminplayers - clients - bots
            #self.debug('bots = %s' % bots)
            #self.debug('clients = %s' % clients)
            #self.debug('bclients = %s' % bclients)
            if bclients == 0 or ((self._clients - self._bots) > self._botminplayers):
                self.debug('bclients = %s, stopping check' % bclients)
                return False
            if self._mapbots > bots:
                self.debug('self._mapbots = %s, bots = %s. STOPPING' % (self._mapbots, bots))
                return False
            self._mapbots = False
            # bclients = (bots + clients)

            if bclients > 0: # Check if we need to add bots
                self.debug('adding bots')
                if self._adding:
                    self._i += 1
                    #self.debug('self._i += 1')
                    #self.debug('self._i = %s' % self._i)

                while bclients > 0: # Add all the necessary bots
                    #if bclients == 0:
                    #    break
                    bclients -= 1
                    if self._i == len(self._allBots):
                        break
                    self.console.write('addbot %s %s %s %s %s' % (self._allBots[self._i][0], self._allBots[self._i][1], self._allBots[self._i][2], self._allBots[self._i][3], self._allBots[self._i][4]))
                    self._bots += 1
                    if self._i < (len(self._allBots)):
                        self._i += 1
                        #self.debug('self._i += 1')
                        #self.debug('self._i = %s' % self._i)
                self._adding = True
                if self._i > 0:
                    self._i -= 1
                #self.debug('self._i -= 1')
                #self.debug('self._i = %s' % self._i)
                    
            elif bclients < 0: # Check if we need to kick bots
                self.debug('kicking bots')
                while bclients < 0:
                    #if bclients == 0:
                    #    self.debug('BREAKED CAUSE ITS 0(kicking)')
                    #    break
                
                    #self.debug('player = %s' % self._allBots[self._i][4])
                    #self.debug('i(kick) = %s and i = %s' % (self._allBots[self._i][4], self._i))
                    self._bots -= 1
                    bclients += 1
                    self.console.write('kick %s' % self._allBots[self._i][4])
                    self._i -= 1

                self._adding = True
            
    def enableBots(self):
        self.console.say('No-bots time finished, adding bots...')
        self._botstart = True
        self.addBots()

    def disableBots(self):
        self._botstart = False
        self._bots = 0
        self._clients = 0
        self._i = 0
        self._adding = False
        self._mapbots = False
        self.console.write("kick allbots")

    def cmd_kickbots(self, data, client, cmd=None):
        """\
        kick all bots in the server. <perm> to kick them until you use !addbots
        """
        input = self._adminPlugin.parseUserCmd(data)
        self.disableBots()
        if not input:
            client.message('^7You ^1kicked ^7all bots in the server')
            client.message('^7Use ^2!abots ^7to add them')
            return false

        regex = re.compile(r"""^(?P<number>\d+)$""");
        match = regex.match(data)

        time = int(match.group('number'))
        t = threading.Timer((time * 60), self.enableBots)
        t.start()
        client.message('^7You ^1kicked ^7all bots in the server for ^5%s ^7minutes' % time)
        client.message('^7Use ^2!abots ^7to add them')
        
    def cmd_addbots(self, data, client, cmd=None):
        """\
        Add bots to the server
        """
        self._botstart = True
        self.addBots()
        client.message('^7Bots ^2added^7.')
