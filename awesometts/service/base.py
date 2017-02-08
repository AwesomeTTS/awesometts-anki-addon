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
Base class for service implementations

Provides an abstract Service class that can be extended for implementing
TTS services for use with AwesomeTTS.
"""

import abc
import os
import shutil
import sys
import subprocess

__all__ = ['Service']


DEFAULT_UA = 'Mozilla/5.0'
DEFAULT_TIMEOUT = 15

PADDING = '\0' * 2**11


class Service(object):
    """
    Represents a TTS service, providing an interface for the framework
    to interact with the service (initialization, description, options,
    and running) in addition to helpers that concrete implementations
    can call into to fulfill the interface (e.g. CLI calls, downloading
    files from the Internet).

    Although not enforced by Python's abc module, concrete classes
    should also specify NAME and TRAITS constants, which the framework
    can use before initializing a service.

    Methods that concrete classes must implement will only be called
    when they are needed (i.e. they are lazily loaded). In addition,
    with the exception of the run() method, these methods will only be
    called once during a particular session (i.e. their results will be
    cached). The run() method will usually only be called one time for a
    particular set of arguments (because the media files it produces are
    retained on the file system).
    """

    __metaclass__ = abc.ABCMeta

    class TinyDownloadError(ValueError):
        """Raises when a download is too small."""

    __slots__ = [
        '_netops',      # number of network ops required by the last run
        '_lame_flags',  # callable to get flag string for LAME transcoder
        '_logger',      # logging interface with debug(), info(), etc.
        'normalize',    # callable for standardizing string values
        '_temp_dir',    # for temporary scratch space
        'ecosystem',    # get information about web API, user agent
    ]

    # when getting CLI output, try using these decodings, in this order
    CLI_DECODINGS = ['ascii', 'utf-8', 'latin-1']

    # where we can find the lame transcoder
    CLI_LAME = 'lame'

    # where we can find the mplayer binary
    CLI_MPLAYER = 'mplayer'

    # startup information for Windows to keep command window hidden
    CLI_SI = None

    # will be set to True if user is running Linux
    IS_LINUX = False

    # will be set to True if user is running Mac OS X
    IS_MACOSX = False

    # will be set to True if user is running Windows
    IS_WINDOWS = False

    # work-in-progress
    APPROX_MAPPER = {
        u'\u00c1': 'A', u'\u00c4': 'A', u'\u00c5': 'A', u'\u00c9': 'E',
        u'\u00cb': 'E', u'\u00cd': 'I', u'\u00d1': 'N', u'\u00d3': 'O',
        u'\u00d6': 'O', u'\u00da': 'U', u'\u00dc': 'U', u'\u00df': 'ss',
        u'\u00e1': 'a', u'\u00e4': 'a', u'\u00e5': 'a', u'\u00e9': 'e',
        u'\u00eb': 'e', u'\u00ed': 'i', u'\u00cf': 'I', u'\u00ef': 'i',
        u'\u0152': 'OE', u'\u0153': 'oe', u'\u00d8': 'O', u'\u00f8': 'o',
        u'\u00c7': 'C', u'\u00e7': 'c', u'\u00f1': 'n', u'\u00f3': 'o',
        u'\u00f6': 'o', u'\u00fa': 'u', u'\u00fc': 'u', u'\u2018': "'",
        u'\u2019': "'", u'\u201c': '"', u'\u201d': '"', u'\u212b': 'A',
    }

    SPLIT_PRIORITY = [
        ['.', '?', '!', u'\u3002'],
        [',', ';', ':', u'\u3001'],
        [' ', u'\u3000'],
        ['-', u'\u2027', u'\u30fb'],
    ]

    SPLIT_CHARACTERS = ''.join(
        symbol
        for symbols in SPLIT_PRIORITY
        for symbol in symbols
    )

    SPLIT_MINIMUM = 5

    # abstract; to be overridden by the concrete classes
    # e.g. NAME = "ABC Service API"
    NAME = None

    # abstract; to be overridden by the concrete classes
    # e.g. TRAITS = [Trait.INTERNET, Trait.TRANSCODING]
    TRAITS = None

    def __init__(self, temp_dir, lame_flags, normalize, logger, ecosystem):
        """
        Attempt to initialize the service, raising a exception if the
        service cannot be used. If the service needs to make any calls
        to determine its viability (e.g. check to see if voices are
        installed on the system), they should be made here.

        This method will be called the first time the user displays the
        list of services or the first time the framework encounters an
        on-the-fly TTS tag for the service.

        The temp_dir will be used as the base for paths that are needed
        only temporarily (e.g. temporary input files to feed services,
        temporary audio files that need to be transcoded to MP3).

        The lame_flags is a callable to retrieve a string of flags to be
        passed to LAME transcoder if the service needs to transcode
        between different audio file types.

        The logger object should have an interface like the one used by
        the standard library logging module, with debug(), info(), and
        so on, available.
        """

        assert self.NAME, "Please specify a NAME for the service"
        assert isinstance(self.TRAITS, list), \
            "Please specify a TRAITS list for the service"

        self._netops = None
        self._lame_flags = lame_flags
        self._logger = logger
        self.normalize = normalize
        self._temp_dir = temp_dir
        self.ecosystem = ecosystem

    @abc.abstractmethod
    def desc(self):
        """
        Return a human-readable description of this service.

        This method will be called the first time the user displays the
        service (e.g. as part of a panel).
        """

        return ""

    @abc.abstractmethod
    def options(self):
        """
        Return a list of settable options for this service, in the order
        that they should be presented to the user.

        This method will be called the first time the user displays the
        service (e.g. as part of a panel), or the first time a set of
        options must be built to call the service (e.g. encountering an
        on-the-fly TTS tag for the service).

        The list should follow a structure like this:

            return [
                dict(
                    key='voice',
                    label="Voice",
                    values=[
                        ('en-us', "American English"),
                        ('en-es', "American Spanish"),
                    ],
                    transform=lambda value: ''.join(
                        char
                        for char in value.strip().lower()
                        if char.isalpha() or char == '-'
                    ),
                ),

                dict(
                    key='speed',
                    label="Speed",
                    items=(150, 175, "wpm"),
                    transform=int,
                    default=175,
                ),
            ]

        Each dict must include 'key', 'label', and 'items'. A dict may
        include 'default', if there is one. An option without a given
        'default' will be considered to be required (e.g. when parsing
        on-the-fly TTS tags for the service).

        If specified, 'normalize' will be used to clean up user input
        before processing it.
        """

        return {}

    def modify(self, text):  # allows overriding, pylint:disable=no-self-use
        """
        Allows a service to modify the phrase before it is hashed for
        caching and before it is passed to run().
        """

        return text

    @abc.abstractmethod
    def run(self, text, options, path):
        """
        Run the service and generate a file at the given path using the
        text and selected options. The passed options will correspond
        with those returned by the options() method.

        A sample call might look like this:

            service.run(
                text="Hello world.",
                options={'voice': 'en-us', 'speed': 200},
                path='/home/user/Anki/addons/awesometts/cache/file.mp3',
            )

        All processing done within this function is allowed to block, as
        the caller is to have already taken care of threading if it is
        necessary to prevent locking of the UI.

        Additionally, it is expected that the caller has already checked
        to see if a temporary file already exists at the given path. If
        it does, the caller will use that file directly rather than
        calling into the run() method.

        If output cannot be written to the path, an exception should be
        raised so the caller knows why.
        """

    def cli_call(self, *args):
        """
        Executes a command line call for its side effects. May be passed
        as a single list or as multiple arguments.
        """

        self._cli_exec(
            subprocess.check_call,
            args,
            "for processing",
        )

    def cli_output(self, *args):
        """
        Executes a command line call to examine its output, returned as
        a list of lines. May be passed as a single list or as multiple
        arguments.
        """

        returned = self._cli_exec(
            subprocess.check_output,
            args,
            "to inspect stdout",
        )

        return self._cli_decode(returned)

    def cli_output_error(self, *args):
        """
        Like cli_output(), but lenient of errors. This means that not
        only does the return code not matter, but stderr will be
        included in the returned result.

        Technically, *most* any call that works with cli_output() will
        also work with cli_output_error() if the underlying CLI tool
        does not write to stderr, but cli_output_error() should be
        avoided unless using a CLI tool that you knowingly must read
        stderr for.
        """

        try:
            returned = self._cli_exec(
                subprocess.check_output,
                args,
                "to inspect stdout/stderr",
                redirect_stderr=True,
            )

        except subprocess.CalledProcessError as cpe:
            returned = cpe.output

        return self._cli_decode(returned)

    def _cli_decode(self, returned):
        """
        Given the raw bytestring from the CLI tool, try to decode it and
        return a usable string.
        """

        if not returned:
            raise EnvironmentError("Call returned no output")

        if not isinstance(returned, unicode):
            for encoding in self.CLI_DECODINGS:
                try:
                    returned = returned.decode(encoding)
                    self._logger.info("CLI decoding success w/ %s", encoding)
                    break
                except (LookupError, UnicodeError):
                    self._logger.warn("CLI decoding failed w/ %s", encoding)
            else:
                self._logger.error("All CLI decodings failed; forcing ASCII")
                returned = returned.decode('ascii', errors='ignore')

        returned = returned.strip()

        if not returned:
            raise EnvironmentError("Call returned whitespace")

        returned = returned.split('\n')

        self._logger.debug(
            "Received %d %s of output from call\n%s",
            len(returned),
            "lines" if len(returned) != 1 else "line",
            '\n'.join(["<<< " + line for line in returned]),
        )

        return returned

    def cli_transcode(self, input_path, output_path, require=None,
                      add_padding=False):
        """
        Runs the LAME transcoder to create a new MP3 file.

        Note that instead of writing the file immediately to the given
        output path, this method first writes it a temporary file and
        then moves it to the output path afterward. This works around a
        bug on Windows where a user with a non-ASCII username would have
        a non-ASCII output_path, causing an error when the path is sent
        via the CLI. However, because the temporary directory on Windows
        will be of the all-ASCII variety, we can send it through there
        first and then move it to its final home.

        If add_padding is True, then some additional null padding will
        be added onto the resulting MP3. This can be helpful to ensure
        that the generated MP3 will not be clipped by `mplayer`.
        """

        if not os.path.exists(input_path):
            raise RuntimeError(
                "The input file to transcode to an MP3 could not be found. "
                "Please report this problem if it persists."
            )

        if require and 'size_in' in require and \
           os.path.getsize(input_path) < require['size_in']:
            raise ValueError(
                "Input to transcoder was %d-byte stream; wanted %d+ bytes "
                "(the service might not have liked your input text)" % (
                    os.path.getsize(input_path),
                    require['size_in'],
                )
            )

        intermediate_path = self.path_temp('mp3')  # see note above

        try:
            self.cli_call(
                self.CLI_LAME,
                self._lame_flags().split(),
                input_path,
                intermediate_path,
            )

        except OSError as os_error:
            from errno import ENOENT
            if os_error.errno == ENOENT:
                raise OSError(
                    ENOENT,
                    "Unable to find lame to transcode the audio. "
                    "It might not have been installed.",
                )
            else:
                raise

        if not os.path.exists(intermediate_path):
            raise RuntimeError(
                "Transcoding the audio stream failed. Are the flags you "
                "specified for LAME (%s) okay?" % self._lame_flags()
            )

        if add_padding:
            self.util_pad(intermediate_path)

        shutil.move(intermediate_path, output_path)  # see note above

    def _cli_exec(self, callee, args, purpose, redirect_stderr=False):
        """
        Handles the underlying system call, logging, and exceptions when
        a call to one of the cli_xxx() methods is made.
        """

        args = [
            arg if isinstance(arg, basestring) else str(arg)
            for arg in self._flatten(args)
        ]

        self._logger.debug(
            "Calling %s binary with %s %s",
            args[0],
            args[1:] if len(args) > 1 else "no arguments",
            purpose,
        )

        return callee(
            args,
            stderr=subprocess.STDOUT if redirect_stderr else None,
            startupinfo=self.CLI_SI,
        )

    def cli_pipe(self, args, input_path, output_path, input_mode='r',
                 output_mode='wb'):
        """
        Takes the given input path, passes it to the specific program as
        stdin, and then pipes the stdout of the program to the other
        given path.
        """

        args = [arg if isinstance(arg, basestring) else str(arg)
                for arg in args]

        self._logger.debug("Piping %s into %s binary with %s then onto %s",
                           input_path, args[0],
                           args[1:] if len(args) > 1 else "no arguments",
                           output_path)

        with open(input_path, input_mode) as input_stream, \
                open(output_path, output_mode) as output_stream:
            subprocess.Popen(args, stdin=input_stream.fileno(),
                             stdout=output_stream.fileno()).communicate()

    def cli_background(self, *args):
        """
        Puts a CLI-based command in the background, terminating it once
        the session has ended.
        """

        args = [arg if isinstance(arg, basestring) else str(arg)
                for arg in self._flatten(args)]

        self._logger.debug("Spinning up %s binary w/ %s to run in background",
                           args[0],
                           args[1:] if len(args) > 1 else "no arguments")

        service = subprocess.Popen(args)

        import atexit
        atexit.register(service.terminate)

    def net_headers(self, url):
        """Returns the headers for a URL."""

        self._logger.debug("GET %s for headers", url)
        self._netops += 1

        from urllib2 import urlopen, Request
        return urlopen(
            Request(url=url, headers={'User-Agent': DEFAULT_UA}),
            timeout=DEFAULT_TIMEOUT,
        ).headers

    def net_stream(self, targets, require=None, method='GET',
                   awesome_ua=False, add_padding=False,
                   custom_quoter=None, custom_headers=None):
        """
        Returns the raw payload string from the specified target(s).
        If multiple targets are specified, their resulting payloads are
        glued together.

        Each "target" is a bare URL string or a tuple containing an
        address and a dict for what to tack onto the query string.

        Finally, a require dict may be passed to enforce a Content-Type
        using key 'mime' and/or a minimum payload size using key 'size'.
        If using multiple targets, these requirements apply to each
        response.

        The underlying library here already understands how to search
        the environment for proxy settings (e.g. HTTP_PROXY), so we do
        not need to do anything extra for that.

        If add_padding is True, then some additional null padding will
        be added onto the stream returned. This is helpful for some web
        services that sometimes return MP3s that `mplayer` clips early.
        """

        assert method in ['GET', 'POST'], "method must be GET or POST"
        from urllib2 import urlopen, Request, quote

        targets = targets if isinstance(targets, list) else [targets]
        targets = [
            (target, None) if isinstance(target, basestring)
            else (
                target[0],
                '&'.join(
                    '='.join([
                        key,
                        (
                            custom_quoter[key] if (custom_quoter and
                                                   key in custom_quoter)
                            else quote
                        )(
                            val.encode('utf-8') if isinstance(val, unicode)
                            else val if isinstance(val, str)
                            else str(val),
                            safe='',
                        ),
                    ])
                    for key, val in target[1].items()
                ),
            )
            for target in targets
        ]

        require = require or {}

        payloads = []

        for number, (url, params) in enumerate(targets, 1):
            desc = "web request" if len(targets) == 1 \
                else "web request (%d of %d)" % (number, len(targets))

            self._logger.debug("%s %s%s%s for %s", method, url,
                               "?" if params else "", params or "", desc)

            headers = {'User-Agent': (self.ecosystem.agent
                                      if awesome_ua else DEFAULT_UA)}
            if custom_headers:
                headers.update(custom_headers)

            self._netops += 1
            response = urlopen(
                Request(
                    url=('?'.join([url, params]) if params and method == 'GET'
                         else url),
                    headers=headers,
                ),
                data=params if params and method == 'POST' else None,
                timeout=DEFAULT_TIMEOUT,
            )

            if not response:
                raise IOError("No response for %s" % desc)

            if response.getcode() != 200:
                value_error = ValueError(
                    "Got %d status for %s" %
                    (response.getcode(), desc)
                )
                try:
                    value_error.payload = response.read()
                    response.close()
                except StandardError:
                    pass
                raise value_error

            if 'mime' in require and \
                    require['mime'] != format(response.info().
                                              gettype()).replace('/x-', '/'):
                value_error = ValueError(
                    "Request got %s Content-Type for %s; wanted %s" %
                    (response.info().gettype(), desc, require['mime'])
                )
                value_error.got_mime = response.info().gettype()
                value_error.wanted_mime = require['mime']
                raise value_error

            payload = response.read()
            response.close()

            if 'size' in require and len(payload) < require['size']:
                raise self.TinyDownloadError(
                    "Request got %d-byte stream for %s; wanted %d+ bytes" %
                    (len(payload), desc, require['size'])
                )

            payloads.append(payload)

        if add_padding:
            payloads.append(PADDING)
        return ''.join(payloads)

    def net_download(self, path, *args, **kwargs):
        """
        Downloads a file to the given path from the specified target(s).
        See net_stream() for information about available options.
        """

        payload = self.net_stream(*args, **kwargs)
        with open(path, 'wb') as response_output:
            response_output.write(payload)

    def net_dump(self, output_path, url):
        """
        Use `mplayer` to retrieve an audio stream and dump it to a raw
        wave audio file.

        Note that output_path must be a safe ASCII one (i.e. generated
        by path_temp()); this method does NOT have the non-ASCII home
        directory workaround like cli_transcode() does.
        """

        if url.startswith('http'):
            self._netops += 1

        try:
            self.cli_call(
                self.CLI_MPLAYER,
                '-benchmark',  # supposedly speeds up dump
                '-vc', 'null',
                '-vo', 'dummy' if self.IS_WINDOWS else 'null',
                '-ao', 'pcm:fast:file="%s"' % output_path,
                url,
            )

        except OSError as os_error:
            from errno import ENOENT
            if os_error.errno == ENOENT:
                raise OSError(ENOENT,
                              "Unable to find mplayer to dump audio stream. "
                              "It might not have been installed.")
            else:
                raise

        if not os.path.exists(output_path):
            raise RuntimeError("Dumping the audio stream w/ mplayer failed.")

    def net_count(self):
        """
        Returns the number of downloads the last run required. Intended
        for use by the router to query after a run.
        """

        return self._netops

    def net_reset(self):
        """
        Resets the download count back to zero. Intended for use by the
        router before a run.
        """

        self._netops = 0

    def path_temp(self, extension):
        """
        Returns a path using the given extension that may be used for
        writing out a temporary file.
        """

        from string import ascii_lowercase, digits
        alphanumerics = ascii_lowercase + digits

        from os.path import join
        from random import choice
        from time import time
        return join(
            self._temp_dir,
            '%x-%s.%s' % (
                int(time()),
                ''.join(choice(alphanumerics) for i in range(30)),
                extension,
            ),
        )

    def path_unlink(self, *args):
        """
        Attempts to remove the given file(s), ignoring any failures. May
        be passed as a single list or as multiple arguments.
        """

        from os import unlink
        for path in self._flatten(args):
            if path:
                try:
                    unlink(path)
                    self._logger.debug("Deleted %s from file system", path)

                except OSError:
                    self._logger.warn("Unable to delete %s", path)

    def path_workaround(self, text):
        """
        If running on Windows and the given text cannot be represented
        purely with ASCII characters, returns a path to a temporary
        text file that may be used to feed a service binary.

        Returns False otherwise.
        """

        if self.IS_WINDOWS:
            try:
                text.encode('ascii')

            except UnicodeError:
                return self.path_input(text)

        return False

    def path_input(self, text):
        """
        Returns a path to a file containing the given unicode text.
        """

        temporary_txt = self.path_temp('txt')

        from codecs import open as copen
        with copen(temporary_txt, mode='w', encoding='utf-8') as out:
            out.write(text)

        return temporary_txt

    def reg_hklm(self, key, name):
        """
        Attempts to retrieve a value within the local machine tree
        stored at the given key and value name.
        """

        self._logger.debug(
            "Reading %s at %s from the Windows registry",
            name,
            key,
        )

        import _winreg as wr  # for Windows only, pylint: disable=F0401
        with wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE) as hklm:
            with wr.OpenKey(hklm, key) as subkey:
                return wr.QueryValueEx(subkey, name)[0]

    def util_approx(self, text):
        """
        Given a unicode string, returns an ASCII string with diacritics
        stripped off.
        """

        return ''.join(self.APPROX_MAPPER.get(char, char)
                       for char in text).encode('ascii', 'ignore') \
               if isinstance(text, unicode) \
               else text

    def util_merge(self, input_files, output_file):
        """
        Given several input files, dumbly merge together into a single
        output file.
        """

        self._logger.debug("Merging %s into %s", input_files, output_file)
        with open(output_file, 'wb') as output_stream:
            for input_file in input_files:
                with open(input_file, 'rb') as input_stream:
                    output_stream.write(input_stream.read())

    def util_pad(self, path):
        """
        Add padding to a file already on the file system.
        """

        self._logger.debug("Adding padding onto %s", path)
        with open(path, 'ab') as output_stream:
            output_stream.write(PADDING)

    def util_split(self, text, limit):
        """
        Intelligently split a string into smaller bits based on the
        passed limit. This utility function can be helpful for services
        that have character limits. Returns a list of strings.
        """

        bits = []

        while len(text) > limit:
            for symbols in self.SPLIT_PRIORITY:
                offsets = [
                    offset
                    for offset in [
                        text.rfind(symbol, 0, limit)
                        for symbol in symbols
                    ]
                    if offset > self.SPLIT_MINIMUM
                ]

                if offsets:
                    offset = sorted(offsets).pop()
                    bits.append(text[:offset + 1].rstrip())
                    text = text[offset + 1:]
                    break

            else:  # force a mid-word break
                bits.append(text[:limit])
                text = text[limit:]

            text = text.lstrip(self.SPLIT_CHARACTERS)

        bits.append(text)

        if len(bits) > 1:
            self._logger.debug(
                "Input phrase split using %d-character limit:\n%s",
                limit,
                "\n".join(
                    '    #%d: "%s"' % (number, bit)
                    for number, bit in enumerate(bits, 1)
                ),
            )

        return bits

    @classmethod
    def _flatten(cls, iterable):
        """
        Given a potentially nested iterable, returns a flat iterable.
        """

        for item in iterable:
            if isinstance(item, list) or isinstance(item, tuple):
                for subitem in cls._flatten(item):
                    yield subitem

            else:
                yield item


# Reinitialize the CLI_LAME, CLI_SI, IS_WINDOWS, and IS_MACOSX constants
# on the base class, if necessary given the running operating system.

if subprocess.mswindows:
    Service.CLI_DECODINGS.append('mbcs')
    Service.CLI_LAME = 'lame.exe'
    Service.CLI_MPLAYER = 'mplayer.exe'
    Service.CLI_SI = subprocess.STARTUPINFO()
    Service.IS_WINDOWS = True

    try:
        Service.CLI_SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    except AttributeError:
        try:
            Service.CLI_SI.dwFlags |= (
                subprocess._subprocess.  # workaround, pylint:disable=W0212
                STARTF_USESHOWWINDOW
            )

        except AttributeError:
            pass

elif sys.platform.startswith('darwin'):
    Service.IS_MACOSX = True

elif sys.platform.startswith('linux'):
    Service.IS_LINUX = True
