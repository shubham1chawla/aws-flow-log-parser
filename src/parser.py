import csv
from collections import defaultdict
import sys

class FlowLogParser:
    def __init__(self, lookup_file):
        self.port_protocol_mapping = {}
        self.load_lookup_table(lookup_file)
        self.tag_counts = defaultdict(int)
        self.port_protocol_counts = defaultdict(int)
        
    def load_lookup_table(self, lookup_file):
        """Load and parse the lookup table CSV file."""
        try:
            with open(lookup_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert port to int and protocol to lowercase
                    port = int(row['dstport'])
                    protocol = self.normalize_protocol(row['protocol'])
                    tag = row['tag'].strip()
                    # Create mapping key
                    key = (port, protocol)
                    self.port_protocol_mapping[key] = tag
        except Exception as e:
            print(f"Error loading lookup table: {e}")
            sys.exit(1)

    def normalize_protocol(self, protocol):
        """Normalize protocol string for comparison."""
        protocol_map = {
            'tcp': 6,
            'udp': 17,
            'icmp': 1
        }
        if isinstance(protocol, str):
            return protocol_map.get(protocol.lower(), protocol)
        return protocol
    
    def textualize_protocol(self, protocol_num):
        """Textualize protocol number for report."""
        protocol_map = {
            6: 'tcp',
            17: 'udp',
            1: 'icmp',
        }
        return protocol_map[protocol_num]

    def get_tag_for_flow(self, port, protocol):
        """Get the tag for a given port/protocol combination."""
        key = (port, int(protocol))
        return self.port_protocol_mapping.get(key, "Untagged")

    def parse_flow_log_line(self, line):
        """Parse a single flow log line and return relevant fields."""
        fields = line.strip().split()
        if len(fields) < 14:  # Minimum fields for version 2
            return None
        
        try:
            # Extract relevant fields (using version 2 format)
            dstport = int(fields[6])
            protocol = int(fields[7])
            return dstport, protocol
        except (ValueError, IndexError):
            return None

    def process_flow_logs(self, flow_log_file):
        """Process the flow log file and update counts."""
        try:
            with open(flow_log_file, 'r') as f:
                for line in f:
                    result = self.parse_flow_log_line(line)
                    if result:
                        dstport, protocol = result
                        # Update port/protocol counts
                        self.port_protocol_counts[(dstport, protocol)] += 1
                        # Update tag counts
                        tag = self.get_tag_for_flow(dstport, protocol)
                        self.tag_counts[tag] += 1
        except Exception as e:
            print(f"Error processing flow logs: {e}")
            sys.exit(1)

    def generate_reports(self, output_file):
        """Generate the required reports and write to output file."""
        try:
            with open(output_file, 'w') as f:
                # Write tag counts
                f.write("Tag Counts:\n")
                f.write("Tag,Count\n")
                for tag, count in sorted(self.tag_counts.items()):
                    f.write(f"{tag},{count}\n")
                
                # Write port/protocol combination counts
                f.write("\nPort/Protocol Combination Counts:\n")
                f.write("Port,Protocol,Count\n")
                for (port, protocol), count in sorted(self.port_protocol_counts.items()):
                    textual_protocol = self.textualize_protocol(protocol)
                    f.write(f"{port},{textual_protocol},{count}\n")
        except Exception as e:
            print(f"Error generating reports: {e}")
            sys.exit(1)
