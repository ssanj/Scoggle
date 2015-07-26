
class Scoggle:

    def does_file_contain_path(self, file, paths):
        result = [p for p in paths if file.find(p) != -1]
        return len(result) > 0

    def get_first_root_path_or_error(self, file, paths): 
        for p in paths:
            if file.find(p) != -1:
                return file.partition(p)[0]

        raise CantFindRootPathError(file, paths)       

class CantFindRootPathError(Exception):
    
    def __init__(self, file, paths):
        self.cause = "Can't find root path of file: " + str(file) + ", from: " + str(paths)        

    def __str__(self):
        return repr(self.cause)    