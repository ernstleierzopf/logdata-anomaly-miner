import unittest
from aminer.events.Utils import VolatileLogarithmicBackoffEventHistory
from time import time
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class UtilsTest(TestBase):
    """Unittests for the Utils."""

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        pid = b" pid="
        test = "Test.%s"
        message = "New value for paths match/s1, match/s2: b' pid=' "
        # In this test case multiple events are received by the VolatileLogarithmicBackoffEventHistory.
        vlbeh = VolatileLogarithmicBackoffEventHistory(10)
        match_context = DummyMatchContext(pid)
        fdme = DummyFixedDataModelElement("s1", pid)
        match_element = fdme.get_match_element("match", match_context)
        t = time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
        self.assertEqual(vlbeh.get_history(), [(0, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)])
        vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
        self.assertEqual(vlbeh.get_history(), [
            (0, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self),
            (1, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)])

        # In this test case no events are received by the VolatileLogarithmicBackoffEventHistory.
        vlbeh = VolatileLogarithmicBackoffEventHistory(10)
        self.assertEqual(vlbeh.get_history(), [])

        # In this test case the EventHandler receives no logAtom from the test class and the output should not contain the log time.
        vlbeh = VolatileLogarithmicBackoffEventHistory(10)
        t = time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
        self.assertEqual(vlbeh.get_history(), [(0, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)])

        # In this test case more events than the VolatileLogarithmicBackoffEventHistory can handle are received (max items overflow).
        deviation = 0.05
        size = 100000
        msg = "%s=%f is not between %f and %f"
        t = time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, self)
        first = 0
        second = 0
        third = 0
        fourth = 0
        for _ in range(size):
            vlbeh = VolatileLogarithmicBackoffEventHistory(2)
            vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
            vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
            vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
            vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
            vlbeh.receive_event(test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
            history = vlbeh.get_history()
            if history == [(0, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                           log_atom.get_parser_match(), self), (4, test % self.__class__.__name__, message,
                           [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
                first += 1
            elif history == [(1, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                             log_atom.get_parser_match(), self), (4, test % self.__class__.__name__, message,
                             [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
                second += 1
            elif history == [(2, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                             log_atom.get_parser_match(), self), (4, test % self.__class__.__name__, message,
                             [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
                third += 1
            elif history == [(3, test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                             log_atom.get_parser_match(), self), (4, test % self.__class__.__name__, message,
                             [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
                fourth += 1
        val = 0.5 * 0.5 * 0.5
        minimum = size * val * (1 - deviation)
        maximum = size * val * (1 + deviation)
        self.assertTrue(minimum <= first <= maximum, msg % ("first", first, minimum, maximum))

        val = 0.5 * 0.5 * 0.5
        minimum = size * val * (1 - deviation)
        maximum = size * val * (1 + deviation)
        self.assertTrue(minimum <= second <= maximum, msg % ("second", second, minimum, maximum))

        val = 2 * 0.5 * 0.5 * 0.5
        minimum = size * val * (1 - deviation)
        maximum = size * val * (1 + deviation)
        self.assertTrue(minimum <= third <= maximum, msg % ("third", third, minimum, maximum))

        val = 0.5
        minimum = size * val * (1 - deviation)
        maximum = size * val * (1 + deviation)
        self.assertTrue(minimum <= fourth <= maximum, msg % ("fourth", fourth, minimum, maximum))


if __name__ == "__main__":
    unittest.main()
