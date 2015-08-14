import sys
import os

import Scoggle.components.scoggle as scoggle
import Scoggle.components.scoggle_types as stypes

class PrefixWildcardSuffixMatcher(stypes.BaseMatcher):
    """
        Matching Strategy of:
         prefix + (.*) + suffix


        Given a prefix of: ABC and suffixes of [Spec.scala, Suite.scala]
        Will find matches for ABCWithSomeContextSpec.scala within the test_dirs.
    """
    def __init__(self, param):
        self.param = param

    def match_test_file(self, root, directories, filename):
        """
            Searches for a file starting with the prefix and ending
            with one of the test suffixes.
            
            Example:
                Given a prod file of: Xyz
                returns test files of:
                    XyzWithSomeContextIntSpec
                    XyzContextSpec
                    XyzSpec

        """
        for s in self.param.suffixes:
            if (filename.startswith(self.param.prefix) and filename.endswith(s)):
                return True

        return False              
        
    # called from test file
    def match_prod_file(self, root, directories, filename):
        """
            Searches for a file starting with the prefix and ending
            with one of the test suffixes.

            Example:
                Given a test file of: XyzWithSomeContextIntSpec
                returns a prod file of: Xyz

        """
        scoggle = self.param.scoggle
        prefix = self.param.prefix
        suffixes = self.param.suffixes
        logger = self.param.logger

        prod_file = scoggle.remove_largest_suffix_from_prefix(prefix, 
                        scoggle.get_files_without_extension(suffixes))
        name_only = scoggle.get_file_without_extension(filename)
        logger.debug("prod_file: " + prod_file + ",name_only: " + name_only)
        return prod_file.startswith(name_only) and filename.endswith(".scala")


