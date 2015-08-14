import sys
import os
<<<<<<< HEAD
=======

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

>>>>>>> 61ad8ec2581e16de49119ab04d58eb02b5deae2a
import Scoggle.components.scoggle as scoggle
import Scoggle.components.scoggle_types as stypes

class WildcardPrefixWildcardSuffixMatcher(stypes.BaseMatcher):
    """
        Matching Strategy of:
         (.*) + prefix + (.*) + suffix


        Given a prefix of: ABC and suffixes of [Spec.scala, Suite.scala]
        Will find matches for AnABCWithSomeContextSpec.scala within the test_dirs.
    """
    def __init__(self, param):
        self.param = param

    def match_test_file(self, root, directories, filename):
        """
            Searches for any file that contains the prefix and ends with
            the longest test suffix.

            Example:
                Given a prod file of: Xyz
                returns matching test files: 
                    AnXyzWithSomeContextSpec
                    OneXyzWithSomeContextIntSpec
                    LetsDoSomethingInteresingWithAnXyzContextSpec
        """        
        prefix = self.param.prefix
        suffixes = self.param.suffixes

        for s in suffixes:
            if ( (filename.find(prefix) != -1) and filename.endswith(s)):
                return True

        return False              
        
    def match_prod_file(self, root, directories, filename):
        """
            Searches for any file that contains the prefix and ends with
            the longest test suffix.

            Example:
                Given a test file of: AnXyzWithSomeContextSpec
                returns matching prod file: Xyz
        """
        scoggle = self.param.scoggle
        prefix = self.param.prefix
        suffixes = self.param.suffixes
        logger = self.param.logger

        prod_file = scoggle.remove_largest_suffix_from_prefix(prefix, 
                        scoggle.get_files_without_extension(suffixes))
        filename_only = scoggle.get_file_without_extension(filename)
        logger.debug("WildcardPrefixWildcardSuffixMatcher: possible_prod_file: " + prod_file + ",filename_only: " + filename_only)
        possible_matching_files = scoggle.find_matching_words(prod_file)
        logger.debug("WildcardPrefixWildcardSuffixMatcher: possible_matches: " + str(possible_matching_files))
        filter = [mf for mf in possible_matching_files if mf.startswith(filename_only) and filename.endswith(".scala")]
        logger.debug("WildcardPrefixWildcardSuffixMatcher: matches: " + str(filter))
        return len(filter) > 0
        