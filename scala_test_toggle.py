import sublime, sublime_plugin, os, fnmatch

class ScoggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_file = self.view.file_name()
        self.base_dir = current_file.partition("/src/")[0]
        # find out if the current file is a test or main file
        # get file name (before .scala)
        
        self.doxx()
        # file_names = ["one", "two", "three"]
        # sublime.active_window().show_quick_panel(file_names, 1)
        # if current_file.endswith("Spec.scala"):
        #     target_file = current_file.replace("/test/", "/main/").replace("Spec.scala", ".scala") #Spec, Suite, #Test
        # else:
        #     target_file = current_file.replace("/main/", "/test/").replace(".scala", "Spec.scala")
        # if not os.path.exists(target_file):
        #     sublime.error_message("could not find " + target_file)
        # else:    
        #     self.view.window().open_file(target_file)

    def doxx(self):
        current_file = self.view.file_name()
        root_dir = current_file.partition("/src/")[0]
        test_dir = "/src/test/scala/"
        search_dir = (root_dir + test_dir)
        # self.base_dir = self.view.file_name().partition("/src/")[0]
        print("search_dir = " + search_dir)
        self.files = []
        for root, dirnames, filenames in os.walk(search_dir):
            for filename in fnmatch.filter(filenames, '*Spec.scala'): # we need to go through all the suffixes here. or just .scala for the reverse
                print ("filename = " + filename)
                self.files.append(os.path.join(root, filename))

        print ("files = " + str(self.files))
        file_names = list(map(lambda x: os.path.split(x)[1], self.files))
        sublime.active_window().show_quick_panel(file_names, self.file_selected)

    def file_selected(self, selected_index):
        if selected_index != -1:
            sublime.active_window().open_file(self.files[selected_index])