# Keypirinha launcher (keypirinha.com)
from .lib import acf
from .lib import appinfo
from .lib import regobj

import keypirinha_util as kpu
import keypirinha_net as kpn
import keypirinha as kp

import collections
import time
import json
import os
import re

STEAM_ICON_CDN = "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/{0.id}/{0.icon}"
App = collections.namedtuple('App', ['id', 'name', 'icon'])


class Steam(kp.Plugin):
    """
    Add installed Steam games to your catalog.

    Version: 2.4
    """

    CATEGORY = kp.ItemCategory.USER_BASE + 1

    def on_start(self):
        # Try to load app cache if there is one
        self.appcache = {}
        cache_path = self.get_package_cache_path(create=True)
        appcache_path = os.path.join(cache_path, 'appcache.json')
        if os.path.exists(appcache_path):
            with open(appcache_path) as fp:
                data = json.load(fp)
            for appid, name, icon in data:
                self.appcache[appid] = App(appid, name, icon)

    def on_catalog(self):
        try:
            # Fetch steam installation from registry
            steam_exe = regobj.HKCU.Software.Valve.Steam['SteamExe'].data
            steam_path = regobj.HKCU.Software.Valve.Steam['SteamPath'].data
        except AttributeError:
            self.error("Steam not found in registry.")
            return

        start_time = time.time()

        # Set default icon to Steam icon
        default_icon_path = "@{},0".format(steam_exe)
        default_icon_handle = self.load_icon(default_icon_path)
        self.set_default_icon(default_icon_handle)

        # Load and cache icons for all the installed games found
        installed_apps = self.get_applist(steam_path)
        icon_dir = os.path.join(steam_path, 'steam', 'games')
        icons = self.get_icons(installed_apps, icon_dir)

        # Create an item for each game and set catalog
        items = [
            self.create_item(
                category=self.CATEGORY,
                label=app.name,
                target=str(app.id),
                data_bag="{}|{}".format(app.id, steam_exe),
                short_desc="Launch game",
                icon_handle=icons.get(app.id),
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.KEEPALL)
            for app in installed_apps]
        self.set_catalog(items)

        elapsed = time.time() - start_time
        stat_msg = "Cataloged {} games in {:0.1f} seconds"
        self.info(stat_msg.format(len(items), elapsed))

    def on_execute(self, item, action):
        # https://developer.valvesoftware.com/wiki/Steam_Application_IDs
        appid, steam_exe = item.data_bag().split('|', 1)
        target = "-applaunch {} {}".format(appid, item.raw_args())
        kpu.shell_execute(steam_exe, args=target)

    def on_suggest(self, user_input, items_chain):
        if items_chain:
            clone = items_chain[-1].clone()
            clone.set_args(user_input)
            self.set_suggestions([clone])

    def get_applist(self, steam_dir):
        # Compute some relative paths
        steamapps_dir = os.path.join(steam_dir, 'steamapps')
        appinfo_path = os.path.join(steam_dir, 'appcache', 'appinfo.vdf')

        # Find extra Steam library folders
        library_list = [steamapps_dir]
        librarylist_path = os.path.join(steamapps_dir, 'libraryfolders.vdf')
        try:
            with open(librarylist_path) as fp:
                library_data = acf.load(fp)
            for key, library_root in library_data['LibraryFolders'].items():
                if not key.isdigit():
                    continue
                extra_library = os.path.join(library_root, 'steamapps')
                library_list.append(extra_library)
        except Exception as e:
            self.warn('Failed to extract extra library paths: {}'.format(e))

        # Scan all Steam libraries to find installed games
        results = []
        installed = []
        for library_folder in library_list:
            for filename in os.listdir(library_folder):
                match = re.match(r'appmanifest_(\d+)\.acf', filename)
                if not match:
                    continue
                appid = int(match.group(1))
                installed.append(appid)

                # If we have the app cached, use that
                if appid in self.appcache:
                    results.append(self.appcache[appid])

        if len(results) == len(installed):
            # Since loading appinfo.vdf is expensive, we only do it if needed
            # We can return if all installed apps were in the cache
            return results

        # Load appinfo.vdf to extract info about games
        with open(appinfo_path, 'rb') as fp:
            data = appinfo.load(fp)

        results = []
        for appid in installed:
            info = data.get(appid)
            if not info:
                self.warn('Did not find info for {}'.format(appid))
                continue

            common = info['sections'][b'appinfo'].get(b'common')
            if not common or common[b'type'].lower() not in [b'game', b'application']:
                continue

            icon = None
            if b'clienticon' in common:
                icon = common[b'clienticon'].decode('utf-8') + '.ico'

            if isinstance(common[b'name'], appinfo.Integer):
                decoded_name = str(common[b'name'])
            else:
                decoded_name = common[b'name'].decode('utf-8')

            app = App(appid, decoded_name, icon)
            results.append(app)

        # Update and save the cache
        for app in results:
            self.appcache[app.id] = app
        cache_path = self.get_package_cache_path(create=True)
        appcache_path = os.path.join(cache_path, 'appcache.json')
        with open(appcache_path, 'w') as fp:
            json.dump(list(self.appcache.values()), fp)

        return results

    def get_icons(self, apps, icon_dir):
        icon_handles = {}
        opener = kpn.build_urllib_opener()
        cache_path = self.get_package_cache_path(create=True)
        for app in apps:
            if app.icon is None:
                continue

            icon_source = "cache://{}/{}".format(self.package_full_name(), app.icon)
            icon_handles[app.id] = self.load_icon(icon_source)

            # First check if we already have the icon in the cache
            cache_icon = os.path.join(cache_path, app.icon)
            if os.path.exists(cache_icon):
                continue

            # If not, check steam's icon cache folder
            steam_icon = os.path.join(icon_dir, app.icon)
            if os.path.exists(steam_icon):
                with open(steam_icon, 'rb') as f1, open(cache_icon, 'wb') as f2:
                    f2.write(f1.read())
                continue

            # Last resort, we download and cache the icon
            icon_url = STEAM_ICON_CDN.format(app)
            self.warn(icon_url)
            self.info('Downloading icon for {}'.format(app.name))
            with opener.open(icon_url) as resp, open(cache_icon, 'wb') as fp:
                fp.write(resp.read())

        return icon_handles
