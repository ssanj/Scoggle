import sublime, sublime_plugin, os, fnmatch

class ScoggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.scoggle()
        
    def scoggle(self):
        current_file = self.view.file_name()
        root_dir = current_file.partition("/src/")[0]
        settings = load_settings(root_dir)
        prod_srcs = settings.get("production_srcs")
        test_srcs = settings.get("test_srcs")
        test_post_fixes = settings.get("test_post_fixes")
        prefix = os.path.splitex(os.path.split(current_file)[1])[0]

        if (is_production_file(current_file, settings)):
            matches = find_matching_files(test_srcs, prefix, test_post_fixes)
            show_results_list(matches)        
        else if (is_test_file(current_file, settings)):
            matches = find_matching_files(prod_srcs, prefix, [".scala"])
            show_results_list(matches)        
        else:
            sublime.show_error("There is a problem with your configuration.")    

    def show_results_list(self, matches):
        file_names = list(map(lambda x: os.path.split(x)[1], matches))
        sublime.active_window().show_quick_panel(file_names, self.file_selected)
        
    def is_production_file(self, current_file, settings):
        return is_on_path(current_file, settings.get("production_srcs"))

    def is_test_file(self, current_file, settings):
        return is_on_path(current_file, settings.get("test_srcs"))

    def is_on_path(self, current_file, paths):
        result = [p for p in paths if current_file.startswith(p)]
        return len(result) > 0        

    def file_selected(self, selected_index):
        if selected_index != -1:
            sublime.active_window().open_file(self.files[selected_index])

    def load_settings(self, root_dir):
        #check for settings in the current dir. If it exists return that
        # root_config = os.path.join(root_dir, "Scoggle.sublime-settings")
        # if (os.path.isfile(root_config)):
        #     return sublime.load_settings("Scoggle.sublime-settings")
        # else:    

        return sublime.load_settings("Scoggle.sublime-settings")

    #post_fixes should be of the form ['Spec.scala', 'Test.scala']
    def find_matching_files(self, src_dirs, prefix, post_fixes):
        matched_files = []
        exts = tuple(post_fixes)
        for src_dir in src_dirs:
            for root, dirnames, filenames in os.walk(src_dir):
                hits = [f for f in filenames if f.endswith(exts)]
                matched_files.extend(hits)

        return matched_files





