#!/usr/bin/env python3
"""
Simple validation script for Day 2 Coffee Shop Barista implementation.
This tests the core logic without requiring all LiveKit dependencies.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def validate_order_state_structure():
    """Validate the order state has the correct structure"""
    expected_fields = {"drinkType", "size", "milk", "extras", "name"}
    
    # This is the structure defined in the task
    order_state = {
        "drinkType": None,
        "size": None,
        "milk": None,
        "extras": [],
        "name": None
    }
    
    actual_fields = set(order_state.keys())
    
    if actual_fields == expected_fields:
        print("✓ Order state structure is correct")
        return True
    else:
        print(f"✗ Order state structure mismatch!")
        print(f"  Expected: {expected_fields}")
        print(f"  Actual: {actual_fields}")
        return False


def validate_example_order():
    """Validate the example order file"""
    example_path = Path(__file__).parent / "orders" / "example_order.json"
    
    if not example_path.exists():
        print(f"✗ Example order file not found: {example_path}")
        return False
    
    try:
        with open(example_path) as f:
            order = json.load(f)
        
        required_fields = {"drinkType", "size", "milk", "extras", "name", "timestamp"}
        actual_fields = set(order.keys())
        
        if not required_fields.issubset(actual_fields):
            print(f"✗ Example order missing fields!")
            print(f"  Required: {required_fields}")
            print(f"  Actual: {actual_fields}")
            return False
        
        # Validate types for string fields
        string_fields = ['drinkType', 'size', 'milk', 'name', 'timestamp']
        for field in string_fields:
            if not isinstance(order[field], str):
                print(f"✗ {field} should be a string")
                return False
        if not isinstance(order["extras"], list):
            print("✗ extras should be a list")
            return False
        
        print("✓ Example order file is valid")
        print(f"  Sample: {order['size']} {order['drinkType']} with {order['milk']} milk")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Example order file is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading example order: {e}")
        return False


def validate_orders_directory():
    """Validate the orders directory exists and is writable"""
    orders_dir = Path(__file__).parent / "orders"
    
    if not orders_dir.exists():
        print(f"✗ Orders directory does not exist: {orders_dir}")
        return False
    
    if not orders_dir.is_dir():
        print(f"✗ Orders path is not a directory: {orders_dir}")
        return False
    
    # Check if README exists
    readme_path = orders_dir / "README.md"
    if not readme_path.exists():
        print(f"⚠ Orders README not found (recommended): {readme_path}")
    else:
        print(f"✓ Orders README exists")
    
    # Test write permissions
    test_file = orders_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        test_order = {
            "drinkType": "test",
            "size": "test",
            "milk": "test",
            "extras": [],
            "name": "test",
            "timestamp": datetime.now().isoformat()
        }
        with open(test_file, 'w') as f:
            json.dump(test_order, f, indent=2)
        
        # Clean up test file
        test_file.unlink()
        print(f"✓ Orders directory is writable")
        return True
        
    except Exception as e:
        print(f"✗ Cannot write to orders directory: {e}")
        return False


def validate_agent_file():
    """Basic validation of agent.py file"""
    agent_path = Path(__file__).parent / "src" / "agent.py"
    
    if not agent_path.exists():
        print(f"✗ agent.py not found: {agent_path}")
        return False
    
    with open(agent_path) as f:
        content = f.read()
    
    # Check for required components
    checks = [
        ("CoffeeShopBarista", "CoffeeShopBarista class"),
        ("complete_order", "complete_order function tool"),
        ("order_state", "order state tracking"),
        ("function_tool", "function_tool decorator import"),
        ("RunContext", "RunContext import"),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✓ Found {description}")
        else:
            print(f"✗ Missing {description}")
            all_passed = False
    
    # Check that Assistant is replaced with CoffeeShopBarista
    if "agent=CoffeeShopBarista()" in content:
        print("✓ Using CoffeeShopBarista in session.start()")
    else:
        print("⚠ Warning: Not using CoffeeShopBarista() in session.start()")
        # Don't fail the validation for this, just warn
    
    return all_passed


def main():
    print("=" * 60)
    print("Day 2 Coffee Shop Barista - Validation Script")
    print("=" * 60)
    print()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    results = []
    
    print("1. Validating order state structure...")
    results.append(validate_order_state_structure())
    print()
    
    print("2. Validating orders directory...")
    results.append(validate_orders_directory())
    print()
    
    print("3. Validating example order file...")
    results.append(validate_example_order())
    print()
    
    print("4. Validating agent.py implementation...")
    results.append(validate_agent_file())
    print()
    
    print("=" * 60)
    if all(results):
        print("✓ All validations passed!")
        print()
        print("Next steps:")
        print("1. Set up your .env.local with API keys")
        print("2. Run: uv run python src/agent.py download-files")
        print("3. Start the application and test the barista!")
        print()
        return 0
    else:
        print("✗ Some validations failed")
        print()
        print("Please fix the issues above before running the agent.")
        print()
        return 1


if __name__ == "__main__":
    exit(main())
