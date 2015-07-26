import unittest
import scoggle

class ScoggleTest(unittest.TestCase):

  def setUp(self):
    self.cut = scoggle.Scoggle()

  def tearDown(self):
    self.cut = None    

  # does_file_contain_path

  def test_does_file_contain_path_with_single_matching_path(self):      
      #tests whether a single path can be is contained within a given file path.
      self.assertEqual(self.cut.does_file_contain_path("/root/project/testDir/package/someFile", ["/testDir"]), True)    

  def test_does_file_contain_path_with_single_matching_path_and_multiple_non_matching_paths(self):            
      #tests whether when given a single matching path and multiple non-matching paths whether the match is found.
      self.assertEqual(self.cut.does_file_contain_path("/root/project/testDir/package/someFile", ["/blah/Dir", "/testDir", "/IntTest"]), True)    

  def test_does_file_contain_path_with_multiple_matching_paths(self):            
      #tests whether when given multiple matching paths for a given file path that a match is found.
      self.assertEqual(self.cut.does_file_contain_path("/root/project/testDir/package/someFile", ["/package", "/testDir", "/project"]), True)    

  def test_does_file_contain_path_with_matching_path_of_the_wrong_case(self):            
      #tests whether when given a matching path of the wrong case for a given file path that the match is not found.
      self.assertEqual(self.cut.does_file_contain_path("/root/project/IntTestDir/package/someFile", ["/testDir"]), False)    

  def test_does_file_contain_path_with_single_non_matching_path(self):            
      #tests whether when given a non-matching path for a given file path that the match is not found.
      self.assertEqual(self.cut.does_file_contain_path("/root/project/suite/package/someFile", ["/testDir"]), False)    

  def test_get_first_root_path_or_error_with_single_matching_path(self):
      self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/testDir"]), "/root/project")            

  # does_file_contain_path

  def test_get_first_root_path_or_error_with_single_matching_path(self):
      self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/testDir"]), "/root/project")            

  def test_get_first_root_path_or_error_with_single_matching_path_with_multiple_non_matching_paths(self):
      self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/blah/Dir", "/testDir", "/IntTest"]), "/root/project")            

  def test_get_first_root_path_or_error_with_single_non_matching_path(self):      
    with self.assertRaises(scoggle.CantFindRootPathError):
        self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/blah/Dir"]), "/root/project")               

  def test_get_first_root_path_or_error_with_multiple_non_matching_paths(self):      
    with self.assertRaises(scoggle.CantFindRootPathError):
        self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/IntTest", "/blah/Dir"]), "/root/project")               

if __name__ == '__main__':
    unittest.main()
