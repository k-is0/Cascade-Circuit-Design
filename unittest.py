import unittest

class TestCircuitAnalysis(unittest.TestCase):
    def test_resistor_abcd(self):
        result = abcd_matrix("n1=1 n2=2 R=50")
        expected = np.array([[1, 50], [0, 1]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_capacitor_abcd(self):
        result = abcd_matrix("n1=1 n2=2 C=1e-6")
        omega = 1  # Assume frequency is 1 rad/s for simplicity
        expected = np.array([[1, 0], [complex(0, -omega * 1e-6), 1]])
        np.testing.assert_array_almost_equal(result, expected)

    def test_series_cascade(self):
        matrix1 = np.array([[1, 50], [0, 1]])
        matrix2 = np.array([[1, 0], [complex(0, -1), 1]])
        result = cascade_matrices([matrix1, matrix2])
        expected = np.dot(matrix1, matrix2)
        np.testing.assert_array_almost_equal(result, expected)

if __name__ == '__main__':
    unittest.main()

    
