#!/usr/bin/env python3

from src.parser import FlowLogParser
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python main.py <flow_log_file> <lookup_file> <output_file>")
        sys.exit(1)

    flow_log_file = sys.argv[1]
    lookup_file = sys.argv[2]
    output_file = sys.argv[3]

    # Initialize parser
    parser = FlowLogParser(lookup_file)
    
    # Process flow logs
    parser.process_flow_logs(flow_log_file)
    
    # Generate reports
    parser.generate_reports(output_file)

if __name__ == "__main__":
    main()