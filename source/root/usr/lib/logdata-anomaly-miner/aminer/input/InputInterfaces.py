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
        is when end_of_stream_flag is set and stream_data not empty.
        """


class AtomHandlerInterface(metaclass=abc.ABCMeta):
    """This is the common interface of all handlers suitable for receiving log atoms."""

    output_event_handlers = None

    def __init__(self, mutable_default_args=None, learn_mode=None, stop_learning_time=None, stop_learning_no_anomaly_time=None,
                 stop_when_handled_flag=None, **kwargs):
        """Initialize the parameters of analysis components. See the classes of the analysis components for parameter descriptions."""
        allowed_kwargs = [
            "mutable_default_args", "aminer_config", "anomaly_event_handlers", "learn_mode", "persistence_id", "id_path_list",
            "stop_learning_time", "stop_learning_no_anomaly_time", "output_logline", "target_path_list", "constraint_list", "ignore_list",
            "allowlist_rules", "subhandler_list", "stop_when_handled_flag", "parsed_atom_handler_lookup_list",
            "default_parsed_atom_handler", "target_path", "parsed_atom_handler_dict", "allow_missing_values_flag",
            "tuple_transformation_function", "prob_thresh", "skip_repetitions", "max_hypotheses", "hypothesis_max_delta_time",
            "generation_probability", "generation_factor", "max_observations", "p0", "alpha", "candidates_size",
            "hypotheses_eval_delta_time", "delta_time_to_discard_hypothesis", "check_rules_flag", "window_size", "scoring_path_list",
            "num_windows", "confidence_factor", "empty_window_warnings", "early_exceeding_anomaly_output", "set_lower_limit",
            "set_upper_limit", "local_maximum_threshold", "seq_len", "allow_missing_id", "timeout", "allowed_id_tuples", "min_num_vals",
            "max_num_vals", "save_values", "track_time_for_tsa", "waiting_time", "num_sections_waiting_time", "histogram_definitions",
            "report_interval", "reset_after_report_flag", "bin_definition", "target_value_list", "timestamp_path", "min_bin_elements",
            "min_bin_time", "debug_mode", "stream", "separator", "missing_value_string", "num_log_lines_solidify_matrix",
            "time_output_threshold", "anomaly_threshold", "default_interval", "realert_interval", "combine_values", "min_allowed_time_diff",
            "target_label_list", "split_reports_flag", "event_type_detector", "num_init", "force_period_length", "set_period_length",
            "alpha_bt", "num_results_bt", "num_min_time_history", "num_max_time_history", "num_periods_tsa_ini", "time_period_length",
            "max_time_diff", "num_reduce_time_list", "min_anomaly_score", "min_variance", "parallel_check_count",
            "record_count_before_event", "use_path_match", "use_value_match", "min_rule_attributes", "max_rule_attributes", "ruleset",
            "exit_on_error_flag", "acf_pause_interval_percentage", "acf_auto_pause_interval", "acf_auto_pause_interval_num_min",
            "build_sum_over_values", "num_division_time_step", "acf_threshold", "round_time_interval_threshold",
            "min_log_lines_per_time_step", "num_update", "disc_div_thres", "num_steps_create_new_rules", "num_upd_until_validation",
            "num_end_learning_phase", "check_cor_thres", "check_cor_prob_thres", "check_cor_num_thres", "min_values_cors_thres",
            "new_vals_alarm_thres", "num_bt", "used_homogeneity_test", "alpha_chisquare_test", "max_dist_rule_distr", "used_presel_meth",
            "intersect_presel_meth", "percentage_random_cors", "match_disc_vals_sim_tresh", "exclude_due_distr_lower_limit",
            "match_disc_distr_threshold", "used_cor_meth", "used_validate_cor_meth", "validate_cor_cover_vals_thres",
            "validate_cor_distinct_thres", "used_gof_test", "gof_alpha", "s_gof_alpha", "s_gof_bt_alpha", "d_alpha", "d_bt_alpha",
            "div_thres", "sim_thres", "indicator_thres", "num_update_unq", "num_s_gof_values", "num_s_gof_bt", "num_d_bt",
            "num_pause_discrete", "num_pause_others", "test_gof_int", "num_stop_update", "silence_output_without_confidence",
            "silence_output_except_indicator", "num_var_type_hist_ref", "num_update_var_type_hist_ref", "num_var_type_considered_ind",
            "num_stat_stop_update", "num_updates_until_var_reduction", "var_reduction_thres", "num_skipped_ind_for_weights",
            "num_ind_for_weights", "used_multinomial_test", "use_empiric_distr", "used_range_test", "range_alpha", "range_threshold",
            "num_reinit_range", "range_limits_factor", "dw_alpha", "save_statistics", "idf", "norm", "add_normal", "check_empty_windows",
            "unique_path_list"
        ]
        self.log_success = 0
        self.log_total = 0
        self.persistence_id = None  # persistence_id is always needed.
        for argument, value in list(locals().items())[1:-1]:  # skip self parameter and kwargs
            if value is not None:
                setattr(self, argument, value)
        for argument, value in kwargs.items():  # skip self parameter and kwargs
            if argument not in allowed_kwargs:
                msg = f"Argument {argument} is unknown. Consider changing it or adding it to the allowed_kwargs list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
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
                if hasattr(self, argument) and getattr(self, argument) is not None:
                    continue
                if argument.endswith("list"):
                    setattr(self, argument, [])
                elif argument.endswith("dict"):
                    setattr(self, argument, {})
                elif argument.endswith("set"):
                    setattr(self, argument, set())
                elif argument.endswith("tuple"):
                    setattr(self, argument, ())

        if hasattr(self, "subhandler_list"):
            if (not isinstance(self.subhandler_list, list)) or \
                    (not all(isinstance(handler, AtomHandlerInterface) for handler in self.subhandler_list)):
                msg = "Only subclasses of AtomHandlerInterface allowed in subhandler_list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            for handler_pos, handler_element in enumerate(self.subhandler_list):
                self.subhandler_list[handler_pos] = (handler_element, stop_when_handled_flag)
        if hasattr(self, "allowed_id_tuples"):
            if self.allowed_id_tuples is None:
                self.allowed_id_tuples = []
            else:
                self.allowed_id_tuples = [tuple(tuple_list) for tuple_list in self.allowed_id_tuples]

        if hasattr(self, "confidence_factor") and not 0 <= self.confidence_factor <= 1:
            logging.getLogger(DEBUG_LOG_NAME).warning('confidence_factor must be in the range [0,1]!')
            self.confidence_factor = 1

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
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in the last 60 minutes.", component_name, self.log_success,
                self.log_total)
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
