import unittest
import importlib
import yaml
import sys
# import json
# import shlex
# import configparser
# import uu
# import resource


class YamlConfigTest(unittest.TestCase):
    sysp = sys.path

    def setUp(self):
        sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']

    def tearDown(self):
        sys.path = self.sysp

    """ Loads a yaml file into the variable aminer_config.yamldata """
    def test_load_generic_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.loadYaml('unit/data/configfiles/template_config.yml')
        self.assertIsNotNone(aminer_config.yamldata)

    """ Tries to load a nonexistent yaml file. a FileNotFoundError is expected """
    def test_load_notexistent_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(FileNotFoundError):
            aminer_config.loadYaml('unit/data/configfiles/doesnotexist.yml')

    """ Tries to load a file with invalid yaml syntax. Expects an YAMLError """
    def test_load_invalid_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(yaml.YAMLError):
            aminer_config.loadYaml('unit/data/configfiles/invalid_config.yml')

    """ Tries to load a yaml-file with an invalid schema. A ValueError is expected """
    def test_load_yaml_file_with_invalid_schema(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.loadYaml('unit/data/configfiles/invalid_schema.yml')

    """ This test builds a analysis_pipeline from a valid yaml-file """
    def test_analysis_pipeline_working_config(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.loadYaml('unit/data/configfiles/apache_inline_config.yml')
        from aminer.AnalysisChild import AnalysisContext
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        """ the following lines help to debug the context for defining the testcases
        from pprint import pprint
        pprint(vars(context))
        pprint(vars(context.atomizer_factory))
        pprint(vars(context.atomizer_factory.parsing_model))
        pprint(vars(context.atomizer_factory.atom_handler_list[0])) """
        from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
        from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
        from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
        from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
        from aminer.parsing.SequenceModelElement import SequenceModelElement
        from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
        from aminer.parsing.FixedDataModelElement import FixedDataModelElement
        from aminer.parsing.DateTimeModelElement import DateTimeModelElement
        from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
        from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
        self.assertTrue(isinstance(context.real_time_triggered_components[0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.real_time_triggered_components[1], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.real_time_triggered_components[2], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, '/accesslog/time')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[3], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[4], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[5], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[6], DateTimeModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[7], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[8], FixedWordlistDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[9], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[10], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[11], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[12], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[13], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[14], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[15], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[16], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[17], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[18], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[19], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.element_id, 'accesslog')

    """ This test checks if the aminer fails without a start-tag for the first parser-model """
    def test_analysis_fail_without_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.loadYaml('unit/data/configfiles/missing_parserstart_config.yml')

    """ This test checks if the aminer fails without a start-tag for the first parser-model """
    def test_analysis_fail_with_double_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.loadYaml('unit/data/configfiles/double_parserstart_config.yml')

    """ This test checks if the config-schema-validator raises an error if an unknown parser is configured  """
    def test_analysis_fail_with_unknown_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.loadYaml('unit/data/configfiles/unknown_parser_config.yml')

    """This test checks if the config can be loaded without any analysis components."""
    def test_analysis_pipeline_working_config_with_analysis_components(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.loadYaml('unit/data/configfiles/apache_inline_config_null_analysis_components.yml')
        from aminer.AnalysisChild import AnalysisContext
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_analysis_components_tests(context)

        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.loadYaml('unit/data/configfiles/apache_inline_config_undefined_analysis_components.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_analysis_components_tests(context)

    def run_empty_analysis_components_tests(self, context):
        """ the following lines help to debug the context for defining the testcases
        from pprint import pprint
        pprint(vars(context))
        pprint(vars(context.atomizer_factory))
        pprint(vars(context.atomizer_factory.parsing_model))
        pprint(vars(context.atomizer_factory.atom_handler_list[0])) """
        from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
        from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
        from aminer.parsing.SequenceModelElement import SequenceModelElement
        from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
        from aminer.parsing.FixedDataModelElement import FixedDataModelElement
        from aminer.parsing.DateTimeModelElement import DateTimeModelElement
        from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
        from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
        self.assertTrue(isinstance(context.real_time_triggered_components[0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, '/accesslog/time')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[3], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[4], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[5], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[6], DateTimeModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[7], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[8], FixedWordlistDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[9], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[10], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[11], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[12], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[13], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[14], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[15], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[16], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[17], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[18], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[19], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.element_id, 'accesslog')


if __name__ == "__main__":
    unittest.main()