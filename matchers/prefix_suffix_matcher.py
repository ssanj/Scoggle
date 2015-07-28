import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import scoggle
import scoggle_types as stypes

class PrefixSuffixMatcher(stypes.BaseMatcher):
    """
        Matching Strategy where the prefix is directly joined to the suffix
        to find the match.

        Given a prefix of: ABC and suffixes of [Spec.scala, Suite.scala]
        Will find matches for ABCSpec.scala and ABCSuite.scala within the test_dirs.
    """
    def __init__(self, param):
        self.param = param
        self.filenameMatches = self.param.scoggle.prepend_prefix_to_suffixes(self.param.prefix, self.param.suffixes)        

    def match_test_file(self, root, directories, filename):
        """
            Searches for a file having the same prefix and the longest
            matching the test suffix.
            
            Example:
                Given a prod file of: Xyz
                returns test files of: 
                    XyzIntSpec                    
        """        
        for m in self.filenameMatches:
            if (filename == m):
                return True

        return False              
        
    def match_prod_file(self, root, directories, filename):
        """
            Searches for a file having the same prefix and the longest
            matching the test suffix.

            Example:
                Given a test file of: XyzIntSpec
                returns a prod file of: Xyz
        """
        prod_file = self.param.scoggle.remove_largest_suffix_from_prefix(self.param.prefix, 
                        self.param.scoggle.get_files_without_extension(self.param.suffixes))
        return filename == (str(prod_file) + ".scala")