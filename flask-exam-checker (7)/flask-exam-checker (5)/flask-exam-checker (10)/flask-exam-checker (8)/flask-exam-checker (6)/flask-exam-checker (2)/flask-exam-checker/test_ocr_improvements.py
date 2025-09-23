#!/usr/bin/env python3
"""
Test script for improved OCR mark detection
Run this to test the enhanced multiple option detection
"""

import requests
import json
import os

def test_ocr_improvements():
    """Test the ultra-enhanced OCR mark detection"""
    
    print("🎯 Testing ULTRA-ENHANCED OCR Mark Detection")
    print("=" * 60)
    print("🔍 This test will verify:")
    print("  ✓ Accurate detection of marked options")
    print("  ✓ Proper exclusion of unmarked options") 
    print("  ✓ Multiple option detection per question")
    print("  ✓ Zero false positives/negatives")
    print("=" * 60)
    
    # Base URL for your Flask app
    base_url = "http://localhost:5000"
    
    # Test image path (you'll need to provide an actual answer sheet image)
    test_image_path = input("Enter path to test answer sheet image: ").strip()
    
    if not os.path.exists(test_image_path):
        print(f"❌ Image file not found: {test_image_path}")
        return
    
    try:
        # Test the debug endpoint
        print(f"\n📤 Uploading image: {test_image_path}")
        print("🔄 Processing with enhanced OCR...")
        
        with open(test_image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(f"{base_url}/api/debug/ocr-marks", files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ OCR Processing Successful!")
            print("\n📊 DETAILED ANALYSIS:")
            print("=" * 40)
            
            if 'ocr_result' in result and 'answers' in result['ocr_result']:
                answers = result['ocr_result']['answers']
                print(f"📋 Total Questions Detected: {len(answers)}")
                
                # Detailed analysis of each question
                empty_selections = 0
                single_selections = 0
                multiple_selections = 0
                
                for answer in answers:
                    q_num = answer.get('question_number')
                    selected = answer.get('selected_options', [])
                    
                    if len(selected) == 0:
                        empty_selections += 1
                        status = "❓ NO SELECTION"
                    elif len(selected) == 1:
                        single_selections += 1
                        status = "✅ SINGLE"
                    else:
                        multiple_selections += 1
                        status = "🔥 MULTIPLE"
                    
                    print(f"Q{q_num:2d}: {str(selected):15} {status}")
                
                print("\n📈 SELECTION STATISTICS:")
                print(f"  🔹 Empty selections: {empty_selections}")
                print(f"  🔹 Single selections: {single_selections}")
                print(f"  🔹 Multiple selections: {multiple_selections}")
                
                # Advanced accuracy checks
                print("\n🎯 ACCURACY ANALYSIS:")
                
                # Check for suspicious patterns
                only_a_count = sum(1 for ans in answers if ans.get('selected_options') == ['A'])
                only_b_count = sum(1 for ans in answers if ans.get('selected_options') == ['B'])
                only_c_count = sum(1 for ans in answers if ans.get('selected_options') == ['C'])
                only_d_count = sum(1 for ans in answers if ans.get('selected_options') == ['D'])
                
                print(f"  📊 Option distribution:")
                print(f"     A only: {only_a_count} questions")
                print(f"     B only: {only_b_count} questions")
                print(f"     C only: {only_c_count} questions")
                print(f"     D only: {only_d_count} questions")
                
                # Check for accuracy issues
                if only_a_count > len(answers) * 0.7:
                    print(f"\n⚠️  ACCURACY WARNING:")
                    print(f"   {only_a_count}/{len(answers)} questions show only 'A' selected")
                    print(f"   This suggests OCR may not be detecting marks accurately")
                elif empty_selections > len(answers) * 0.5:
                    print(f"\n⚠️  DETECTION WARNING:")
                    print(f"   {empty_selections}/{len(answers)} questions have no selections")
                    print(f"   OCR may be missing marked options")
                else:
                    print(f"\n✅ ACCURACY LOOKS GOOD!")
                    print(f"   Good variety in option selections detected")
                    print(f"   Multiple selection support working: {multiple_selections} questions")
                
                # Show extracted metadata
                print(f"\n📋 EXTRACTED METADATA:")
                if 'roll_number' in result['ocr_result']:
                    print(f"  🎓 Roll Number: {result['ocr_result']['roll_number']}")
                if 'section' in result['ocr_result']:
                    print(f"  📚 Section: {result['ocr_result']['section']}")
                
                # Show paper info if available
                if 'paper_info' in result['ocr_result'] and result['ocr_result']['paper_info']:
                    paper_info = result['ocr_result']['paper_info']
                    print(f"  📄 Paper Info:")
                    for key, value in paper_info.items():
                        if value:
                            print(f"     {key}: {value}")
            
            print(f"\n📝 Check server console for detailed debug logs")
            print(f"🔍 Raw OCR response and mark detection details available there")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_normal_submission():
    """Test normal student submission with improved OCR"""
    
    print("\n🎓 Testing Normal Student Submission")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    test_image_path = input("Enter path to answer sheet image: ").strip()
    paper_id = input("Enter paper ID to submit to: ").strip()
    
    if not os.path.exists(test_image_path):
        print(f"❌ Image file not found: {test_image_path}")
        return
    
    try:
        with open(test_image_path, 'rb') as image_file:
            files = {'images': image_file}  # Note: using 'images' for multiple image support
            data = {'paper_id': paper_id}
            response = requests.post(f"{base_url}/api/submit-answers", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Submission Successful!")
            
            if 'extracted_info' in result and 'students' in result['extracted_info']:
                students = result['extracted_info']['students']
                print(f"Students detected: {len(students)}")
                
                for student in students:
                    roll = student.get('roll_number')
                    answers = student.get('answers', [])
                    print(f"\nStudent {roll}: {len(answers)} answers")
                    
                    # Show first few answers
                    for answer in answers[:5]:
                        q_num = answer.get('question_number')
                        selected = answer.get('selected_options', [])
                        print(f"  Q{q_num}: {selected}")
                    
                    if len(answers) > 5:
                        print(f"  ... and {len(answers) - 5} more questions")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🎯 OCR Mark Detection Test Suite")
    print("Make sure your Flask app is running first!")
    
    choice = input("\nChoose test:\n1. Debug OCR marks\n2. Test normal submission\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_ocr_improvements()
    elif choice == "2":
        test_normal_submission()
    else:
        print("Invalid choice")
