# -*- coding: utf-8 -*-

# AwesomeTTS text-to-speech add-on for Anki
# Copyright (C) 2010-Present  Anki AwesomeTTS Development Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Entry point for AwesomeTTS add-on from Anki

Performs any migration tasks and then loads the 'awesometts' package.
"""

from sys import stderr

__all__ = []


if __name__ == "__main__":
    stderr.write(
        "AwesomeTTS is a text-to-speech add-on for Anki.\n"
        "It is not intended to be run directly.\n"
        "To learn more or download Anki, visit <https://apps.ankiweb.net>.\n"
    )
    exit(1)


# n.b. Import is intentionally placed down here so that Python processes it
# only if the module check above is not tripped.

import awesometts  # noqa, pylint:disable=wrong-import-position


# If a specific component of AwesomeTTS that you do not need is causing a
# problem (e.g. conflicting with another add-on), you can disable it here by
# prefixing it with a hash (#) sign and restarting Anki.

awesometts.browser_menus()     # mass generator and MP3 stripper
awesometts.cache_control()     # automatically clear the media cache regularly
awesometts.cards_button()      # on-the-fly templater helper in card view
awesometts.config_menu()       # provides access to configuration dialog
awesometts.editor_button()     # single audio clip generator button
awesometts.reviewer_hooks()    # on-the-fly playback/shortcuts, context menus
awesometts.sound_tag_delays()  # delayed playing of stored [sound]s in review
awesometts.temp_files()        # remove temporary files upon session exit
awesometts.update_checker()    # if enabled, runs the add-on update checker
awesometts.window_shortcuts()  # enable/update shortcuts for add-on windows
