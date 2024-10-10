import unittest
import os
import sys
from tempfile import NamedTemporaryFile

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.parser import FlowLogParser

class TestFlowLogParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temporary files for testing
        # Sample flow logs
        cls.flow_log_data = """2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-4d3c2b1a 192.168.1.100 203.0.113.101 23 49154 6 15 12000 1620140761 1620140821 REJECT OK
2 123456789012 eni-5e6f7g8h 192.168.1.101 198.51.100.3 25 49155 6 10 8000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-9h8g7f6e 172.16.0.100 203.0.113.102 110 49156 6 12 9000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-7i8j9k0l 172.16.0.101 192.0.2.203 993 49157 6 8 5000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-6m7n8o9p 10.0.2.200 198.51.100.4 143 49158 6 18 14000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-1a2b3c4d 192.168.0.1 203.0.113.12 1024 80 6 10 5000 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-1a2b3c4d 203.0.113.12 192.168.0.1 80 1024 6 12 6000 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-1a2b3c4d 10.0.1.102 172.217.7.228 1030 443 6 8 4000 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-5f6g7h8i 10.0.2.103 52.26.198.183 56000 23 6 15 7500 1620140661 1620140721 REJECT OK
2 123456789012 eni-9k10l11m 192.168.1.5 51.15.99.115 49321 25 6 20 10000 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-1a2b3c4d 192.168.1.6 87.250.250.242 49152 110 6 5 2500 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-2d2e2f3g 192.168.2.7 77.88.55.80 49153 993 6 7 3500 1620140661 1620140721 ACCEPT OK
2 123456789012 eni-4h5i6j7k 172.16.0.2 192.0.2.146 49154 143 6 9 4500 1620140661 1620140721 ACCEPT OK"""

        # Sample lookup table
        cls.lookup_data = """dstport,protocol,tag
25,tcp,sv_P1
68,udp,sv_P2
23,tcp,sv_P1
31,udp,SV_P3
443,tcp,sv_P2
22,tcp,sv_P4
3389,tcp,sv_P5
0,icmp,sv_P5
110,tcp,email
993,tcp,email
143,tcp,email"""

        # Create temporary directory for test files if it doesn't exist
        cls.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(cls.test_dir, exist_ok=True)

        # Create temporary files in the test directory
        cls.flow_log_file = NamedTemporaryFile(mode='w', delete=False, dir=cls.test_dir)
        cls.lookup_file = NamedTemporaryFile(mode='w', delete=False, dir=cls.test_dir)
        cls.output_file = NamedTemporaryFile(mode='w', delete=False, dir=cls.test_dir)

        # Write sample data to temporary files
        cls.flow_log_file.write(cls.flow_log_data)
        cls.lookup_file.write(cls.lookup_data)
        
        cls.flow_log_file.close()
        cls.lookup_file.close()
        cls.output_file.close()

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary files
        for file_path in [cls.flow_log_file.name, cls.lookup_file.name, cls.output_file.name]:
            try:
                os.unlink(file_path)
            except OSError:
                pass
        
        # Remove test directory if empty
        try:
            os.rmdir(cls.test_dir)
        except OSError:
            pass

    def setUp(self):
        # Create a new parser instance for each test
        self.parser = FlowLogParser(self.lookup_file.name)

    # Rest of the test methods remain the same as in the previous version
    def test_load_lookup_table(self):
        """Test if lookup table is loaded correctly"""
        self.assertEqual(self.parser.port_protocol_mapping[(25, 6)], "sv_P1")
        self.assertEqual(self.parser.port_protocol_mapping[(443, 6)], "sv_P2")
        self.assertEqual(self.parser.port_protocol_mapping[(110, 6)], "email")

    def test_normalize_protocol(self):
        """Test protocol normalization"""
        self.assertEqual(self.parser.normalize_protocol("tcp"), 6)
        self.assertEqual(self.parser.normalize_protocol("TCP"), 6)
        self.assertEqual(self.parser.normalize_protocol("udp"), 17)
        self.assertEqual(self.parser.normalize_protocol("icmp"), 1)
        self.assertEqual(self.parser.normalize_protocol("6"), "6")

    def test_textualize_protocol(self):
        """Test protocol normalization"""
        self.assertEqual(self.parser.textualize_protocol(6), "tcp")
        self.assertEqual(self.parser.textualize_protocol(17), "udp")
        self.assertEqual(self.parser.textualize_protocol(1), "icmp")

    def test_get_tag_for_flow(self):
        """Test tag lookup for flows"""
        self.assertEqual(self.parser.get_tag_for_flow(25, 6), "sv_P1")
        self.assertEqual(self.parser.get_tag_for_flow(443, 6), "sv_P2")
        self.assertEqual(self.parser.get_tag_for_flow(110, 6), "email")
        self.assertEqual(self.parser.get_tag_for_flow(8080, 6), "Untagged")

    def test_parse_flow_log_line(self):
        """Test parsing of flow log lines"""
        test_line = "2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK"
        dstport, protocol = self.parser.parse_flow_log_line(test_line)
        self.assertEqual(dstport, 49153)
        self.assertEqual(protocol, 6)

        # Test invalid line
        invalid_line = "invalid flow log line"
        self.assertIsNone(self.parser.parse_flow_log_line(invalid_line))

    def test_process_flow_logs(self):
        """Test processing of flow logs"""
        self.parser.process_flow_logs(self.flow_log_file.name)
        
        # Test tag counts
        expected_tag_counts = {
            "sv_P1": 2,
            "sv_P2": 1,
            "email": 3,
            "Untagged": 8,
        }
        
        for tag, expected_count in expected_tag_counts.items():
            if expected_count > 0:
                self.assertEqual(self.parser.tag_counts[tag], expected_count)

    def test_generate_reports(self):
        """Test report generation"""
        self.parser.process_flow_logs(self.flow_log_file.name)
        self.parser.generate_reports(self.output_file.name)
        
        # Verify the output file exists and contains the expected sections
        with open(self.output_file.name, 'r') as f:
            content = f.read()
            
            # Check for section headers
            self.assertIn("Tag Counts:", content)
            self.assertIn("Port/Protocol Combination Counts:", content)
            
            # Check for specific tag counts
            self.assertIn("sv_P1,2", content)
            self.assertIn("sv_P2,1", content)
            self.assertIn("email,3", content)
            self.assertIn("Untagged,8", content)

    def test_case_insensitive_matching(self):
        """Test case insensitive protocol matching"""
        self.assertEqual(self.parser.normalize_protocol("TCP"), 
                        self.parser.normalize_protocol("tcp"))
        self.assertEqual(self.parser.normalize_protocol("UDP"), 
                        self.parser.normalize_protocol("udp"))

if __name__ == '__main__':
    unittest.main()