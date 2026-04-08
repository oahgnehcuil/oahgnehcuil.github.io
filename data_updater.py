#!/usr/bin/env python3
"""
Data updater script for DAT.co Financial Monitor
This script can be run independently to update the data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import update_data, load_historical_data
import json

def main():
    """Main function to update data"""
    print("Starting data update...")
    
    # Update current data
    current_data = update_data()
    
    if current_data:
        print(f"✓ Data updated successfully!")
        print(f"  BTC Price: ${current_data['btc_price']}")
        print(f"  MSTR Price: ${current_data['mstr_price']}")
        print(f"  MNAV: ${current_data['mnav']}B")
        print(f"  Premium: {current_data['premium']}%")
        print(f"  Update Time: {current_data['time']}")
        
        # Show historical data summary
        historical_data = load_historical_data()
        print(f"  Historical data points: {len(historical_data['data'])}")
        
        return 0
    else:
        print("✗ Failed to update data")
        return 1

if __name__ == "__main__":
    sys.exit(main())
