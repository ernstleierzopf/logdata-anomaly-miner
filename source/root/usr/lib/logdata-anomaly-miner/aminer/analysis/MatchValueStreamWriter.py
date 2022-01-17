"""
This module defines a writer that forwards match information to a stream.

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

from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
import _io


class MatchValueStreamWriter(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class extracts values from a given match and writes them to a stream.
    This can be used to forward these values to another program (when stream is a wrapped network socket) or to a file for further analysis.
    A stream is used instead of a file descriptor to increase performance. To flush it from time to time, add the writer object also to the
    time trigger list.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, stream, match_value_path_list, separator_string, missing_value_string):
        """Initialize the writer."""
        self.stream = stream
        self.match_value_path_list = match_value_path_list
        self.separator_string = separator_string
        self.missing_value_string = missing_value_string

    def receive_atom(self, log_atom):
        """Forward match value information to the stream."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        add_sep_flag = False
        contains_data = False
        result = b''
        for path in self.match_value_path_list:
            if add_sep_flag:
                result += self.separator_string
            match = match_dict.get(path)
            if match is None:
                result += self.missing_value_string
            else:
                matches = []
                if isinstance(match, list):
                    matches = match
                else:
                    matches.append(match)
                for match in matches:
                    result += match.match_string + self.separator_string
                    contains_data = True
                if len(self.separator_string) > 0:
                    result = result[:-len(self.separator_string)]
            add_sep_flag = True
        if contains_data:
            if not isinstance(self.stream, _io.BytesIO):
                self.stream.write(result.decode('ascii', 'ignore'))
                self.stream.write('\n')
            else:
                self.stream.write(result)
                self.stream.write(b'\n')
            self.log_success += 1

    def do_timer(self, _trigger_time):
        """Flush the timer."""
        self.stream.flush()
        return 10

    def do_persist(self):
        """Flush the timer."""
        self.stream.flush()
