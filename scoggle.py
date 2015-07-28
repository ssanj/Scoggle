import os
import re

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

        raise CantFindRootPathError(file, paths)

    def prepend_prefix_to_suffixes(self, prefix, suffixes):
        return tuple(map(lambda x: (prefix + x) , suffixes))

    def prepend_root_dir_to_paths(self, root_dir, src_dirs):
        return list(map(lambda path: os.path.join(root_dir, path.lstrip(os.path.sep)), src_dirs))

    # src_dirs - This should be a list absolute paths to the directories to search
    # suffixes - This should be a tuple of suffixes. suffixes should be of the form ['Name1.ext1', 'Name2.ext2]
    # its probably better to pass in the file extension as well.
    # walker - something that returns a [(root, dirnames, filesnames)]
    def search_dirs_for_files_with_suffix(self, src_dirs, suffixes, walker):
        matched_files = []
        for src_dir in src_dirs:
            for root, dirnames, filenames in walker(src_dir):
                print("filenames: " + str(filenames))
                #TODO: pass the filter in a function.
                hits = [os.path.join(root, f) for f in filenames if f.endswith(suffixes)]
                matched_files.extend(hits)  
        return matched_files              

    def remove_largest_suffix_from_prefix(self, prefix, suffixes):        
        possibleSuffixes = [ts for ts in suffixes if prefix.endswith(ts)]
        if (len(possibleSuffixes) == 0):
            return prefix
        else:        
            suffix = max(possibleSuffixes, key=len) #find longest match
            prefixMinusTestSuffix = re.sub(suffix + '$', '', prefix)
            return prefixMinusTestSuffix    


    # suffixes - should be of the form ['Name1.ext1', 'Name2.ext2]
    def find_matching_files(self, root_dir, src_dirs, prefix, suffixes):       
        extensions = self.prepend_prefix_to_suffixes(prefix, suffixes)
        fullpath_srcs = self.prepend_root_dir_to_paths(root_dir, src_dirs)
        return self.search_dirs_for_files_with_suffix(fullpath_srcs, extensions, os.walk)

class CantFindRootPathError(Exception):
    
    def __init__(self, file, paths):
        self.cause = "Can't find root path of file: " + str(file) + ", from: " + str(paths)        

    def __str__(self):
        return repr(self.cause)    