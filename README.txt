BotHandler
==========

========== DESCRIPTION ==========

B3 plugin that handles game bots for Urban Terror server.

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

Optional Usage:
Use this when bots are not being regulated (after !kb is used).

!addbots <number> or !ab <number> - add <number> extra bots to server. Will not change regulating mode (seperate from normal bots in !addbots)


About extra bots:
The extra bots are defined in the config file (bothandler.xml). You can specify the bot's cofiguration there.
These extra bots are seperate from the other bots defined in the config.
The amount of extra bots are limited to 2, trying to add more than 2 will result in an error.
You can technically add them again and again (for example typing "!ab 2" then "!ab 2" again).
However, doing that will result in dulicate name issues, which can potentially cause problems with other plugins.
You MUST kick other bots and disable regulating (by using !kb) or else the extra bots will be regulated and kicked.


========== Changelog ==========

V 3.1
Complete recode from LouK's version...Fully Functional!
Added extra bots functions
