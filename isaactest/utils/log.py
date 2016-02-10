import datetime
from ..emails.result_email import send_results


__all__ = ['INFO', 'PASS', 'ERROR', 'log', 'start_testing', 'end_testing']

_LOGFILE = None
INFO = "INFO"
PASS = "PASS"
ERROR = "ERROR"
TEST = "TEST"


_errors = 0

# Customise which log events are printed:
_OUTPUT_LOGGING_LEVELS = [INFO, PASS, ERROR]


def log(level, message):
    """Log a message to stdout and to file. Not thread safe!

       Use to log messages; manages formatting and printing of only requested levels
       of logging.
        - 'level' should be one of the level constants from isaactest.utils.log
          either INFO or ERROR for user-written code.
        - 'message' is the string of the message to log.
    """
    global _OUTPUT_LOGGING_LEVELS, ERROR, _tests_passed, _errors
    if (level == ERROR):
        _errors += 1
    if level != TEST:
        message = " - " + message
    if (level in _OUTPUT_LOGGING_LEVELS) or (level == TEST):
        log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = "[%s]" % level.ljust(5)
        log_item = "%s %s\t%s" % (log_time, level, message)
        print log_item
        _LOGFILE.write(log_item + "\n")
        _LOGFILE.flush()


def _generate_summary(Results, aborted):
    """When testing has finished, return a string of the results in a nice format."""
    passes = len([v for v in Results.values() if v])
    fails = len([v for v in Results.values() if v is False])
    total = len(Results)
    if not aborted:
        summary = "Testing Finished. %s of %s passed. %s failed, %s errors!\n" % (passes, total, fails, _errors)
    else:
        summary = "Testing Failed. %s of %s passed. %s failed, %s errors, 1 fatal!\n" % (passes, total, fails, _errors)
    for k in Results:
        status = {True: "Pass", False: "Failed", None: "Not Run"}[Results[k]]
        summary += " - %s: %s\n" % (k.ljust(25), status)
    return summary


def start_testing():
    """Run before tests start!

       Opens the logfile and records the time at which the test started.
    """
    global _LOGFILE
    log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "%s \t Starting Regression Testing." % log_time
    _LOGFILE = open("_TEST_LOG.txt", "a")
    _LOGFILE.write("%s \t Starting Regression Testing.\n" % log_time)


def end_testing(Results, email=True, aborted=False):
    """Run when testing finishes.

       Closes the logfile, records the time testing finishes, manages the displaying
       of the results of the tests and sends the emails out.
        - 'Results' should be an OrderedDict of {TestName: bool} pairs.
    """
    global _LOGFILE, _tests_passed, _errors
    now = datetime.datetime.now()
    log_time = "[%s]" % now.strftime("%Y-%m-%d %H:%M:%S")
    summary = _generate_summary(Results, aborted)
    print ("%s \t " % log_time) + summary
    _LOGFILE.write(("%s \t " % log_time) + summary + "\n")
    _LOGFILE.close()
    if email:
        send_results(now.strftime("%d/%m/%Y at %H:%M"), summary)
