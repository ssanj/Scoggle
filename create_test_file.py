import sublime
import sublime_plugin
import os

from Scoggle.components import scoggle as scoggle
from Scoggle.components import sublime_wrapper as sublime_wrapper
from Scoggle.components import scoggle_types as stypes


class PromptCreateTestCommand(sublime_plugin.TextCommand):

    def is_visible(self):
        return scoggle.Scoggle.is_visible(self.view, sublime.version())

    def run(self, edit):
        self.scoggle = scoggle.Scoggle()
        self.wrapper = sublime_wrapper.SublimeWrapper()
        self.config  = stypes.ScoggleConfig(self.view, self.wrapper, self.scoggle)
        self.logger  = self.config.logger

        view = self.view
        self.window = self.wrapper.getActiveWindow()

        if view:
            try:
                current_file = self.wrapper.current_file(view)
                self.logger.debug("current file: ", str(current_file))
                test_srcs = self.config.test_srcs
                prod_srcs = self.config.prod_srcs
                file_ext = self.config.file_ext

                root_dir, selected_prod_src = self.scoggle.get_first_root_path_pair_or_error(current_file, prod_srcs)
                source_dir_minus_package = os.path.join(root_dir, selected_prod_src)

                ## TODO: check for at least 3 elements
                path_pieces = current_file.partition(str(source_dir_minus_package))
                # the partition should return 3 pieces:
                # 0 -> The String before the of source_dir_minus_package
                # 1 -> The match: source_dir_minus_package
                # 2 -> The String following the match (package path + file name + ext)
                if len(path_pieces) >= 3:
                    package_path_and_file_ext = path_pieces[2] #get the package path + file name + ext
                    package_path = os.path.split(package_path_and_file_ext)[0] #get the package path

                    self.handle_test_file_creation(view, root_dir, package_path, test_srcs)
                else:
                    self.logger.error("Could not split source_dir_minus_package into 3: {0}".format(str(path_pieces)))

            except stypes.CantFindRootPathError as cfrpe:
                self.logger.error(cfrpe.cause)
                self.wrapper.show_error_message_with_location(cfrpe.cause, display_error_location)
        else:
             self.logger.error("Could not find active view")


    def handle_test_file_creation(self, view, root_dir, package_path, test_srcs):
        region_string = view.sel()[0] #get the first selection region
        if region_string:
            selected_text = view.substr(region_string)
            self.logger.debug("you selected {0}".format(str(selected_text)))
            heading = "Create test file for: {0}".format(selected_text)
            result = self.wrapper.yes_no_cancel_dialog(heading, "Yes", "No")
            selected_file_name = os.path.splitext(selected_text)[0] # get file name without the ext
            if isinstance(result, stypes.Yes):
                 param = stypes.TestFileCreationParam(root_dir, package_path, test_srcs, selected_file_name)
                 self.window.show_quick_panel(test_srcs, self.test_src_selected(param), placeholder="select test source directory")
            else:
                pass
                # No or Cancel
        else:
            # TODO: We should probably just use the file name here.
            print("invalid selection")

    # Handles the selected test source path
    def test_src_selected(self, params):
        def handle_test_src_path_selected(selected_index):
            if selected_index != -1:
                 self.logger.debug("file_selected params: {0}".format(str(params)))
                 # TODO: Do this in another class
                 test_src_path = params.test_srcs[selected_index] # test source path selected by user
                 root_test_src_path = os.path.join(params.root_dir, test_src_path.lstrip(os.path.sep)) # strip starting path separators
                 root_test_src_path_package = os.path.join(root_test_src_path, params.package_dir.lstrip(os.path.sep)) # strip starting path separators
                 test_file_name = params.file_name + "Spec.scala" # TODO: we should define the default suffix somewhere.
                 test_file_path = os.path.join(root_test_src_path_package, test_file_name.lstrip(os.path.sep)) # strip starting path separators
                 self.logger.debug("test_file_path: {0}".format(test_file_path))
                 self.wrapper.show_input_panel("create test file at:", test_file_path, self.create_test_file, None, None)

        return handle_test_src_path_selected

    # Creates test file path
    def create_test_file(self, incoming):
        test_file_name_parts = os.path.split(incoming) #split file into path and file
        test_file_dir  = test_file_name_parts[0] # path up to the file name
        test_file_name = test_file_name_parts[1] # file name and extension
        if not os.path.isfile(incoming): # File doesn't already exist, so proceed
            if not os.path.exists(test_file_dir): # if the path doesn't exist, create it
                self.logger.debug("creating parent directory: {0} for file: {1}".format(str(test_file_dir), str(test_file_name)))
                os.makedirs(test_file_dir)

            f = open(incoming, "w+")
            f.write("//generated by Scoggle")
            f.close()
            view = self.window.open_file(incoming)
            tries = 5
            sublime.set_timeout_async(lambda: self.expand_snippet(view, tries), 1) # try to expand snippet in one second
        else:
            result = self.wrapper.yes_no_cancel_dialog("Test file: {0} already exists\nUse different name?".format(str(incoming)), "Yes", "No")
            if (isinstance(result, stypes.Yes)):
                new_test_file_name = "UNIQUE-PREFIX-{0}".format(str(test_file_name))
                test_file_path = os.path.join(test_file_dir, new_test_file_name.lstrip(os.path.sep))
                self.wrapper.show_input_panel("create test file at:", test_file_path, self.create_test_file, None, None)

    def expand_snippet(self, view, tries):
      if not view.is_loading(): # if the view has loaded
          self.logger.debug("the test file view has loaded")
          view.sel().clear()
          view.sel().add(sublime.Region(0))
          view.show(0)

          # TODO: Pull these in from the settings
          view.run_command('insert_snippet', { "name": 'Packages/User/snippets/scala_spec_template.sublime-snippet', "PACKAGE": 'x.y.z', "TEST_NAME": "Blee"})
      elif tries > 0:
          self.logger.debug("waiting for view with {0} retries".format(str(tries)))
          sublime.set_timeout_async(lambda: self.expand_snippet(view, tries - 1), 1) # keep trying until we run out of retries
      else:
          self.logger.error("View did not load within allotted retries")
          self.wrapper.show_error_message("Could not load snippet :(")


