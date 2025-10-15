#!/usr/bin/env python3
"""
Test script for SS2 and SS3 API integration
This script tests the external API integration without running the full Flask app
"""

import requests
import json
import sys
from datetime import datetime

# API Configuration
API_BASE_URL = "https://questions.aloc.com.ng/api/v2/q"
API_TOKEN = "QB-23b20d59287d87f94d94"
API_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'AccessToken': API_TOKEN
}

def test_api_connection():
    """Test basic API connection"""
    print("🔍 Testing API connection...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}?subject=chemistry",
            headers=API_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connection successful!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response contains: {len(data.get('data', []))} questions")
            return True
        else:
            print(f"❌ API connection failed!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed with error: {e}")
        return False

def test_ss2_ss3_subjects():
    """Test different subjects for SS2 and SS3"""
    subjects = ['chemistry', 'physics', 'mathematics', 'biology', 'english']
    class_levels = ['SS2', 'SS3']
    
    print("\n📚 Testing subjects for SS2 and SS3...")
    
    results = {}
    
    for subject in subjects:
        print(f"\n🔬 Testing {subject}...")
        try:
            response = requests.get(
                f"{API_BASE_URL}?subject={subject}",
                headers=API_HEADERS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                question_count = len(data.get('data', []))
                results[subject] = {
                    'success': True,
                    'question_count': question_count,
                    'status_code': response.status_code
                }
                print(f"   ✅ {subject}: {question_count} questions available")
            else:
                results[subject] = {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'status_code': response.status_code
                }
                print(f"   ❌ {subject}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            results[subject] = {
                'success': False,
                'error': str(e),
                'status_code': None
            }
            print(f"   ❌ {subject}: {e}")
    
    return results

def test_year_filtering():
    """Test year filtering functionality"""
    print("\n📅 Testing year filtering...")
    
    years = ['2024', '2023', '2022']
    subject = 'chemistry'
    
    for year in years:
        try:
            response = requests.get(
                f"{API_BASE_URL}?subject={subject}&year={year}",
                headers=API_HEADERS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                question_count = len(data.get('data', []))
                print(f"   ✅ {year}: {question_count} chemistry questions")
            else:
                print(f"   ❌ {year}: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {year}: {e}")

def display_sample_questions():
    """Display sample questions from the API"""
    print("\n📝 Sample Questions:")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}?subject=chemistry",
            headers=API_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Successfully retrieved questions data")
            print(f"   📊 Response structure: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            print(f"   📚 Questions available: {len(data.get('data', {})) if isinstance(data.get('data'), dict) else 'Unknown'}")
            print(f"   🎯 Subject: {data.get('subject', 'N/A')}")
            print(f"   📈 Status: {data.get('status', 'N/A')}")
        else:
            print(f"   Failed to fetch questions: HTTP {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   Error fetching sample questions: {e}")

def main():
    """Main test function"""
    print("🚀 SS2 & SS3 API Integration Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"🔑 Using token: {API_TOKEN[:10]}...")
    
    # Run tests
    connection_ok = test_api_connection()
    
    if connection_ok:
        subject_results = test_ss2_ss3_subjects()
        test_year_filtering()
        display_sample_questions()
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 30)
        successful_subjects = [s for s, r in subject_results.items() if r['success']]
        failed_subjects = [s for s, r in subject_results.items() if not r['success']]
        
        print(f"✅ Successful subjects: {', '.join(successful_subjects)}")
        if failed_subjects:
            print(f"❌ Failed subjects: {', '.join(failed_subjects)}")
        
        total_questions = sum(r.get('question_count', 0) for r in subject_results.values() if r['success'])
        print(f"📚 Total questions available: {total_questions}")
        
        print(f"\n🎉 Integration test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(successful_subjects) >= 3:
            print("✅ Integration appears to be working correctly!")
            return 0
        else:
            print("⚠️  Some subjects failed - check API availability")
            return 1
    else:
        print("❌ Basic API connection failed - check network and credentials")
        return 1

if __name__ == "__main__":
    sys.exit(main())
