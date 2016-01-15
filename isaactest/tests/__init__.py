from functools import wraps
from ..utils.log import log, TEST, ERROR


__all__ = ['TestWithDependency']


def TestWithDependency(Name, Results, deps=[]):
    """Declares a Regression Test item with dependencies and track results.

       Use as a decorator for each regression test function to ensure the test is
       run only if the tests it depends upon have run successfully. Automatically
       keeps track of the results of tests using 'Results'.
       Throws 'KeyError' if dependency in 'deps' has not been run/defined!
        - 'Name' should be an uppercase string of max length 25 characters to describe
          the test and is the name to be used in 'deps' if any other test depends
          on this test.
        - 'Results' should be an OrderedDict containing {TestName: bool} pairs;
          it will be updated with the results of the test once complete. If a test
          does not run, 'Results' will be updated to have 'None' as the value.
        - 'deps' is an optional list of test names that must have completed successfully
          for this test to be run. If a test name is listed in 'deps' and does not
          appear in 'Results' keys; a 'KeyError' exception will be raised.
    """
    def _Dependency(test_func):
        def _decorator(*args, **kwargs):
            if all([Results[d] for d in deps]):
                log(TEST, "Test '%s'." % Name)
                result = test_func(*args, **kwargs)
                Results[Name] = result
                return result
            else:
                not_met = ", ".join([d for d in deps if not Results[d]])
                log(TEST, "Test '%s' not run, dependencies '%s' not met!" % (Name, not_met))
                log(ERROR, "Test could not run!")
                Results[Name] = None
                return None
        return wraps(test_func)(_decorator)
    return _Dependency
