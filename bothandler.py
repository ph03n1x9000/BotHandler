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
    _adding = False
    _first = True
    
    
    #Get details from config file
    def onLoadConfig(self):


                self.NameBot1 = self.config.get('settings', 'name_bot1')
                self.NameBot2 = self.config.get('settings', 'name_bot2')
                self.NameBot3 = self.config.get('settings', 'name_bot3')
                self.NameBot4 = self.config.get('settings', 'name_bot4')
                self.NameBot5 = self.config.get('settings', 'name_bot5')
                self.NameBot6 = self.config.get('settings', 'name_bot6')
                self.NameBot7 = self.config.get('settings', 'name_bot7')
                self.NameBot8 = self.config.get('settings', 'name_bot8')
                
                self.ConfigBot1 = self.config.get('settings', 'caracteristic_bot1')
                self.ConfigBot2 = self.config.get('settings', 'caracteristic_bot2')
                self.ConfigBot3 = self.config.get('settings', 'caracteristic_bot3')
                self.ConfigBot4 = self.config.get('settings', 'caracteristic_bot4')
                self.ConfigBot5 = self.config.get('settings', 'caracteristic_bot5')
                self.ConfigBot6 = self.config.get('settings', 'caracteristic_bot6')
                self.ConfigBot7 = self.config.get('settings', 'caracteristic_bot7')
                self.ConfigBot8 = self.config.get('settings', 'caracteristic_bot8')
                    
                self.Max_Bot = self.config.getint('settings', 'maximum_bot')
                self.min_level_kickbots_cmd = self.config.getint('settings', 'min_level_kickbots_cmd')
                self.min_level_addbot_cmd = self.config.getint('settings', 'min_level_addbot_cmd')

                
    #get admin plugin before registering commands
    self._adminPlugin = self.console.getPlugin('admin')
                if not self._adminPlugin:
                    # Error: cannot start without admin plugin
                    self.error('Could not find admin plugin')
                else:
                    self._adminPlugin.registerCommand(self, 'kickbots', self.min_level_kickbots_cmd, self.kickBots, 'kb')
                    self._adminPlugin.registerCommand(self, 'addbots', self.min_level_addbot_cmd, self.addBots, 'ab')
        

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_STOP)

     ### Stopped here ###
       
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
"""  # This section to be removed           
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
                    
        try:
            self._botminplayers = self.config.getint('settings', 'bot_minplayers')
            if self._botminplayers < 0:
                self._botminplayers = 0
        except:
            self._botminplayers = 4
""" # End of removed section
            
    def addBots(self):
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
            client.message('^7Use ^2!addbots ^7to add them')
            return false

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
