__version__ = '1.0'
__author__  = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin
import shutil
import os
    
class BothandlerPlugin(b3.plugin.Plugin):
    _allBots = []
    _clients = 0 # Clients control at round_start
    _botstart = True # To control if the plugin has to to add bots or not
    _botminplayers = 6 # Add bots until this number of players in game
    _clients = 0 # Clients number
    _bots = 0 # bots number
    _i = 0 # used in funtioning
    _adding = False
    _first = True
    
    
    #Function to get details from config file
    def onLoadConfig(self):
        self.loadBotstuff()
                
    #Getting xml config here            
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

    #get admin plugin and register commands
    self._adminPlugin = self.console.getPlugin('admin')
            if not self._adminPlugin:
                # Error: cannot start without admin plugin
                self.error('Could not find admin plugin')
                
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
        
    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_STOP)

    def onEvent(self, event):
        if event.type == b3.events.EVT_GAME_ROUND_START:
                self.console.write('bot_minplayers "0"')
                self.console.write("kick allbots")
                self.addBots()
        elif event.type == b3.events.EVT_GAME_EXIT:
            if self._clients <= self._botminplayers
                    self.console.write("bot_enable 1")
                if self._botstart:
                    self._botstart = False
            else:
                self._first = True
        elif event.type == b3.events.EVT_CLIENT_AUTH:
            sclient = event.client
                if self._botstart:
                    self.addBots()
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
        elif event.type == b3.events.EVT_STOP:
            self.console.write("kick allbots")

    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
        
    def addBots(self):
        self._bots = 0
        self._clients = 0
        if self._botstart: # if bots are enabled
            self.console.write("bot_enable 1")
            for c in self.console.clients.getClientsByLevel(): # Get allplayers
                self._clients += 1
                
                if 'BOT' in c.guid:
                    self._clients -= 1
                    self._bots += 1

            clients = self._clients
            bots = self._bots
            bclients = self._botminplayers - clients - bots
            
            if bclients == 0 or ((self._clients - self._bots) > self._botminplayers):
                self.debug('bclients = %s, stopping check' % bclients)
                return False
            
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

    def cmd_kickbots(self, data, client, cmd=None):
        """\
        kick all bots in the server. <perm> to kick them until you use !addbots
        """
        input = self._adminPlugin.parseUserCmd(data)
        self.disableBots()
        if not input:
            client.message('^7You ^1kicked ^7all bots in the server')
            client.message('^7Use ^2!addbots ^7to add them')
            return None

        regex = re.compile(r"""^(?P<number>\d+)$""");
        match = regex.match(data)

        time = int(match.group('number'))
        t = threading.Timer((time * 60), self.enableBots)
        t.start()
        client.message('^7You ^1kicked ^7all bots in the server for ^5%s ^7minutes' % time)
        client.message('^7Use ^2!addbots ^7to add them')
        
    def cmd_addbots(self, data, client, cmd=None):
        #Add bots to the server
        self._botstart = True
        self.addBots()
        client.message('^7Bots ^2added^7.')
