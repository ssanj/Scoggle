import unittest
import Scoggle.components.scoggle as sc
import Scoggle.components.scoggle_types as stypes
import os

class ScoggleTest(unittest.TestCase):

  def setUp(self):
    self.cut = sc.Scoggle()

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

  # def test_get_first_root_path_pair(self):
  #     self.assertEqual(self.cut.get_first_root_path_pair_or_error("/root/project/src/main/scala-2.12/package/someFile.scala", ["/src/main/scala", "/src/main/scala-2.12"]), ("/root/project", "/src/main/scala-2.12"))

  def test_get_longest_root_path_pair(self):
      self.assertEqual(self.cut.get_longest_root_path_pair_or_error("/root/project/src/main/scala-2.12/package/someFile.scala", ["/src/main/scala", "/src/main/scala-2.12"]), ("/root/project", "/src/main/scala-2.12"))

  def test_get_module_path_or_error_with_single_matching_path(self):
      self.assertEqual(
        self.cut.get_module_path_or_error("/root/some_project/some_module1/src/main/scala/package/someFile",
            [
              "/some_module1/src/main/scala",
              "/some_module1/src/test/scala",
              "/some_module2/src/main/scala",
              "/some_module2/src/test/scala"
            ]),
            "some_module1")

  # On a non-multi-module project, returns the root project name
  def test_get_module_path_or_error_on_single_project(self):
      self.assertEqual(
        self.cut.get_module_path_or_error("/root/some_project/src/main/scala/package/someFile",
            [
              "/src/main/scala",
              "/src/test/scala",
            ]),
            "some_project")


  def test_get_module_path_or_error_without_a_match(self):
    try:
      self.cut.get_module_path_or_error("/root/some_project/some_moduleX/src/main/scala/package/someFile",
            [
              "/some_module1/src/main/scala",
              "/some_module1/src/test/scala",
              "/some_module2/src/main/scala",
              "/some_module2/src/test/scala"
            ])
    except stypes.CantFindModuleNameError as e:
      self.assertEqual(e.cause,
        "Can't find module name of file: /root/some_project/some_moduleX/src/main/scala/package/someFile, from these paths: ['/some_module1/src/main/scala', '/some_module1/src/test/scala', '/some_module2/src/main/scala', '/some_module2/src/test/scala']")


  # does_file_contain_path
  def test_get_first_root_path_or_error_with_single_matching_path(self):
      self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/testDir"]), "/root/project")

  def test_get_first_root_path_or_error_with_single_matching_path_with_multiple_non_matching_paths(self):
      self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/blah/Dir", "/testDir", "/IntTest"]), "/root/project")

  def test_get_first_root_path_or_error_with_single_non_matching_path(self):
      with self.assertRaises(stypes.CantFindRootPathError):
            self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/blah/Dir"]), "/root/project")

  def test_get_first_root_path_or_error_with_multiple_non_matching_paths(self):
      with self.assertRaises(stypes.CantFindRootPathError):
          self.assertEqual(self.cut.get_first_root_path_or_error("/root/project/testDir/package/someFile", ["/IntTest", "/blah/Dir"]), "/root/project")

  # get_base_file

  def test_get_base_file_with_pathed_file_and_extension(self):
      self.assertEqual(self.cut.get_base_file("/root/project/testDir/package/someFile.ext"), "someFile")

  def test_get_base_file_with_pathed_file_without_extension(self):
      self.assertEqual(self.cut.get_base_file("/root/project/testDir/package/someFile"), "someFile")

  def test_get_base_file_without_path(self):
      self.assertEqual(self.cut.get_base_file("someFile.abc"), "someFile")

  # get_path_minus_file

  def test_get_path_minus_file(self):
    self.assertEqual(self.cut.get_path_minus_file("/root/project/testDir/package/someFile.ext"), "/root/project/testDir/package")
    self.assertEqual(self.cut.get_path_minus_file("/root/project/testDir/package"), "/root/project/testDir")


  # get_package_path

  def test_get_package_path(self):
    current = "/root/project/src/test/scala/one/two/three/someFile.scala"
    paths = ["src/main/scala", "src/test/scala"]
    self.assertEqual(self.cut.get_package_path(current, paths), "one.two.three")

  def test_get_package_path_with_unmatched_file(self):
    current = "/root/project/src/dir/scala/one/two/three/someFile.scala"
    paths = ["src/main/scala", "src/test/scala"]

    with self.assertRaises(stypes.CantFindRootPathError):
      self.assertEqual(self.cut.get_package_path(current, paths), "one.two.three")

  # get_updated_package_text

  def test_get_updated_package_text_new_file(self):
    newline  = os.linesep
    expected = "one.two.three" + newline + newline
    self.assertEqual(self.cut.get_updated_package_text("", "one.two.three"), expected)
    self.assertEqual(self.cut.get_updated_package_text(None, "one.two.three"), expected)

  def test_get_updated_package_text_file_with_newline_only(self):
    newline = os.linesep
    self.assertEqual(self.cut.get_updated_package_text(newline, "one.two.three"), "one.two.three" + newline + newline)

  def test_get_updated_package_text_existing_file_without_package(self):
    newline  = os.linesep
    dotted   = "one.two.three"
    content  = "import scala.concurrent.Future"
    expected = dotted + newline + newline + content
    self.assertEqual(self.cut.get_updated_package_text(content, dotted), expected)

  def test_get_updated_package_text_existing_file_without_package_with_empty_first_line(self):
    newline  = os.linesep
    dotted   = "one.two.three"
    content  = newline + "import scala.concurrent.Future"
    expected = dotted + newline + content
    self.assertEqual(self.cut.get_updated_package_text(content, dotted), expected)

  def test_get_updated_package_text_existing_file_without_package_with_empty_first_two_lines(self):
    newline = os.linesep
    dotted = "one.two.three"
    content = newline + newline
    expected = dotted + content
    self.assertEqual(self.cut.get_updated_package_text(content, dotted), expected)

  def test_get_updated_package_text_existing_file_with_package(self):
    newline  = os.linesep
    dotted   = "one.two.three"
    content  = "package " + dotted + newline + "import scala.concurrent.ExecutionContext"
    expected = content
    self.assertEqual(self.cut.get_updated_package_text(content, dotted), expected)

  def test_get_updated_package_text_existing_file_without_package_and_two_empty_lines(self):
    newline  = os.linesep
    dotted   = "one.two.three"
    content  = newline + newline + "import scala.concurrent.ExecutionContext"
    expected = dotted + content
    self.assertEqual(self.cut.get_updated_package_text(content, dotted), expected)

  #already_has_package
  def test_already_has_package_without_package_line(self):
    self.assertEqual(self.cut.already_has_package(None), False)
    self.assertEqual(self.cut.already_has_package(""), False)
    self.assertEqual(self.cut.already_has_package("line without newline"), False)

  def test_already_has_package_with_package_line(self):
    self.assertEqual(self.cut.already_has_package("package blah.de.blee"), True)
    self.assertEqual(self.cut.already_has_package("package blah.de.blah\n"), True)
    self.assertEqual(self.cut.already_has_package("package net.ssanj.test\n\nimport scala.util.Random"), True)

  #get_package_steps
  def test_get_package_steps_with_sub_package(self):
      full = "net.ssanj.dabble.dsl.property"
      sub  = "net.ssanj.dabble"
      self.assertEqual(self.cut.get_package_steps(full, sub), "package net.ssanj.dabble\npackage dsl\npackage property")

  def test_get_package_steps_with_sub_package_ending_with_dot(self):
      full = "net.ssanj.dabble.dsl.property"
      sub  = "net.ssanj.dabble."
      self.assertEqual(self.cut.get_package_steps(full, sub), "package net.ssanj.dabble\npackage dsl\npackage property")

  def test_get_package_steps_without_sub_package(self):
      self.assertEqual(self.cut.get_package_steps("net.ssanj.dabble", "dabble.ssanj.net"), None)
      self.assertEqual(self.cut.get_package_steps("net.ssanj.dabble", "net.ssanj.dabble"), None)

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

  def test_find_matching_words_with_no_prefix(self):
      self.assertEqual(self.cut.find_matching_words(""), [])

  def test_find_matching_words_with_prefix(self):
      result = self.cut.find_matching_words("AnXyzWithSomeContext")
      self.assertEqual(result,
          ["AnXyzWithSomeContext", "XyzWithSomeContext", "WithSomeContext", "SomeContext", "Context"])
