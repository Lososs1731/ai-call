# database/__init__.py - BEZPEČNÉ IMPORTY
"""
Database package
"""

# Import s error handling
try:
    from .cold_calling_db import ColdCallingDB
except ImportError as e:
    print(f"⚠️  ColdCallingDB import error: {e}")
    ColdCallingDB = None

try:
    from .admin_db import AdminDB
except ImportError as e:
    print(f"⚠️  AdminDB import error: {e}")
    AdminDB = None

try:
    from .call_analytics import CallAnalytics
except ImportError as e:
    print(f"⚠️  CallAnalytics import error: {e}")
    CallAnalytics = None

# CallDB je OPTIONAL
try:
    from .call_db import CallDB
except ImportError:
    CallDB = None
    # Toto je OK - CallDB není nutná

__all__ = ['ColdCallingDB', 'AdminDB', 'CallAnalytics', 'CallDB']