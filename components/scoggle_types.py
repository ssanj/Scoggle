
# Use simple types to designate an enum since we don't have Enum in this version of python.

# Types of searches. Currently only prod and test.
class SearchType(): pass
class PROD(SearchType): pass
class TEST(SearchType): pass

class YesNoCancel(): pass
class Yes(YesNoCancel): pass
class No(YesNoCancel): pass
class Cancel(YesNoCancel): pass

class HowToDisplayErrors():
    """
        Takes a partial function that takes a message of type String and displays that message
        in whatever form it can (String => None).
        Calls display.display_message to display the message in the correct manner.

        Example:

            To use the sublime error dialog we would call:
            Dialog(sublime.error_message)

            To use the status bar we would call:
            StatusBar(sublime.status_message)
    """
    def __init__(self, display):
        self.display = display

    def display_message(self, message):
        if (self.display):
            self.display(message)

class Dialog(HowToDisplayErrors):
    def __init__(self, dialog):
        HowToDisplayErrors.__init__(self, dialog)

class StatusBar(HowToDisplayErrors):
    def __init__(self, status_bar):
        HowToDisplayErrors.__init__(self, status_bar)

    # append plugin name because there are multiple messages displayed on the status bar
    def display_message(self, message):
        HowToDisplayErrors.display_message(self, " Scoggle: {0}".format(message))

class DontDisplay(HowToDisplayErrors):
    def __init__(self):
        HowToDisplayErrors.__init__(self, None)



# Matcher parameters
class MatcherParam():
    """
        Parameters every Matcher is provided.
        root_dir - the first directory in the list of production_srcs or test_srcs (Scoggle.sublime-settings) that contains the target file.
        test_dirs - the list of test directories defined in test_srcs ((Scoggle.sublime-settings)).
        prefix - the target file (prod or test) without an extension.
        suffixes - the list of test suffixes defined in test_suffixes (Scoggle.sublime-settings).
        scoggle - reference to the scoggle module.
        logger - the logger to use for logging.
    """
    def __init__(self, root_dir, test_dirs, prefix, suffixes, scoggle, logger):
        self.root_dir = root_dir
        self.test_dirs = test_dirs
        self.prefix = prefix
        self.suffixes = suffixes
        self.scoggle = scoggle
        self.logger = logger


class BaseMatcher:
    """
        Base class for all Matchers.
    """
    def __init__(self, param):
        """
            param - contains a bunch of useful fields. Please see MatcherParam.
        """
        raise NotImplementedError("please override this in your matcher.")

    def match_test_file(self, root, directories, filename):
        """
            root - the full directory path to the filename.
            directories - each sub directory within the root.
            filename - each file name inspected when looking through supplied test_srcs.

            return True if a matching test file was found or False if not.
        """
        raise NotImplementedError("please override this in your matcher.")

    def match_prod_file(self, root, directories, filename):
        """
            root - the full directory path to the filename.
            directories - each sub directory within the root.
            filename - each file name inspected when looking through supplied production_srcs.

            return True if a matching prod file was found or False if not.
        """
        raise NotImplementedError("please override this in your matcher.")

# Exception thrown when the root path of a file can't be determined from those supplied.
class CantFindRootPathError(Exception):

    def __init__(self, file, paths):
        self.cause = "Can't find root path of file: " + str(file) + ", in these paths: " + str(paths)

    def __str__(self):
        return repr(self.cause)

# Exception thrown when the module name of a file can't be determined from those supplied.
class CantFindModuleNameError(Exception):

    def __init__(self, file, paths):
        self.cause = "Can't find module name of file: " + str(file) + ", from these paths: " + str(paths)

    def __str__(self):
        return repr(self.cause)

# Exception thrown when the matching strategy requested can't be found.
class UnknownStrategy(Exception):
    def __init__(self, strategy):
        self.cause = "Can't load strategy: " + str(strategy) + ". See log for details. (CTRL + `)"

    def __str__(self):
        return repr(self.cause)

# Exception thrown when we can't determine the package path.
class CantDeterminePackageError(Exception):

    def __init__(self, file, paths):
        self.cause = "Can't find package of file: " + str(file) + ", from these paths: " + str(paths)

    def __str__(self):
        return repr(self.cause)

class TestFileCreationParam():
    """
        All the bits and pieces required to create a test file from a production file.
        root_dir - the first directory in the list of production_srcs (Scoggle.sublime-settings) that contains the current file.
        package_dir - the package path to the chosen test file without the root path
        test_srcs - the list of test source directories
        file_name - the prefix for the test file
        suffix - the test file suffix
    """
    def __init__(self, root_dir, package_dir, test_srcs, file_name, suffix):
        self.root_dir = root_dir
        self.package_dir = package_dir
        self.test_srcs = test_srcs
        self.file_name = file_name
        self.suffix = suffix
        self.root_test_src_path = None

    def with_new_file_name(self, package_dir, new_file_name, new_suffix):
        new_params = TestFileCreationParam(self.root_dir, package_dir, self.test_srcs, new_file_name, new_suffix)
        new_params.root_test_src_path = self.root_test_src_path
        return new_params

    def __str__(self):
        to_string = (
            "TestFileCreationParam(" +
                "root_dir=" + str(self.root_dir) +
                ", package_dir=" + str(self.package_dir) +
                ", test_srcs=" + str(self.test_srcs) +
                ", file_name=" + str(self.file_name) +
                ", suffix=" + str(self.suffix) +
                ", root_test_src_path=" + str(self.root_test_src_path) +
             ")"
        )
        return repr(to_string)

class ScoggleConfig():

    def __init__(self, view, sublimeWrapper, scoggle, override_debug):
        import logging
        # TODO: Create a log wrapper
        FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(format=FORMAT)
        self.logger = logging.getLogger('scoggle.plugin')

        settings = sublimeWrapper.load_settings("Scoggle")
        project_settings_dict = sublimeWrapper.load_project_settings(view)
        self.test_srcs = sublimeWrapper.get_setting("test_srcs", project_settings_dict, settings)
        self.test_suffixes = sublimeWrapper.get_setting("test_suffixes", project_settings_dict, settings)
        self.production_srcs = sublimeWrapper.get_setting("production_srcs", project_settings_dict, settings)
        self.file_ext = sublimeWrapper.get_setting("file_ext", project_settings_dict, settings)
        self.default_test_suffix = sublimeWrapper.get_setting_with_default("default_test_suffix", project_settings_dict, settings, "Spec.scala")

        self.should_log = sublimeWrapper.get_setting("log", project_settings_dict, settings)

        self.display_error_location = scoggle.get_display_error_location(
            sublimeWrapper.get_setting("display_errors_in", project_settings_dict, settings),
            sublimeWrapper.show_error_message,
            sublimeWrapper.show_status_message)

        if (self.should_log or override_debug):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)


    def __str__(self):
        fields = [
                "test_suffixes={0}".format(str(self.test_suffixes))
            ,   ", test_srcs={0}".format(str(self.test_srcs))
            ,   ", production_srcs={0}".format(str(self.production_srcs))
            ,   ", should_log={0}".format(str(self.should_log))
            ,   ", file_ext={0}".format(str(self.file_ext))
            ,   ", default_test_suffix={0}".format(str(self.default_test_suffix))
        ]

        to_string ="ScoggleConfig({0})".format('\n'.join(fields))
        return repr(to_string)
