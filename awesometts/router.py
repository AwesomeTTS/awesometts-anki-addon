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
Dispatch management of available services
"""

import os
import os.path
from random import shuffle
import re
from http.client import IncompleteRead
from socket import error as SocketError
from time import time
from urllib.error import URLError

from PyQt5 import QtCore, QtWidgets

from .service import Trait as BaseTrait

__all__ = ['Router']


FAILURE_CACHE_SECS = 3600  # ignore/dump failures from cache after one hour

RE_MUSTACHE = re.compile(r'\{?\{\{(.+?)\}\}\}?')
RE_UNSAFE = re.compile(r'[^\w\s()-]', re.UNICODE)
RE_WHITESPACE = re.compile(r'[\0\s]+', re.UNICODE)

WINDOWS_RESERVED = ['com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7',
                    'com8', 'com9', 'con', 'lpt1', 'lpt2', 'lpt3', 'lpt4',
                    'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9', 'nul', 'prn']


def _prefixed(lines, prefix="!!! "):
    """Take incoming `lines` and prefix each line with `prefix`."""

    return "\n".join(
        prefix + line
        for line in (lines if isinstance(lines, list) else lines.split("\n"))
    )


class Router(object):
    """
    Allows the registration, lookup, and routing of concrete Service
    implementations.

    By having a routing-like object sit in-between the UI and the actual
    service code, Service implementations can be lazily loaded and their
    results can be cached, transparently to both sides.
    """

    Trait = BaseTrait

    class BusyError(RuntimeError):
        """Raised for requests for files that are already underway."""

    __slots__ = [
        '_busy',       # list of file paths that are in-progress
        '_cache_dir',  # path for writing cached media files
        '_config',     # user configuration (dict-like)
        '_failures',   # lookup of file paths that raised exceptions
        '_logger',     # logger-like interface with debug(), info(), etc.
        '_pool',       # instance of the _Pool class for managing threads
        '_services',   # bundle with dead services, aliases, avail, lookup
        '_temp_dir',   # path for writing human-readable filenames
    ]

    def __init__(self, services, cache_dir, temp_dir, logger, config):
        """
        The services should be a bundle with the following:

            - mappings (list of tuples): each with service ID, class
            - dead (dict): map of dead service IDs to an error message
            - aliases (list of tuples): alternate-to-official service IDs
            - normalize (callable): for service IDs and option keys
            - args (tuple): to be passed to Service constructors
            - kwargs (dict): to be passed to Service constructors
            - config (dict-like): user configuration lookup

        The cache directory should be one where media files get stored
        for a semi-permanent time.

        The logger object should have an interface like the one used by
        the standard library logging module, with debug(), info(), and
        so on, available.
        """

        services.aliases = {
            services.normalize(from_svc_id): services.normalize(to_svc_id)
            for from_svc_id, to_svc_id in services.aliases
        }

        services.avail = None

        services.lookup = {
            services.normalize(svc_id): {
                'class': svc_class,
                'name': svc_class.NAME or svc_id,
                'traits': svc_class.TRAITS or [],
            }
            for svc_id, svc_class in services.mappings
        }

        self._busy = []
        self._cache_dir = cache_dir
        self._config = config
        self._failures = {}
        self._logger = logger
        self._pool = _Pool(logger)
        self._services = services
        self._temp_dir = temp_dir

    def by_trait(self, trait):
        """
        Returns a list of service names that advertise the given trait.
        """

        return sorted([
            service['name']
            for service
            in self._services.lookup.values()
            if trait in service['traits']
        ], key=lambda name: name.lower())

    def has_trait(self, svc_id, trait):
        """
        Return True if the service (given by its string service ID or
        alias) has the passed trait (given by either the enum integer or
        string). Returns False if not.

        Returns None if the passed service does not exist.
        """

        svc_id = self._services.normalize(svc_id)
        if svc_id in self._services.aliases:
            svc_id = self._services.aliases[svc_id]

        if isinstance(trait, str):
            trait = getattr(BaseTrait, trait.upper())

        try:
            traits = self._services.lookup[svc_id]['traits']
        except KeyError:
            return None
        else:
            return trait in traits

    def get_unavailable_msg(self, svc_id):
        """
        Helper method that returns an error message when a particular
        service ID is not available (e.g. in the GUI).
        """

        return (self._services.dead[svc_id] if svc_id in self._services.dead
                else "'%s' service is not available." % svc_id)

    def get_services(self):
        """
        Returns available services.
        """

        if not self._services.avail:
            self._logger.debug("Building the list of services...")

            for service in self._services.lookup.values():
                self._load_service(service)

            self._services.avail = sorted([
                (svc_id, service['name'])
                for svc_id, service in self._services.lookup.items()
                if service['instance']
            ], key=lambda service: service[1].lower())

        return self._services.avail

    def get_desc(self, svc_id):
        """
        Returns the description associated with the service.
        """

        svc_id, service = self._fetch_service(svc_id)

        if 'desc' not in service:
            self._logger.debug(
                "Retrieving the description for %s",
                service['name'],
            )
            try:
                service['desc'] = service['instance'].desc()
            except Exception:  # catch all, pylint:disable=broad-except
                service['desc'] = svc_id + " service"

        return service['desc']

    def get_options(self, svc_id):
        """
        Returns a list of options that should be displayed for the
        service, with defaults highlighted.
        """

        svc_id, service = self._fetch_options_and_extras(svc_id)
        return service['options']

    def get_extras(self, svc_id):
        """
        Returns a list of "extra" options that the user might need
        to enter. Returns an empty list if none.
        """

        svc_id, service = self._fetch_options_and_extras(svc_id)
        return service['extras']

    def get_failure_count(self):
        """
        Returns the number of cached failures, after dumping any expired
        entries from the cache.
        """

        now = time()
        for path, (when, _) in self._failures.items():
            if now - when > FAILURE_CACHE_SECS:
                del self._failures[path]

        return len(self._failures)

    def forget_failures(self):
        """Delete the cache of remembered failures."""

        self._failures = {}

    def group(self, text, group, presets, callbacks,
              want_human=False, note=None):
        """
        Execute a group playback request using the passed group to be
        looked up using the passed presets.

        The callbacks follow the same rules as in the regular bare call
        method.

        If passed, want_human should be a template string that dictates
        how the caller wants the filename in the path to be formatted.
        Additionally, note may be passed to provide mustache values for
        the given template string.
        """

        self._call_assert_callbacks(callbacks)

        try:
            mode = group['mode']
            if mode not in ['ordered', 'random']:
                raise ValueError("Invalid group mode")

            presets = [presets.get(preset) for preset in group.get('presets')]
            if not presets:
                raise ValueError("Group has no presets defined")
            presets = [preset for preset in presets if preset]
            if not presets:
                raise ValueError("None of the group presets exist")

            presets = [dict(preset) for preset in presets]  # deep copy
            if mode == 'random':  # shuffle (but allow duplicates to weight)
                shuffle(presets)

        except Exception as exception:  # all, pylint:disable=broad-except
            if 'done' in callbacks:
                callbacks['done']()
            callbacks['fail'](exception, text)
            if 'then' in callbacks:
                callbacks['then']()

        else:
            def on_okay(path):
                """Executes caller callbacks with path."""
                if 'done' in callbacks:
                    callbacks['done']()
                callbacks['okay'](path)  # n.b. self() below handles want_human
                if 'then' in callbacks:
                    callbacks['then']()

            def on_fail(exception, text):
                """Go to next, unless playback already queued."""
                if isinstance(exception, self.BusyError):
                    if 'done' in callbacks:
                        callbacks['done']()
                    callbacks['fail'](exception, text)
                    if 'then' in callbacks:
                        callbacks['then']()
                else:
                    try_next()

            internal_callbacks = dict(okay=on_okay, fail=on_fail)
            if 'miss' in callbacks:
                internal_callbacks['miss'] = callbacks['miss']

            def try_next():
                """Pop next preset off and try playing text with it."""

                try:
                    preset = presets.pop(0)
                except IndexError:
                    if 'done' in callbacks:
                        callbacks['done']()
                    callbacks['fail'](IndexError(
                        "None of the presets in this group were able to play "
                        "the input text."
                    ), text)
                    if 'then' in callbacks:
                        callbacks['then']()
                else:
                    svc_id = preset.pop('service')
                    self(svc_id=svc_id, text=text, options=preset,
                         callbacks=internal_callbacks,
                         want_human=want_human, note=note)

            try_next()

    def __call__(self, svc_id, text, options, callbacks,
                 want_human=False, note=None, async_variable=True):
        """
        Given the service ID and associated options, pass the text into
        the service for processing.

        Note that it is the caller who has the context of how the text
        is being used (e.g. if it's from a database field, an on-the-fly
        tag, or from user input). Therefore, it is the responsibility of
        the caller to normalize the text before passing it. The service
        MAY apply additional normalization afterward, however, if it has
        implemented as modify() method.

        On the other hand, the passed service ID and options are indeed
        normalized, since this does not vary from context to context,
        and can be passed in directly by the caller.

        The callbacks parameter is a dict and contains the following:

            - 'done' (optional): called before the okay/fail callback
            - 'miss' (optional): called after done with a svc_id and download
               count if a cache miss occurred running the service
            - 'okay' (required): called with a path to the media file
            - 'fail' (required): called with an exception for validation
               errors or failed service calls occurs
            - 'then' (optional): called after the okay/fail callback

        Because it is asynchronous in nature, this method does not raise
        exceptions normally; they are passed to callbacks['fail'].

        "Exceptions" to that rule:

            - an AssertionError is raised if the caller failed to supply
              the required callbacks
            - an exception could be theoretically be raised if the
              threading subsystem failed
            - an exception raised in the callbacks themselves must be
              handled in the actual callback code; e.g. an exception in
              the 'done' handler will not cause the 'fail' handler to
              be called, or an exception in the 'fail' handler would
              not recall the 'fail' handler again

        If passed, want_human should be a template string that dictates
        how the caller wants the filename in the path to be formatted.
        Additionally, note may be passed to provide mustache values for
        the given template string.

        For synchronous testing (without the use of main event loop and
        process spawning) async_variable=False can be used.
        """

        self._call_assert_callbacks(callbacks)

        try:
            self._logger.debug("Call for '%s' w/ %s", svc_id, options)

            svc_id, service, options = self._validate_service(svc_id, options)
            if not text:
                raise ValueError("No speakable text is present")
            limit = 5000
            if len(text) > limit:
                raise ValueError("Text to speak is too long")
            text = service['instance'].modify(text)
            if not text:
                raise ValueError("Text not usable by " + service['class'].NAME)
            path = self._validate_path(svc_id, text, options)
            cache_hit = os.path.exists(path)

            self._logger.debug(
                "Parsed call to '%s' w/ %s and \"%s\" at %s (cache %s)",
                svc_id, options, text, path, "hit" if cache_hit else "miss",
            )

            # If we didn't get a cache hit, we have to call the real service,
            # so check to see if it has any extras defined, and if so, add
            # them to the options lookup for the service to use.
            #
            # n.b.: Even though the extras do not factor into an audio clip's
            # cache path, they MIGHT need to factor into the failure cache in
            # the future... This could be done by generating a special `fpath`
            # value during this loop, and use that with the `_failures` lookup
            # instead of the vanilla `path` (but this is a non-issue today,
            # because iSpeech is the only `extras` service, and it has caching
            # turned off, being that it is a paid-for key service

            if not cache_hit:
                for extra in self.get_extras(svc_id):
                    key = extra['key']
                    try:
                        options[key] = self._config['extras'][svc_id][key]
                        options[key] = options[key].strip()
                        if not options[key]:
                            raise KeyError
                    except KeyError:
                        if extra['required']:
                            raise KeyError(
                                "%s required to access %s" %
                                (extra['label'].rstrip(':'), svc_id)
                            )
                        else:
                            options[key] = None

        except Exception as exception:  # catch all, pylint:disable=W0703
            if 'done' in callbacks:
                callbacks['done']()
            callbacks['fail'](exception, text)
            if 'then' in callbacks:
                callbacks['then']()

            return

        def human(path):
            """Converts path into a human-readable one, if enabled."""

            if not want_human:
                return path

            if not os.path.isdir(self._temp_dir):
                os.mkdir(self._temp_dir)

            def substitute(match):
                """Perform variable substitution on filename."""

                key = match.group(1).strip()

                if key:
                    lower = key.lower()

                    if lower == 'service':
                        return svc_id
                    if lower == 'text':
                        return text
                    if lower == 'voice':
                        return options['voice'].lower()

                    try:
                        return note[key]  # exact field match
                    except:  # ignore error, pylint:disable=bare-except
                        pass

                    try:
                        for other_key in note.keys():
                            if other_key.strip().lower() == lower:
                                return note[other_key]  # fuzzy field match
                    except:  # ignore error, pylint:disable=bare-except
                        pass

                return ''  # invalid key / no such note field

            filename = RE_MUSTACHE.sub(substitute, want_human)
            filename = RE_UNSAFE.sub('', filename)
            filename = RE_WHITESPACE.sub(' ', filename).strip()
            if not filename or filename.lower() in WINDOWS_RESERVED:
                filename = 'AwesomeTTS Audio'
            else:
                filename = filename[0:90]  # accommodate NTFS path limits
            filename = 'ATTS ' + filename + '.mp3'

            from shutil import copyfile
            new_path = os.path.join(self._temp_dir, filename)
            copyfile(path, new_path)

            return new_path

        if cache_hit:
            if 'done' in callbacks:
                callbacks['done']()
            callbacks['okay'](human(path))
            if 'then' in callbacks:
                callbacks['then']()

        elif (path in self._failures and
              time() - self._failures[path][0] < FAILURE_CACHE_SECS):
            if 'done' in callbacks:
                callbacks['done']()
            callbacks['fail'](self._failures[path][1], text)
            if 'then' in callbacks:
                callbacks['then']()

        else:
            def on_error(exception):
                """
                For Internet-based services, cache errors. Certain
                exceptions are not cached, as they are usually network
                or connectivity errors.

                Afterward, pass exception to the fail handler.
                """

                if BaseTrait.INTERNET in service['class'].TRAITS and \
                   not isinstance(exception, IncompleteRead) and \
                   not isinstance(exception, SocketError) and \
                   not isinstance(exception, URLError):
                    self._failures[path] = time(), exception
                callbacks['fail'](exception, text)

            service['instance'].net_reset()
            self._busy.append(path)

            def completion_callback(exception, text="Not available by Router.__call__.completion_callback"):
                """Intermediate callback handler for all service calls."""

                self._busy.remove(path)

                if 'done' in callbacks:
                    callbacks['done']()

                if 'miss' in callbacks:
                    callbacks['miss'](svc_id, service['instance'].net_count())

                if exception:
                    on_error(exception)
                elif os.path.exists(path):
                    callbacks['okay'](human(path))
                else:
                    on_error(RuntimeError(
                        "The %s service did not successfully write out an "
                        "MP3." % service['name']
                    ))

                if 'then' in callbacks:
                    callbacks['then']()

            def task():
                service['instance'].run(text, options, path)

            if async_variable:
                def do_spawn():
                    """Call if ready to start a thread to run the service."""
                    self._pool.spawn(
                        task=task,
                        callback=completion_callback,
                    )
            else:
                callback_exception = None
                try:
                    task()
                except Exception as exception:
                    callback_exception = exception
                completion_callback(callback_exception)

            if hasattr(service['instance'], 'prerun'):
                def prerun_ok(result):
                    """Callback handler for successful prerun hook."""
                    options['prerun'] = result
                    do_spawn()

                def prerun_error(exception):
                    """Callback handler for unsuccessful prerun hook."""
                    self._logger.error("Asynchronous exception in prerun: %s",
                                       exception)
                    completion_callback(exception)

                try:
                    service['instance'].prerun(text, options, path,
                                               prerun_ok, prerun_error)
                except Exception as exception:  # all, pylint:disable=W0703
                    self._logger.error("Synchronous exception in prerun: %s",
                                       exception)
                    completion_callback(exception)
            else:
                do_spawn()

    def _call_assert_callbacks(self, callbacks):
        """Checks the callbacks argument for validity."""

        assert 'done' not in callbacks or callable(callbacks['done'])
        assert 'miss' not in callbacks or callable(callbacks['miss'])
        assert 'okay' in callbacks and callable(callbacks['okay'])
        assert 'fail' in callbacks and callable(callbacks['fail'])
        assert 'then' not in callbacks or callable(callbacks['then'])

    def _validate_service(self, svc_id, options):
        """
        Finds the given service ID, normalizes the text, and validates
        the options, returning the following:

            - 0th: normalized service ID
            - 1st: service lookup dict
            - 2nd: normalized text
            - 3rd: options, normalized and defaults filled in
            - 4th: cache path
        """

        svc_id, service = self._fetch_options_and_extras(svc_id)
        svc_options = service['options']
        svc_options_keys = [svc_option['key'] for svc_option in svc_options]

        options = {
            key: value
            for key, value in [
                (self._services.normalize(key), value)
                for key, value in options.items()
            ]
            if key in svc_options_keys
        }

        problems = self._validate_options(options, svc_options)
        if problems:
            raise ValueError(
                "Running the '%s' (%s) service failed: %s." %
                (svc_id, service['name'], "; ".join(problems))
            )

        return svc_id, service, options

    def _validate_options(self, options, svc_options):
        """
        Attempt to normalize and validate the passed options in-place,
        given the official svc_options.

        Returns a list of problems, if any.
        """

        problems = []

        for svc_option in svc_options:
            key = svc_option['key']

            if key in options:
                try:
                    # transform is inside try as it might throw a ValueError
                    transformed_value = svc_option['transform'](options[key])

                    if isinstance(svc_option['values'], tuple):
                        if transformed_value < svc_option['values'][0] or \
                           transformed_value > svc_option['values'][1]:
                            raise ValueError("outside of %d..%d" % (
                                svc_option['values'][0],
                                svc_option['values'][1],
                            ))

                    else:  # list of tuples
                        next(
                            True
                            for item in svc_option['values']
                            if item[0] == transformed_value
                        )

                    options[key] = transformed_value

                except ValueError as exception:
                    problems.append(
                        "invalid value '%s' for '%s' attribute (%s)" %
                        (options[key], key, exception)
                    )

                except StopIteration:
                    problems.append(
                        "'%s' is not an option for '%s' attribute (try %s)" %
                        (
                            options[key], key,
                            ", ".join(v[0] for v in svc_option['values']),
                        )
                    )

            elif 'default' in svc_option:
                options[key] = svc_option['default']

            else:
                problems.append("'%s' attribute is required" % key)

        self._logger.debug(
            "Validated and normalized '%s' with failure count of %d",
            "', '".join(svc_option['key'] for svc_option in svc_options),
            len(problems),
        )

        return problems

    def _validate_path(self, svc_id, text, options):
        """
        Given the service ID, its associated options, and the desired
        text, generate a cache path. If the file is already being
        processed, raise a BusyError.
        """

        path = self._path_cache(svc_id, text, options)
        if path in self._busy:
            raise self.BusyError(
                "The '%s' service is already busy processing %s." %
                (svc_id, path)
            )

        return path

    def _fetch_options_and_extras(self, svc_id):
        """
        Identifies the service by its ID, checks to see if the options
        list need construction, and then return back the normalized ID
        and service lookup dict.
        """

        svc_id, service = self._fetch_service(svc_id)

        if 'options' not in service:
            self._logger.debug(
                "Building the options list for %s",
                service['name'],
            )

            service['options'] = []

            for option in service['instance'].options():
                assert 'key' in option, "missing option key for %s" % svc_id
                assert self._services.normalize(option['key']) == \
                    option['key'], "bad %s key %s" % (svc_id, option['key'])
                assert option['key'] not in ['group', 'preset', 'service',
                                             'style'], \
                    option['key'] + " is reserved for use in TTS tags"
                assert 'label' in option, \
                    "missing %s label for %s" % (option['key'], svc_id)
                assert 'values' in option, \
                    "missing %s values for %s" % (option['key'], svc_id)
                assert isinstance(option['values'], list) or \
                    isinstance(option['values'], tuple) and \
                    len(option['values']) in range(2, 4), \
                    "%s values for %s should be list or 2-3-tuple" % \
                    (option['key'], svc_id)
                assert 'transform' in option, \
                    "missing %s transform for %s" % (option['key'], svc_id)

                if not option['label'].endswith(":"):
                    option['label'] += ":"

                if 'default' in option and \
                   isinstance(option['values'], list) and \
                   len(option['values']) > 1:
                    option['values'] = [
                        item if item[0] != option['default'] or item[1] == 'Default'
                        else (item[0], item[1] + " [default]")
                        for item in option['values']
                    ]

                service['options'].append(option)

        if 'extras' not in service:  # extras are like options, but universal
            service['extras'] = []

            if hasattr(service['instance'], 'extras'):
                self._logger.debug("Building the extras list for %s",
                                   service['name'])
                for extra in service['instance'].extras():
                    assert 'key' in extra, "missing extra key for %s" % svc_id
                    assert self._services.normalize(extra['key']) == \
                        extra['key'], "bad %s key %s" % (svc_id, extra['key'])
                    assert 'label' in extra, \
                        "missing %s label for %s" % (extra['key'], svc_id)

                    if 'required' not in extra:
                        extra['required'] = False
                    if not extra['label'].endswith(":"):
                        extra['label'] += ":"

                    service['extras'].append(extra)

        return svc_id, service

    def _fetch_service(self, svc_id):
        """
        Finds the service using the svc_id, normalizing it and using the
        aliases list, initializes if this is its first use, and returns
        the normalized svc_id and service lookup dict.

        Raises KeyError if a bad svc_id is passed.

        Raises EnvironmentError if a good svc_id is passed, but the
        given service is not available for this session.
        """

        svc_id = self._services.normalize(svc_id)
        if svc_id in self._services.aliases:
            svc_id = self._services.aliases[svc_id]

        try:
            service = self._services.lookup[svc_id]
        except KeyError:
            raise ValueError(
                self._services.dead[svc_id] if svc_id in self._services.dead
                else "There is no '%s' service" % svc_id
            )

        self._load_service(service)

        if not service['instance']:
            raise EnvironmentError(
                "The %s service is not currently available" %
                service['name']
            )

        return svc_id, service

    def _load_service(self, service):
        """
        Given a service lookup dict, tries to initialize the service if
        it is not already initialized. Exceptions are trapped and logged
        with the 'instance' then set to None. Successful initializations
        set the 'instance' to the resulting object.
        """

        if 'instance' in service:
            return

        self._logger.info("Initializing %s service...", service['name'])

        try:
            service['instance'] = service['class'](
                *self._services.args,
                **self._services.kwargs
            )

            self._logger.info("%s service initialized", service['name'])

        except Exception:  # catch all, pylint:disable=W0703
            service['instance'] = None  # flag this service as unavailable

            from traceback import format_exc
            self._logger.warn(
                "Initialization failed for %s service\n%s",
                service['name'], _prefixed(format_exc()),
            )

    def _path_cache(self, svc_id, text, options):
        """
        Returns a consistent cache path given the svc_id, text, and
        options. This can be used to repeat the same request yet reuse
        the same path.
        """

        hash_input = '/'.join([
            text,
            svc_id,
            ';'.join(
                '='.join([
                    key,
                    value if isinstance(value, str) else str(value),
                ])
                for key, value
                in sorted(options.items())
            )
        ])

        from hashlib import sha1

        hex_digest = sha1(
            hash_input.encode('utf-8') if isinstance(hash_input, str)
            else hash_input
        ).hexdigest().lower()

        assert len(hex_digest) == 40, "unexpected output from hash library"
        return os.path.join(
            self._cache_dir,
            '.'.join([
                '-'.join([
                    svc_id, hex_digest[:8], hex_digest[8:16],
                    hex_digest[16:24], hex_digest[24:32], hex_digest[32:],
                ]),
                'mp3',
            ]),
        )


class _Pool(QtWidgets.QWidget):
    """
    Managers a pool of worker threads to keep the UI responsive.
    """

    __slots__ = [
        '_current_id',  # the last/current worker ID in-use
        '_logger',      # for writing messages about threads
        '_threads',     # dict of IDs mapping workers and callbacks in Router
    ]

    def __init__(self, logger, *args, **kwargs):
        """
        Initialize my internal state (next ID and lookup pools for the
        callbacks and workers).
        """

        super(_Pool, self).__init__(*args, **kwargs)

        self._current_id = 0
        self._logger = logger
        self._threads = {}

    def spawn(self, task, callback):
        """
        Create a worker thread for the given task. When the thread
        completes, the callback will be called.
        """

        self._current_id += 1
        thread = self._threads[self._current_id] = {
            # keeping a reference to worker prevents garbage collection
            'callback': callback,
            'done': False,
            'worker': _Worker(self._current_id, task),
        }

        thread['worker'].tts_thread_done.connect(self._on_worker_signal)
        thread['worker'].tts_thread_raised.connect(self._on_worker_signal)
        thread['worker'].finished.connect(self._on_worker_finished)
        thread['worker'].start()

        self._logger.debug(
            "Spawned thread [%d]; pool=%s",
            self._current_id, self._threads,
        )

    def _on_worker_signal(self, thread_id, exception=None, stack_trace=None):
        """
        When the worker signals it's done with its task, execute the
        callback that was registered for it, passing on any exception.
        """

        if exception:
            message = str(exception)
            if not message:
                message = "No additional details available"

            self._logger.debug(
                "Exception from thread [%d] (%s); executing callback\n%s",

                thread_id, message,

                _prefixed(stack_trace)
                if isinstance(stack_trace, str)
                else "Stack trace unavailable",
            )

        else:
            self._logger.debug(
                "Completion from thread [%d]; executing callback",
                thread_id,
            )

        self._threads[thread_id]['callback'](exception)
        self._threads[thread_id]['done'] = True

    def _on_worker_finished(self):
        """
        When the worker is finished, which happens sometime briefly
        after it's done with its task, delete it from the thread pool if
        its callback has already executed.
        """

        thread_ids = [
            thread_id
            for thread_id, thread in self._threads.items()
            if thread['done'] and thread['worker'].isFinished()
        ]

        if not thread_ids:
            return

        for thread_id in thread_ids:
            del self._threads[thread_id]

        self._logger.debug(
            "Reaped thread%s %s; pool=%s",
            "s" if len(thread_ids) != 1 else "", thread_ids, self._threads,
        )


class _Worker(QtCore.QThread):
    """
    Generic worker for running processes in the background.
    """

    tts_thread_done = QtCore.pyqtSignal(int, name='awesomeTtsThreadDone')
    tts_thread_raised = QtCore.pyqtSignal(int, Exception, str, name='awesomeTtsThreadRaised')

    __slots__ = [
        '_thread_id',  # my thread ID; used to communicate back to main thread
        '_task',       # the task I will need to call when run
    ]

    def __init__(self, thread_id, task):
        """
        Save my worker ID and task.
        """

        super(_Worker, self).__init__()

        self._id = thread_id
        self._task = task

    def run(self):
        """
        Run my assigned task. If an exception is raised, pass it back to
        the main thread via the callback.
        """

        try:
            self._task()
        except Exception as exception:  # catch all, pylint:disable=W0703
            from traceback import format_exc
            self.tts_thread_raised.emit(self._id, exception, format_exc())
            return

        self.tts_thread_done.emit(self._id)
