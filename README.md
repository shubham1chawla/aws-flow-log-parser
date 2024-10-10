# Flow Log Parser

A Python utility for parsing AWS VPC Flow Logs and mapping them to tags based on destination port and protocol combinations.

## Overview

This tool processes AWS VPC Flow Logs and maps each flow to a tag based on a lookup table. The lookup table is defined in a CSV file with three columns: dstport, protocol, and tag. The destination port and protocol combination determines which tag is applied to each flow.

## Requirements

- Python 3.6 or higher
- No additional external dependencies required

## Project Structure

```
[ROOT]/
│
├── src/
│   ├── __init__.py     # Empty file to mark directory as Python package
│   └── parser.py       # Contains the FlowLogParser class
│
├── tests/
│   ├── __init__.py     # Empty file to mark directory as Python package
│   └── test_parser.py  # Test cases
│
├── main.py             # Entry point for the CLI interface
└── README.md           # This file
```

## Installation

Clone the repository:
```bash
git clone https://github.com/shubham1chawla/aws-flow-log-parser.git
cd aws-flow-log-parser
```

## Usage

The program can be run from the command line with three required arguments:

```bash
python main.py ./data/flow.logs ./data/lookup.csv ./data/report
```

### Input Files

1. Flow Log File:
   - Plain text file containing AWS VPC Flow Log records
   - Must be in default format (Version 2)
   - Maximum file size: 10MB

2. Lookup Table File:
   - CSV file with header row
   - Columns: dstport,protocol,tag
   - Maximum entries: 10000

Example lookup table format:
```csv
dstport,protocol,tag
25,tcp,sv_P1
443,tcp,sv_P2
110,tcp,email
```

### Output

The program generates a report file containing:
1. Count of matches for each tag
2. Count of matches for each port/protocol combination

Example output:
```
Tag Counts:
Tag,Count
Untagged,8
email,3
sv_P1,2
sv_P2,1

Port/Protocol Combination Counts:
Port,Protocol,Count
23,tcp,1
25,tcp,1
80,tcp,1
110,tcp,1
143,tcp,1
443,tcp,1
993,tcp,1
1024,tcp,1
49153,tcp,1
49154,tcp,1
49155,tcp,1
49156,tcp,1
49157,tcp,1
49158,tcp,1
```

## Testing

To run the test suite:

```bash
# Run all tests
python -m unittest discover

# Run specific test file with verbose output
python -m unittest -v tests.test_parser
```

The test suite includes:
- Unit tests for all major functionality
- Integration tests for file processing
- Edge case handling
- Test data based on provided sample logs

## Assumptions and Limitations

1. Flow Log Format:
   - Only supports Version 2 flow logs
   - Only supports default format (not custom formats)
   - Fields must be space-separated
   - Minimum of 14 fields per line required

2. Protocol Handling:
   - Protocols are mapped as follows:
     - TCP = 6
     - UDP = 17
     - ICMP = 1
   - Protocol matching is case-insensitive

3. File Requirements:
   - Input files must be UTF-8 encoded
   - Flow log file size limited to 10MB
   - Lookup table limited to 10000 entries
   - Files must be accessible with read permissions

4. Tag Mapping:
   - Multiple port/protocol combinations can map to the same tag
   - Unknown combinations are marked as "Untagged"
   - Tag matching is case-sensitive

5. Error Handling:
   - Invalid flow log lines are skipped
   - File access errors terminate the program
   - Invalid lookup table entries are ignored

## Performance Considerations

- Files are processed line by line to minimize memory usage
- Lookup table is stored in memory for faster access
- Port/protocol combinations are cached in a dictionary
- Large files (>10MB) should be split before processing

## Development Notes

1. Code Organization:
   - Main functionality encapsulated in FlowLogParser class
   - Separate test suite with comprehensive coverage
   - Modular design for easy extension

2. Testing Strategy:
   - Unit tests for individual components
   - Integration tests for full workflow
   - Test data matches provided examples
   - Temporary files used for testing

3. Error Handling:
   - Robust error checking for file operations
   - Clear error messages for common issues
   - Graceful handling of invalid input

## Future Improvements

1. Potential Enhancements:
   - Support for custom flow log formats
   - Support for additional flow log versions
   - Parallel processing for large files
   - Additional report formats (JSON, CSV)
   - Command-line interface improvements

2. Known Limitations:
   - No support for compressed files
   - No real-time processing
   - Single-threaded execution
