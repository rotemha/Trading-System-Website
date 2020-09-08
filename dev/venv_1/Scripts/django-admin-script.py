#!C:\Code\School\SADNA\Workshop-On-Software-Engineering-Project-2019\dev\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'django==2.2.2','console_scripts','django-admin'
__requires__ = 'django==2.2.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('django==2.2.2', 'console_scripts', 'django-admin')()
    )
