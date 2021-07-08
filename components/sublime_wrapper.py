import sublime
import sublime_plugin
import os

from . import scoggle_types as stypes

class SublimeWrapper:

    def current_file(self, view):
        return view.file_name()

    def show_error_message(self, message):
        sublime.error_message(message)

    def show_error_message_with_location(self, message, location):
        location.display_message(message)

    def yes_no_cancel_dialog(self, heading, yesString, noString):
        sublimeResult = sublime.yes_no_cancel_dialog(heading, yesString, noString)
        result = stypes.Yes() if sublimeResult == 1 else stypes.No() if sublimeResult == 2 else stypes.Cancel()
        return result

    def show_status_message(self, message):
        sublime.status_message(message)

    def getActiveWindow(self):
        return sublime.active_window()

    def get_packages_path(self):
        return sublime.packages_path()

    def get_packages_path_with(self, relative_path):
        return os.path.join(self.get_packages_path(), relative_path.lstrip(os.path.sep))

    def show_input_panel(self, caption, text, on_done, on_change, on_cancel):
        sublime.active_window().show_input_panel(caption, text, on_done, on_change, on_cancel)

    def show_results_list_with_location(self, matches, display_location):
        if (len(matches) == 0):
            display_location.display_message("Could not find matching file.")
        elif (len(matches) == 1):
            sublime.active_window().open_file(matches[0])
        else:
            file_names = list(map(lambda x: [os.path.split(x)[1], x], matches))
            sublime.active_window().show_quick_panel(file_names, self.file_selected(matches))

    def file_selected(self, matches):
        def handle_selection(selected_index):
            if selected_index != -1:
                sublime.active_window().open_file(matches[selected_index])

        return handle_selection

    def load_settings(self, name):
        return sublime.load_settings("{0}.sublime-settings".format(name))

    def load_project_settings(self, view):
        settings = None
        if (view):
            s = view.settings()
            if s and s.has("Scoggle"):
                settings = s.get("Scoggle")

        return settings

    def get_setting(self, key, project_settings_dict, plugin_settings):
        if project_settings_dict and key in project_settings_dict:
            return project_settings_dict[key]
        elif plugin_settings and plugin_settings.has(key):
            return plugin_settings.get(key)
        else:
            return None

    def get_setting_with_default(self, key, project_settings_dict, plugin_settings, default_value):
        if project_settings_dict and key in project_settings_dict:
            return project_settings_dict[key]
        elif plugin_settings and plugin_settings.has(key):
            return plugin_settings.get(key)
        else:
            return default_value

    def settings_as_string(self, prod_srcs, test_srcs, test_suffixes, file_ext, should_log):
        newline = '\n'
        newlineTab = "%(newline)c\t" % locals()

        return "{%(newlineTab)s'test_suffixes' : %(test_suffixes)s,%(newlineTab)s'test_srcs' : %(test_srcs)s,%(newlineTab)s'production_srcs' : %(prod_srcs)s,%(newlineTab)s'log' : %(should_log)s,%(newlineTab)s'file_ext' : %(file_ext)s%(newline)s}" % locals()
