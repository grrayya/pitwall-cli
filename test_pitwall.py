import unittest
from pitwall import calculate_form_index

class TestPitwallLogic(unittest.TestCase):
    def test_form_index_normalization(self):
        # Mock data representing two drivers
        mock_standings = [
            {
                "points": "100", 
                "wins": "2", 
                "Driver": {"givenName": "Max", "familyName": "Verstappen"}
            },
            {
                "points": "50", 
                "wins": "0", 
                "Driver": {"givenName": "Lando", "familyName": "Norris"}
            }
        ]
        
        results = calculate_form_index(mock_standings)
        
        # Verify both drivers are processed
        self.assertEqual(len(results), 2)
        
        # Verify total probability matches exactly 100%
        total_percentage = sum(d['form_index'] for d in results)
        self.assertAlmostEqual(total_percentage, 100.0, places=4)
        
        # Max should have a higher score due to points and win bonus
        self.assertTrue(results[0]['form_index'] > results[1]['form_index'])

if __name__ == "__main__":
    unittest.main()
