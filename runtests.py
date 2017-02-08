import os
import sys
import unittest

import django
from django.conf import settings
from django.test.utils import get_runner

from test import *

if __name__ == '__main__':
    os.environ['DJANG_SETTINGS_MODULE'] = 'googlesheetsrestbackend.django_host.settings'
    django.setup()
    test_runner = get_runner(settings)()
    failures = test_runner.run_tests(['googlesheetsrestbackend.django_host.test'])
    if bool(failures):
        sys.exit(bool(failures))
    unittest.main()
