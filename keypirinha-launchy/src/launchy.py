# Keypirinha launcher (keypirinha.com)

import keypirinha_util as kpu
import keypirinha as kp
import time
import os


class Launchy(kp.Plugin):
    """
    Populate catalog using Launchy's configuration format.

    This plugin allows you to populate your catalog the same way you would
    in Launchy. You can simply copy your configuration over and this plugin
    will be able to parse and replicate the same list as in Launchy.

	Version: 1.2
    """
    def __init__(self):
        super().__init__()

    def _update_config(self):
        self.dir_configs = []
        settings = self.load_settings()
        size = settings.get_int('size', 'directories')
        if size is None:
            self.warn('No size parameter specified')
            return

        for i in range(size):
            k = str(i + 1)
            self.dir_configs.append({
                'name': settings.get_stripped(k + '\\name', 'directories'),
                'types': settings.get_stripped(k + '\\types', 'directories', fallback=''),
                'depth': settings.get_int(k + '\\depth', 'directories', fallback=0),
                'indexdirs': settings.get_bool(k + '\\indexdirs', 'directories', fallback=False),
                'excludedirs': settings.get_stripped(k + '\\exclude_dirs', 'directories', fallback=''),
            })

        self.settings = settings

        loaded_msg = "Successfully updated the configuration, found {} entries"
        self.info(loaded_msg.format(len(self.dir_configs)))

    def _load_dir(self, i, config):
        if config['name'] is None:
            self.warn("No 'name' provided for config #{}".format(i + 1))
            return 0

        path_name = config['name'].replace('\\\\', '\\')
        root_path = os.path.expandvars(path_name)
        if not os.path.exists(root_path):
            self.warn("Path '{}' in config #{} does not exist".format(path_name, i + 1))
            return 0

        paths = []

        conf_dirs = config['indexdirs']

        # Generates a tuple of allowed file types
        inc_files = config['types'].split(',')
        if '' in inc_files: inc_files.remove('')
        if '@Invalid()' in inc_files: inc_files.remove('@Invalid()')
        inc_files = [i.strip('.*') for i in inc_files]
        inc_files = tuple(inc_files)

        # Generates list of forbided strings from direcory paths
        exclude = config['excludedirs'].split(',')
        if '' in exclude: exclude.remove('')

        self.should_terminate()
        # Walks down directory tree adding to paths[]
        for walk_root, walk_dirs, walk_files in os.walk(root_path):
                if not any(ext in walk_root for ext in exclude):

                    # If indexing directories add the current directory to the index.
                    if conf_dirs:
                        paths.append(walk_root)

                    if inc_files:
                        for name in walk_files:
                            if name.endswith(inc_files):
                                paths.append(os.path.join(walk_root, name))


        self.merge_catalog([
            self.create_item(
                category=kp.ItemCategory.FILE,
                label=os.path.basename(path),
                short_desc="",
                target=os.path.join(root_path, path),
                args_hint=kp.ItemArgsHint.ACCEPTED,
                hit_hint=kp.ItemHitHint.KEEPALL)
            for path in paths])

        return len(paths)

    def on_start(self):
        self._update_config()

    def on_catalog(self):
        catalog_size = 0
        self.set_catalog([])
        start_time = time.time()

        for i, config in enumerate(self.dir_configs):
            catalog_size += self._load_dir(i, config)

        elapsed = time.time() - start_time
        stat_msg = "Cataloged {} items in {:0.1f} seconds"
        self.info(stat_msg.format(catalog_size, elapsed))

    def on_suggest(self, user_input, items_chain):
        if not items_chain:
            return

        target_path = items_chain[-1].target()
        if os.path.isdir(target_path):
            suggestions = [
                self.create_item(
                    category=kp.ItemCategory.FILE,
                    label=subdir,
                    short_desc="",
                    target=os.path.join(target_path, subdir),
                    args_hint=kp.ItemArgsHint.ACCEPTED,
                    hit_hint=kp.ItemHitHint.KEEPALL,
                    loop_on_suggest=True)
                for subdir in os.listdir(target_path)]
        else:
            clone = items_chain[-1].clone()
            clone.set_args(user_input)
            suggestions = [clone]

        self.set_suggestions(suggestions)

    def on_execute(self, item, action):
        kpu.execute_default_action(self, item, action)

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self._update_config()
            self.on_catalog()
