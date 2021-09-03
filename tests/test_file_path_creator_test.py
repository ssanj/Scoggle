import unittest
import Scoggle.components.scoggle_types as stypes
import Scoggle.components.test_path_creator as tftypes
import os

class TestFilePathCreatorTest(unittest.TestCase):

  def test_get_test_file_params(self):
      root_dir = "/some/root/dir"
      package_dir = "my/awesome/project/"
      test_srcs = ["/src/test/"]
      file_name = "AwesomeThing"
      suffix = "Suite.scala"
      params = stypes.TestFileCreationParam(root_dir, package_dir, test_srcs, file_name, suffix)

      creator = tftypes.TestFilePathCreator(params, None)

      created_path = creator.get_test_file_path(0)
      test_file_class_name = creator.get_test_file_class_name()
      package_path = creator.get_dotted_package_path()

      self.assertEqual(created_path, "/some/root/dir/src/test/my/awesome/project/AwesomeThingSuite.scala")
      self.assertEqual(test_file_class_name, "AwesomeThingSuite")
      self.assertEqual(package_path, "my.awesome.project")

  def test_get_test_file_params_with_new_file(self):
      root_dir = "/some/root/dir"
      package_dir = "my/awesome/project/"
      test_srcs = ["/src/test/"]
      file_name = "AwesomeThing"
      suffix = "Suite.scala"
      params = stypes.TestFileCreationParam(root_dir, package_dir, test_srcs, file_name, suffix)

      creator = tftypes.TestFilePathCreator(params, None)

      # This changes the file name (nothing else)
      new_creator = creator.with_new_test_file_name("AnotherThingThatIsCoolSpec.scala")

      # Old Creator
      created_path = creator.get_test_file_path(0)
      test_file_class_name = creator.get_test_file_class_name()
      package_path = creator.get_dotted_package_path()

      self.assertEqual(created_path, "/some/root/dir/src/test/my/awesome/project/AwesomeThingSuite.scala")
      self.assertEqual(test_file_class_name, "AwesomeThingSuite")
      self.assertEqual(package_path, "my.awesome.project")

      # New creator
      new_created_path = new_creator.get_test_file_path(0)
      new_test_file_class_name = new_creator.get_test_file_class_name()
      new_package_path = new_creator.get_dotted_package_path()

      self.assertEqual(new_created_path, "/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCoolSpec.scala")
      self.assertEqual(new_test_file_class_name, "AnotherThingThatIsCoolSpec")
      self.assertEqual(new_package_path, "my.awesome.project")

