import pathlib
import math
import unittest
from simplesi.dimensions import Dimensions  # noqa protected
from simplesi import Physical, environment  # noqa protected
import simplesi as si

# preferred_units = {"mm": [0, 1, 0, 0, 0, 0, 0],
#                    "s": [0, 0, 1, 0, 0, 0, 0],
#                    "kg": [1, 0, 0, 0, 0, 0, 0],
#                    "kN": [1, 1, -2, 0, 0, 0, 0],
#                    "kNm": [1, 2, -2, 0, 0, 0, 0],
#                    "MPa": [1, -1, -2, 0, 0, 0, 0]
#                    }
preferred_units = {}
env_settings = {"to_fails": "raise",
                "print_unit": "smallest",
                "significant_digits": 3
                }

si.environment(env_name='test_US_customary', env_path=pathlib.Path('.'), preferred_units=preferred_units, settings=env_settings)
si.environment(env_name='test_structural', env_path=pathlib.Path('.'), replace=False)
si.environment.settings['significant_digits'] = 3


class TestPhysicalWithUnits(unittest.TestCase):

    def test_relation(self):
        self.assertTrue(1 * si.m == 1000 * si.mm)
        self.assertTrue(1 * si.m != 1 * si.ft)
        self.assertTrue(0.5 * si.m <= 500 * si.mm)
        self.assertTrue(3 * si.cm >= 30 * si.mm)
        self.assertTrue(3 * si.cm > 1 * si.inch)
        self.assertTrue(1 * si.yard < 1258 * si.mm)

        self.assertFalse(1 * si.m != 1000 * si.mm)
        self.assertFalse(1 * si.m == 1 * si.ft)
        self.assertFalse(0.5 * si.m > 500 * si.mm)
        self.assertFalse(3 * si.cm > 30 * si.mm)
        self.assertFalse(3 * si.cm < 1 * si.inch)
        self.assertFalse(1 * si.yard > 1258 * si.mm)

    def test_to(self):
        self.assertEqual((1 * si.inch).to('inch'), '1 inch')
        self.assertEqual((1 * si.ft).to('inch'), '12.00 inch')
        self.assertEqual((1 * si.m).to('m'), '1 m')
        self.assertEqual((12 * si.inch).to('ft'), '1.00 ft')
        self.assertEqual((1 * si.yard).to('ft'), '3 ft')

        self.assertEqual((1 * si.m).to('inch'), '39.37 inch')
        self.assertEqual((1 * si.m).to('ft'), '3.28 ft')

        self.assertEqual((10 * si.inch).to('m'), '0.254 m')
        self.assertEqual((1 * si.ft).to('cm'), '30.48 cm')
        self.assertEqual((1 * si.ft).to('mm'), '304.80 mm')
        self.assertEqual((2 * si.yard).to('mm'), '1828.80 mm')

        self.assertEqual(12 * si.inch + 2 * si.ft, 1 * si.yard)
        self.assertEqual(12 * si.cm + 2 * si.m, 2120 * si.mm)


    def test_as_str(self):

        sigdig = environment.settings.get('significant_digits')

        self.assertEqual(Physical.as_str(12.2535), '12.25')
        self.assertEqual(Physical.as_str(0.2535), '0.254')
        self.assertEqual(Physical.as_str(0.253), '0.253')
        self.assertEqual(Physical.as_str(0.25), '0.25')
        self.assertEqual(Physical.as_str(0.2), '0.20')
        self.assertEqual(Physical.as_str(0.02), '0.02')
        self.assertEqual(Physical.as_str(0.002), '0.002')
        self.assertEqual(Physical.as_str(0.0002), '0.0002')
        self.assertEqual(Physical.as_str(1.2), '1.20')
        self.assertEqual(Physical.as_str(1.02), '1.02')
        self.assertEqual(Physical.as_str(1.002), '1.00')
        self.assertEqual(Physical.as_str(1.0002), '1.00')
        self.assertEqual(Physical.as_str(2535), '2535')
        self.assertEqual(Physical.as_str(253.5), '253.50')

        environment.settings['significant_digits'] = 1
        self.assertEqual(Physical.as_str(12.2535), '12.3')
        self.assertEqual(Physical.as_str(0.2535), '0.3')
        self.assertEqual(Physical.as_str(0.253), '0.3')
        self.assertEqual(Physical.as_str(0.25), '0.2')
        self.assertEqual(Physical.as_str(0.2), '0.2')
        self.assertEqual(Physical.as_str(0.02), '0.02')
        self.assertEqual(Physical.as_str(0.002), '0.002')
        self.assertEqual(Physical.as_str(0.0002), '0.0002')
        self.assertEqual(Physical.as_str(1.2), '1.2')
        self.assertEqual(Physical.as_str(1.02), '1.0')
        self.assertEqual(Physical.as_str(1.002), '1.0')
        self.assertEqual(Physical.as_str(1.0002), '1.0')
        self.assertEqual(Physical.as_str(2535), '2535')
        self.assertEqual(Physical.as_str(253.5), '253.5')

        print(12.2535 * si.m)
        print(12 * si.m)
        print(12 * si.mm)

        # setting it back
        environment.settings['significant_digits'] = sigdig

        # self.assertNotEqual(Physical.as_str(1.002), '1.002')
        #
        # self.assertEqual(Physical.as_str(1), '1')
        # self.assertNotEqual(Physical.as_str(1), '1.0')


    def test_print(self):

        # setting the environment to print an exception if to() fails
        si.environment.settings['to_fails'] = 'print'

        # not None as a text is printed
        self.assertIsNotNone(si.km.to())
        self.assertIsNotNone(si.Hz.to())

        # unit unknown,prints something but no return value
        self.assertIsNone(si.Hz.to('1/hour'))  # unkown
        self.assertIsNone(si.Hz.to('whatever'))  # unknown
        self.assertIsNone(si.Hz.to('1/s'))  # only as Hz available

        # this makes sense
        self.assertEqual(si.Hz.__str__(), '1 Hz')

        # making sure the Physical object is available: importing it
        import importlib
        importlib.import_module('simplesi')
        self.assertEqual(eval(si.km.__repr__()), si.km)

        # setting the environment to raise an exception if to() fails
        si.environment.settings['to_fails'] = 'raise'
        with self.assertRaises(ValueError):
            si.km.to()
            si.Hz.to()

        # setting the environment to print an exception if to() fails
        si.environment.settings['to_fails'] = 'print'

    def test_split_str(self):
        # splitting to value and unit
        self.assertEqual(si.split_str('1.00 km'), (1.00, 'km'))
        self.assertEqual(si.split_str('1.345 km'), (1.345, 'km'))

    def test_SI(self):
        self.assertTrue(si.m.is_SI)
        self.assertFalse(si.ft.is_SI)

    def test_addition(self):
        self.assertEqual(1 * si.m + 1 * si.mm, 1001 * si.mm)
        self.assertAlmostEqual(3 * si.ft + 1 * si.yard, 2 * si.yard, delta=0.01 * si.mm)
        self.assertAlmostEqual(3 * si.ft + 25.4 * si.mm, 0.9398 * si.m, delta=0.01 * si.mm)
        self.assertAlmostEqual(3 * si.ft + 25.4 * si.mm, 25.4 * si.mm + 3 * si.ft + 0, delta=0.01 * si.mm)  # radd

        with self.assertRaises(ValueError):
            3 * si.ft + 5
            3 * si.ft + 4 * si.kNm

        # summing
        vals = [x * 1 * si.mm for x in range(1, 11)]
        self.assertEqual(sum(vals), sum(range(1, 11)) * si.mm)

    def test_subtraction(self):
        self.assertEqual(1 * si.m - 1 * si.mm, 999 * si.mm)
        self.assertAlmostEqual(3 * si.ft - 1 * si.yard, 0 * si.yard, delta=0.01 * si.mm)
        self.assertAlmostEqual(3 * si.ft - 25.4 * si.mm, 939.8 * si.mm - 2 * 25.4 * si.mm, delta=0.01 * si.mm)
        self.assertAlmostEqual(3 * si.ft - 25.4 * si.mm, - 1 * 25.4 * si.mm + 3 * si.ft + 0, delta=0.01 * si.mm)  # rsub

        with self.assertRaises(ValueError):
            3 * si.ft - 5
            3 * si.ft - 4 * si.kNm

    def test_multiplication(self):
        self.assertAlmostEqual(1 * si.m * 1 * si.N, 1 * si.Nm, delta=1 * si.N * si.mm)
        self.assertEqual((1 * si.m) * 1, 1000 * si.mm)
        self.assertEqual(2 * (si.m * 1), 2000 * si.mm)

    def test_division(self):
        self.assertEqual((1 * si.m) / 2, 500 * si.mm)
        self.assertEqual((1 * si.kNm) / (2 * si.m), 0.5 * si.kN)
        self.assertEqual((1 * si.kN) / (2 * si.m ** 2), 0.5 * si.kN_m2)

        self.assertEqual((1 * si.m) / (1 * si.s), 1 * si.m_s)


        # rtruediv
        self.assertEqual(5 / (1 * si.s), 5 * si.Hz)
        self.assertEqual(1 / (1 * si.m ** 2), 1 * (si.m ** -2))
        self.assertEqual((3 * si.kN) / (si.m ** 2), 3 * si.kN_m2)

        with self.assertRaises(ZeroDivisionError):
            1 * si.m / 0

    def test_power(self):
        self.assertEqual((1 * si.m) ** 2, 1 * si.m2)
        self.assertEqual((1 * si.s) ** -1, 1 * si.Hz)
        self.assertEqual((4 * si.m2) ** 0.5, 2 * si.m)
        self.assertEqual((4 * si.m2).sqrt(), 2 * si.m)
        self.assertEqual((4 * si.m2).sqrt(), (4 * si.m2).root(2))
        self.assertEqual((8 * si.m3).root(3), 2 * si.m)

        with self.assertRaises(TypeError):
            math.sqrt(4 * si.m2)
            math.pow(4 * si.m2, 0.5)

        with self.assertRaises(ValueError):
            si.m ** si.s

    def test_environment_definition(self):

        from simplesi.environment import Environment
        from simplesi import base_units  # , environment_settings, preferred_units

        # everything is correct
        correct_environment = {'kg': {"Dimension": [1, 0, 0, 0, 0, 0, 0],
                                        "Value": 1,
                                        "Symbol": "kg",
                                        "Factor": 1},
                                 }
        # all is OK
        self.assertTrue(Environment._check_environment_definition(correct_environment) == ())
        si.environment('default', top_level=True)

        # unit is not a string
        with self.assertRaises(ValueError):
            incorrect_environment = {2: {"Dimension": [1, 0, 0, 0, 0, 0, 0],
                                         "Value": 0.001},
                                     }
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment)

        # false number of dimensions
        with self.assertRaises(ValueError):
            incorrect_environment = {'2': {"Dimension": [1, 0, 0, ],
                                         "Value": 0.001},
                                     }
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment)

        # no dimensions
        with self.assertRaises(ValueError):
            incorrect_environment2 = {'2': {"Value": 0.001},}
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment2)

        # dimensionsless
        dimless = {'deg': {"Dimension": [0, 0, 0, 0, 0, 0, 0], "Value": 1}, }
        Environment(si_base_units=base_units,
                    preferred_units={},
                    environment=dimless)

        # symbol
        with self.assertRaises(ValueError):
            incorrect_environment4 = {'2': {"Dimension": [1, 0, 0, 0, 0, 0, 0],
                                            "Symbol": 0.001},}
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment4)

        # factor
        with self.assertRaises(ValueError):
            incorrect_environment5 = {'2': {"Dimension": [1, 0, 0, 0, 0, 0, 0],
                                            "Factor": "0.001"},}
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment5)

        # value
        with self.assertRaises(ValueError):
            incorrect_environment6 = {'2': {"Dimension": [1, 0, 0, 0, 0, 0, 0],
                                            "Value": "0.001"},}
            Environment(si_base_units=base_units,
                        preferred_units={},
                        environment=incorrect_environment6)

    def test_env_path(self):
        with self.assertRaises(ValueError):
            si.environment(env_path=pathlib.Path('foo'), env_name='bar')

        # incorrect environment json file
        incorrect_environment = {"2": {"Dimension": [1, 0, 0], "Value": 0.001}}
        # dump it in an utf-8 json file
        import json
        with open('incorrect_environment.json', 'w', encoding='utf-8') as f:
            json.dump(incorrect_environment, f, ensure_ascii=True)
        with self.assertRaises(ValueError):
            si.environment(env_path=pathlib.Path('.'), env_name='incorrect_environment')
        # delete the .json file
        import os
        os.remove("incorrect_environment.json")



class TestRepresentation(unittest.TestCase):

    def test_PhysRepr_int(self):
        physical = 1200 * si.mm
        as_meter = physical('m')
        self.assertEqual(as_meter.value, 1.2)
        self.assertEqual(as_meter.unit, 'm')

        as_centimeter = physical('cm')
        self.assertEqual(as_centimeter.value, 120)
        self.assertEqual(as_centimeter.unit, 'cm')
        self.assertEqual(as_centimeter.physical, 1200 * si.mm)
        self.assertEqual(as_centimeter.physical, 120 * si.cm)

    def test_PhysRepr_float(self):
        p = 12 * si.mm
        some_distance = p('cm')
        self.assertEqual(some_distance.value, 1.2)

    def test_repr_preferred(self):
        preferred_units = {"mm": Dimensions(0, 1, 0, 0, 0, 0, 0)}
        si.environment.apply_preferences(preferred_units)

        # there is a preferred unit set
        physical = 1200 * si.mm
        as_mm = physical()
        self.assertEqual(as_mm.value, 1200)
        self.assertEqual(as_mm.unit, 'mm')
        # unit directly provided
        as_cm = physical('cm')
        self.assertEqual(as_cm.value, 120)
        self.assertEqual(as_cm.unit, 'cm')

        # no preferred unit set - the PhysRep is the same as the input value
        second = 25 * si.s
        as_minute = second()
        self.assertEqual(as_minute.value, second.value)
        self.assertEqual(as_minute.unit, 's')

        # no unit found - the provided unit is not defined so it is not possible to convert to it.
        with self.assertRaises(AttributeError):
            as_cm = physical('whatever')


if __name__ == '__main__':
    unittest.main()
