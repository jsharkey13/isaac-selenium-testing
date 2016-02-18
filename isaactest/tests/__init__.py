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
    _Tests = OrderedDict()
    _Dependencies = dict()

    def __init__(self, Name, deps=[]):
        self.Name = Name
        self.deps = deps
        self.Results[Name] = None
        self._Dependencies[Name] = self.deps

    def __call__(self, test_func):
        def _decorator(*args, **kwargs):
            if type(self.Results[self.Name]) == bool:  # Don't re-run previosuly run tests
                log(TEST, "Test '%s'." % self.Name)
                log(INFO, "Test has already run.")
                return
            if self.dependencies_met(self.Name):
                log(TEST, "Test '%s'." % self.Name)
                self.Results[self.Name] = False  # If it dies; ensure this test marked as a fail!
                result = test_func(*args, **kwargs)
                if type(result) != bool:
                    log(INFO, "Test returned unexpected value. Assuming failure!")
                    result = False
                del self.Results[self.Name]  # This moves the entry to the end,
                self.Results[self.Name] = result  # So it is clearer which were not run.
                return result
            else:
                not_met = ", ".join([d for d in self.deps if not self.Results[d]])
                log(TEST, "Test '%s' not run, dependencies '%s' not met!" % (self.Name, not_met))
                log(ERROR, "Test could not run!")
                del self.Results[self.Name]  # This moves the entry to the end,
                self.Results[self.Name] = None  # So it is clearer which were not run.
                return None
        test = wraps(test_func)(_decorator)
        self._Tests[self.Name] = test
        return test

    @classmethod
    def dependencies_met(cls, name):
        return all([cls.Results[d] for d in cls._Dependencies[name]])

    @classmethod
    def run_test_with_deps(cls, name, driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR):
        """Run a single test from the test suite, first running all dependencies.

           This ideally should not be used as a stand in to run a short list of tests
           (though it ought to work if made to). It is designed for running single
           tests when a feature of the website has changed and only one area needs
           testing. It avoids having to work out the dependencies by hand.
            - 'cls' is automatically passed in because this function is decorated
              as a classmethod. IGNORE THIS ARGUMENT.
            - 'name' is the uppercase name of the test to run.
            - 'driver' should be a Selenium WebDriver.
            - 'inbox' must be a GuerrillaInbox object.
            - 'Users' should be the TestUsers object.
            - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
            - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
            - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
        """
        # This is the superset of all arguments required by tests. Their "**kwargs"
        # argument allows us to pass in all arguments and any extra ones will simply
        # be ignored.
        kwargs = {"driver": driver, "inbox": inbox, "Users": Users, "ISAAC_WEB": ISAAC_WEB,
                  "GUERRILLAMAIL": GUERRILLAMAIL, "WAIT_DUR": WAIT_DUR}

        # Run each of the dependency tests if necessary, and recursively run their
        # dependencies. DOES NOT CHECK FOR SUCCESS of dependencies, that is left to
        # the main decorator above.
        for t in cls._Dependencies[name]:
            if type(cls.Results[t]) != bool:
                cls.run_test_with_deps(t, **kwargs)
        cls._Tests[name](**kwargs)

    @classmethod
    def run_all_tests(cls, driver, inbox, Users, ISAAC_WEB, GUERRILLAMAIL, WAIT_DUR):
        """Run all tests from the test suite.

           This will run all defined tests, in the order set by their imports. This
           ordering is important if all are to run successfully.
            - 'cls' is automatically passed in because this function is decorated
              as a classmethod. IGNORE THIS ARGUMENT.
            - 'driver' should be a Selenium WebDriver.
            - 'inbox' must be a GuerrillaInbox object.
            - 'Users' should be the TestUsers object.
            - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
            - 'GUERRILLAMAIL' is the string URL of GuerrillaMail.
            - 'WAIT_DUR' is the time in seconds to wait for JavaScript to run/load.
        """
        # This is the superset of all arguments required by tests. Their "**kwargs"
        # argument allows us to pass in all arguments and any extra ones will simply
        # be ignored.
        kwargs = {"driver": driver, "inbox": inbox, "Users": Users, "ISAAC_WEB": ISAAC_WEB,
                  "GUERRILLAMAIL": GUERRILLAMAIL, "WAIT_DUR": WAIT_DUR}

        for test in cls._Tests:
            cls._Tests[test](**kwargs)


# Import all known tests into the namespace of this file, also avoids extra imports
# in any file using the module. It can just import TestWithDependency from this
# file and these imports will declare all the requisite tests.
from .login import login
from .questionnaire import questionnaire
from .global_nav import global_nav
from .logout import logout
from .login_throttle import login_throttle
from .login_timeout import login_timeout
from .signup import signup
from .welcome_email import welcome_email
from .req_verify_emails import req_verify_emails
from .recieve_verify_emails import recieve_verify_emails
from .verify_link import verify_link
from .verify_banner_gone import verify_banner_gone
from .pwd_reset_throttle import pwd_reset_throttle
from .recieve_pwd_reset_emails import recieve_pwd_reset_emails
from .pwd_reset_link import pwd_reset_link
from .reset_pwd_login import reset_pwd_login
from .login_uppercase import login_uppercase
from .signup_uppercase import signup_uppercase
from .user_consistency import user_consistency
from .user_consistency_popup import user_consistency_popup
from .email_change import email_change
from .email_change_emails import email_change_emails
from .email_change_login_status import email_change_login_status
from .admin_page_access import admin_page_access
from .delete_user import delete_user
from .accordion_behaviour import accordion_behavior
from .quick_questions import quick_questions
from .multiple_choice_questions import multiple_choice_questions
from .numeric_q_units_select import numeric_q_units_select
from .numeric_q_all_correct import numeric_q_all_correct
from .numeric_q_answer_change import numeric_q_answer_change
from .numeric_q_incorrect_unit import numeric_q_incorrect_unit
from .numeric_q_incorrect_value import numeric_q_incorrect_value
from .numeric_q_all_incorrect import numeric_q_all_incorrect
from .numeric_q_incorrect_sf import numeric_q_incorrect_sf
from .numeric_q_incorrect_sf_u import numeric_q_incorrect_sf_u
from .numeric_q_known_wrong_ans import numeric_q_known_wrong_ans
from .numeric_q_known_wrong_sf import numeric_q_known_wrong_sf
from .numeric_q_help_popup import numeric_q_help_popup
from .answer_saved_login import answer_saved_login
from .tab_behaviour import tab_behavior
from .back_to_board import back_to_board
from .filter_behaviour import filter_behaviour
from .filter_by_concept import filter_by_concept
from .admin_stats_summary import admin_stats_summary
from .admin_stats_analytics import admin_stats_analytics
from .admin_stats_gameboards import admin_stats_gameboards
from .admin_stats_schools import admin_stats_schools
from .admin_user_search import admin_user_search
from .non_admin_user_search import non_admin_user_search
