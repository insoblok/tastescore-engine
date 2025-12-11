"""Test script for sanctions and mixers feature."""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8080"


def test_api_health():
    """Test if API is running."""
    print("=" * 50)
    print("Test 1: API Health Check")
    print("=" * 50)
    try:
        response = requests.get(f"{BASE_URL}/api")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ofac_ingestion():
    """Test OFAC ingestion."""
    print("\n" + "=" * 50)
    print("Test 2: OFAC Ingestion")
    print("=" * 50)
    try:
        response = requests.post(f"{BASE_URL}/api/sanctions/ingest")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_check_address(address: str, chain: str, expected_label: str = None):
    """Test address checking."""
    print("\n" + "=" * 50)
    print(f"Test 3: Check Address ({address[:10]}...)")
    print("=" * 50)
    try:
        response = requests.get(
            f"{BASE_URL}/api/sanctions/check",
            params={"address": address, "chain": chain}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if expected_label:
            actual_label = data.get("data", {}).get("label")
            if actual_label == expected_label:
                print(f"✓ Expected label '{expected_label}' found")
                return True
            else:
                print(f"✗ Expected label '{expected_label}', got '{actual_label}'")
                return False
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_calculate_metrics(address: str, chain: str, transactions: list):
    """Test metrics calculation."""
    print("\n" + "=" * 50)
    print(f"Test 4: Calculate Metrics ({address[:10]}...)")
    print("=" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/api/sanctions/calculate-metrics",
            params={"address": address, "chain": chain},
            json=transactions
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_metrics(address: str, chain: str):
    """Test getting metrics."""
    print("\n" + "=" * 50)
    print(f"Test 5: Get Metrics ({address[:10]}...)")
    print("=" * 50)
    try:
        response = requests.get(
            f"{BASE_URL}/api/sanctions/metrics",
            params={"address": address, "chain": chain}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_get_risk_flags(address: str, chain: str):
    """Test getting risk flags."""
    print("\n" + "=" * 50)
    print(f"Test 6: Get Risk Flags ({address[:10]}...)")
    print("=" * 50)
    try:
        response = requests.get(
            f"{BASE_URL}/api/sanctions/risk-flags",
            params={"address": address, "chain": chain}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("SANCTIONS & MIXERS FEATURE TEST SUITE")
    print("=" * 50)
    
    results = []
    
    # Test 1: API Health
    results.append(("API Health", test_api_health()))
    
    # Test 2: OFAC Ingestion
    print("\n⏳ Running OFAC ingestion (this may take a minute)...")
    results.append(("OFAC Ingestion", test_ofac_ingestion()))
    time.sleep(2)  # Wait for ingestion to complete
    
    # Known Tornado Cash address (0.1 ETH mixer)
    tornado_cash_addr = "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc"
    
    # Test 3: Check Tornado Cash address
    results.append(("Check Tornado Cash Address", 
                   test_check_address(tornado_cash_addr, "ETH", "mixer")))
    
    # Test 4: Calculate metrics
    test_transactions = [
        {
            "time": int(time.time()) - 86400,  # 1 day ago
            "src": tornado_cash_addr,
            "dst": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "amount": 0.1,
            "value": 0.1
        }
    ]
    results.append(("Calculate Metrics", 
                   test_calculate_metrics(tornado_cash_addr, "ETH", test_transactions)))
    
    # Test 5: Get metrics
    results.append(("Get Metrics", 
                   test_get_metrics(tornado_cash_addr, "ETH")))
    
    # Test 6: Get risk flags
    results.append(("Get Risk Flags", 
                   test_get_risk_flags(tornado_cash_addr, "ETH")))
    
    # Test 7: Check clean address
    clean_addr = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    results.append(("Check Clean Address", 
                   test_check_address(clean_addr, "ETH", None)))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

