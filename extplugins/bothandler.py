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
# version 1.0.3:
#   - Added ability to balance bots after 1 or more bots are kicked
# version 1.0.4
#   - Added ability to auto-start bot regulating if server becomes empty
# version 1.0.5
#   - Recoded addbots and kickbots function to fix bots having duplicate names
#   - Changed event handling to work better with B3 v1.10
#   - Added ability to individually kick a single bot using !kick without breaking plugin functions.

__version__ = '1.0.5'
__author__  = 'ph03n1x'

import b3, threading, re
import b3.events
import b3.plugin
from ConfigParser import ConfigParser


class BothandlerPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    _allBots = {}
    _botStart = True # Is adding bots enabled
    _botminplayers = 4 # Default amount of bots
    _humans = 0  # Used to count humans.
    _empty = False
    botsEnabled = False  # Used to determine whether we already set bot_enable cvar to 1

# ---------------------------------- PLUGIN INITIALIZATION ------------------------------------
    def onStartup(self):
        self.registerEvent('EVT_CLIENT_DISCONNECT', self.playerDisconnected)
        self.registerEvent('EVT_CLIENT_JOIN', self.playerJoinGame)
        self._adminPlugin = self.console.getPlugin('admin')
        # Load admin plugin so we can register commands
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
            
    def onLoadConfig(self):
        config = ConfigParser
        config.optionxform = str
        config.read(self.config.fileName)
        self.loadBotstuff() # Get settings from config
        
    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None
        
    def loadBotstuff(self):
        self._botminplayers = self.config.getint('settings', 'bot_minplayers')
        # Load bot config. Used for xml config
        # for bot in self.config.get('bots/bot'):
        #     nameBot = bot.find('name').text
        #     confBot = bot.find('config').text
        #     self._allBots[nameBot] = {}
        #     self._allBots[nameBot]['config'] = confBot
        #     self._allBots[nameBot]['active'] = False
        #     self.debug('Bot added: %s %s' % (confBot, nameBot))
        if self.config.has_section('bots'):
            for (botname, botconfig) in self.config.items('bots'):
                self._allBots[botname] = {}
                self._allBots[botname]['config'] = botconfig
                self._allBots[botname]['active'] = False
                self.debug('Bot loaded: %s %s' % (botconfig, botname))
        if len(self._allBots.keys()) < self._botminplayers:
            self.debug('bot_minplayers set to %s but %s bots defined in config. bot_minplayers set to %s' % (self._botminplayers, len(self._allBots.keys()), len(self._allBots.keys())))
            self._botminplayers = len(self._allBots.keys())
        elif len(self._allBots.keys()) > self._botminplayers:
            self.debug('Extra bots defined in config, but not used. Removing unneeded config items')
            amountToRemove = len(self._allBots.keys()) - self._botminplayers
            for bot in self._allBots.keys():
                if amountToRemove == 0:
                    break
                self._allBots.pop(bot, None)
                amountToRemove -= 1

# ---------------------------------- EVENT HANDLING ----------------------------------
    def playerJoinGame(self, event):
        if event.client.bot:
            return
        if self._botStart:
            self.countPlayers()

    def playerDisconnected(self, event):
        if event.client.bot:
            if self._allBots[event.client.name]['active']:
                self._allBots[event.client.name]['active'] = False
            return
        if not self._botStart:
            # Automatically enable bots if server is empty
            checkPlayers = self.console.clients.getClientsByLevel()
            if len(checkPlayers) == 0:
                self._empty = True
                self.countPlayers()
        elif self._botStart:
            self.countPlayers()

# ---------------------------------- FUNCTIONS ----------------------------------------
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
        self._humans = humans
        # Check if any bots are incorrectly marked active/inactive
        aMarked = 0
        for c in self._allBots:
            if self._allBots[c]['active']:
                aMarked += 1
        if aMarked != bots:
            self.debug('%s bots on server -> %s marked active' % (bots, aMarked))
            self.debug('There are bots incorrectly marked active/inactive. Recalibrating...')
            self.checkBotCount()
        # Bot [active] checking complete. Continue with bot handling
        if self._empty:
            if humans > 0 and self._botStart != True:
                self._empty = False
                return
            elif humans == 0 and self._botStart != True:
                self._botStart = True
                self._empty = False
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
        if not self.botsEnabled:
            self.enableServerBots()
        self.verbose('about to add %s bots' % amount)
        for b in self._allBots:
            if amount == 0:
                break
            if not self._allBots[b]['active']:
                self.console.write('addbot %s %s' % (self._allBots[b]['config'], b))
                self._allBots[b]['active'] = True
                amount -= 1

    def kickBots(self, amount):
        self.verbose('about to kick %s bots' % amount)
        for b in self._allBots:
            if amount == 0:
                break
            if self._allBots[b]['active']:
                self.console.write('kick %s' % b)
                self._allBots[b]['active'] = False
                amount -= 1
        # Balance bot teams after kicking if any bots are in server
        self.verbose('Balancing bots...')
        bal = True
        for botName in self._allBots:
            if not bal:
                break
            if self._allBots[botName]['active']:
                self.console.write('forceteam %s free' % botName)
                bal = False

    def enableBots(self):
        self.console.say('Bots: ^2Enabled')
        self._botStart = True
        self.countPlayers()

    def disableBots(self):
        self.console.say('Bots: ^1Disabled')
        self._botStart = False
        self.console.write("kick allbots")
        for bot in self._allBots:
            self._allBots[bot]['active'] = False

    def enableServerBots(self):
        self.console.write('bot_enable 1')
        self.botsEnabled = True
        self.debug('Sent [bot_enable 1] to server')

    def checkBotCount(self):
        self.verbose('Checking which bots are incorrectly tagged as active/inactive')
        for a in self._allBots:
            self._allBots[a]['active'] = False
        # Get a list of clients from server and check against our bots
        for c in self.console.clients.getClientsByLevel():
            if c.bot:
                if c.name in self._allBots:
                    self._allBots[c.name]['active'] = True
                    self.verbose('Bot %s --> Active' % c.name)
                elif c.name not in self._allBots:
                    # We don't know this bot, kick him
                    self.debug('Unable to identify bot with name: %s. Kicking...' % c.name)
                    self.console.write('kick %s' % c.name)


# ------------------------------------------------- COMMANDS -----------------------------------------------------------
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
            self._botStart = True
            self.countPlayers()
            client.message('^7Bots ^2added^7.')
        elif input:
            regex = re.compile(r"""^(?P<number>\d+)$""");
            match = regex.match(data)
            amount = int(match.group('number'))
            if self._botStart:
                client.message('^1Error: Bot regulation is enabled.')
                client.message('^7Use ^2!kickbots ^7and try again')
                return
            elif not self._botStart:
                if amount > len(self._allBots):
                    client.message('^1Cannot send that many bots. ^7Sending ^2%s ^7bots' % (len(self._allBots)))
                    amount = len(self._allBots)
                client.message('^2Adding requested bots')
                self.addBots(amount)
