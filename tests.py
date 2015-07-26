import unittest
import scoggle
import os

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

  # get_base_file
  
  def test_get_base_file_with_pathed_file_and_extension(self):
      self.assertEqual(self.cut.get_base_file("/root/project/testDir/package/someFile.ext"), "someFile")                  

  def test_get_base_file_with_pathed_file_without_extension(self):
      self.assertEqual(self.cut.get_base_file("/root/project/testDir/package/someFile"), "someFile")                  

  def test_get_base_file_without_path(self):
      self.assertEqual(self.cut.get_base_file("someFile.abc"), "someFile")                  

  # prepend_prefix_to_suffixes
 
  def test_prepend_prefix_to_suffixes_with_multiple_suffixes(self):
      self.assertEqual(self.cut.prepend_prefix_to_suffixes("BaseFile", ["Test", "Suite", "Spec"]), ("BaseFileTest", "BaseFileSuite", "BaseFileSpec"))

  def test_prepend_prefix_to_suffixes_with_empty_suffix_list(self):
      self.assertEqual(self.cut.prepend_prefix_to_suffixes("BaseFile", []), ())

  # prepend_root_dir_to_paths

  def test_prepend_root_dir_to_paths_with_single_source_dir_with_leading_path_sep(self):
      self.assertEqual(self.cut.prepend_root_dir_to_paths("/root/project/", ["/package1"]), ["/root/project/package1"]) 

  def test_prepend_root_dir_to_paths_with_single_source_dir_without_leading_path_sep(self):
      self.assertEqual(self.cut.prepend_root_dir_to_paths("/root/project/", ["package1"]), ["/root/project/package1"]) 

  def test_prepend_root_dir_to_paths_with_multiple_source_dirs_with_and_without_leading_path_seps(self):
      self.assertEqual(self.cut.prepend_root_dir_to_paths("/root/project/", ["package1", "/package2", "/package3/package4/"]), 
          ["/root/project/package1", "/root/project/package2", "/root/project/package3/package4/"]) 

  # remove_largest_suffix_from_prefix
  
  def test_remove_largest_suffix_from_prefix_with_single_matching_suffix(self):
      self.assertEqual(self.cut.remove_largest_suffix_from_prefix("FoobarSpec", ["Spec"]), "Foobar")  

  def test_remove_largest_suffix_from_prefix_with_multiple_matching_suffixes(self):
      self.assertEqual(self.cut.remove_largest_suffix_from_prefix("FoobarIntSpec", ["Spec", "IntSpec"]), "Foobar")  

  def test_remove_largest_suffix_from_prefix_without_matching_suffixes(self):
      self.assertEqual(self.cut.remove_largest_suffix_from_prefix("FoobarSuite", ["Spec", "IntSpec"]), "FoobarSuite")  

  def test_remove_largest_suffix_from_prefix_without_empty_suffixes(self):
      self.assertEqual(self.cut.remove_largest_suffix_from_prefix("FoobarSuite", []), "FoobarSuite")

  # get_file_without_extension
  
  def test_get_file_without_extension_with_file_without_an_extension(self):
      self.assertEqual(self.cut.get_file_without_extension("Foobar"), "Foobar")

  def test_get_file_without_extension_with_file_with_an_extension(self):
      self.assertEqual(self.cut.get_file_without_extension("Foobar.baz"), "Foobar")

  # get_files_without_extension    

  def test_get_files_without_extension_with_files_with_mixed_extensions(self):
      self.assertEqual(self.cut.get_files_without_extension(["Flee", "Foo.bar", "Boo", "Baree.baz"]), ["Flee", "Foo", "Boo", "Baree"])

  def test_get_files_without_extension_with_files_with_an_extension(self):
      self.assertEqual(self.cut.get_files_without_extension(["Foo.bar", "Baree.baz"]), ["Foo", "Baree"])

  # search_dirs_for_files_with_suffix
  def test_search_dirs_for_files_with_suffix(self):

    class Directory:
        def __init__(self, name, files):
             self.name = name
             self.files = files

    class FileStructure:
        def __init__(self, name, directories):
            self.name = name
            self.directories = directories

    unit_dir = FileStructure("/root/projects/Random/unit", [Directory("package1", ["Feature1Spec", "Feature2Spec"]),
                                                            Directory("package2", ["Feature4Spec", "Feature5Spec"])])

    int_dir = FileStructure("/root/projects/Random/integration", [Directory("package1", ["Feature1IntSpec", "Feature2IntSpec"]),
                                                                 Directory("package2", ["Feature4IntSpec", "Feature5IntSpec"]),
                                                                 Directory("package3", ["Feature3IntSpec"])])                                                               

    acceptance_dir = FileStructure("/root/projects/Random/acceptance", [Directory("package1", ["Feature1AcceptanceSpec"])])

    src_dirs = [unit_dir, int_dir, acceptance_dir]

    suffixes = ("Feature1Spec", "Feature1IntSpec", "Feature1AcceptanceSpec") #includes prefix and suffix together.

    def testWalker(src_dir):
      root = src_dir.name
      dirs = src_dir.directories

      matched_files = []
      for d in dirs:
          t = tuple([os.path.join(root, d.name), [], d.files])
          matched_files.append(t)        

      return matched_files          

    self.assertEqual(self.cut.search_dirs_for_files_with_suffix(src_dirs, suffixes, testWalker), 
        ["/root/projects/Random/unit/package1/Feature1Spec", 
         "/root/projects/Random/integration/package1/Feature1IntSpec", 
         "/root/projects/Random/acceptance/package1/Feature1AcceptanceSpec"])      


if __name__ == '__main__':
    unittest.main()
