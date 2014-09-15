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
!kickbots <number> or !kb <number> - Kick all bots from server for <number> minutes.
!addbots or !ab - Add bots to the server and enable regulating (kicks bots as player enters server)


========== Notes ==========

Info for new function added with update 1.0.1:
!ab <number> - will add <number> bots to server.

For this function to work, you must first disable regulating by using !kb.
When this is used, the specified bots will not be regulated, thus will not be kicked unless you use !kb.

========== Changelog ==========

v1 - Initial release
v1.0.1 - Changed functioning and excluded spectators from regulation.
v1.0.2 - Changed player counting function to query server directly instead of B3. Removed map change params.
