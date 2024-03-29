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
                'excludedirs': settings.get_stripped(k + '\\excludedirs', 'directories', fallback=''),
            })

        self.settings = settings

        loaded_msg = "Successfully updated the configuration, found {} entries"
        self.info(loaded_msg.format(len(self.dir_configs)))

    def _scan_directory(self, root_path, name_patterns=None,  exclude=None, inc_dirs=None, max_level=None):
        """
        This function replaces the scan_directory() function from the api adding
        the ability to filter by file name as well.
        """

        name_patterns = name_patterns or []
        exclude = exclude or []
        inc_dirs = inc_dirs or 0
        max_level = max_level or -1

        paths=[]

        # Generates a tuple of allowed file types
        if '' in name_patterns: name_patterns.remove('')
        if '@Invalid()' in name_patterns: name_patterns.remove('@Invalid()')
        name_patterns = [i.strip('.*') for i in name_patterns]
        name_patterns = tuple(name_patterns)

        # Generates list of forbided strings from direcory paths
        if '' in exclude: exclude.remove('')

        # Gets the max depth from a system level
        root_path = root_path.rstrip(os.path.sep)
        assert os.path.isdir(root_path)
        num_sep = root_path.count(os.path.sep) + 1

        # Walks down directory tree adding to paths[]
        for walk_root, walk_dirs, walk_files in os.walk(root_path):
            if self.should_terminate():
                return paths

            # Checks the level is valid
            num_sep_this = walk_root.count(os.path.sep)
            if (num_sep + max_level > num_sep_this) or (max_level == -1):

                if not any(ext in walk_root for ext in exclude):

                    # If indexing directories add the current directory to the index.
                    if inc_dirs:
                        paths.append(walk_root)

                    if name_patterns:
                        for name in walk_files:
                            if name.endswith(name_patterns):
                                paths.append(os.path.join(walk_root, name))

        return paths


    def _load_dir(self, i, config):

        if config['name'] is None:
            self.warn("No 'name' provided for config #{}".format(i + 1))
            return 0

        path_name = config['name'].replace('\\\\', '\\')
        root_path = os.path.expandvars(path_name)
        if not os.path.exists(root_path):
            self.warn("Path '{}' in config #{} does not exist".format(path_name, i + 1))
            return 0

        paths = self._scan_directory(root_path,
                                     config['types'].split(','),
                                     config['excludedirs'].split(','),
                                     config['indexdirs'],
                                     config['depth'])


        self.merge_catalog([
            self.create_item(
                category=kp.ItemCategory.FILE,
                label=os.path.basename(path) or path,
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
