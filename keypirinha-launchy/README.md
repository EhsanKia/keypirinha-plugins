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
To install this plugin, simply copy `Launchy.keypirinha-package` from the `build` folder to `InstalledPackages`:
- Portable version: `Keypirinha\portable\Profile\InstalledPackages`
- Installed version: `%APPDATA%\Keypirinha\Profile\InstalledPackages`

You may need to restart Keypirinha afterwards to load the plugin.

Next, find launchy.ini (under `%appdata%\Launchy`), and copy the content of the `[directories]` section.
Then configure the Launchy plugin in Keypirinha and paste the config under `[directories]`.
Finally, refresh your Catalog and the items should appear as you type.

For debugging, you can use the Keypirinha console, which will display errors as well as information
about how many items were indexed by the Launchy plugin and issues with the configuration.

## Changelog

- 1.0: Initial release