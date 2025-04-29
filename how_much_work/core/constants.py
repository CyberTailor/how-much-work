# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
All important constants in one place.
"""

#: Application package name.
PACKAGE = "how-much-work"

#: Application version.
VERSION = "0.0.1"

#: Application homepage.
HOMEPAGE = "https://how-much-work.sysrq.in"

#: Application affiliation.
ENTITY = "sysrq.in"

#: Application's User-agent header.
USER_AGENT = f"Mozilla/5.0 (compatible; {PACKAGE}/{VERSION}; +{HOMEPAGE})"

#: Entry point for package registry plugins.
REGISTRY_PLUGINS_ENTRY_POINT = "how_much_work.plugins.registry_v1"
