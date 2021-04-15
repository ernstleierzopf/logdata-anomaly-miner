"""
This module defines an detector for event and value sequences.
The concept is based on STIDE which was first published by Forrest, S.,
Hofmeyr, S. A., Somayaji, A., & Longstaff, T. A. (1996, May). A sense of self
for unix processes. In Proceedings of the 1996 IEEE Symposium on Security and
Privacy (pp. 120-128). IEEE.
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

import time
import os
import logging

from aminer.AminerConfig import build_persistence_file_name, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class EventSequenceDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when new event or value sequences were found."""

    def __init__(self, aminer_config, anomaly_event_handlers, id_path_list=None, target_path_list=None, seq_len=3, allow_missing_id=False,
                 timeout=-1, persistence_id='Default', auto_include_flag=False, output_log_line=True, ignore_list=None,
                 constraint_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param id_path_list one or more paths that specify the trace of the sequence detection, i.e., incorrect sequences that are
        generated by interleaved events can be avoided when event sequence identifiers are available.
        @param seq_len the length of the sequences to be learned (larger lengths increase precision, but may overfit the data).
        @param allow_missing_id specifies whether log atoms without id path should be omitted (only if id path is set).
        @param timeout maximum allowed seconds between two entries of sequence; sequence is split in subsequences if exceeded.
        @param persistence_id name of persistency document.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param constrain_list list of paths that have to be present in the log atom to be analyzed.
        """
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id
        self.id_path_list = id_path_list
        self.allow_missing_id = allow_missing_id
        self.timeout = timeout
        if id_path_list is None:
            self.id_path_list = []
        self.constraint_list = constraint_list
        if self.constraint_list is None:
            self.constraint_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.seq_len = seq_len
        self.sequences = set()
        self.current_sequences = {}
        self.last_seen_times = {}
        self.log_total = 0
        self.log_success = 0
        self.log_learned = 0
        self.log_learned_sequences = []

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        parser_match = log_atom.parser_match
        self.log_total += 1

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return

        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in paths
            values = []
            all_values_none = True
            for path in self.target_path_list:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                if isinstance(match.match_object, bytes):
                    value = match.match_object.decode(AminerConfig.ENCODING)
                else:
                    value = str(match.match_object)
                if value is not None:
                    all_values_none = False
                values.append(value)
            if all_values_none is True:
                return
            log_event = tuple(values)

        # In case that id_path_list is set, use it to differentiate sequences by their id.
        # Otherwise, the empty tuple () is used as the only key of the current_sequences dict.
        id_tuple = ()
        for id_path in self.id_path_list:
            id_match = parser_match.get_match_dictionary().get(id_path)
            if id_match is None:
                if self.allow_missing_id is True:
                    # Insert placeholder for id_path that is not available
                    id_tuple += ('',)
                else:
                    # Omit log atom if one of the id paths is not found.
                    return
            else:
                if isinstance(match.match_object, bytes):
                    id_tuple += (id_match.match_object.decode(AminerConfig.ENCODING),)
                else:
                    id_tuple += (id_match.match_object,)

        # Create entry for the id_tuple in the current_sequences dict if it did not occur before.
        if id_tuple not in self.current_sequences:
            self.current_sequences[id_tuple] = ()

        # If too much time passed between two values, start a new sequence
        if self.timeout != -1:
            if id_tuple in self.last_seen_times and self.last_seen_times[id_tuple] is not None and \
                    log_atom.atom_time is not None and self.last_seen_times[id_tuple] + self.timeout < log_atom.atom_time:
                self.current_sequences[id_tuple] = ()
            self.last_seen_times[id_tuple] = log_atom.atom_time

        # If the sequence has not reached its full length, append the newest element and stop.
        # Otherwise, the current sequence is used as a queue, where the oldest entry is removed.
        if len(self.current_sequences[id_tuple]) < self.seq_len:
            self.current_sequences[id_tuple] += (log_event,)
            if len(self.current_sequences[id_tuple]) != self.seq_len:
                return
        else:
            self.current_sequences[id_tuple] = self.current_sequences[id_tuple][1:] + (log_event,)

        # Report anomalies if the current processed sequence never occurred before.
        if self.current_sequences[id_tuple] not in self.sequences:
            if self.auto_include_flag is True:
                self.sequences.add(self.current_sequences[id_tuple])
                self.log_learned += 1
                self.log_learned_sequences.append(self.current_sequences[id_tuple])
                if self.next_persist_time is None:
                    self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                        KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            if self.output_log_line:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix +
                                    data]
            else:
                sorted_log_lines = [data]
            if self.target_path_list is None or len(self.target_path_list) == 0:
                analysis_component = {'AffectedLogAtomPaths': self.current_sequences[id_tuple]}
            else:
                analysis_component = {'AffectedLogAtomPaths': self.target_path_list,
                                      'AffectedLogAtomValues': list(self.current_sequences[id_tuple])}
            if self.id_path_list is not None:
                analysis_component['AffectedIdValues'] = list(id_tuple)
            event_data = {'AnalysisComponent': analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New sequence detected', sorted_log_lines, event_data,
                                       log_atom, self)
        self.log_success += 1

    def get_time_trigger_class(self):  # skipcq: PYL-R0201
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        # Persisted data contains lists of sequences, i.e., [[<seq1_elem1>, <seq1_elem2>], [<seq2_elem1, ...], ...]
        # Thereby, sequence elements may be tuples, i.e., combinations of values, or paths that define events.
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for sequence in persistence_data:
                sequence_elem_tuple = []
                for sequence_elem in sequence:
                    sequence_elem_tuple.append(tuple(sequence_elem))
                self.sequences.add(tuple(sequence_elem_tuple))
            logging.getLogger(DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, self.sequences)
        self.next_persist_time = None
        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.constraint_list:
            self.constraint_list.append(event_data)
        return 'Allowlisted path %s.' % event_data

    def blocklist_event(self, event_type, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return 'Blocklisted path %s.' % event_data

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new sequences in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new sequences in the last 60"
                " minutes. Following new sequences were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned, str(self.log_learned_sequences))
        self.log_success = 0
        self.log_total = 0
        self.log_learned = 0
        self.log_learned_sequences = []
