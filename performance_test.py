#!/usr/bin/env python3
"""
Basic performance testing script for the Customer Management API
This script tests the key endpoints and measures response times
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json

API_BASE_URL = "http://localhost:8000"

class PerformanceTester:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_test_user(self) -> bool:
        """Create a test user for authentication"""
        url = f"{self.base_url}/auth/create/user"
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            async with self.session.post(url, json=test_user) as response:
                return response.status in [200, 201]
        except Exception as e:
            print(f"Warning: Could not create test user - {e}")
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate and get token"""
        url = f"{self.base_url}/auth/token"
        auth_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        try:
            async with self.session.post(url, data=auth_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    return True
                return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    async def measure_endpoint(self, method: str, endpoint: str, 
                              data: dict = None, iterations: int = 10) -> Dict:
        """Measure performance of a specific endpoint"""
        if not self.auth_token:
            return {"error": "Not authenticated"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        url = f"{self.base_url}{endpoint}"
        response_times = []
        status_codes = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, headers=headers) as response:
                        end_time = time.time()
                        response_times.append(end_time - start_time)
                        status_codes.append(response.status)
                        
                elif method.upper() == "POST":
                    async with self.session.post(url, headers=headers, json=data) as response:
                        end_time = time.time()
                        response_times.append(end_time - start_time)
                        status_codes.append(response.status)
                        
            except Exception as e:
                print(f"Request failed: {e}")
                continue
                
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        if not response_times:
            return {"error": "No successful requests"}
        
        return {
            "endpoint": endpoint,
            "method": method.upper(),
            "iterations": len(response_times),
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "median_response_time": statistics.median(response_times),
            "status_codes": list(set(status_codes)),
            "success_rate": len([s for s in status_codes if 200 <= s < 300]) / len(status_codes) * 100
        }
    
    async def run_tests(self) -> List[Dict]:
        """Run performance tests on key endpoints"""
        print("🧪 Starting performance tests...")
        
        # Check if API is running
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status != 200:
                    print("❌ API is not running or healthy")
                    return []
        except:
            print("❌ Cannot connect to API. Make sure it's running on the correct port.")
            return []
        
        # Create test user and authenticate
        print("Setting up test user...")
        await self.create_test_user()
        
        if not await self.authenticate():
            print("❌ Authentication failed")
            return []
        
        print("✅ Authentication successful")
        
        # Define test endpoints
        test_cases = [
            {"method": "GET", "endpoint": "/", "iterations": 20},
            {"method": "GET", "endpoint": "/health", "iterations": 20},
            {"method": "GET", "endpoint": "/users/", "iterations": 15},
            {"method": "GET", "endpoint": "/musteriler/", "iterations": 15},
            {"method": "GET", "endpoint": "/musteriler/?limit=10", "iterations": 15},
            {"method": "GET", "endpoint": "/musteriler/?search=test", "iterations": 10},
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"Testing {test_case['method']} {test_case['endpoint']}...")
            result = await self.measure_endpoint(**test_case)
            results.append(result)
            
            if "error" not in result:
                print(f"  ✅ Avg: {result['avg_response_time']:.3f}s, "
                      f"Success: {result['success_rate']:.1f}%")
            else:
                print(f"  ❌ {result['error']}")
        
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print performance test summary"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        successful_tests = [r for r in results if "error" not in r]
        
        if not successful_tests:
            print("❌ No successful tests")
            return
        
        # Overall statistics
        all_response_times = []
        for result in successful_tests:
            all_response_times.append(result['avg_response_time'])
        
        print(f"Total endpoints tested: {len(successful_tests)}")
        print(f"Overall average response time: {statistics.mean(all_response_times):.3f}s")
        print(f"Fastest endpoint: {min(all_response_times):.3f}s")
        print(f"Slowest endpoint: {max(all_response_times):.3f}s")
        
        print("\n📈 DETAILED RESULTS:")
        print("-" * 60)
        
        for result in successful_tests:
            print(f"Endpoint: {result['method']} {result['endpoint']}")
            print(f"  Average: {result['avg_response_time']:.3f}s")
            print(f"  Min/Max: {result['min_response_time']:.3f}s / {result['max_response_time']:.3f}s")
            print(f"  Success Rate: {result['success_rate']:.1f}%")
            print(f"  Iterations: {result['iterations']}")
            print()
        
        # Performance grades
        fast_endpoints = [r for r in successful_tests if r['avg_response_time'] < 0.1]
        medium_endpoints = [r for r in successful_tests if 0.1 <= r['avg_response_time'] < 0.5]
        slow_endpoints = [r for r in successful_tests if r['avg_response_time'] >= 0.5]
        
        print("🎯 PERFORMANCE GRADES:")
        print(f"  🟢 Fast (<100ms): {len(fast_endpoints)} endpoints")
        print(f"  🟡 Medium (100-500ms): {len(medium_endpoints)} endpoints")
        print(f"  🔴 Slow (>500ms): {len(slow_endpoints)} endpoints")
        
        if slow_endpoints:
            print("\n⚠️  SLOW ENDPOINTS NEED ATTENTION:")
            for endpoint in slow_endpoints:
                print(f"  - {endpoint['method']} {endpoint['endpoint']}: {endpoint['avg_response_time']:.3f}s")

async def main():
    async with PerformanceTester() as tester:
        results = await tester.run_tests()
        tester.print_summary(results)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Performance tests interrupted by user")
    except Exception as e:
        print(f"❌ Performance test failed: {e}")