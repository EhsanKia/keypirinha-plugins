# Keypirinha Plugin: Steam

This is keypirinha-steam, a plugin for the [Keypirinha](http://keypirinha.com) launcher.


## Description

This plugin adds installed Steam games to your catalog, letting you launch them from keypirinha.

The current implemented method uses the registry to get a list of installed games.
It also fetches a database of game names from the Steam, which it then caches.

The database is a ~3MB download and 1.5MB when processed and saved on disk.
The plugin will automatically try updating the database if it runs into an app
which it can't find in the database. It will do so at most once a day.

You can also press tab to set launch options on a selected game.

Currently, game icons are not yet supported. A default Steam icon is used for all games.
I might add per game icons in the future if I find a reliable method to get them.


## Installation

1. Copy `Steam.keypirinha-package` from the `build` folder to `InstalledPackages`:
  * Portable version: `Keypirinha\portable\Profile\InstalledPackages`
  * Installed version: `%APPDATA%\Keypirinha\Profile\InstalledPackages`
2. Restart Keypirinha to load the plugin.


## Debugging

If needed, you can use the Keypirinha console to debug your Launchy configuration. The console will display errors as well as information about how many games were indexed.


## Changelog

- 1.0: Initial release
