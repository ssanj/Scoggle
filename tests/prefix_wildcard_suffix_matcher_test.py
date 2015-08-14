import unittest
import Scoggle.components.scoggle as sc
import Scoggle.components.scoggle_types as stypes
import Scoggle.matchers.prefix_wildcard_suffix_matcher as matcher
import os
import functools as fp

class PrefixWildcardSuffixMatcherTest(unittest.TestCase):

  scoggle = sc.Scoggle()  

  def test_match_test_file(self):                  
      param = stypes.MatcherParam(None, None, "Contrast", ["Spec.scala", "Suite.scala", "IntSpec.scala"], PrefixWildcardSuffixMatcherTest.scoggle, None)
      cut = matcher.PrefixWildcardSuffixMatcher(param)
      matches_file = fp.partial(cut.match_test_file, None, None)

      # matches
      self.assertEqual(matches_file("ContrastWithinSomeContextSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastWithinAnotherContextIntSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastThrowingAnExceptionSuite.scala"), True)         

      # additional matches
      self.assertEqual(matches_file("ContrastSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastSuite.scala"), True)         
      self.assertEqual(matches_file("ContrastIntSpec.scala"), True)         
      
      # misses
      self.assertEqual(matches_file("AContrastSpec.scala"), False)         
      self.assertEqual(matches_file("ContrastSpecification.scala"), False)         
      self.assertEqual(matches_file("MirrorSpec.scala"), False)         

  def test_match_prod_file_with_suffix(self): 

    class DummyLogger:
      def debug(self, message): pass

    
    param = stypes.MatcherParam(None, None, "ContrastThrowingAnExceptionSuite", ["Spec.scala", "Suite.scala", "IntSpec.scala"], PrefixWildcardSuffixMatcherTest.scoggle, DummyLogger())
    cut = matcher.PrefixWildcardSuffixMatcher(param)

    matches_file = fp.partial(cut.match_prod_file, None, None)
    
    # matches
    self.assertEqual(matches_file("Contrast.scala"), True)    
    self.assertEqual(matches_file("ContrastThrowing.scala"), True)         
    self.assertEqual(matches_file("ContrastThrowingAn.scala"), True)         
    self.assertEqual(matches_file("ContrastThrowingAnException.scala"), True)         

    # misses
    self.assertEqual(matches_file("AContrast.scala"), False)         
    self.assertEqual(matches_file("ContrastThrowingAnExceptionSuite.scala"), False)         
