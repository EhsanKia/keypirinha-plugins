# Keypirinha Plugin: Steam

This is Launchy, a plugin for the [Keypirinha](http://keypirinha.com) launcher.


## Description

This plugin adds installed Steam games to your catalog, and let's you launch them.

The current implemented method uses the registry to get a list of installed games.
It also fetches a database of game names from Steam, which it then caches.

The database is a ~3MB download and 1.5MB when processed and saved on disk.
This plugin will automatically try updating the database if it runs into an app
which it can't find in the database. It will do so at most once a day.

You can also press tab to set launch options for the game.

Currently, game icons are not yet supported. A default Steam icon is used for all games.
Might add per game icons in the future if I find a reliable method to get them.


## Installation

1. Copy `Steam.keypirinha-package` from the `build` folder to `InstalledPackages`:
  * Portable version: `Keypirinha\portable\Profile\InstalledPackages`
  * Installed version: `%APPDATA%\Keypirinha\Profile\InstalledPackages`
2. Restart Keypirinha to load the plugin.


## Debugging

If needed, you can use the Keypirinha console to debug your Launchy configuration. The console will display errors as well as information about how many games were indexed.


## Changelog

- 1.0: Initial release
