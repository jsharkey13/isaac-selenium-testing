import datetime
from ..emails.result_email import send_results


__all__ = ['INFO', 'PASS', 'ERROR', 'FATAL', 'log', 'stop', 'start_testing', 'end_testing']

_LOGFILE = None
INFO = "INFO"
PASS = "PASS"
ERROR = "ERROR"
FATAL = "FATAL"


_tests_passed = 0
_errors = 0

# Customise which log events are printed:
_OUTPUT_LOGGING_LEVELS = [INFO, PASS, ERROR, FATAL]


def stop(driver, message="Fatal Error! Stopping"):
    log(FATAL, message)
    raw_input("Paused (Press Enter to Quit)")
    driver.quit()
    end_testing()
    raise SystemExit


def log(level, message):
    """NOT THREAD SAFE!"""
    global _OUTPUT_LOGGING_LEVELS, FATAL, ERROR, _tests_passed, _errors
    if level == PASS:
        _tests_passed += 1
    if ((level == ERROR) or (level == FATAL)):
        _errors += 1
    if (level in _OUTPUT_LOGGING_LEVELS) or (level == FATAL):
        log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = "[%s]" % level.ljust(5)
        log_item = "%s %s\t- %s" % (log_time, level, message)
        print log_item
        _LOGFILE.write(log_item + "\n")
        _LOGFILE.flush()


def start_testing():
    global _LOGFILE
    log_time = "[%s]" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print "%s \t Starting Regression Testing." % log_time
    _LOGFILE = open("_TEST_LOG.txt", "a")
    _LOGFILE.write("%s \t Starting Regression Testing.\n" % log_time)


def end_testing():
    global _LOGFILE, _tests_passed, _errors
    now = datetime.datetime.now()
    log_time = "[%s]" % now.strftime("%Y-%m-%d %H:%M:%S")
    print "%s \t Testing Finished. %s passes, %s errors.\n\n" % (log_time, _tests_passed, _errors)
    _LOGFILE.write("%s \t Testing Finished. %s passes, %s errors.\n\n\n" % (log_time, _tests_passed, _errors))
    _LOGFILE.close()
    send_results(now.strftime("%d/%m/%Y at %H:%M"))
