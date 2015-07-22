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
    "production_srcs" :
    [
        "/src/main/scala"
    ],
    "test_srcs" :
    [
        "/src/test/scala",
        "/src/it/scala"
    ],
    "test_suffixes" :
    [
        "Spec.scala",
        "IntSpec.scala",
        "Suite.scala",
        "Test.scala",
        "Specification.scala"
    ]
}
```

## TODOs ##

1. Remove the .scala at the end of test_suffixes and create with file_ext.
1. What should we do if we can't get root_path? Encode in a type/class?
1. Find a better way to log debug messages.
1. Add a way to create a test/prod class if not found. Expand a template?
1. Add local configuration in the working directory to override settings.
1. Add an excludes dir to configuration.
1. Add support for contexts. Eg. XYZWithSomeConditionSpec.