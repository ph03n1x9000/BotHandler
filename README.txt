BotHandler
==========

========== DESCRIPTION ==========

B3 plugin that handles game bots for Urban Terror server
The goal is to have smooth bot handling...

Special thanks to TheLouK (www.sniperjum.com)!

========== INSTALLATION ==========

1) Copy bothandler.py to b3/extplugins 
2) Copy bothandler.xml to b3/extplugins/conf
3) Add "<plugin name="bothandler" config="@b3/extplugins/conf/bothandler.xml" />" to your b3.xml plugin section 
4) Edit the bothandler.xml to meet your needs
5) Restart B3 


========== USAGE ==========

!kickbots or !kb - Kick all bots from the server permanently and disable regulating.
!kickbots <number> or !kb <number> - Kill all bots from server for <number> minutes.
!addbots or !ab - Add bots to the server and enable regulating (kick bots as player enters server)
!addbots <number> or !ab <number> - add <number> extra bots to server. Will not change regulating mode (seperate from normal bots in !addbots)


About extra bots:
The extra bots are defined in the config file (bothandler.xml). You can specify the bot's cofiguration there.
These extra bots are seperate from the other bots defined in the config.
This means that you can add them even if the others are in game. No duplicate name issues will arise.
They were meant to take your place in the game if you need to spec or will be afk for a while.
The amount of extra bots are limited to 2, trying to add more than 2 will result in an error.
You can technically add them again and again (for example typing "!ab 2" then "!ab 2" again).
However, doing that will result in dulicate name issues, which can potentially cause problems with other plugins.
You can kick other bots and disable regulating and still use the extra bots, useful in some cases.

========== Changelog ==========
V1.0.1
Added Extra-bot functions

V 1.0.0
Complete recode from scratch...Fully Functional!
