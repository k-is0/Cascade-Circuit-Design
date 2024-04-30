import unittest
import numpy as np
from main import parse_component, parse_net_file, impedance_matrix, cascade_matrices, calculate_output_variables
import main
import os

class TestCircuitAnalysis(unittest.TestCase):

    def test_parse_component(self):
        # Test correct parsing of component data
        component = "n1=1 n2=2 R=100"
        output_file = "test_output.csv"
        expected = (1, 2, 'R', 100.0)
        result = parse_component(component, output_file)
        self.assertEqual(result, expected)
        
        # Test incorrect component format
        with self.assertRaises(ValueError):
            component = "n1=1 n2=2 X=100"
            parse_component(component, output_file)

    def test_impedance_matrix(self):
        # Test impedance matrix calculation for a resistor
        frequency = 50  # Hz
        n1, n2 = 1, 2
        component_type = 'R'
        value = 100  # Ohms
        expected = [[1, 100], [0, 1]]
        result = impedance_matrix(frequency, n1, n2, component_type, value)
        np.testing.assert_array_equal(result, expected)

        # Test invalid component type
        with self.assertRaises(ValueError):
            impedance_matrix(frequency, n1, n2, 'X', value)

    def test_cascade_matrices(self):
        # Test cascading of multiple matrices
        matrices = [np.array([[1, 2], [3, 4]]), np.array([[1, 0], [0, 1]])]
        expected = [[1, 2], [3, 4]]
        result = cascade_matrices(matrices)
        np.testing.assert_array_almost_equal(result, expected)

    def test_calculate_output_variables(self):
        abcd_matrix = np.array([[1, 0], [0, 1]])  # Identity matrix, implying no transformation
        vt, rs, rl = 10, 50, 100
        expected = {
            'Vin': 6.66666667, 'Vout': 6.66666667, 'Iin': 0.06666667, 'Iout': 0.06666667,
            'Pin': 0.44444444, 'Zin': 50, 'Pout': 0.44444444, 'Zout': 50,
            'Av': 1.0, 'Ai': 1.0
        }
        result = calculate_output_variables(abcd_matrix, vt, rs, rl)
        for key in expected:
            self.assertAlmostEqual(result[key], expected[key], places=7)


    def test_full_integration(self):
        # Assuming the main function processes the input and writes to the output
        input_file = 'User_files/a_Test_Circuit_1.net'
        output_file = 'Model_files/a_Test_Circuit_1_model.csv'
        
        # Run the main function
        main(input_file, output_file)
        
        # Verify the output
        self.assertTrue(os.path.exists(output_file))
        
        # Further checks could include reading the output file and checking contents
        with open(output_file, 'r') as file:
            data = file.readlines()
            # Perform specific checks on data
            self.assertIn('ExpectedHeader', data[0])
            self.assertIn('ExpectedData', data[1])

        # Clean up test artifacts
        os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
