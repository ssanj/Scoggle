import os
import re
import sys

from . import scoggle_types as stypes

class Scoggle:

    def get_base_file(self, file):
        return os.path.splitext(os.path.split(file)[1])[0]

    def get_file_without_extension(self, file):
        return os.path.splitext(file)[0]

    def get_files_without_extension(self, files):
        return list(map(lambda x: self.get_file_without_extension(x), files))

    def does_file_contain_path(self, file, paths):
        result = [p for p in paths if file.find(p) != -1]
        return len(result) > 0

    def get_first_root_path_or_error(self, file, paths):
        for p in paths:
            if file.find(p) != -1:
                return file.partition(p)[0]
        raise stypes.CantFindRootPathError(file, paths)

    def get_module_path_or_error(self, file, paths):
        for p in paths:
            if file.find(p) != -1:
                partitions = file.partition(p)
                if len(partitions) >= 2:
                    module_partition = partitions[1]
                    module_parts = list(filter(None, module_partition.split(os.path.sep)))
                    if (len(module_partition) > 0):
                        result = module_parts[0]
                        # single module project
                        # assumption: If you have a multi-module project you will
                        # use custom settings for paths, a couple for each module
                        if result == 'src':
                            # return project name
                            root = self.get_first_root_path_or_error(file, paths)
                            return os.path.basename(os.path.normpath(root))
                        else:
                            return result
                    else: # raise CantFindModuleNameError
                        pass
                else: # raise CantFindModuleNameError
                    pass
            else: # raise CantFindModuleNameError
                pass

        raise stypes.CantFindModuleNameError(file, paths)

    def get_first_root_path_pair_or_error(self, file, paths):
        for p in paths:
            if file.find(p) != -1:
                return (file.partition(p)[0], p)

        raise stypes.CantFindRootPathError(file, paths)

    def get_path_minus_file(self, current_file):
        return os.path.split(current_file)[0]

    def get_package_path(self, current_file, paths):
        root_dir = self.get_first_root_path_or_error(current_file, paths)
        fullpath_srcs = self.prepend_root_dir_to_paths(root_dir, paths)
        for p in fullpath_srcs:
            if current_file.startswith(p):
                return os.path.split(current_file)[0][len(p):][1:].replace(os.sep, ".")

        raise sypes.CantDeterminePackageError(current_file, paths)

    def already_has_package(self, content):
        if (content is None):
            return False
        else:
            newline = "\n"
            lines = content.split(newline)
            return len(lines) > 0 and lines[0].startswith("package")

    def get_updated_package_text(self, content, dotted):
        """
            content - the content of the source file.
            dotted - the dotted package path.
            This function tries to maintain 2 newlines between the package
            declaration first line of code.
            Example:
             returns the default package dotted with 2 new lines for:
                 - empty source file
                 - source file with one newline
                 - source file with two newlines
             squashes a newline if:
                - first two lines are newlines
             adds a new line if:
                - first line is a newline but the second isn't
            adds two newlines if:
               - none of the first two lines are newlines
        """
        #sublime seems to use '\n' as a line separator for windows as well.
        #Not sure why? It should be '\r\n'. If you use '\r\n', sublime interprets
        #it as two lines. Go figure.
        #os.linesep works for linux and mac but not windows.
        #Hard-coding to '\n' as it seems to work across all operation systems.
        newline = '\n'
        defaultContent = newline.join([dotted, "", ""])
        if (content is None):
            return defaultContent

        lines = content.split(newline)
        #an empty file or a file with one newline
        if (len(lines) == 0 or
            (len(lines) == 1 and len(lines[0]) == 0) or
            (len(lines) == 2 and (len(lines[0]) == 0 and len(lines[1]) == 0))):
            return defaultContent
        #files with more than one line that don't have a package
        elif (not(lines[0].startswith("package"))):
            if (len(lines[0]) == 0 and len(lines[1]) == 0):
                #the first line is a newline
                return newline.join([dotted] + lines[1:])
            elif (len(lines[0]) == 0 and len(lines[1]) != 0):
                return newline.join([dotted] + lines)
            else:
                #the first line is not a newline
                return newline.join([dotted, ""] + lines)
        else:
            #already has a package
            return newline.join(lines)

    def prepend_prefix_to_suffixes(self, prefix, suffixes):
        return tuple(map(lambda x: (prefix + x) , suffixes))

    def prepend_root_dir_to_paths(self, root_dir, src_dirs):
        return list(map(lambda path: os.path.join(root_dir, path.lstrip(os.path.sep)), src_dirs))

    def search_dirs_for_files_with_suffix(self, src_dirs, strategy, walker, logger):
        """
            src_dirs - this should be a list absolute paths to the directories to search
            suffixes - this should be a tuple of suffixes. suffixes should be of the form ['Name1.ext1', 'Name2.ext2]
                       its probably better to pass in the file extension as well.
            walker - something that returns a [(root, dirnames, filesnames)]
            logger - logger
        """
        matched_files = []
        for src_dir in src_dirs:
            for root, dirnames, filenames in walker(src_dir):
                # insert an empty element as the first element to allow for proper formatting with str.join
                # this entry will be filtered out because we filter on ".file_ext"
                filenames.insert(0, "")
                logger.debug("processing directory %s: %s", str(root), "\n\t".join(filenames))
                hits = [os.path.join(root, f) for f in filenames if f.endswith(".scala") and strategy(root, dirnames, f)]
                matched_files.extend(hits)

        return matched_files

    def remove_largest_suffix_from_prefix(self, prefix, suffixes):
        possibleSuffixes = [ts for ts in suffixes if prefix.endswith(ts)]
        if (len(possibleSuffixes) == 0):
            return prefix
        else:
            suffix = max(possibleSuffixes, key=len) #find longest matches
            prefixMinusTestSuffix = re.sub(suffix + '$', '', prefix)
            return prefixMinusTestSuffix


    # suffixes - should be of the form ['Name1.ext1', 'Name2.ext2]
    def find_matching_files(self, fullpath_srcs, strategy, logger):
        # extensions = self.prepend_prefix_to_suffixes(prefix, suffixes)
        return self.search_dirs_for_files_with_suffix(fullpath_srcs, strategy, os.walk, logger)

    def find_matching_words(self, prefix):
        filename = str(prefix)
        if (len(filename) == 0):
            return []
        else:
            results = []
            # Use * as the separator because it is an invalid character to use in a java/scala filename.
            words_separated_by_star = re.sub('(?!^)([A-Z]+)', r'*\1',prefix)
            words = words_separated_by_star.split('*')
            for idx, value in enumerate(words):
                results.append(''.join(words[idx:]))

            return results

    def make_class_name(self, matcher):
        module_name = "Scoggle.matchers." + matcher
        class_name = "".join(matcher.title().split('_'))
        return module_name + "." + class_name

    #http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    def get_class(self, kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def get_display_error_location(self, display_error_setting, dialog, status_bar):
        """
            Takes the display_error_setting, a partial function for displaying with the sublime
            dialog, status bar or not displaying any messages.

            dialog, status_bar take the format of: String => None

            Example:
                sublime.error_message
        """
        if (display_error_setting):
            if (display_error_setting == "dont_display"):
                return stypes.DontDisplay()
            elif (display_error_setting == "status_bar"):
                return stypes.StatusBar(status_bar)
            else:
                return stypes.Dialog(dialog)
        else:
            return stypes.Dialog(dialog)

    def display_error_in(self, message, location):
        location.display_message(message)

    def get_package_steps(self, full, sub):
        if (not(sub.endswith("."))):
            sub  += "."

        if (full.startswith(sub)):
            other = full.replace(sub, "")
            parts = [sub[:-1]] + other.split(".")
            newline = "\n"
            return newline.join(list(map(lambda p: "package " + p, parts)))
        else:
            # the sub package requested is not a valid prefix of the full package.
            return None

    @staticmethod
    def is_visible(view, version):
        if (view and view.sel() and len(view.sel()) != 0):
             if "source.scala" in view.scope_name(view.sel()[0].begin()):
                return True
             else:
                return False
        else:
            return False
