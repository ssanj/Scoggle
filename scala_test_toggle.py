import sublime
import sublime_plugin
import os
import fnmatch
import re
import sys

#hack to add scoggle as a module to this plugin. Is there a better way?
#http://stackoverflow.com/questions/15180537/how-to-include-third-party-python-packages-in-sublime-text-2-plugins
sys.path.append(os.path.join(os.path.dirname(__file__), "."))

import scoggle
import sublime_wrapper

class ScoggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):        
        self.scoggle = scoggle.Scoggle()
        self.wrapper = sublime_wrapper.SublimeWrapper()
        self.perform()
        
    def perform(self):        
        # current_file = self.view.file_name()
        current_file = self.wrapper.current_file(self.view)
        #hide all the settings code in a class.
        settings = self.load_settings()
        project_settings = self.load_project_settings()

        prod_srcs = self.getSetting("production_srcs", project_settings, settings)
        test_srcs = self.getSetting("test_srcs", project_settings, settings)
        test_suffixes = self.getSetting("test_suffixes", project_settings, settings)

        prefix = self.scoggle.get_base_file(current_file)

        if (self.is_production_file(current_file, prod_srcs)):
            self.findProdMatches(current_file, prod_srcs, test_srcs, prefix, test_suffixes)
        elif (self.is_test_file(current_file, test_srcs)):
            self.findTestMatches(current_file, prod_srcs, test_srcs, prefix, test_suffixes)
        else:
            self.show_error_message("There is a problem with your configuration.")    

    def findProdMatches(self, current_file, prod_srcs, test_srcs, prefix, test_suffixes):
        try:
            root_dir = self.scoggle.get_first_root_path_or_error(current_file, prod_srcs)
            matches = self.find_matching_files(root_dir, test_srcs, prefix, test_suffixes)
            self.show_results_list(matches)        
        except scoggle.CantFindRootPathError as cfrpe:
            self.show_error_message("Could not find root path for production. " + cfrpe.cause)
                

    def findTestMatches(self, current_file, prod_srcs, test_srcs, prefix, test_suffixes):    
        try:
            root_dir = self.scoggle.get_first_root_path_or_error(current_file, test_srcs)
            #since it is a test file we need to remove the test suffixes from the prefix
            prefixMinusTestSuffix = self.removeTestSuffixes(prefix, test_suffixes)
            matches = self.find_matching_files(root_dir, prod_srcs, prefixMinusTestSuffix, [".scala"])
            self.show_results_list(matches)
        except scoggle.CantFindRootPathError as cfrpe:
            self.show_error_message("Could not find root path for tests. " + cfrpe.cause)    

    def show_error_message(self, message):        
        sublime.error_message(message)  

    def show_status_message(self, message):        
        sublime.status_message(message)                

    def removeTestSuffixes(self, prefix, suffixes):    
        return self.scoggle.remove_largest_suffix_from_prefix(prefix, 
                self.scoggle.get_files_without_extension(suffixes))

    def show_results_list(self, matches):
        if (len(matches) == 0):
            self.show_error_message("Could not find matching file.")
        elif (len(matches) == 1):
            sublime.active_window().open_file(matches[0])
        else:    
            file_names = list(map(lambda x: [os.path.split(x)[1], x], matches))
            sublime.active_window().show_quick_panel(file_names, self.file_selected(matches))
        
    def is_production_file(self, current_file, prod_srcs):
        return self.scoggle.does_file_contain_path(current_file, prod_srcs)

    def is_test_file(self, current_file, test_srcs):
        return self.scoggle.does_file_contain_path(current_file, test_srcs)

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
        return self.scoggle.find_matching_files(root_dir, src_dirs, prefix, suffixes)

    def out(self, name, value): print(str(name) + ":" + str(value))    


