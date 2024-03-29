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

      # Old Creator
      created_path = creator.get_test_file_path(0)
      test_file_class_name = creator.get_test_file_class_name()
      package_path = creator.get_dotted_package_path()

      self.assertEqual(created_path, "/some/root/dir/src/test/my/awesome/project/AwesomeThingSuite.scala")
      self.assertEqual(test_file_class_name, "AwesomeThingSuite")
      self.assertEqual(package_path, "my.awesome.project")

      # New creator
      new_creator = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCoolSpec.scala")
      new_test_file_class_name = new_creator.get_test_file_class_name()
      new_package_path = new_creator.get_dotted_package_path()

      self.assertEqual(new_test_file_class_name, "AnotherThingThatIsCoolSpec")
      self.assertEqual(new_package_path, "my.awesome.project")
      new_created_path = new_creator.get_test_file_path(0)
      self.assertEqual(new_created_path, "/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCoolSpec.scala")


  def test_with_new_test_file_name_with_odd_file_names(self):
      root_dir = "/some/root/dir"
      package_dir = "my/awesome/project/"
      test_srcs = ["/src/test/"]
      file_name = "AwesomeThing"
      suffix = "Suite.scala"
      params = stypes.TestFileCreationParam(root_dir, package_dir, test_srcs, file_name, suffix)
      logger =  MyLogger()

      creator = tftypes.TestFilePathCreator(params, logger)
      creator.get_test_file_path(0) #needed to select the test source

      new_creator1 = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCoolSPEC.scala")
      self.assertEqual(logger.message, None)
      self.assertEqual(new_creator1.get_test_file_class_name(), "AnotherThingThatIsCoolSPEC")

      new_creator2 = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCool$$#.scala")
      self.assertEqual(logger.message, "Could not use supplied test name to extract suffix from root_test_src_path of /some/root/dir/src/test/, new_test_file of /some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCool$$#.scala. Please retry with another name.")
      self.assertEqual(new_creator2, None)

      logger.message = None
      new_creator3 = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/AnotherThingThatIsCooltest.scala")
      self.assertEqual(logger.message, None)
      self.assertEqual(new_creator3.get_test_file_class_name(), "AnotherThingThatIsCooltest")

      logger.message = None
      new_creator4 = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/alllowercasespec.scala")
      self.assertEqual(logger.message, "Could not use supplied test name to extract suffix from root_test_src_path of /some/root/dir/src/test/, new_test_file of /some/root/dir/src/test/my/awesome/project/alllowercasespec.scala. Please retry with another name.")
      self.assertEqual(new_creator4, None)


  def test_get_test_file_params_with_new_file_and_package(self):
      root_dir = "/some/root/dir"
      package_dir = "my/awesome/project/"
      test_srcs = ["/src/test/"]
      file_name = "AwesomeThing"
      suffix = "Suite.scala"
      params = stypes.TestFileCreationParam(root_dir, package_dir, test_srcs, file_name, suffix)
      logger = MyLogger()
      creator = tftypes.TestFilePathCreator(params, logger)

      # Old Creator
      created_path = creator.get_test_file_path(0)
      test_file_class_name = creator.get_test_file_class_name()
      package_path = creator.get_dotted_package_path()

      self.assertEqual(created_path, "/some/root/dir/src/test/my/awesome/project/AwesomeThingSuite.scala")
      self.assertEqual(test_file_class_name, "AwesomeThingSuite")
      self.assertEqual(package_path, "my.awesome.project")

      # New creator
      new_creator = creator.with_new_test_file_name("/some/root/dir/src/test/my/awesome/project/take2/AwesomeThingSuite.scala")
      self.assertEqual(new_creator is None, False)
      new_test_file_class_name = new_creator.get_test_file_class_name()
      new_package_path = new_creator.get_dotted_package_path()

      self.assertEqual(new_test_file_class_name, "AwesomeThingSuite")
      self.assertEqual(new_package_path, "my.awesome.project.take2")


class MyLogger():

  def __init__(self):
    self.message = None

  def error(self, message):
    self.message = message

