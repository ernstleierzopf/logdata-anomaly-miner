from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.analysis.VariableTypeDetector import VariableTypeDetector, convert_to_floats, consists_of_ints, consists_of_floats
from aminer.input import LogAtom
from aminer.parsing import ParserMatch, MatchElement
from unit.testutilities.ContinuousSampleGenerator import generate_sample
from unit.TestBase import TestBase

from collections import Counter
import time
import copy
import pickle
import random


class VariableTypeDetectorTest(TestBase):

    def test1convert_to_floats(self):
        """This unittest tests possible inputs of the convert_to_floats function."""
        # use a list full of floats
        float_list = [11.123, 12.0, 13.55, 12.11]
        result = convert_to_floats(float_list)
        self.assertEqual(float_list, result, result)

        # use a list containing some floats and integers
        float_int_list = [11.123, 12, 13.55, 12.11, 120]
        result = convert_to_floats(float_int_list)
        self.assertEqual([11.123, 12.0, 13.55, 12.11, 120.0], result, result)

        # use a list of strings with float values
        string_float_list = ['11.123', '12.0', '13.55', b'12.11']
        result = convert_to_floats(string_float_list)
        self.assertEqual(float_list, result, result)

        # use a list of strings with values being no floats
        string_no_float_list = ['11.123', '10:24 AM', '13.55', b'12.11']
        result = convert_to_floats(string_no_float_list)
        self.assertFalse(result)

    def test2consists_of_ints(self):
        """This unittest tests possible inputs of the consists_of_ints function."""
        # use a list full of integers
        int_list = [11, 12, 27, 33, 190]
        self.assertTrue(consists_of_ints(int_list))

        # use a list containing integers and floats
        int_float_list = [11, 12, 27, 33.0, 190]
        self.assertTrue(consists_of_ints(int_float_list))

        # use a list containing integers and floats
        int_float_list = [11, 12, 27, 33.0, 190.2]
        self.assertFalse(consists_of_ints(int_float_list))

        # use a list with integers as strings
        string_int_list = ['11', '12', '27', '33', b'190']
        self.assertFalse(consists_of_ints(string_int_list))

    # This test is commented out to prevent false positives in the CI/CD. It is useful for fuzz testing and therefore just commented out.
    '''def test3detect_continuous_shape_random_data(self):
        """This unittest tests possible continuously distributed variables raising from the detect_continous_shape method. It uses randomly
        generated data from the ContinuousSampleGenerator."""
        iterations = 30
        accuracy = 0.90
        dataset_size = 2000

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 0.5, 'testInt': True, 'simThres': 0.3})

        var_ev = 0
        var_var = 2
        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], dataset_size, plot_bool=False)
            uni_data_list = []
            for desc, data in data_list:
                uni_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(uni_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['uni'] >= iterations * accuracy, counts)

        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [['nor', 100, 1, 90, 110]], dataset_size, plot_bool=False)
            nor_data_list = []
            for desc, data in data_list:
                nor_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(nor_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['nor'] >= iterations * accuracy, counts)

        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [
                ['beta', (-0.5 + var_ev) / 0.35355339059327379 * var_var, 1 / 0.35355339059327379 * var_var, -1000, 1000, 1]], dataset_size,
                plot_bool=False)
            beta_data_list = []
            for desc, data in data_list:
                beta_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(beta_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['beta'] >= iterations * accuracy, counts)

        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [
                ['beta', (-0.7142857142857143 + var_ev) / 0.15971914124998499 * var_var, 1 / 0.15971914124998499 * var_var, -1000, 1000,
                    2]], dataset_size * 2, plot_bool=False)
            beta_data_list = []
            for desc, data in data_list:
                beta_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(beta_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['beta'] >= iterations * accuracy, counts)

        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [
                ['beta', (-0.5 + var_ev) / 0.35355339059327379 * var_var, 1 / 0.35355339059327379 * var_var, -1000, 1000, 4]],
                int(dataset_size / 2), plot_bool=False)
            data_list += generate_sample([], [
                ['beta', (-0.5 + var_ev) / 0.35355339059327379 * var_var, 1 / 0.35355339059327379 * var_var, -1000, 1000, 5]],
                int(dataset_size / 2), plot_bool=False)
            beta_data_list = []
            for desc, data in data_list:
                beta_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(beta_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['betam'] >= iterations * accuracy, counts)

        result_shapes = []
        for i in range(iterations):
            data_list = generate_sample([], [
                ['spec', 0, 1, -1000, 1000, 0]], dataset_size, plot_bool=False,
                 spec_distr_file_name='unit/data/vtd_data/spec_distribution_k')
            spec_data_list = []
            for desc, data in data_list:
                spec_data_list.append(data)
            result_shapes.append(vtd.detect_continuous_shape(spec_data_list)[0])
        counts = Counter(result_shapes)
        self.assertTrue(counts['spec'] >= iterations * accuracy, counts)'''

    def test3detect_continuous_shape_fixed_data(self):
        """This unittest tests possible continuously distributed variables raising from the detect_continous_shape method. It uses fix
        datasets. Every distribution has generated 20*100 Datasets and var_ev = 0, var_var = 1. Data was generated with following methods:
        iterations = 20
        dataset_sizes = [100]
        significance_niveaus = [0.05]
        var_ev = 0
        var_var = 1
        uni_data_list = [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], max(dataset_sizes)*iterations, plot_bool=False)]
        nor_data_list = [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], max(dataset_sizes)*iterations, plot_bool=False)]
        beta1_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], max(dataset_sizes)*iterations, plot_bool=False)]
        beta2_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], max(dataset_sizes)*iterations, plot_bool=False)]
        beta3_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], max(dataset_sizes)*iterations, plot_bool=False)]
        beta4_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], max(dataset_sizes)*iterations, plot_bool=False)]
        beta5_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], max(dataset_sizes)*iterations, plot_bool=False)]
        """
        # This Variable states if the data sets should be generated. If not True then the deterministic standard test is executed
        generate_data_sets = False

        # Number of execution of the tested function 
        iterations = 20
        # Size of the initial datasample
        dataset_sizes = [100]
        # Significance level
        significance_niveaus = [0.05]

        if generate_data_sets:
            # generate data
            var_ev = 0
            var_var = 1
            uni_data_list = [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], max(dataset_sizes)*iterations, plot_bool=False)]
            nor_data_list = [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], max(dataset_sizes)*iterations, plot_bool=False)]
            beta1_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], max(dataset_sizes)*iterations, plot_bool=False)]
            beta2_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], max(dataset_sizes)*iterations, plot_bool=False)]
            beta3_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], max(dataset_sizes)*iterations, plot_bool=False)]
            beta4_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], max(dataset_sizes)*iterations, plot_bool=False)]
            beta5_data_list = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], max(dataset_sizes)*iterations, plot_bool=False)]
        else:
            # load data
            with open('unit/data/vtd_data/uni_data_test3', 'rb') as f:
                [uni_data_list, uni_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/nor_data_test3', 'rb') as f:
                [nor_data_list, nor_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta1_data_test3', 'rb') as f:
                [beta1_data_list, beta1_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta2_data_test3', 'rb') as f:
                [beta2_data_list, beta2_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta3_data_test3', 'rb') as f:
                [beta3_data_list, beta3_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta4_data_test3', 'rb') as f:
                [beta4_data_list, beta4_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta5_data_test3', 'rb') as f:
                [beta5_data_list, beta5_result_shapes] = pickle.load(f)

        for dataset_size in dataset_sizes:
            for significance_niveau in significance_niveaus:
                etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
                vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
                    'numMinAppearance': dataset_size, 'divThres': 0.5, 'testInt': True, 'simThres': 0.3, 'KS_Alpha': significance_niveau})
                
                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(uni_data_list[i * dataset_size:(i + 1) * dataset_size])

                    # Add if the seached distribution is present in the found distributions
                    if distribution_list[0] == 'uni' or 'uni' in [distr[0] for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/uni_data_test3', 'wb+')
                    pickle.dump([uni_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('uni accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == uni_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(nor_data_list[i * dataset_size:(i + 1) * dataset_size])

                    # Add if the seached distribution is present in the found distributions
                    if distribution_list[0] == 'nor' or 'nor' in [distr[0] for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/nor_data_test3', 'wb+')
                    pickle.dump([nor_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('nor accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == nor_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(beta1_data_list[i * dataset_size:(i + 1) * dataset_size])
                    
                    # Add if the seached distribution is present in the found distributions
                    if (distribution_list[0] == 'beta' and distribution_list[-1] == 1) or 'beta1' in [distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/beta1_data_test3', 'wb+')
                    pickle.dump([beta1_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('beta1 accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == beta1_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(beta2_data_list[i * dataset_size:(i + 1) * dataset_size])

                    # Add if the seached distribution is present in the found distributions
                    if (distribution_list[0] == 'beta' and distribution_list[-1] == 2) or 'beta2' in [distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/beta2_data_test3', 'wb+')
                    pickle.dump([beta2_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('beta2 accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == beta2_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(beta3_data_list[i * dataset_size:(i + 1) * dataset_size])
                    
                    # Add if the seached distribution is present in the found distributions
                    if (distribution_list[0] == 'beta' and distribution_list[-1] == 3) or 'beta3' in [distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/beta3_data_test3', 'wb+')
                    pickle.dump([beta3_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('beta3 accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == beta3_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(beta4_data_list[i * dataset_size:(i + 1) * dataset_size])
                    
                    # Add if the seached distribution is present in the found distributions
                    if (distribution_list[0] == 'beta' and distribution_list[-1] == 4) or 'beta4' in [distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/beta4_data_test3', 'wb+')
                    pickle.dump([beta4_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('beta4 accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == beta4_result_shapes)

                result_list = [] # List of the results of the single tests
                for i in range(iterations):
                    distribution_list = vtd.detect_continuous_shape(beta5_data_list[i * dataset_size:(i + 1) * dataset_size])
                    
                    # Add if the seached distribution is present in the found distributions
                    if (distribution_list[0] == 'beta' and distribution_list[-1] == 5) or 'beta5' in [distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                        result_list.append(1)
                    else:
                        result_list.append(0)

                if generate_data_sets:
                    # Save the data set and print the accuracy
                    f = open('unit/data/vtd_data/beta5_data_test3', 'wb+')
                    pickle.dump([beta5_data_list, result_list], f)
                    self.assertTrue(sum(result_list) / iterations >= 0.5)
                    print('beta5 accuracy: %.3f, dataset_size: %d' % (sum(result_list) / iterations, dataset_size))
                else:
                    # Test if the result list is correct
                    self.assertTrue(result_list == beta5_result_shapes)

    def test4detect_var_type(self):
        """This unittest tests possible scenarios of the detect_var_type method."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={'numMinAppearance': 100})
        t = time.time()
        # test the 'static' path of detect_var_type
        stat_data = b'5.3.0-55-generic'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # check what happens if less than numMinAppearance values are available
        for i in range(100):
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['stat', [stat_data.decode()], False], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={'numMinAppearance': 100})

        # test ascending with float values
        for i in range(100):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['asc', 'float'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={'numMinAppearance': 100})

        # test ascending with integer values
        for i in range(100):
            stat_data = bytes(str(i), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['asc', 'int'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={'numMinAppearance': 100})

        # test descending with float values
        for i in range(100, 0, -1):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['desc', 'float'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={'numMinAppearance': 100})

        # test descending with integer values
        for i in range(100, 0, -1):
            stat_data = bytes(str(i), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['desc', 'int'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 0.3, 'testInt': True})

        # test 'numMinAppearance' and 'divThres' options
        # prevent results from becoming asc or desc
        stat_data = bytes(str(99), 'utf-8')
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        etd.receive_atom(log_atom)
        values = [float(stat_data)]
        for i in range(99):
            stat_data = bytes(str(i), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # this means that the uniformal distribution must be detected.
        self.assertNotEqual('uni' == result[0] or 'uni' in [distr[0] for distr in result[-1]], result)

        # test 'divThres' option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 1.0, 'testInt': True})
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['unq', values], result)

        # test 'testInt' option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 0.3, 'testInt': False})
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['unq', values], result)

        # test 'simThres' option to result in 'others'
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 0.5, 'testInt': False, 'simThres': 0.5})
        values = []
        for i in range(100):
            stat_data = bytes(str((i % 50) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # at least (1 - 'simThresh') * 'numMinAppearance' and maximal 'numMinAppearance' * 'divThres' - 1 unique values must exist.
        self.assertEqual(['others', 0], result)

        # test discrete result
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'divThres': 0.5, 'testInt': False, 'simThres': 0.3})
        values = []
        for i in range(100):
            stat_data = bytes(str((i % 50) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        values_set = list(set(values))
        values_app = [0 for _ in range(len(values_set))]
        for value in values:
            values_app[values_set.index(value)] += 1
        values_app = [x / len(values) for x in values_app]
        self.assertEqual(['d', values_set, values_app, len(values)], result)

    def test5consists_of_floats(self):
        """This unittest tests the consists_of_floats method."""
        # test an empty list
        data_list = []
        self.assertTrue(consists_of_floats(data_list))

        # test a list of integers and floats
        data_list = [10, 11.12, 13, 177, 0.5, 0.]
        self.assertTrue(consists_of_floats(data_list))

        # test a list containing a string
        data_list = [10, 11.12, 13, 177, 0.5, 0., 'dd']
        self.assertFalse(consists_of_floats(data_list))

        # test a list containing bytes
        data_list = [10, 11.12, 13, 177, 0.5, 0., b'x']
        self.assertFalse(consists_of_floats(data_list))

    def test6receive_atom(self):
        """This unittest tests if atoms are sorted to the right distribution and if the update steps also work properly.
        Therefore the assumption that after 200 values the VTD with the default parameters can change to the right distribution."""
        generate_data_sets = False

        if generate_data_sets:
            # generate data
            uni_data_list = [val[1] for val in generate_sample([], [['uni', -1, 1]], 100, plot_bool=False)]
            nor_data_list = [val[1] for val in generate_sample([], [['nor', 0, 1, -1000, 1000]], 100, plot_bool=False)]
            beta1_data_list = [val[1] for val in generate_sample([], [['beta', 0, 1, -1000, 1000, 1]], 100, plot_bool=False)]
            with open('unit/data/vtd_data/uni_data_test8', 'wb+') as f:
                pickle.dump(uni_data_list, f)
            with open('unit/data/vtd_data/nor_data_test8', 'wb+') as f:
                pickle.dump(nor_data_list, f)
            with open('unit/data/vtd_data/beta1_data_test8', 'wb+') as f:
                pickle.dump(beta1_data_list, f)
        else:
            # load data
            with open('unit/data/vtd_data/uni_data_test8', 'rb') as f:
                uni_data_list = pickle.load(f)
            with open('unit/data/vtd_data/nor_data_test8', 'rb') as f:
                nor_data_list = pickle.load(f)
            with open('unit/data/vtd_data/beta1_data_test8', 'rb') as f:
                beta1_data_list = pickle.load(f)

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'numUpdate': 50, 'simThres': 0.3, 'divThres': 0.8, 'numPauseOthers': 0})
        t = time.time()
        stat_data = b'True'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # initialize data
        for i in range(100):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['stat', [stat_data.decode()], True], result)

        # static -> static
        for i in range(50):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['stat', [stat_data.decode()], True], result)

        # static -> uni
        for uni_data in uni_data_list:
            log_atom = LogAtom(uni_data, ParserMatch(MatchElement('', uni_data, str(uni_data), None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        posdistr = vtd.possible_var_type[0][0]
        self.assertTrue('uni' == result[0] or 'uni' in [distr[0] for distr in posdistr])

        # uni -> others
        for i in range(50):
            stat_data = bytes(str((i % 75) * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['others', 0], result)

        # others -> d
        for i in range(50):
            stat_data = bytes(str((i % 10) * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual('d', result[0])

        # reset all
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'numUpdate': 50, 'simThres': 0.3, 'divThres': 0.3, 'numPauseOthers': 0})
        t = time.time()
        stat_data = b'True'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # initialize data
        for i in range(100):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['stat', [stat_data.decode()], True], result)

        # static -> asc
        for i in range(100):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['asc', 'float'], result)

        # asc -> desc
        for i in range(100, 0, -1):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['desc', 'float'], result)

        # reset all
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'numUpdate': 50, 'simThres': 0.3, 'divThres': 0.3, 'numPauseOthers': 0})
        t = time.time()
        stat_data = b'True'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # initialize data
        for i in range(100):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['stat', [stat_data.decode()], True], result)

        # static -> nor
        for nor_data in nor_data_list:
            log_atom = LogAtom(nor_data, ParserMatch(MatchElement('', nor_data, str(nor_data), None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        posdistr = vtd.possible_var_type[0][0]
        self.assertTrue('nor' == result[0] or 'nor' in [distr[0] for distr in posdistr])

        # nor -> beta1
        for beta1_data in beta1_data_list:
            log_atom = LogAtom(beta1_data, ParserMatch(MatchElement('', beta1_data, str(beta1_data), None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        posdistr = vtd.possible_var_type[0][0]
        self.assertTrue(('beta' == result[0] and result[-1] == 1) or 'beta1' in [distr[0]+str(distr[-1]) for distr in posdistr])

        # reset all
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'numUpdate': 50, 'simThres': 0.3, 'divThres': 0.3, 'numPauseOthers': 0})
        t = time.time()
        stat_data = b'True'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # initialize data
        for i in range(100):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(['stat', [stat_data.decode()], True], result)

        # static -> unq
        vtd.options['testInt'] = False
        unq_data_list = [bytes(str(i), 'utf-8') for i in range(100)]
        random.shuffle(unq_data_list)
        for unq_data in unq_data_list:
            log_atom = LogAtom(unq_data, ParserMatch(MatchElement('', unq_data, unq_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual('unq', result[0])

    def run_update_data(self, data_list):
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
            'numMinAppearance': 100, 'sKS_NumValues': 50, 'numUpdate': 50})
        t = time.time()
        # initialize vtd buckets
        for i in range(100):
            stat_data = bytes(str(data_list[i]), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        old_bucket_num = copy.deepcopy(vtd.bucket_num)
        for i in range(1, 1000, 1):
            stat_data = bytes(str(data_list[i]), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
            if i % (vtd.options['numUpdate']) == 0 and i != 0:
                if vtd.var_type[0][0] != ['others', 0] and vtd.bucket_num != [[[]]]:
                    self.assertNotEqual(vtd.bucket_num, old_bucket_num)
                    # missing tests for the correct calculation of the bucket_num's

                    ###############################################################
                old_bucket_num = copy.deepcopy(vtd.bucket_num)
            else:
                self.assertEqual(vtd.bucket_num, old_bucket_num)

    def test7update_continuous_VT_random_data(self):
        """This unittest tests the s_ks_test method. It uses randomised datasets, which can be printed in the terminal.
        Every distribution has generated 30*300 Datasets and var_ev = 0, var_var = 1. Data was generated with following methods:
        ..."""
        # This Variable states if the data sets should be generated. If not True then the deterministic standard test is executed
        generate_data_sets = False
        # Number of execution of the tested function 
        iterations = 20
        # Size of the initial datasample
        dataset_sizes_ini = [100]
        # Size of the update datasample
        dataset_sizes_upd = [50]
        # Significance level
        significance_niveaus = [0.05]

        if generate_data_sets:
            # generate data
            var_ev = 0
            var_var = 1

            uni_data_list_ini = [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            uni_data_list_upd = [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            nor_data_list_ini = [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            nor_data_list_upd = [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            beta1_data_list_ini = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            beta1_data_list_upd = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            beta2_data_list_ini = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            beta2_data_list_upd = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            beta3_data_list_ini = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            beta3_data_list_upd = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            beta4_data_list_ini = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            beta4_data_list_upd = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
            beta5_data_list_ini = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], max(dataset_sizes_ini)*iterations, plot_bool=False)]
            beta5_data_list_upd = [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], max(dataset_sizes_upd)*iterations, plot_bool=False)]
        else:
            # load data
            with open('unit/data/vtd_data/uni_data_test9', 'rb') as f:
                [uni_data_list_ini, uni_data_list_upd, uni_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/nor_data_test9', 'rb') as f:
                [nor_data_list_ini, nor_data_list_upd, nor_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta1_data_test9', 'rb') as f:
                [beta1_data_list_ini, beta1_data_list_upd, beta1_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta2_data_test9', 'rb') as f:
                [beta2_data_list_ini, beta2_data_list_upd, beta2_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta3_data_test9', 'rb') as f:
                [beta3_data_list_ini, beta3_data_list_upd, beta3_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta4_data_test9', 'rb') as f:
                [beta4_data_list_ini, beta4_data_list_upd, beta4_result_shapes] = pickle.load(f)
            with open('unit/data/vtd_data/beta5_data_test9', 'rb') as f:
                [beta5_data_list_ini, beta5_data_list_upd, beta5_result_shapes] = pickle.load(f)

        for dataset_size_ini in dataset_sizes_ini:
            for dataset_size_upd in dataset_sizes_upd:
                for significance_niveau in significance_niveaus:
                    etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
                    vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, options={
                        'numMinAppearance': dataset_size_ini, 'numUpdate': dataset_sizes_upd, 'KS_Alpha': significance_niveau})

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'uni':
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'uni' in [distr[0] for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'uni':
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], dataset_size_ini, plot_bool=False)])

                        # Test and save the result of the sKS-Test
                        etd.values = [[uni_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/uni_data_test9', 'wb+')
                        pickle.dump([uni_data_list_ini, uni_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('uni accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == uni_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'nor':
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'nor' in [distr[0] for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'nor':
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], dataset_size_ini, plot_bool=False)])

                        # Test and save the result of the sKS-Test
                        etd.values = [[nor_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/nor_data_test9', 'wb+')
                        pickle.dump([nor_data_list_ini, nor_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('nor accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == nor_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(beta1_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'beta' and (variable_type_ini[-1] == 1 or (type(variable_type_ini[-1]) == list and variable_type_ini[-2] == 1)):
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'beta1' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'beta' and variable_type_ini[-1][j][-1] == 1:
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    beta1_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(beta1_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 1]], dataset_size_ini, plot_bool=False)])
                        
                        # Test and save the result of the sKS-Test
                        etd.values = [[beta1_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/beta1_data_test9', 'wb+')
                        pickle.dump([beta1_data_list_ini, beta1_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('beta1 accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == beta1_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(beta2_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'beta' and (variable_type_ini[-1] == 2 or (type(variable_type_ini[-1]) == list and variable_type_ini[-2] == 2)):
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'beta2' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'beta' and variable_type_ini[-1][j][-1] == 2:
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    beta2_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(beta2_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 2]], dataset_size_ini, plot_bool=False)])
                        
                        # Test and save the result of the sKS-Test
                        etd.values = [[beta2_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/beta2_data_test9', 'wb+')
                        pickle.dump([beta2_data_list_ini, beta2_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('beta2 accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == beta2_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(beta3_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'beta' and (variable_type_ini[-1] == 3 or (type(variable_type_ini[-1]) == list and variable_type_ini[-2] == 3)):
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'beta3' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'beta' and variable_type_ini[-1][j][-1] == 3:
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    beta3_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(beta3_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 3]], dataset_size_ini, plot_bool=False)])
                        
                        # Test and save the result of the sKS-Test
                        etd.values = [[beta3_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/beta3_data_test9', 'wb+')
                        pickle.dump([beta3_data_list_ini, beta3_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('beta3 accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == beta3_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(beta4_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'beta' and (variable_type_ini[-1] == 4 or (type(variable_type_ini[-1]) == list and variable_type_ini[-2] == 4)):
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'beta4' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'beta' and variable_type_ini[-1][j][-1] == 4:
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    beta4_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(beta4_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 4]], dataset_size_ini, plot_bool=False)])
                        
                        # Test and save the result of the sKS-Test
                        etd.values = [[beta4_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/beta4_data_test9', 'wb+')
                        pickle.dump([beta4_data_list_ini, beta4_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('beta4 accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == beta4_result_shapes)

                    result_list = [] # List of the results of the single tests
                    for i in range(iterations):
                        # Create the initial distribution, which has to pass the initial test
                        variable_type_ini = vtd.detect_continuous_shape(beta5_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                        while True:
                            if variable_type_ini[0] == 'beta' and (variable_type_ini[-1] == 5 or (type(variable_type_ini[-1]) == list and variable_type_ini[-2] == 5)):
                                if type(variable_type_ini[-1]) == list:
                                    variable_type_ini = variable_type_ini[:-1]
                                break
                            elif 'beta5' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                                for j in range(len(variable_type_ini[-1])):
                                    if variable_type_ini[-1][j][0] == 'beta' and variable_type_ini[-1][j][-1] == 5:
                                        variable_type_ini = variable_type_ini[-1][j]
                                        break
                            else:
                                if generate_data_sets:
                                    beta5_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini] = \
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], dataset_size_ini, plot_bool=False)]
                                    variable_type_ini = vtd.detect_continuous_shape(beta5_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
                                else:
                                    variable_type_ini = vtd.detect_continuous_shape(
                                            [val[1] for val in generate_sample([], [['beta', var_ev, var_var, -1000, 1000, 5]], dataset_size_ini, plot_bool=False)])
                        
                        # Test and save the result of the sKS-Test
                        etd.values = [[beta5_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
                        vtd.var_type = [[variable_type_ini]]
                        result_list.append(vtd.s_ks_test(0, 0, True)[0])

                    if generate_data_sets:
                        f = open('unit/data/vtd_data/beta5_data_test9', 'wb+')
                        pickle.dump([beta5_data_list_ini, beta5_data_list_upd, result_list], f)
                        self.assertTrue(sum(result_list) >= iterations * 0.5, sum(result_list))
                        print('beta5 accuracy: %.3f, dataset_size_ini: %d, dataset_size_upd: %d' % (sum(result_list) / iterations, dataset_size_ini, dataset_size_upd))
                    else:
                        # Test if the result list is correct
                        self.assertTrue(result_list == beta5_result_shapes)
