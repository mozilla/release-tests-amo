import os

import pytest


# Window resolutions
DESKTOP = (1920, 1080)


@pytest.fixture(scope="session")
def base_url(base_url, variables):
    return variables['base_url']


@pytest.fixture(scope="session")
def sensitive_url(request, base_url):
    # Override sensitive url check
    return False


@pytest.fixture
def firefox_options(firefox_options):
    """Firefox options.

    These options configure firefox to allow for addon installation,
    as well as allowing it to run headless.

    'extensions.install.requireBuiltInCerts', False: This allows extensions to
        be installed with a self-signed certificate.
    'xpinstall.signatures.required', False: This allows an extension to be
        installed without a certificate.
    'extensions.webapi.testing', True: This is needed for whitelisting
        mozAddonManager
    '-foreground': Firefox will run in the foreground with priority
    '-headless': Firefox will run headless

    """
    firefox_options.set_preference(
        'extensions.install.requireBuiltInCerts', False
    )
    firefox_options.set_preference('xpinstall.signatures.required', False)
    firefox_options.set_preference('xpinstall.signatures.dev-root', True)
    firefox_options.set_preference('extensions.webapi.testing', True)
    firefox_options.set_preference('ui.popup.disable_autohide', True)
    firefox_options.set_preference('devtools.console.stdout.content', True)
    firefox_options.add_argument('-headless')
    firefox_options.log.level = 'trace'
    return firefox_options


@pytest.fixture
def firefox_notifications(notifications):
    return notifications


@pytest.fixture(
    scope='function',
    params=[DESKTOP],
    ids=['Resolution: 1920x1080'],
)
def selenium(selenium, request):
    """Fixture to set a custom resolution for tests running on Desktop."""
    selenium.set_window_size(*request.param)
    return selenium


@pytest.fixture
def fxa_account(request):
    """Fxa account to use during tests that need to login.

    Returns the email and password of the fxa account set in Makefile-docker.

    """
    try:
        fxa_account.email = os.environ['UITEST_FXA_EMAIL']
        fxa_account.password = os.environ['UITEST_FXA_PASSWORD']
    except KeyError:
        if request.node.get_closest_marker('fxa_login'):
            pytest.skip(
                'Skipping test because no fxa account was found.'
                ' Are FXA_EMAIL and FXA_PASSWORD environment variables set?')
    return fxa_account
