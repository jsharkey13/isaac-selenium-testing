from functools import wraps
from ..utils.log import log, TEST, ERROR


__all__ = ['TestWithDependency']


def TestWithDependency(Name, Results, deps=[]):
    """Throws KeyError if dependency has not been run!"""
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
