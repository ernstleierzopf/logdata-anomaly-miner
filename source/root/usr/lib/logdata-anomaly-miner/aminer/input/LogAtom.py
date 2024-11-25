"""This module defines a log atom.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.ParserMatch import ParserMatch


class LogAtom:
    """This class defines a log atom used for parsing."""
    idCounter = -1

    def __init__(self, raw_data, parser_match, atom_time, source):
        """Create a log atom from scratch."""
        if not isinstance(raw_data, bytes):
            msg = "raw_data must be of type bytes."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(raw_data) == 0:
            msg = "raw_data must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.raw_data = raw_data
        if parser_match is not None and not isinstance(parser_match, ParserMatch):
            msg = "parser_match must be of type ParserMatch."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.parser_match = parser_match
        if atom_time is not None and (not isinstance(atom_time, (int, float)) or isinstance(atom_time, bool)):
            msg = "atom_time must be of type integer or float."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.atom_time = atom_time
        self.source = source
        LogAtom.idCounter += 1
        self.log_line_identifier = LogAtom.idCounter

    def get_parser_match(self):
        """Get the parser match associated with this LogAtom.

        @return the match or None for (yet) unparsed LogAtoms.
        """
        return self.parser_match

    def set_timestamp(self, timestamp):
        """Update the default timestamp value associated with this LogAtom.

        The method can be called more than once to allow correction of
        fine-adjusting of timestamps by analysis filters after initial
        parsing procedure.
        """
        self.atom_time = timestamp

    def get_timestamp(self):
        """Get the default timestamp value for this LogAtom.

        @return the timestamp as number of seconds since 1970.
        """
        return self.atom_time

    def is_parsed(self):
        """Check if this atom is parsed by checking if parserMatch object is
        attached."""
        return self.parser_match is not None
