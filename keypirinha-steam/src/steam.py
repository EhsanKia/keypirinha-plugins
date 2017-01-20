# Keypirinha launcher (keypirinha.com)
from .lib import regobj
import keypirinha_util as kpu
import keypirinha_net as kpn
import keypirinha as kp
import time
import json
import os


class Steam(kp.Plugin):
    """
    Add installed Steam games to your catalog.
    """

    APPLIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    CATEGORY = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self.applist = None

    def on_start(self):
        cache_path = self.get_package_cache_path(create=True)
        applist_path = os.path.join(cache_path, 'applist.json')

        if not os.path.exists(applist_path):
            self.info('Applist not found, downloading...')
            self.download_applist()

        with open(applist_path) as fp:
            self.applist = json.load(fp)

    def on_catalog(self):
        items = []
        start_time = time.time()
        installed_apps = self.apps_from_registry()

        icon_path = "@{},0".format(self.steam_exe)
        icon_handle = self.load_icon(icon_path)
        self.set_default_icon(icon_handle)

        items = [
            self.create_item(
                category=self.CATEGORY,
                label=name,
                target=appid,
                data_bag=appid,
                short_desc="Launch game",
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.KEEPALL)
            for appid, name in installed_apps]

        self.set_catalog(items)
        elapsed = time.time() - start_time
        stat_msg = "Cataloged {} games in {:0.1f} seconds"
        self.info(stat_msg.format(len(items), elapsed))

    def on_execute(self, item, action):
        target = "-applaunch {} {}".format(item.data_bag(), item.raw_args())
        kpu.shell_execute(self.steam_exe, args=target)

    def on_suggest(self, user_input, items_chain):
        if items_chain:
            clone = items_chain[-1].clone()
            clone.set_args(user_input)
            self.set_suggestions([clone])

    def apps_from_registry(self):
        failed = []
        results = []

        try:
            self.steam_exe = regobj.HKCU.Software.Valve.Steam['SteamExe'].data
            SteamApps = regobj.HKCU.Software.Valve.Steam.Apps
        except AttributeError:
            self.error("Steam not found in registry.")
            return

        for app in SteamApps:
            if 'Installed' not in app:
                continue
            if app['Installed'].data != 1:
                continue

            name = self.applist.get(app.name)
            if name:
                results.append((app.name, name))
            else:
                failed.append(app)

        if failed:
            msg = 'Failed to find {}. Updating applist...'
            self.warn(msg.format(', '.join(failed)))
            self.download_applist()

        return results

    def download_applist(self):
        if self.applist and time.time() - self.applist['last_update'] < 60 * 60 * 24:
            return

        opener = kpn.build_urllib_opener()
        with opener.open(self.APPLIST_URL) as response:
            data = json.loads(response.read().decode('utf-8'))

        applist = {}
        for app in data['applist']['apps']:
            key = str(app['appid'])
            applist[key] = app['name']

        applist['last_update'] = time.time()

        cache_path = self.get_package_cache_path(create=True)
        applist_path = os.path.join(cache_path, 'applist.json')
        with open(applist_path, 'w') as fp:
            json.dump(applist, fp)
