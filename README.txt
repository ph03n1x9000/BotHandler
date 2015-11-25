BotHandler
==========

========== DESCRIPTION ==========

B3 plugin that handles game bots for Urban Terror server.

========== INSTALLATION ==========

1) Copy bothandler.py to b3/extplugins 
2) Copy bothandler.ini to b3/extplugins/conf
3) If you are using b3.xml as config file, add the following to the plugin section:
     <plugin name="bothandler" config="@b3/extplugins/conf/bothandler.ini" />
   If you are using b3.ini for config file enter the following under the plugin section:
   bothandler: @b3/extplugins/conf/bothandler.ini
4) Edit the bothandler.ini to meet your needs
5) Restart B3 


========== USAGE ==========

!kickbots or !kb - Kick all bots from the server permanently and disable regulating.
!kickbots <number> or !kb <number> - Kick all bots from server for <number> minutes.
!addbots or !ab - Add bots to the server and enable regulating (kicks bots as player enters server)
!addbots <number> - Add <number> of bots to server and do not regulate them. Bots must be disabled (by using !kickbots) for this to work

