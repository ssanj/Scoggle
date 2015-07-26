import sublime
import sublime_plugin

class SublimeWrapper:

    def current_file(self, view):
        return view.file_name()    