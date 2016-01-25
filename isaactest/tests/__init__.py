from functools import wraps
from ..utils.log import log, TEST, INFO, ERROR
from collections import OrderedDict


__all__ = ['TestWithDependency']


class TestWithDependency(object):
    """Declares a Regression Test item with dependencies and tracks results.

       Use as a decorator for each regression test function to ensure the test is
       run only if the tests it depends upon have run successfully. Automatically
       keeps track of the results of tests using the class variable 'Results'. To
       access the results of tests, 'TestWithDependency.Results' provides the internal
       OrderedDict used to track results; 'True' is a pass, 'False' is a fail,
       'None' denotes that the test was not run.

        - Tests must return a boolean 'True' for pass, 'False' for failure. Any other
          return value will be considered a failure!
        - Throws 'KeyError' if dependency in 'deps' has not been run/defined!
        - 'Name' should be an uppercase string of max length 25 characters to describe
          the test and is the name to be used in 'deps' if any other test depends
          on this test.
        - 'deps' is an optional list of test names that must have completed successfully
          for this test to be run. If a test name is listed in 'deps' and does not
          appear in 'Results' keys; a 'KeyError' exception will be raised.
    """
    Results = OrderedDict()

    def __init__(self, Name, deps=[]):
        self.Name = Name
        self.deps = deps
        self.Results[Name] = None

    def __call__(self, test_func):
        def _decorator(*args, **kwargs):
            if all([self.Results[d] for d in self.deps]):
                log(TEST, "Test '%s'." % self.Name)
                self.Results[self.Name] = False  # If it dies; ensure this test marked as a fail!
                result = test_func(*args, **kwargs)
                if type(result) != bool:
                    log(INFO, "Test returned unexpected value. Assuming failure!")
                    result = False
                self.Results[self.Name] = result
                return result
            else:
                not_met = ", ".join([d for d in self.deps if not self.Results[d]])
                log(TEST, "Test '%s' not run, dependencies '%s' not met!" % (self.Name, not_met))
                log(ERROR, "Test could not run!")
                self.Results[self.Name] = None
                return None
        return wraps(test_func)(_decorator)
