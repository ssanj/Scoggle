import os
import re

class TestFilePathCreator():

    def __init__(self, params, logger):
        self.params = params
        self.logger = logger

    def get_test_file_path(self, selected_index):
        params = self.params
        if selected_index != -1 and selected_index < len(params.test_srcs):
            test_src_path = params.test_srcs[selected_index] # test source path selected by user
            root_test_src_path = os.path.join(params.root_dir, test_src_path.lstrip(os.path.sep)) # strip starting path separators
            self.params.root_test_src_path = root_test_src_path
            root_test_src_path_package = os.path.join(root_test_src_path, params.package_dir.lstrip(os.path.sep)) # strip starting path separators
            test_file_name = "{0}{1}".format(params.file_name, params.suffix)
            test_file_path = os.path.join(root_test_src_path_package, test_file_name.lstrip(os.path.sep)) # strip starting path separators
            return test_file_path
        else:
            return None

    ## uses old suffix - we need the new suffix
    def get_test_file_class_name(self):
        file_name_with_ext = "{0}{1}".format(self.params.file_name, self.params.suffix)
        file_name = os.path.splitext(file_name_with_ext)[0] # get only the file name
        return file_name

    def with_new_test_file_name(self, new_test_file_name_and_ext):
        base_name = os.path.basename(new_test_file_name_and_ext) # file name and extension (without path)
        (file_name, ext) = os.path.splitext(base_name) #split into file and ext
        test_framework_ext_match = re.findall(r'([A-Z][A-Za-z0-9]+)$', file_name) #Find last word - example Spec or Suite or Test etc


        if test_framework_ext_match is not None and len(test_framework_ext_match) != 0:
            test_framework_ext = test_framework_ext_match[0]
            suffix = "{0}{1}".format(test_framework_ext, ".scala") # Append .scala extension to test extension - Spec.scala, Suite.scala etc
            file_name_without_test_ext = file_name.split(test_framework_ext)[0] #Get file name without the test extension
            new_params = self.params.with_new_file_name(file_name_without_test_ext, suffix)
            return TestFilePathCreator(new_params, self.logger)
        else:
            self.logger.error("Could not use supplied test name to extract suffix. File name supplied {0}. Please retry with another name.".format(str(new_test_file_name_and_ext)))
            return None

    def with_new_test_file_name2(self, new_test_file):
        # How do we know which test source was selected?
        root_test_src_path = self.params.root_test_src_path
        if root_test_src_path is not None:
            parts = new_test_file.split(root_test_src_path)
            if len(parts) > 1:
                package_file = parts[1] # part after root + test source
                (package_path, base_name) = os.path.split(package_file)
                (file_name, ext) = os.path.splitext(base_name) #split into file and ext
                test_framework_ext_match = re.findall(r'([A-Z][A-Za-z0-9]+)$', file_name) #Find last word - example Spec or Suite or Test etc


                if test_framework_ext_match is not None and len(test_framework_ext_match) != 0:
                    test_framework_ext = test_framework_ext_match[0]
                    suffix = "{0}{1}".format(test_framework_ext, ".scala") # Append .scala extension to test extension - Spec.scala, Suite.scala etc
                    file_name_without_test_ext = file_name.split(test_framework_ext)[0] #Get file name without the test extension
                    new_params = self.params.with_new_file_name2(package_path, file_name_without_test_ext, suffix)
                    return TestFilePathCreator(new_params, self.logger)
                else:
                    self.logger.error("Could not use supplied test name to extract suffix from root_test_src_path of {0}, new_test_file of {1}. Please retry with another name.".format(str(root_test_src_path), str(new_test_file)))
                    return None
            else:
                self.logger.error("Could not determine package path from root_test_src_path of {0}, new_test_file of {1}".format(str(root_test_src_path), str(new_test_file)))
                return None

        else:
            self.logger.error("Could not determine root + test source selected")
            return None


    def get_dotted_package_path(self):
        remove_left_sep = self.params.package_dir.lstrip(os.path.sep)
        remove_right_sep = remove_left_sep.rstrip(os.path.sep)
        dotted = remove_right_sep.replace(os.sep, ".")
        return dotted

    def __str__(self):
        to_string = "TestFilePathCreator(params={0})".format(str(self.params))
        return repr(to_string)
