import requests
import time
from ..utils.log import log, INFO, ERROR, PASS
from ..tests import TestWithDependency

__all__ = ["hsts_header"]


#####
# Test : Check a Strict Transport Security Header is Present
#####
@TestWithDependency("HSTS_HEADER")
def hsts_header(ISAAC_WEB, WAIT_DUR, **kwargs):
    """Test if responses from Isaac contain a Strict Transport Security Header.

        - 'ISAAC_WEB' is the string URL of the Isaac website to be tested.
    """
    time.sleep(WAIT_DUR)
    try:
        log(INFO, "Making direct HTTP request to '%s'" % ISAAC_WEB)
        response = requests.get(ISAAC_WEB)
        assert "Strict-Transport-Security" in response.headers, "No HSTS header present in response from '%s'!" % ISAAC_WEB
        hsts_header = response.headers["Strict-Transport-Security"]
        log(INFO, "HSTS header present in response: '%s'." % hsts_header)
        hsts_directives = [p.strip() for p in hsts_header.split(";")]
        n_hsts_directives = len(hsts_directives)
        assert n_hsts_directives == 3, "Expected 3 directives in header, found %s!" % n_hsts_directives

        assert any([d.startswith("max-age=") for d in hsts_directives]), "HSTS requires a max-age directive to be effective!"
        assert "includeSubDomains" in hsts_directives, "Expected 'includeSubdomains' directive: not found!"
        assert "preload" in hsts_directives, "Expected 'includeSubdomains' directive: not found!"
        log(INFO, "HSTS header contains all required directives.")

        max_age_directive = [d for d in hsts_directives if d.startswith("max-age=")][0]
        max_age = int(max_age_directive.replace("max-age=", ""))
        assert max_age > 60*60*24*365, "HSTS max-age should be greater than 1 year!"
        log(INFO, "HSTS header contains suitable max-age directive.")

        log(PASS, "Valid and sensible HSTS header found.")
        return True
    except AssertionError as e:
        log(ERROR, e.message)
        return False
    except IndexError:
        log(ERROR, "Can't access max-age directive; can't continue!")
        return False
    except ValueError:
        log(ERROR, "Malformed max-age directive!")
        return False
    except IOError:
        log(ERROR, "Cannot connect to '%s'; can't continue!" % ISAAC_WEB)
        return False
