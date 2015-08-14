
# Use simple types to designate an enum since we don't have Enum in this version of python.

# Types of searches. Currently only prod and test.
class SearchType(): pass
class PROD(SearchType): pass   
class TEST(SearchType): pass

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

# Exception thrown when the matching strategy requested can't be found.
class UnknownStrategy(Exception):
    def __init__(self, strategy):
        self.cause = "Can't load strategy: " + str(strategy) + ". See log for details. (CTRL + `)"     

    def __str__(self):
        return repr(self.cause)    

