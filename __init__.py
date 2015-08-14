import os

import Scoggle.components.scoggle
import Scoggle.components.scoggle_types

# We remove this if we are running the unit tests as we are running outside sublime.
if not (os.environ.get("UNIT_TEST", False)):
    import Scoggle.components.sublime_wrapper

import Scoggle.matchers.prefix_suffix_matcher
import Scoggle.matchers.prefix_wildcard_suffix_matcher
import Scoggle.matchers.wildcard_prefix_wildcard_suffix_matcher