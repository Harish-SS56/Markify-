#!/usr/bin/env python3
"""
Universal OCR Test Script - Tests all marking styles
This script tests the enhanced OCR system that detects marks in ANY position
"""

import requests
import json
import os

def test_universal_ocr():
    """Test the universal OCR system with different marking styles"""
    
    print("🌟 UNIVERSAL OCR DETECTION TEST")
    print("=" * 60)
    print("🎯 This test verifies detection of:")
    print("  ✅ Marks ABOVE options (floating above letters)")
    print("  ✅ Marks THROUGH options (crossing through letters)")
    print("  ✅ Marks ON options (directly on letters)")
    print("  ✅ Marks AROUND options (circles, boxes)")
    print("  ✅ Marks NEAR options (vicinity of letters)")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test multiple images with different marking styles
    test_images = []
    
    while True:
        image_path = input(f"\nEnter path to test image {len(test_images) + 1} (or 'done' to finish): ").strip()
        if image_path.lower() == 'done':
            break
        if os.path.exists(image_path):
            test_images.append(image_path)
            print(f"✅ Added: {image_path}")
        else:
            print(f"❌ File not found: {image_path}")
    
    if not test_images:
        print("❌ No test images provided")
        return
    
    print(f"\n🚀 Testing {len(test_images)} images with Universal OCR...")
    
    for i, image_path in enumerate(test_images, 1):
        print(f"\n{'='*60}")
        print(f"📋 TEST {i}: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                response = requests.post(f"{base_url}/api/debug/ocr-marks", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ OCR Processing Successful!")
                
                if 'ocr_result' in result and 'answers' in result['ocr_result']:
                    answers = result['ocr_result']['answers']
                    
                    print(f"\n📊 DETECTION RESULTS:")
                    print(f"Questions detected: {len(answers)}")
                    
                    # Analyze marking patterns
                    empty_count = 0
                    single_count = 0
                    multiple_count = 0
                    
                    print(f"\n📋 QUESTION-BY-QUESTION ANALYSIS:")
                    for answer in answers:
                        q_num = answer.get('question_number')
                        selected = answer.get('selected_options', [])
                        
                        if len(selected) == 0:
                            empty_count += 1
                            status = "❓ EMPTY"
                        elif len(selected) == 1:
                            single_count += 1
                            status = "✅ SINGLE"
                        else:
                            multiple_count += 1
                            status = "🔥 MULTIPLE"
                        
                        print(f"  Q{q_num:2d}: {str(selected):20} {status}")
                    
                    print(f"\n📈 PATTERN ANALYSIS:")
                    print(f"  🔹 Empty selections: {empty_count}")
                    print(f"  🔹 Single selections: {single_count}")
                    print(f"  🔹 Multiple selections: {multiple_count}")
                    
                    # Check for accuracy indicators
                    total_questions = len(answers)
                    if total_questions > 0:
                        # Option distribution analysis
                        option_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
                        for answer in answers:
                            for option in answer.get('selected_options', []):
                                if option in option_counts:
                                    option_counts[option] += 1
                        
                        print(f"\n📊 OPTION DISTRIBUTION:")
                        for option, count in option_counts.items():
                            percentage = (count / total_questions) * 100
                            print(f"  {option}: {count} times ({percentage:.1f}%)")
                        
                        # Accuracy assessment
                        max_single_option = max(option_counts.values())
                        if max_single_option > total_questions * 0.8:
                            print(f"\n⚠️  POTENTIAL ISSUE:")
                            print(f"   One option appears in {max_single_option}/{total_questions} questions")
                            print(f"   This might indicate detection problems")
                        else:
                            print(f"\n✅ DETECTION LOOKS GOOD!")
                            print(f"   Good distribution across options")
                    
                    # Show metadata
                    if 'roll_number' in result['ocr_result']:
                        print(f"\n🎓 Roll Number: {result['ocr_result']['roll_number']}")
                    if 'section' in result['ocr_result']:
                        print(f"📚 Section: {result['ocr_result']['section']}")
                
                print(f"\n📝 Check server console for detailed debug logs")
                
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
        
        except Exception as e:
            print(f"❌ Error processing {image_path}: {e}")
    
    print(f"\n🎯 UNIVERSAL OCR TEST COMPLETE!")
    print("Check the results above to verify all marking styles are detected correctly.")

def compare_marking_styles():
    """Compare detection results between different marking styles"""
    
    print("\n🔄 MARKING STYLE COMPARISON")
    print("=" * 50)
    
    style1_path = input("Enter path to 'marks through options' image: ").strip()
    style2_path = input("Enter path to 'marks above options' image: ").strip()
    
    if not (os.path.exists(style1_path) and os.path.exists(style2_path)):
        print("❌ One or both image files not found")
        return
    
    base_url = "http://localhost:5000"
    
    results = {}
    
    for style_name, image_path in [("Through Options", style1_path), ("Above Options", style2_path)]:
        print(f"\n📋 Testing {style_name} style...")
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                response = requests.post(f"{base_url}/api/debug/ocr-marks", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if 'ocr_result' in result and 'answers' in result['ocr_result']:
                    results[style_name] = result['ocr_result']['answers']
                    print(f"✅ {len(results[style_name])} questions detected")
                else:
                    print(f"❌ No answers detected")
            else:
                print(f"❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Compare results
    if len(results) == 2:
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"{'Question':<10} {'Through':<15} {'Above':<15} {'Match':<10}")
        print("-" * 50)
        
        style1_answers = results["Through Options"]
        style2_answers = results["Above Options"]
        
        max_questions = max(len(style1_answers), len(style2_answers))
        
        for i in range(max_questions):
            q_num = i + 1
            
            style1_sel = style1_answers[i].get('selected_options', []) if i < len(style1_answers) else []
            style2_sel = style2_answers[i].get('selected_options', []) if i < len(style2_answers) else []
            
            match = "✅" if style1_sel == style2_sel else "❌"
            
            print(f"Q{q_num:<9} {str(style1_sel):<15} {str(style2_sel):<15} {match}")
        
        print(f"\n🎯 Both marking styles should be detected accurately!")

if __name__ == "__main__":
    print("🌟 UNIVERSAL OCR TESTING SUITE")
    print("Make sure your Flask app is running first!")
    
    choice = input("\nChoose test:\n1. Universal OCR test\n2. Compare marking styles\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_universal_ocr()
    elif choice == "2":
        compare_marking_styles()
    else:
        print("Invalid choice")
