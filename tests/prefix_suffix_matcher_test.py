import unittest
import Scoggle.components.scoggle as sc
import Scoggle.components.scoggle_types as stypes
import Scoggle.matchers.prefix_suffix_matcher as matcher
import os
import functools as fp

class PrefixSuffixMatcherTest(unittest.TestCase):

  scoggle = sc.Scoggle()  

  def test_match_test_file(self):                  
      param = stypes.MatcherParam(None, None, "Contrast", ["Spec.scala", "Suite.scala", "IntSpec.scala"], PrefixSuffixMatcherTest.scoggle, None)
      cut = matcher.PrefixSuffixMatcher(param)
      matches_file = fp.partial(cut.match_test_file, None, None)

      # matches
      self.assertEqual(matches_file("ContrastSpec.scala"), True)         
      self.assertEqual(matches_file("ContrastSuite.scala"), True)         
      self.assertEqual(matches_file("ContrastIntSpec.scala"), True)         
      
      # misses
      self.assertEqual(matches_file("ContrastSpecification.scala"), False)         
      self.assertEqual(matches_file("MirrorSpec.scala"), False)         

  def test_match_prod_file_with_long_suffix(self): 
    self.match_prod_file_with_suffix("ContrastIntSpec", "Contrast", "AContrast")
    self.match_prod_file_with_suffix("ContrastSpec", "Contrast", "ContrastWithContext")

  def match_prod_file_with_suffix(self, prefix, match, miss): 
    param = stypes.MatcherParam(None, None, prefix, ["Spec.scala", "Suite.scala", "IntSpec.scala"], PrefixSuffixMatcherTest.scoggle, None)
    cut = matcher.PrefixSuffixMatcher(param)

    matches_file = fp.partial(cut.match_prod_file, None, None)
    
    # matches
    self.assertEqual(matches_file(match + ".scala"), True)         

    # misses
    self.assertEqual(matches_file(miss + ".scala"), False)         
