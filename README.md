# Scoggle #

An attempt at a Sublime Text 3 plugin that will allow you to toggle between production and test code.

I did find [sublimetext-scalatest](https://github.com/patgannon/sublimetext-scalatest) but it doesn't do most of the things I want to do in the way I want to do them.

Here are some of the things I want to implement through this plugin:

1. Toggling from a production file will bring up a list of matching test files based on configured suffixes. Eg. Spec, Test, Suite, IntSpec etc.
2. Toggling from a test file will bring the matching source file. I'm not sure whether to show a list of possibly matching source files?
3. Provide a way to match on package-path on either production or test source directories.
4. Provide a way to match on file name irrespective of package-path.
5. Maybe a have a nice way to create production or test sources if they don't exist. Maybe run a file template.
6. Have a way to override configuration of source and test source directories on a per project basis.

Configuration would take the form of:

```{.javascript}
{
    "main_dir": ["dir1", "dir2"],
    "test_dir": ["dir1", "dir2", "dir3"],
    "test_suffixes": ["Test", "Spec", "Suite", "Specification", "IntSpec"],
    "allow_project_override": true
}
```

As my Python knowledge is almost non-existent, I would welcome help from anyone who is knowledgeable in Python or who wants to hack on a Sublime plugin for Scala.