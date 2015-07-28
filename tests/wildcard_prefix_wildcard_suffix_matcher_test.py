import unittest
import scoggle as sc
import scoggle_types as stypes
import matchers.wildcard_prefix_wildcard_suffix_matcher as matcher
import os
import functools as fp

class WildcardPrefixWildcardSuffixMatcherTest(unittest.TestCase):

  scoggle = sc.Scoggle()  

  def test_match_test_file(self):                  
      param = stypes.MatcherParam(None, None, "Contrast", ["Spec.scala", "Suite.scala", "IntSpec.scala"], WildcardPrefixWildcardSuffixMatcherTest.scoggle, None)
      cut = matcher.WildcardPrefixWildcardSuffixMatcher(param)
      matches_file = fp.partial(cut.match_test_file, None, None)

      # matches
      self.assertEqual(matches_file("AContrastWithinSomeContextSpec.scala"), True)         
      self.assertEqual(matches_file("ABeautifulContrastContextIntSpec.scala"), True)         
      self.assertEqual(matches_file("SomeContrastContextSuite.scala"), True)         
      self.assertEqual(matches_file("ThisCouldBeAnythingHavingContrastInItsNameSpec.scala"), True)         

      # additional matches
      self.assertEqual(matches_file("ContrastWithinSomeContextSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastWithinAnotherContextIntSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastThrowingAnExceptionSuite.scala"), True)               
      self.assertEqual(matches_file("ContrastSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastSuite.scala"), True)         
      self.assertEqual(matches_file("ContrastIntSpec.scala"), True)         
      
      # misses
      self.assertEqual(matches_file("MirrorSpec.scala"), False)         

  def test_match_prod_file_with_suffix(self): 

    class DummyLogger:
        def debug(self, message): pass
    
    param = stypes.MatcherParam(None, None, "ABeautifulContrastContextIntSpec", ["Spec.scala", "Suite.scala", "IntSpec.scala"], WildcardPrefixWildcardSuffixMatcherTest.scoggle, DummyLogger())
    cut = matcher.WildcardPrefixWildcardSuffixMatcher(param)

    matches_file = fp.partial(cut.match_prod_file, None, None)
    
    # matches
    self.assertEqual(matches_file("Contrast.scala"), True)    

    self.assertEqual(matches_file("ABeautiful.scala"), True)         
    self.assertEqual(matches_file("ABeautifulContrast.scala"), True)         
    self.assertEqual(matches_file("ABeautifulContrastContext.scala"), True)         
    self.assertEqual(matches_file("BeautifulContrast.scala"), True)         
    self.assertEqual(matches_file("BeautifulContrastContext.scala"), True)         
    self.assertEqual(matches_file("ContrastContext.scala"), True)         
    self.assertEqual(matches_file("Context.scala"), True)         
    self.assertEqual(matches_file("A.scala"), True)         

    # misses
    self.assertEqual(matches_file("BeautifulContext.scala"), False)         
    self.assertEqual(matches_file("Mirror.scala"), False)         
