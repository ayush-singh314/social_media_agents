#!/usr/bin/env python3
"""
Simple test script to verify the Content Ideation Agent API server is working
"""

import requests
import json

def test_server():
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Content Ideation Agent API Server")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might not be running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing Root Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Generate Ideas
    print("\n3. Testing Generate Ideas...")
    try:
        test_data = {
            "user_niche": "AI Technology",
            "platform_choice": "linkedin",
            "media_url": None
        }
        response = requests.post(
            f"{base_url}/api/generate-ideas",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Generate ideas working")
            data = response.json()
            print(f"   Generated {len(data['ideas'])} ideas for {data['niche']}")
        else:
            print(f"❌ Generate ideas failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Server test completed!")
    return True

if __name__ == "__main__":
    test_server()
