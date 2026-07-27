import os
import sys


def _resource_path(*relative_parts):
    """Resolve a bundled resource path, whether running from source or from a PyInstaller-frozen executable."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *relative_parts)


with open(_resource_path('template', 'changelog.md'), 'r', encoding='UTF-8') as _template_file:
    template = _template_file.read()
