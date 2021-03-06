# Isaac Selenium Testing
Testing Isaac Physics using Selenium WebDriver.

#### Running the code
Right now, there are no command line flags or runtime parameters. The code can be run using `python selenium_tester.py` and it will output the results to the directory `./testing/test_[run-date]` and stdout. The `./testing` directory must be created by hand before running any tests, since it needs to contain the `TestUsers.pickle` file containing the login info for the test accounts (produce this yourself or ask for a copy).

If you want to run tests locally and use Chrome, the ChromeDriver executable will also need to go in the `./testing` directory. An appropriate copy can be obtained from http://chromedriver.storage.googleapis.com/index.html, where the latest tested version is `2.30`.

If you want to run tests locally and use Firefox, the GeckoDriver executable will also need to go in the `./testing` directory. An appropriate copy can be obtained from https://github.com/mozilla/geckodriver/releases, where the latest tested version is `0.17.0`. Then uncomment [Line 59](/selenium_tester.py#L59) and comment out [Line 60](/selenium_tester.py#L60) and run as usual.

If you want the code to send emails, edit [Line 9](/isaactest/emails/result_email.py#L9) of the `./isaactest/emails/result_email.py` file to contain a list of appropriate email addresses, and remove the `emails=False` section of [Line 80](/selenium_tester.py#L80) of `selenium_tester.py`.

#### Adding Tests
To add more tests, see the [wiki page](https://github.com/jsharkey13/isaac-selenium-testing/wiki/Adding-New-Tests).

#### Dependencies
[Selenium WebDriver](http://www.seleniumhq.org/projects/webdriver/) is a required dependency; the code was developed using `Version 3.4` and this or a more up-to-date version may be required for some tests. The Python module for Selenium is what this project uses; install it using `pip install selenium`, provided that `pip` is also installed.

[Firefox](https://www.mozilla.org/en-GB/firefox/new/) or [Chrome](https://www.google.com/chrome/browser/desktop/) are obviously prerequisites. See above for information regarding the drivers, which are required to control both browsers.

[Vagrant](https://www.vagrantup.com/) is an optional dependency to allow headless testing on a Linux virtual machine. Once installed and on the path, run `vagrant up` in the root directory of the project and the [Vagrantfile](/Vagrantfile) and [setup.sh](/setup.sh) files will do the rest. Then type `vagrant ssh` to connect to the machine and run the Python commands from the `/isaac-selenium-testing/` directory.

To run headlessly [Xvfb](http://www.x.org/archive/X11R7.6/doc/man/man1/Xvfb.1.xhtml) is required, as is [Pyvirtualdisplay](https://github.com/ponty/PyVirtualDisplay). These are installed automatically by the `setup.sh` file for the Vagrant machine.
