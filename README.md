# Isaac Selenium Testing
Testing Isaac Physics using Selenium WebDriver.

#### Running the code
Right now, there are no command line flags or runtime parameters. The code can be run using `python selenium_tester.py` and it will output the results to the directory `./testing/test_[run-date]` and stdout. The `./testing` directory must be created by hand before running any tests, since it needs to contain the `TestUsers.pickle` file containing the login info for the test accounts (produce this yourself or ask for a copy).

If you want to run tests locally and use Chrome, the ChromeDriver executable will also need to go in the `./testing` directory. An appropriate copy can be obtained from http://chromedriver.storage.googleapis.com/index.html, where the latest tested version is `2.21`. Then uncomment [Line 56](https://github.com/jsharkey13/isaac-selenium-testing/blob/master/selenium_tester.py#L56) and comment out [Line 55](https://github.com/jsharkey13/isaac-selenium-testing/blob/master/selenium_tester.py#L55) and run as usual.

If you want the code to send emails, edit [Line 9](https://github.com/jsharkey13/isaac-selenium-testing/blob/master/isaactest/emails/result_email.py#L9) of the `./isaactest/emails/result_email.py` file to contain a list of appropriate email addresses, and remove the `emails=False` section of [Line 80](https://github.com/jsharkey13/isaac-selenium-testing/blob/master/selenium_tester.py#L80) of `selenium_tester.py`.

#### Adding Tests
To add more tests, see the [wiki page](https://github.com/jsharkey13/isaac-selenium-testing/wiki/Adding-New-Tests).

#### Dependencies
[Selenium WebDriver](http://www.seleniumhq.org/projects/webdriver/) is a required dependency; the code was developed using `Version 2.48.0`. The Python module for Selenium is what this project uses; install it using `pip install selenium`, provided that `pip` is also installed.
