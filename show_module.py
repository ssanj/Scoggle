import sublime
import sublime_plugin
import os
import re

from Scoggle.components import scoggle as scoggle
from Scoggle.components import sublime_wrapper as sublime_wrapper
from Scoggle.components import scoggle_types as stypes
from Scoggle.components import test_path_creator as tpc

class ShowModuleCommand(sublime_plugin.TextCommand):

    def is_visible(self):
        return scoggle.Scoggle.is_visible(self.view, sublime.version())

    def run(self, edit):
        self.scoggle = scoggle.Scoggle()
        self.wrapper = sublime_wrapper.SublimeWrapper()
        self.config  = stypes.ScoggleConfig(self.view, self.wrapper, self.scoggle, override_debug = True)
        self.logger  = self.config.logger

        self.logger.debug("loaded the following configX: {0}".format(str(self.config)))
        display_error_location = self.config.display_error_location

        view = self.view
        self.window = self.wrapper.getActiveWindow()
        current_file = self.wrapper.current_file(view)

        # The current file can be null, if there isn't an open file
        if current_file is not None:
            module_name = self.extract_module_name(current_file)
            if module_name is not None:
                self.logger.debug("module: %s", str(module_name))
                view.show_popup("<h1>{0}</h1>".format(str(module_name)), sublime.HIDE_ON_MOUSE_MOVE)
            else:
                error_message = "Could not determine module"
                self.logger.error(error_message)
        else:
            self.logger.debug("No file selected")

    def is_production_file(self, current_file, prod_srcs):
        return self.scoggle.does_file_contain_path(current_file, prod_srcs)

    def is_test_file(self, current_file, test_srcs):
        return self.scoggle.does_file_contain_path(current_file, test_srcs)

    def extract_module_name(self, current_file):
        try:
            self.logger.debug("current file: {0}".format(str(current_file)))
            test_srcs = self.config.test_srcs
            prod_srcs = self.config.production_srcs
            display_error_location = self.config.display_error_location

            if self.is_production_file(current_file, prod_srcs):
                result = self.get_production_module_name(current_file, prod_srcs)
                self.logger.debug("prod module: %s", str(result))
                return result
            elif self.is_test_file(current_file, test_srcs):
                result = self.get_test_module_name(current_file, test_srcs)
                self.logger.debug("test module: %s", str(result))
                return result
            else:
                error_message = "Unknown source root: not production or test source"
                self.logger.error(error_message)
                self.wrapper.show_error_message_with_location(error_message, display_error_location)
                return None
        except stypes.CantFindRootPathError as cfrpe:
            self.logger.error(cfrpe.cause)
            self.wrapper.show_error_message_with_location(cfrpe.cause, display_error_location)
            return None

    def get_production_module_name(self, current_file, prod_srcs):
        result = self.scoggle.get_first_root_path_or_error(current_file, prod_srcs)
        return os.path.basename(os.path.normpath(result))

    def get_test_module_name(self, current_file, test_srcs):
        result = self.scoggle.get_first_root_path_or_error(current_file, test_srcs)
        return os.path.basename(os.path.normpath(result))

