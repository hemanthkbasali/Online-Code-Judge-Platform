"""CodeSentinel project package.

PyMySQL is optional at import time. If installed, it lets Django's MySQL backend
use PyMySQL as a MySQLdb-compatible adapter.
"""

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass
