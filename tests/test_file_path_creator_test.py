import unittest
import Scoggle.components.scoggle_types as stypes
import Scoggle.components.test_path_creator as tftypes
import os

class TestFilePathCreatorTest(unittest.TestCase):

  def test_get_test_file_class_name(self):
      root_dir = "/some/root/dir"
      package_dir = "my/awesome/project/"
      test_srcs = ["/src/test/"]
      file_name = "AwesomeThing"
      suffix = "Suite.scala"
      params = stypes.TestFileCreationParam(root_dir, package_dir, test_srcs, file_name, suffix)

      creator = tftypes.TestFilePathCreator(params, None)

      created_path = creator.get_test_file_path(0)

      self.assertEqual(created_path, "/some/root/dir/src/test/my/awesome/project/AwesomeThingSuite.scala")
