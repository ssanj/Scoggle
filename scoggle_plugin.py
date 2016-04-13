import sublime
import sublime_plugin
import os
import fnmatch
import re
import sys
import logging

from Scoggle.components import scoggle as scoggle
from Scoggle.components import sublime_wrapper as sublime_wrapper
from Scoggle.components import scoggle_types as stypes

class ScoggleCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        self.scoggle = scoggle.Scoggle()
        self.wrapper = sublime_wrapper.SublimeWrapper()
        self.matching_strategy = args["matcher"]
        FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('scoggle.plugin')
        self.perform()

    def is_visible(self):
        return scoggle.Scoggle.is_visible(self.view, sublime.version())

    def perform(self):
        current_file = self.wrapper.current_file(self.view)
        settings = self.wrapper.load_settings("Scoggle")
        project_settings_dict = self.wrapper.load_project_settings(self.view)

        should_log = self.wrapper.get_setting("log", project_settings_dict, settings)
        prod_srcs = self.wrapper.get_setting("production_srcs", project_settings_dict, settings)
        test_srcs = self.wrapper.get_setting("test_srcs", project_settings_dict, settings)
        test_suffixes = self.wrapper.get_setting("test_suffixes", project_settings_dict, settings)
        file_ext = self.wrapper.get_setting("file_ext", project_settings_dict, settings)
        display_error_location = self.scoggle.get_display_error_location(
            self.wrapper.get_setting("display_errors_in", project_settings_dict, settings),
            self.wrapper.show_error_message,
            self.wrapper.show_status_message)

        if (should_log):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        self.logger.debug("using %s: %s ", ("project" if project_settings_dict else "plugin"),
            self.wrapper.settings_as_string(prod_srcs, test_srcs, test_suffixes, file_ext, should_log))

        prefix = self.scoggle.get_base_file(current_file)

        if (self.is_production_file(current_file, prod_srcs)):
            self.toggle_matching_files(stypes.TEST(), current_file, prod_srcs, test_srcs, prefix, test_suffixes, display_error_location)
        elif (self.is_test_file(current_file, test_srcs)):
            self.toggle_matching_files(stypes.PROD(), current_file, prod_srcs, test_srcs, prefix, test_suffixes, display_error_location)
        else:
            error = ("Could not find matching file path for %(prefix)s in %(prod_srcs)s or %(test_srcs)s. Please update *.sublime-project or Scoggle.sublime-settings."  % locals())
            self.logger.error(error)
            self.scoggle.display_error_in("Could not find matching production or test files. Please refer to the console log for details. (CTRL + `)", display_error_location)

    def toggle_matching_files(self, search_type, current_file, prod_srcs, test_srcs, prefix, test_suffixes, display_error_location):
        try:
            root_dir = ""
            fullpath_srcs = []
            if (isinstance(search_type, stypes.TEST)):
                root_dir = self.scoggle.get_first_root_path_or_error(current_file, prod_srcs)
                fullpath_srcs = self.scoggle.prepend_root_dir_to_paths(root_dir, test_srcs)
            else:
                root_dir = self.scoggle.get_first_root_path_or_error(current_file, test_srcs)
                fullpath_srcs = self.scoggle.prepend_root_dir_to_paths(root_dir, prod_srcs)

            self.logger.debug("searching toggles for %s, in toggle paths: %s", prefix, str(fullpath_srcs))
            strategy = self.findStrategy(search_type, root_dir, test_srcs, prefix, test_suffixes)
            self.logger.debug("using strategy: %s", str(self.matching_strategy))
            matches = self.scoggle.find_matching_files(fullpath_srcs, strategy, self.logger)
            self.logger.debug("matches : %s", str(matches))
            self.wrapper.show_results_list_with_location(matches, display_error_location)
        except stypes.CantFindRootPathError as cfrpe:
            self.logger.error(cfrpe.cause)
            self.wrapper.show_error_message_with_location(cfrpe.cause, display_error_location)
        except stypes.UnknownStrategy as unst:
            self.logger.error(unst.cause)
            self.wrapper.show_error_message_with_location(unst.cause, display_error_location)

    def findStrategy(self, searchType, root_dir, test_srcs, prefix, test_suffixes):
        try:
            class_name = self.scoggle.make_class_name(self.matching_strategy)
            self.logger.debug("loading strategy class %s", str(class_name))
            strategyClass = self.scoggle.get_class(class_name)

            strategy = strategyClass(stypes.MatcherParam(root_dir, test_srcs, prefix, test_suffixes, self.scoggle, self.logger))
            if (isinstance(searchType, stypes.TEST)):
                return strategy.match_test_file
            else:
                return strategy.match_prod_file

        except Exception as e:
            self.logger.error(e)
            raise stypes.UnknownStrategy(self.matching_strategy)

    def is_production_file(self, current_file, prod_srcs):
        return self.scoggle.does_file_contain_path(current_file, prod_srcs)

    def is_test_file(self, current_file, test_srcs):
        return self.scoggle.does_file_contain_path(current_file, test_srcs)

class PackageCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.scoggle = scoggle.Scoggle()
        self.wrapper = sublime_wrapper.SublimeWrapper()
        FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('scoggle.plugin')
        self.perform(edit)

    def is_visible(self):
        return scoggle.Scoggle.is_visible(self.view, sublime.version())

    def perform(self, edit):
        current_file = self.wrapper.current_file(self.view)
        settings = self.wrapper.load_settings("Scoggle")
        project_settings_dict = self.wrapper.load_project_settings(self.view)

        should_log = self.wrapper.get_setting("log", project_settings_dict, settings)
        prod_srcs = self.wrapper.get_setting("production_srcs", project_settings_dict, settings)
        test_srcs = self.wrapper.get_setting("test_srcs", project_settings_dict, settings)
        display_error_location = self.scoggle.get_display_error_location(
            self.wrapper.get_setting("display_errors_in", project_settings_dict, settings),
            self.wrapper.show_error_message,
            self.wrapper.show_status_message)

        if (should_log):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        if (self.is_production_file(current_file, prod_srcs)):
            self.update_package_for(edit, current_file, prod_srcs)
        elif (self.is_test_file(current_file, test_srcs)):
            self.update_package_for(edit, current_file, test_srcs)
        else:
            if current_file is not None:
                errorD = ("Could not derive package for %(current_file)s"  % locals())
                errorL = ("Could not derive package for %(current_file)s from %(prod_srcs)s or %(test_srcs)s. Please update *.sublime-project or Scoggle.sublime-settings."  % locals())
            else:
                errorD = ("Please save the buffer as a scala file before inserting a package.")
                errorL = ("Packages can only be derived from scala files that have a name and path. Please save the file and try again.")

            self.logger.error(errorL)
            self.scoggle.display_error_in(errorD, display_error_location)

    def is_production_file(self, current_file, prod_srcs):
        if current_file is not None:
            return self.scoggle.does_file_contain_path(current_file, prod_srcs)
        else:
            return False

    def is_test_file(self, current_file, test_srcs):
        if current_file is not None:
            return self.scoggle.does_file_contain_path(current_file, test_srcs)
        else:
            return False

    def update_package_for(self, edit, current_file, paths):
        dotted = self.scoggle.get_package_path(current_file, paths)
        updated_text = self.scoggle.get_updated_package_text(self.get_all_content(), dotted)
        self.update_view_text(edit, updated_text)

    def get_all_content(self):
        region = sublime.Region(0, self.view.size())
        return self.view.substr(region)

    def update_view_text(self, edit, content):
        region = sublime.Region(0, self.view.size())
        self.view.replace(edit, region, content)