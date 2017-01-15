# Keypirinha Plugin: Launchy

This is Launchy, a plugin for the [Keypirinha](http://keypirinha.com) launcher.


## Description

This plugin helps populate your Catalog with files and folders using the same
configuration format that Launchy uses. You can either copy your directory settings
straight from the launchy configuration file, or setup your own following a similar format.

In short, this plugin allows you to specify a location to index, a specific depth to look,
as well as file formats you would like to add to the catalog. It will then scan all the
specified directories, filter items according to your configuration and add them to Keypirinha's Catalog.

A more detailed specification of the configuration format can be found in the configuration file.

## Installation

1. Copy `Launchy.keypirinha-package` from the `build` folder to `InstalledPackages`:
  * Portable version: `Keypirinha\portable\Profile\InstalledPackages`
  * Installed version: `%APPDATA%\Keypirinha\Profile\InstalledPackages`
2. Restart Keypirinha to load the plugin.
3. Open Keypirinha and type `Configure Launchy`. This will open the plugin configuration file for editing in Notepad.
4. Follow the instructions in the configuration file to add directories to the Keypirinha catalogue. 
5. ***Optional:*** *Copy your existing Launchy configuration directly over to the plugin. This is possible because the plugin uses the same configuration file format as the orginal Launchy.* <br>
  Find launchy.ini (under `%appdata%\Launchy`) and copy the content of the `[directories]` section. 
6. Open Keypirinha and type `Refresh Catalogue`. 
7. Done! The Keypirinha catalogue should now be populated with the additional items specified in the configuration file. 
  
## Debugging  

If needed, you can use the Keypirinha console to debug your Launchy configuration. The console will display errors as well as information about how many items were indexed.

## Changelog

- 1.0: Initial release
