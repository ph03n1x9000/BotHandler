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

# version 1.0.1:
#  - complete recode for faster functioning
#  - players that are in spec will no longer be counted as active players

# version 1.0.2:
#   - Changed the counting function. Will now query the players directly from server
#   - Removed all instances of EVT_GAME_MAP_CHANGE. It is not needed with new counting functioning.
#   - SPECIAL THANKS TO COURGETTE FOR THIS UPDATE!


__version__ = '1.0.2'
__author__  = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin
    
class BothandlerPlugin(b3.plugin.Plugin):
    _allBots = []
    _botsAdded = False # Used withing addBots function to see if we added bots before; to fix indexing.
    _botstart = True # Is adding bots enabled at startup?
    _botminplayers = 4 # Default amount of bots
    _i = 0 # Used in index counting

    
    def onStartup(self):
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_CLIENT_JOIN)
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
        if event.type == b3.events.EVT_CLIENT_JOIN:
            sclient = event.client     
            if not sclient.bot:
                if self._botstart:
                    self.countPlayers()             
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
            sclient = event.client
            if not sclient.bot:
                if self._botstart:
                    self.countPlayers()
            
    def onLoadConfig(self):
        self.loadBotstuff() # Get settings from config
        
    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
        
    def loadBotstuff(self):
        self._botminplayers = self.config.getint('settings', 'bot_minplayers')
        for bot in self.config.get('bots/bot'):
            nameBot = bot.find('name').text
            confBot = bot.find('config').text
            self._allBots.insert(1, [confBot, nameBot])
            self.debug('Bot added: %s %s' % (confBot, nameBot))
            
    def countPlayersBotsAndSpectators(self):
        data = self.console.write('players')
        total = int(data.split('\n')[1][9:])
        players = 0
        spectators = 0
        for m in re.finditer('(?m)' + self.console._rePlayerScore.pattern, data):
            if m.group('team') == 'SPECTATOR':
                spectators += 1
            else:
                players += 1
        bots = total - players - spectators
        return players, bots, spectators

            
    def countPlayers(self):
        humans, bots, _ = self.countPlayersBotsAndSpectators()
        if humans >= self._botminplayers and bots == 0:
            self.debug('No need to act. Minimum human player limit reached')
            return
        elif ((humans + bots) >= self._botminplayers):
            if bots > 0:
                self.debug('We need to kick bots...')
                amount = humans + bots - self._botminplayers 
                self.kickBots(amount)
        elif ((humans + bots) < self._botminplayers):
            self.debug('We need to add bots...')
            amount = self._botminplayers - humans - bots
            self.addBots(amount)
            
    def addBots(self, amount):
        self.verbose('about to add %s bots' % amount)
        if self._botsAdded:
            self._i += 1
        while amount > 0:
            if self._i == len(self._allBots):
                self.debug('self._i is past limit: %s. Breaking...' % self._i)
                break
            amount -= 1
            self.console.write('addbot %s %s' % (self._allBots[self._i][0], self._allBots[self._i][1]))
            if self._i < len(self._allBots):
                self._i += 1

        self._botsAdded = True
        if self._i > 0:
            self._i -= 1

    def kickBots(self, amount):
        self.verbose('about to kick %s bots' % amount)
        while amount > 0:
            amount -= 1
            self.console.write('kick %s' % self._allBots[self._i][1])
            self._i -= 1                
            
    def enableBots(self):
        self.console.say('Bots on the way, brace yourself...')
        self._botstart = True
        self.countPlayers()

    def disableBots(self):
        self._botstart = False
        self._i = 0
        self._botsAdded = False
        self.console.write("kick allbots")
        
# ---------------------------------------------------- COMMANDS ------------------------------------------------------------
    def cmd_kickbots(self, data, client, cmd=None):
        """\
        Kick all bots on server and turn off regulation.
        """
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
        """\
        Add bots to server and turn on regulation.
        """
        input = self._adminPlugin.parseUserCmd(data)
        if not input:
            self._botstart = True
            self.countPlayers()
            client.message('^7Bots ^2added^7.')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            amount = int(match.group('number'))
            if self._botstart:
                client.message('^1Error: Bot regulation is enabled.')
                client.message('^7Use ^2!kickbots ^7and try again')
                return
            elif not self._botstart:
                if amount > len(self._allBots):
                    client.message('^1Cannot send that many bots. ^7Sending ^2%s ^7bots' % (len(self._allBots)))
                    amount = len(self._allBots)
                client.message('^2Adding requested bots')
                self.addBots(amount)
