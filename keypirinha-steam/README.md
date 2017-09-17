# Keypirinha Plugin: Steam

This is keypirinha-steam, a plugin for the [Keypirinha](http://keypirinha.com) launcher.


## Description

This plugin adds installed Steam games to your catalog, letting you launch them from keypirinha.

The current implemented method uses the registry to get a list of installed games.
It also fetches a database of game names from the Steam, which it then caches.

Version 2.0 completely reworked the way games are loaded.
First, to get the list of installed games, the plugin scans the steamapps folder for asf files.
Next, it loads appinfo.vdf, which contains name and icon information for each owned app.
Since this file can be very large and slow to load, the plugin will cache this information,
so unless new games are installed, refreshing the catalog is generally instant.

As for icons, the plugins first tries to fetch them from Steam's icon cache folder,
and if it doesn't find it, it will download it from the Steam CDN. The plugin keeps
its own cache of game icons for future uses.

You can also press tab to set launch options on a selected game.


## Installation

1. Copy `Steam.keypirinha-package` from the `build` folder to `InstalledPackages`:
  * Portable version: `Keypirinha\portable\Profile\InstalledPackages`
  * Installed version: `%APPDATA%\Keypirinha\Profile\InstalledPackages`
2. Restart Keypirinha to load the plugin.


## Debugging

If needed, you can use the Keypirinha console to debug your Launchy configuration. The console will display errors as well as information about how many games were indexed.


## Changelog

- 1.0: Initial release
- 2.0: Complete rewrite of the way games are loaded
- 2.1: Add support for multiple Steam library folders
