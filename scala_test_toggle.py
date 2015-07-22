import sublime, sublime_plugin, os, fnmatch, re


#TODO: Remove the .scala at the end of test_suffixes and create with file_ext.
#TODO: What should we do if we can't get root_path? Encode in a type/class.
#TODO: Find a better way to log debug messages.
#TODO: Add a way to create a test/prod class if not found. Expand a template?
#TODO: Add local configuration in the working directory to override settings.
#TODO: Add an excludes dir to configuration.
class ScoggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):        
        self.scoggle()
        
    def scoggle(self):        
        current_file = self.view.file_name()
        #hide all the settings code in a class.
        settings = self.load_settings()
        project_settings = self.load_project_settings()

        prod_srcs = self.getSetting("production_srcs", project_settings, settings)
        test_srcs = self.getSetting("test_srcs", project_settings, settings)
        test_suffixes = self.getSetting("test_suffixes", project_settings, settings)

        prefix = os.path.splitext(os.path.split(current_file)[1])[0]

        if (self.is_production_file(current_file, prod_srcs)):
            self.findProdMatches(current_file, prod_srcs, test_srcs, prefix, test_suffixes)
        elif (self.is_test_file(current_file, test_srcs)):
            self.findTestMatches(current_file, prod_srcs, test_srcs, prefix, test_suffixes)
        else:
            self.show_error_message("There is a problem with your configuration.")    

    def findProdMatches(self, current_file, prod_srcs, test_srcs, prefix, test_suffixes):
        root_dir = self.get_root_path(current_file, prod_srcs)
        matches = self.find_matching_files(root_dir, test_srcs, prefix, test_suffixes)
        self.show_results_list(matches)        

    def findTestMatches(self, current_file, prod_srcs, test_srcs, prefix, test_suffixes):    
        print("test route")
        root_dir = self.get_root_path(current_file, test_srcs)
        #since it is a test file we need to remove the test suffixes from the prefix
        prefixMinusTestSuffix = self.removeTestSuffixes(prefix, test_suffixes)
        matches = self.find_matching_files(root_dir, prod_srcs, prefixMinusTestSuffix, [".scala"])
        self.show_results_list(matches)

    def show_error_message(self, message):        
        sublime.error_message(message)  

    def show_status_message(self, message):        
        sublime.status_message(message)                

    def removeTestSuffixes(self, prefix, suffixes):
        test_suffixes = list(map(lambda x: os.path.splitext(x)[0], suffixes))
        print("prefix, test_suffixes: " + str(test_suffixes))
        possibleSuffixes = [ts for ts in test_suffixes if prefix.endswith(ts)]
        if (len(possibleSuffixes) == 0):
            self.out("returning default prefix", prefix)
            return prefix
        else:        
            suffix = max(possibleSuffixes, key=len) #find longest match
            prefixMinusTestSuffix = re.sub(suffix + '$', '', prefix)
            self.out("returning stripped prefix", prefixMinusTestSuffix)
            return prefixMinusTestSuffix

    def show_results_list(self, matches):
        if (len(matches) == 0):
            self.show_error_message("Could not find matching file.")
        elif (len(matches) == 1):
            sublime.active_window().open_file(matches[0])
        else:    
            file_names = list(map(lambda x: [os.path.split(x)[1], x], matches))
            sublime.active_window().show_quick_panel(file_names, self.file_selected(matches))
        
    def is_production_file(self, current_file, prod_srcs):
        return self.is_on_path(current_file, prod_srcs)

    def is_test_file(self, current_file, test_srcs):
        return self.is_on_path(current_file, test_srcs)

    def is_on_path(self, current_file, paths):
        result = [p for p in paths if current_file.find(p) != -1]
        return len(result) > 0

    def get_root_path(self, current_file, paths):
        for p in paths:
            if current_file.find(p) != -1:
                return current_file.partition(p)[0]
        #what if we can't determine root path?

    def file_selected(self, matches):
        def handle_selection(selected_index):
            if selected_index != -1:
                sublime.active_window().open_file(matches[selected_index])

        return handle_selection

    def load_settings(self):
        return sublime.load_settings("Scoggle.sublime-settings")

    def load_project_settings(self):
        return self.view.settings()     

    def getSetting(self, key, conf1, conf2):    
        return conf1.get(key, conf2.get(key))

    #post_fixes should be of the form ['Spec.scala', 'Test.scala']
    def find_matching_files(self, root_dir, src_dirs, prefix, suffixes):
        matched_files = []
        print("prefix: " + prefix)
        print("suffixes" + str(suffixes))
        extensions = tuple(map(lambda x: (prefix + x) , suffixes))
        print("extensions: " + str(extensions))
        fullpath_srcs = list(map(lambda path: os.path.join(root_dir, path.lstrip(os.path.sep)), src_dirs))
        print("fullpath_srcs: " + str(fullpath_srcs))

        for src_dir in fullpath_srcs:
            for root, dirnames, filenames in os.walk(src_dir):
                print("filenames: " + str(filenames))
                hits = [os.path.join(root, f) for f in filenames if f.endswith(extensions)]
                matched_files.extend(hits)

        print("matches:" + str(matched_files))        
        return matched_files

    def out(self, name, value): print(str(name) + ":" + str(value))    


