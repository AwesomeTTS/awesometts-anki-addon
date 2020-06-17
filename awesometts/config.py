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
Storage and management of add-on configuration
"""

# TODO Would it be possible to get these configuration options to sync with
#      AnkiWeb, e.g. by moving them into the collections database?
#      See also <https://anki.tenderapp.com/discussions/add-ons/8512>.

import sqlite3

__all__ = ['Config']


class Config(object):
    """
    Exposes a class whose instances have a dict-like interface for
    handling retrieving, caching, and serializing configuration stored
    in a given SQLite3 database table.

    As an alternative to the dict-like interface, attributes may be used
    for both reading and assigning, and kwargs may be used for update().
    """

    class _LoggableCursor(sqlite3.Cursor):  # no init, pylint: disable=W0232
        """
        Extends the SQLite3 Cursor class to support logging during
        execute() calls. Note that SQLite3 cursors are not initialized
        in the normal way, and a separate call to set_logger() is
        needed to correctly setup the object.
        """

        def set_logger(self, logger):
            """
            Initializes our reference to the target logger. This must be
            called on new instances.
            """

            self._logger = logger  # no init, pylint: disable=W0201

        def execute(self, sql, parameters=None):
            """
            Makes a debug() call and then proxies the call to parent.
            """

            if parameters:
                self._logger.debug("Executing '%s' with %s", sql, parameters)
                return sqlite3.Cursor.execute(self, sql, parameters)
            else:
                self._logger.debug("Executing '%s'", sql)
                return sqlite3.Cursor.execute(self, sql)

    __slots__ = [
        '_db',           # path to database, table name, normalize callable
        '_cols',         # map of official lookup names to column definitions
        '_cache',        # in-memory lookup of preferences
        '_logger',       # where to send logging messages
        '_events',       # map of lookup names to the callable(s) they trigger
    ]

    def __init__(self, db, cols, logger, events=None):
        """
        Given a database specification, list of column definitions,
        logger, and optional event list, loads the configuration state.

        The database specification should be a bundle, with:

            - path: full path to database
            - table: table name
            - normalize: sanitization function for normalizing columns

        The column definitions should be a list of tuples, each with:

            - 0th: SQLite3 column name
            - 1st: SQLite3 column affinity
            - 2nd: default Python value to use when introducing a new
                   configuration item or a value cannot be parsed
            - 3rd: mapping function from SQLite3 type to Python type
            - 4th: mapping function from Python type to SQLite3 type

        The logger is a reference to any class instance or module with a
        logger-like interface (e.g. debug(), info(), warn() callables).

        The event list should be a list of tuples, each with:

            - 0th: list of column names or single column name to trigger
            - 1th: callable when this value is loaded or updated
        """

        self._db = db

        self._cols = {
            self._db.normalize(col[0]): col
            for col in cols
        }
        self._logger = logger

        self._events = {}
        if events:
            for triggers, callback in events:
                self.bind(triggers, callback)

        self._cache = {}
        self._load()

    def bind(self, triggers, callback):
        """
        Registers a callable to be called with the current state of the
        configuration instance whenever a column in the triggers list is
        loaded or updated.

        The triggers may be a list of column names or a single string
        containing one column.
        """

        if isinstance(triggers, str):
            triggers = [triggers]

        for trigger in triggers:
            trigger = self._db.normalize(trigger)
            assert trigger in self._cols, "%s does not exist" % trigger

            try:
                self._events[trigger].append(callback)
            except KeyError:
                self._events[trigger] = [callback]

    def _load(self):
        """
        Reads the state of the SQLite3 database to populate our cache.
        If necessary, the database or table will be created with the
        default values. If they already exist, but a new column has been
        added, the already-existing table will be migrated to support
        the new column(s) using the default value(s).
        """

        # open database connection
        connection = sqlite3.connect(self._db.path, isolation_level=None)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor(self._LoggableCursor)
        cursor.set_logger(self._logger)

        # check for existence of the configuration table
        if len(cursor.execute('SELECT name FROM sqlite_master '
                              'WHERE type=? AND name=?',
                              ('table', self._db.table)).fetchall()):
            # detect existing columns
            existing_cols = [
                meta['name'].lower()
                for meta
                in cursor.execute('PRAGMA table_info(%s)' % self._db.table)
            ]

            # detect any new columns not present in database
            missing_cols = [
                col
                for col in self._cols.values()
                if col[0].lower() not in existing_cols
            ]

            if missing_cols:
                self._logger.info(
                    "Performing table update for %s",
                    ", ".join([col[0] for col in missing_cols]),
                )

                # insert any missing columns
                for col in missing_cols:
                    cursor.execute('ALTER TABLE %s ADD COLUMN %s %s' % (
                        self._db.table,
                        col[0],
                        col[1],
                    ))

                # set default values for newly-inserted columns
                cursor.execute(
                    'UPDATE %s SET %s' % (
                        self._db.table,
                        ', '.join(["%s=?" % col[0] for col in missing_cols]),
                    ),
                    tuple(col[4](col[2]) for col in missing_cols),
                )

            # populate in-memory store of the values from database
            row = cursor.execute('SELECT * FROM %s' % self._db.table) \
                .fetchone()
            for name, col in self._cols.items():
                # attempt to retrieve value; if it fails, use the default
                try:
                    self._cache[name] = col[3](row[col[0]])
                except ValueError:
                    self._cache[name] = col[2]

        else:
            all_cols = list(self._cols.values())

            self._logger.info("Creating new configuration table")

            # create the table
            cursor.execute('CREATE TABLE %s (%s)' % (
                self._db.table,
                ', '.join([
                    '%s %s' % (col[0], col[1])
                    for col in all_cols
                ]),
            ))

            # set the default values
            cursor.execute(
                'INSERT INTO %s VALUES(%s)' % (
                    self._db.table,
                    ', '.join(['?' for col in all_cols]),
                ),
                tuple(col[4](col[2]) for col in all_cols),
            )

            # populate in-memory store with the defaults we just inserted
            for name, col in self._cols.items():
                self._cache[name] = col[2]

        # close database connection
        cursor.close()
        connection.close()

        # since this is the initial load, notify all registered event handlers
        unique_callbacks = set()
        for callbacks in list(self._events.values()):
            unique_callbacks.update(callbacks)
        for callback in unique_callbacks:
            callback(self)

    def get(self, name, default=None):
        """
        Retrieve the current value for the given named configuration
        option. If the name does not exist, default will be returned.
        """

        name = self._db.normalize(name)
        return self._cache[name] if name in self._cache else default

    def __getattr__(self, name):
        """
        Retrieve a configuration value using the config.xxx syntax,
        raising an AttributeError if the name does not exist.
        """

        try:
            return self[name]
        except KeyError:
            raise AttributeError("'%s' is not a supported name" % name)

    def __getitem__(self, name):
        """
        Retrieve a configuration value using the config['xxx'] syntax,
        raising a KeyError if the name does not exist.
        """

        return self._cache[self._db.normalize(name)]

    def update(self, *updates_dict, **kw_updates):
        """
        Updates the value(s) of the given configuration option(s) passed
        as a dict, and persists those values back to the database.

        Raises KeyError if any key is not a supported name.
        """

        assert (
            bool(len(kw_updates)) !=  # xor
            bool(len(updates_dict) == 1 and isinstance(updates_dict[0], dict))
        ), "Must call update() with a dict or kwargs-style arguments"

        updates = kw_updates or updates_dict[0]

        # remap dict into a list of (name, col, new value)-tuples
        updates = [
            (name, self._cols[name], value)
            for name, value
            in [
                (self._db.normalize(unnormalized_name), value)
                for unnormalized_name, value
                in updates.items()
            ]
            if value != self._cache[name]  # filter out unchanged values
        ]

        # return if no updates
        if not updates:
            return

        # update in-memory store of the values and notify callback handlers
        unique_callbacks = set()
        for name, col, value in updates:
            self._cache[name] = value
            if name in self._events:
                unique_callbacks.update(self._events[name])
        for callback in unique_callbacks:
            callback(self)

        # open database connection
        connection = sqlite3.connect(self._db.path, isolation_level=None)
        cursor = connection.cursor(self._LoggableCursor)
        cursor.set_logger(self._logger)

        # persist to SQLite3 database
        cursor.execute(
            'UPDATE %s SET %s' % (
                self._db.table,
                ', '.join([
                    "%s=?" % col[0]
                    for name, col, value in updates
                ]),
            ),
            tuple(
                col[4](value)
                for name, col, value in updates
            ),
        )

        # close database connection
        cursor.close()
        connection.close()

    def __setattr__(self, name, value):
        """
        Handled the same as for update(), but with a single name using
        the config.xxx = yyy syntax.

        Raises KeyError if any key is not a supported name.
        """

        if name not in self.__slots__:
            name = self._db.normalize(name)
            if name in self._cols:
                self.update({name: value})
                return

        object.__setattr__(self, name, value)

    def __setitem__(self, name, value):
        """
        Handled the same as for update(), but with a single name using
        the config['xxx'] = yyy syntax.

        Raises KeyError if any key is not a supported name.
        """

        self.update({name: value})
