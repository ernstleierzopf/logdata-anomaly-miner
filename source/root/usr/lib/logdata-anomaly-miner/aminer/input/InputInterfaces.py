"""
This file contains interface definition useful implemented by classes in this directory and for use from code outside this directory.
All classes are defined in separate files, only the namespace references are added here to simplify the code.

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
import abc
import time
import logging
from aminer.AminerConfig import STAT_LOG_NAME, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD
from aminer import AminerConfig


class AtomizerFactory(metaclass=abc.ABCMeta):
    """
    This is the common interface of all factories to create atomizers for new data sources.
    These atomizers are integrated into the downstream processing pipeline.
    """

    @abc.abstractmethod
    def get_atomizer_for_resource(self, resource_name):
        """
        Get an atomizer for a given resource.
        @return a StreamAtomizer object
        """


class StreamAtomizer(metaclass=abc.ABCMeta):
    """
    This is the common interface of all binary stream atomizers.
    Atomizers in general should be good detecting and reporting malformed atoms but continue to function by attempting error correction or
    resynchronization with the stream after the bad atom. This type of atomizer also signals a stream source when the stream data cannot be
    handled at the moment to throttle reading  of the underlying stream.
    """

    @abc.abstractmethod
    def consume_data(self, stream_data, end_of_stream_flag=False):
        """
        Consume data from the underlying stream for atomizing. Data should only be consumed after splitting of an atom.
        The caller has to keep unconsumed data till the next invocation.
        @param stream_data the data offered to be consumed or zero length data when endOfStreamFlag is True (see below).
        @param end_of_stream_flag this flag is used to indicate, that the streamData offered is the last from the input stream.
        If the streamData does not form a complete atom, no rollover is expected or rollover would have honoured the atom boundaries,
        then the StreamAtomizer should treat that as an error. With rollover, consuming of the stream end data will signal the
        invoker to continue with data from next stream. When end of stream was reached but invoker has no streamData to send,
        it will invoke this method with zero-length data, which has to be consumed with a zero-length reply.
        @return the number of consumed bytes, 0 if the atomizer would need more data for a complete atom or -1 when no data was
        consumed at the moment but data might be consumed later on. The only situation where 0 is not an allowed return value
        is when endOfStreamFlag is set and streamData not empty.
        """


class AtomHandlerInterface(metaclass=abc.ABCMeta):
    """This is the common interface of all handlers suitable for receiving log atoms."""

    log_success = 0
    log_total = 0
    output_event_handlers = None

    def __init__(
            self, mutable_default_args=None, aminer_config=None, anomaly_event_handlers=None, learn_mode=None, persistence_id=None,
            id_path_list=None, stop_learning_time=None, stop_learning_no_anomaly_time=None, output_logline=None, target_path_list=None,
            constraint_list=None, ignore_list=None, allowlist_rules=None, subhandler_list=None, stop_when_handled_flag=None,
            parsed_atom_handler_lookup_list=None, default_parsed_atom_handler=None, path=None, parsed_atom_handler_dict=None
    ):
        """
        Initialize the parameters of analysis components.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param id_path_list specifies group identifiers for which data should be learned/analyzed.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths
        are considered for value range generation.
        @param persistence_id name of persistence file.
        @param learn_mode specifies whether value ranges should be extended when values outside of ranges are observed.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        @param allowlist_rules list of rules executed until the first rule matches.
        @param subhandler_list a list of objects implementing the AtomHandlerInterface which are run until the end, if
               stop_when_handled_flag is False or until an atom handler can handle the log atom.
        @param stop_when_handled_flag True, if the atom handler processing should stop after successfully receiving the log atom.
        @param parsed_atom_handler_lookup_list contains tuples with search path string and handler. When the handler is None,
        the filter will just drop a received atom without forwarding.
        @param default_parsed_atom_handler invoke this handler when no handler was found for given match path or do not invoke any
        handler when None.
        @param path the path to be analyzed in the parser match of the log atom.
        @param parsed_atom_handler_dict a dictionary of match value to atom handler.
        @param default_parsed_atom_handler invoke this default handler when no value handler was found or do not invoke any handler
        when None.
        """
        self.persistence_id = None  # persistence_id is always needed.
        for argument, value in list(locals().items())[1:]:  # skip self parameter
            if value is not None:
                setattr(self, argument, value)

        if learn_mode is False and (stop_learning_time is not None or stop_learning_no_anomaly_time is not None):
            msg = "It is not possible to use the stop_learning_time or stop_learning_no_anomaly_time when the learn_mode is False."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if stop_learning_time is not None and stop_learning_no_anomaly_time is not None:
            msg = "stop_learning_time is mutually exclusive to stop_learning_no_anomaly_time. Only one of these attributes may be used."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if not isinstance(stop_learning_time, (type(None), int)):
            msg = "stop_learning_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not isinstance(stop_learning_no_anomaly_time, (type(None), int)):
            msg = "stop_learning_no_anomaly_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)

        self.stop_learning_timestamp = None
        if stop_learning_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_time
        self.stop_learning_no_anomaly_time = stop_learning_no_anomaly_time
        if stop_learning_no_anomaly_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_no_anomaly_time

        if hasattr(self, "aminer_config"):
            self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        if mutable_default_args is not None:
            for argument in mutable_default_args:
                if hasattr(self, argument):
                    continue
                if "list" in argument:
                    setattr(self, argument, [])
                elif "dict" in argument:
                    setattr(self, argument, {})

        if hasattr(self, "subhandler_list"):
            if (not isinstance(self.subhandler_list, list)) or \
                    (not all(isinstance(handler, AtomHandlerInterface) for handler in self.subhandler_list)):
                msg = "Only subclasses of AtomHandlerInterface allowed in subhandler_list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            self.subhandler_list = [None] * len(subhandler_list)
            for handler_pos, handler_element in enumerate(subhandler_list):
                self.subhandler_list[handler_pos] = (handler_element, stop_when_handled_flag)

    @abc.abstractmethod
    def receive_atom(self, log_atom):
        """
        Receive a log atom from a source.
        @param log_atom binary raw atom data
        @return True if this handler was really able to handle and process the atom. Depending on this information, the caller
        may decide if it makes sense passing the atom also to other handlers or to retry later. This behaviour has to be documented
        at each source implementation sending LogAtoms.
        """

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL > 0:
            logging.getLogger(STAT_LOG_NAME).info("'%s' processed %d out of %d log atoms successfully in the last 60"
                                                  " minutes.", component_name, self.log_success, self.log_total)
        self.log_success = 0
        self.log_total = 0


class LogDataResource(metaclass=abc.ABCMeta):
    """
    This is the superinterface of each logdata resource monitored by aminer.
    The interface is designed in a way, that instances of same subclass can be used both on aminer parent process side for keeping track of
    the resources and forwarding the file descriptors to the child, but also on child side for the same purpose. The only difference is,
    that on child side, the stream reading and read continuation features are used also. After creation on child side, this is the sole
    place for reading and closing the streams. An external process may use the file descriptor only to wait for input via select.
    """

    @abc.abstractmethod
    def __init__(self, log_resource_name, log_stream_fd, default_buffer_size=1 << 16, repositioning_data=None):
        """
        Create a new LogDataResource. Object creation must not touch the logStreamFd or read any data, unless repositioning_data  was given.
        In the later case, the stream has to support seek operation to reread data.
        @param log_resource_name the unique encoded name of this source as byte array.
        @param log_stream_fd the stream for reading the resource or -1 if not yet opened.
        @param repositioning_data if not None, attemt to position the the stream using the given data.
        """

    @abc.abstractmethod
    def open(self, reopen_flag=False):
        """
        Open the given resource.
        @param reopen_flag when True, attempt to reopen the same resource and check if it differs from the previously opened one.
        @raise Exception if valid logStreamFd was already provided, is still open and reopenFlag is False.
        @raise OSError when opening failed with unexpected error.
        @return True if the resource was really opened or False if opening was not yet possible but should be attempted again.
        """

    @abc.abstractmethod
    def get_resource_name(self):
        """Get the name of this log resource."""

    @abc.abstractmethod
    def get_file_descriptor(self):
        """Get the file descriptor of this open resource."""

    @abc.abstractmethod
    def fill_buffer(self):
        """
        Fill the buffer data of this resource. The repositioning information is not updated, update_position() has to be used.
        @return the number of bytes read or -1 on error or end.
        """

    @abc.abstractmethod
    def update_position(self, length):
        """Update the positioning information and discard the buffer data afterwards."""

    @abc.abstractmethod
    def get_repositioning_data(self):
        """Get the data for repositioning the stream. The returned structure has to be JSON serializable."""

    @abc.abstractmethod
    def close(self):
        """Close this logdata resource. Data access methods will not work any more afterwards."""
