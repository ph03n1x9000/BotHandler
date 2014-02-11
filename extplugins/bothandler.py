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
#

__version__ = '1.0.0'
__author__ = 'ph03n1x'

import b3, time, threading, re
import b3.events
import b3.plugin
import shutil
import os


class BothandlerPlugin(b3.plugin.Plugin):
    requiresConfigFile = True
    _clients = 0 # Clients at round start
    _bots = 0 # Bots at round start
    _usebots = True

    def onLoadConfig(self):
        self.verbose('Loading config')
        cmdlvl = self.config.get('settings', 'admin_level')
        botminplayers = self.config.get('settings', 'bot_amount')
        bot1 = self.config.get('bots', 'bot1')
        bot2 = self.config.get('bots', 'bot2')
        bot3 = self.config.get('bots', 'bot3')
        bot4 = self.config.get('bots', 'bot4')
        bot5 = self.config.get('bots', 'bot5')
        bot6 = self.config.get('bots', 'bot6')
        bot7 = self.config.get('bots', 'bot7')
        bot8 = self.config.get('bots', 'bot8')

    def onStartup(self):
        # get the admin plugin so we can register commands
        self._adminPlugin = self.console.getPlugin('admin')
 
        if not self._adminPlugin:
            # something is wrong, can't start without admin plugin
            self.error('Could not find admin plugin')
            return

        #registering commands
        self._adminPlugin.registerCommand(self, 'kickbots', int(cmdlvl), self.kickBots, 'kb')
        self._adminPlugin.registerCommand(self, 'addbots', int(cmdlvl), self.addBots, 'ab')

        # Registering events
        self.verbose('Registering events')
        self.registerEvent(b3.events.EVT_CLIENT_AUTH)
        self.registerEvent(b3.events.EVT_CLIENT_DISCONNECT)
        self.registerEvent(b3.events.EVT_CLIENT_JOIN)
        self.registerEvent(b3.events.EVT_CLIENT_TEAM_CHANGE)
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        self.registerEvent(b3.events.EVT_GAME_ROUND_START)
        self.registerEvent(b3.events.EVT_STOP)

        #kick all bots that might already be in game and make sure bots are enabled
        self.console.write("kick allbots")
        self.consold.write("bot_enable 1")
        self._bots = 0

    def onEvent(self, event):
        if event.type == b3.EVT_GAME_ROUND_START:
            self.console.write('bot_minplayers "0"')
            self.console.write("kick allbots")
            self.addBots()
        elif event.type == b3.events.EVT_CLIENT_JOIN:
            sclient = event.client
            if self._usebots:
                self.addBots()
            elif 'BOT' not in sclient.guid:
                if self._usebots:
                    self.addBots()
                else:
                    self._clients = 0
                    for c in self.console.clients.getClientsByLevel(): #get current players again
                        self._clients += 1
        elif event.type == b3.events.EVT_CLIENT_DISCONNECT:
                sclient = event.client
                if 'BOT' not in sclient.guid:
                if self._usebots:
                    self.addBots()
        elif event.type == b3.events.EVT_STOP:
                self.console.write("kick allbots")
                
    def addBots(self):
        self.console.write('bot_enable 1')
        self._usebots = True
        self._clients = 0
        for c in self.console.clients.getClientsByLevel(): # Get allplayers
                self._clients += 1

                if 'BOT' in c.guid:
                    self._clients -= 1
                    self._bots += 1

        humans = self._clients
        bots = self._bots
        humanbots = humans + bots
        toadd = self.botminplayers - humanbots

        if humanbots < self.botminplayers:
            self.verbose('Adding bots')
            if toadd == 8:
                self.console.write('addbot %s' % (self.bot1))
                self.console.write('addbot %s' % (self.bot2))
                self.console.write('addbot %s' % (self.bot3))
                self.console.write('addbot %s' % (self.bot4))
                self.console.write('addbot %s' % (self.bot5))
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 7:
                self.console.write('addbot %s' % (self.bot2))
                self.console.write('addbot %s' % (self.bot3))
                self.console.write('addbot %s' % (self.bot4))
                self.console.write('addbot %s' % (self.bot5))
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 6:
                self.console.write('addbot %s' % (self.bot3))
                self.console.write('addbot %s' % (self.bot4))
                self.console.write('addbot %s' % (self.bot5))
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 5:
                self.console.write('addbot %s' % (self.bot4))
                self.console.write('addbot %s' % (self.bot5))
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 4:
                self.console.write('addbot %s' % (self.bot5))
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 3:
                self.console.write('addbot %s' % (self.bot6))
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 2:
                self.console.write('addbot %s' % (self.bot7))
                self.console.write('addbot %s' % (self.bot8))
            elif toadd == 1:
                self.console.write('addbot %s' % (self.bot8))
            else
                client.message('^2Bots already on server')
                
    def reEnable(self):
        self.console.say('Bots on the way, brace yourself...')
        self._usebots = True
        self.addBots()

    def kickBots(self, data, client, cmd=None):
        """\
        kick all bots in the server. <perm> to kick them until you use !addbots
        """
        input = self._adminPlugin.parseUserCmd(data)
        self._usebots = False
        if not input:
            self.console.write('kick allbots')
            client.message('^7You ^1kicked ^7all bots')
            client.message('^7Use ^2!ab ^7to add them')
            return None

        regex = re.compile(r"""^(?P<number>\d+)$""");
        match = regex.match(data)

        time = int(match.group('number'))
        t = threading.Timer((time * 60), self.reEnable)
        t.start()
        client.message('^7You ^1kicked ^7all bots for ^5%s ^7minutes' % time)
        client.message('^7Use ^2!ab ^7to add them')
        
