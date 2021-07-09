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
        self.config  = stypes.ScoggleConfig(self.view, self.wrapper, self.scoggle, override_debug = True)
        self.logger  = self.config.logger

        self.logger.debug("loaded the following config: {0}".format(str(self.config)))
        display_error_location = self.config.display_error_location

        view = self.view
        self.window = self.wrapper.getActiveWindow()
        current_file = self.wrapper.current_file(view)

        self.logger.debug("current file: {0}".format(str(current_file)))
        test_srcs = self.config.test_srcs
        prod_srcs = self.config.production_srcs
        file_ext = self.config.file_ext
        default_test_suffix = self.config.default_test_suffix

        ## only run for production files not for test files
        if self.is_production_file(current_file, prod_srcs):

            # Only run if there are test and production sources
            if len(test_srcs) != 0 and len(prod_srcs) != 0:
                try:
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
                        (package_path, file_name_ext) = os.path.split(package_path_and_file_ext) #get the package path

                        self.handle_test_file_creation(view, root_dir, package_path, test_srcs, file_name_ext, default_test_suffix)
                    else:
                        self.logger.error("Could not split source_dir_minus_package into 3: {0}".format(str(path_pieces)))

                except stypes.CantFindRootPathError as cfrpe:
                    self.logger.error(cfrpe.cause)
                    self.wrapper.show_error_message_with_location(cfrpe.cause, display_error_location)
            else:
                self.wrapper.show_error_message_with_location("Ensure to have at least one test_srcs and at least one production_srcs defined to use this functionality", display_error_location)
        else:
            self.wrapper.show_error_message_with_location("You can only create a test file from a production file", display_error_location)

    def handle_test_file_creation(self, view, root_dir, package_path, test_srcs, file_name_ext, test_suffix):
        region_string = view.sel()[0] #get the first selection region
        selected_text = self.choose_file_name(region_string, view, file_name_ext)

        self.logger.debug("you selected {0}".format(str(selected_text)))
        heading = "Create test file for: {0}".format(selected_text)
        result = self.wrapper.yes_no_cancel_dialog(heading, "Yes", "No")
        selected_file_name = os.path.splitext(selected_text)[0] # get file name without the ext
        if isinstance(result, stypes.Yes):
            param = stypes.TestFileCreationParam(root_dir, package_path, test_srcs, selected_file_name, test_suffix)
            self.logger.debug("TestFileCreationParam: {0}".format(str(param)))
            test_file_path_creator = TestFilePathCreator(param)

            if len(test_srcs) == 1:
                self.test_src_selected(test_file_path_creator)(0)
            else:
                self.window.show_quick_panel(test_srcs, self.test_src_selected(test_file_path_creator), placeholder="select test source directory")
        else:
            pass # No or Cancel

    def choose_file_name(self, cursor, view, file_name_ext):
        cursor_string = view.substr(cursor)
        cursor_word   = view.substr(view.word(cursor))

        self.logger.debug("cursor_string:".format(str(cursor_string)))
        self.logger.debug("cursor_word:".format(str(cursor_word)))

        if cursor_string:
            return cursor_string
        elif cursor_word:
            return cursor_word
        else:
            return file_name_ext

    def is_production_file(self, current_file, prod_srcs):
        return self.scoggle.does_file_contain_path(current_file, prod_srcs)

    # Handles the selected test source path
    def test_src_selected(self, test_file_path_creator):
        def handle_test_src_path_selected(selected_index):
            test_file_path = test_file_path_creator.get_test_file_path(selected_index)
            self.logger.debug("test_file_path1: ".format(str(test_file_path)))
            if test_file_path is not None:
                self.logger.debug("test_file_path2: {0}".format(test_file_path))
                self.wrapper.show_input_panel("create test file at:", test_file_path, self.create_test_file(test_file_path_creator), None, None)
            else:
                self.logger.debug("Could not get test_file_path")

        return handle_test_src_path_selected

    # Creates test file path
    def create_test_file(self, test_file_path_creator):
        def handle_create_test_file(incoming):
            test_file_name_parts = os.path.split(incoming) #split file into path and file
            test_file_dir  = test_file_name_parts[0] # path up to the file name
            test_file_name = test_file_name_parts[1] # file name and extension
            ## Move file functionality into separate class
            if not os.path.isfile(incoming): # File doesn't already exist, so proceed
                if not os.path.exists(test_file_dir): # if the path doesn't exist, create it
                    self.logger.debug("creating parent directory: {0} for file: {1}".format(str(test_file_dir), str(test_file_name)))
                    os.makedirs(test_file_dir)

                test_template = self.template_string(test_file_path_creator)
                template_lines = len(test_template.split('\n'))
                self.create_template_file(incoming, test_template)

                file_name_with_position = "{0}:{1}".format(str(incoming), str(template_lines))
                self.window.open_file(file_name_with_position, sublime.ENCODED_POSITION)
            else:
                result = self.wrapper.yes_no_cancel_dialog("Test file: {0} already exists\nUse different name?".format(str(incoming)), "Yes", "No")
                if (isinstance(result, stypes.Yes)):
                    new_test_file_name = "UNIQUE-PREFIX-{0}".format(str(test_file_name))
                    test_file_path = os.path.join(test_file_dir, new_test_file_name.lstrip(os.path.sep))
                    self.wrapper.show_input_panel("create test file at:", test_file_path, self.create_test_file(test_file_path_creator), None, None)

        return handle_create_test_file

    def template_string(self, test_file_path_creator):
        test_name = test_file_path_creator.get_test_file_class_name()
        package_path = test_file_path_creator.get_dotted_package_path()
        template = [
                     "package {0}".format(package_path),
                     "",
                     "//class name: {0}".format(str(test_name)),
                     ""
                   ]
        return '\n'.join(template)

    def create_template_file(self, file_name, template_string):
        f = open(file_name, "w+")
        f.write(template_string)
        f.close()

class TestFilePathCreator():

    def __init__(self, params):
        self.params = params

    def get_test_file_path(self, selected_index):
        params = self.params
        if selected_index != -1 and selected_index < len(params.test_srcs):
            test_src_path = params.test_srcs[selected_index] # test source path selected by user
            root_test_src_path = os.path.join(params.root_dir, test_src_path.lstrip(os.path.sep)) # strip starting path separators
            root_test_src_path_package = os.path.join(root_test_src_path, params.package_dir.lstrip(os.path.sep)) # strip starting path separators
            test_file_name = "{0}{1}".format(params.file_name, params.suffix)
            test_file_path = os.path.join(root_test_src_path_package, test_file_name.lstrip(os.path.sep)) # strip starting path separators
            return test_file_path
        else:
            return None

    def get_test_file_class_name(self):
        file_name_with_ext = "{0}{1}".format(self.params.file_name, self.params.suffix)
        file_name = os.path.splitext(file_name_with_ext)[0] # get only the file name
        return file_name

    def get_dotted_package_path(self):
        remove_left_sep = self.params.package_dir.lstrip(os.path.sep)
        remove_right_sep = remove_left_sep.rstrip(os.path.sep)
        dotted = remove_right_sep.replace(os.sep, ".")
        return dotted

    def __str__(self):
        to_string = "TestFilePathCreator(params={0})".format(str(self.params))
        return repr(to_string)

