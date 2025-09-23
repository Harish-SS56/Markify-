#!/usr/bin/env python3
"""
Test script for the new partial marking system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import calculate_partial_marks

def test_partial_marking():
    """Test all scenarios of the partial marking system"""
    
    print("🧪 TESTING PARTIAL MARKING SYSTEM")
    print("=" * 60)
    
    # Test cases: (student_options, correct_options, total_marks, expected_result)
    test_cases = [
        # FULL MARKS SCENARIOS
        {
            'name': 'Full Marks - Single Option',
            'student': ['A'],
            'correct': ['A'],
            'marks': 2,
            'expected_marks': 2,
            'expected_status': 'fully_correct'
        },
        {
            'name': 'Full Marks - Multiple Options',
            'student': ['A', 'B'],
            'correct': ['A', 'B'],
            'marks': 2,
            'expected_marks': 2,
            'expected_status': 'fully_correct'
        },
        {
            'name': 'Full Marks - All Three Options',
            'student': ['A', 'B', 'C'],
            'correct': ['A', 'B', 'C'],
            'marks': 3,
            'expected_marks': 3,
            'expected_status': 'fully_correct'
        },
        
        # PARTIAL MARKS SCENARIOS
        {
            'name': 'Partial Marks - Half Correct (1 of 2)',
            'student': ['A'],
            'correct': ['A', 'B'],
            'marks': 2,
            'expected_marks': 1.0,
            'expected_status': 'partially_correct'
        },
        {
            'name': 'Partial Marks - Two-thirds Correct (2 of 3)',
            'student': ['A', 'B'],
            'correct': ['A', 'B', 'C'],
            'marks': 3,
            'expected_marks': 2.0,
            'expected_status': 'partially_correct'
        },
        {
            'name': 'Partial Marks - One-third Correct (1 of 3)',
            'student': ['C'],
            'correct': ['A', 'B', 'C'],
            'marks': 3,
            'expected_marks': 1.0,
            'expected_status': 'partially_correct'
        },
        
        # ZERO MARKS SCENARIOS
        {
            'name': 'Zero Marks - Wrong Option',
            'student': ['B'],
            'correct': ['A'],
            'marks': 2,
            'expected_marks': 0,
            'expected_status': 'has_wrong'
        },
        {
            'name': 'Zero Marks - Correct + Wrong Options',
            'student': ['A', 'C'],
            'correct': ['A', 'B'],
            'marks': 2,
            'expected_marks': 0,
            'expected_status': 'has_wrong'
        },
        {
            'name': 'Zero Marks - All Wrong Options',
            'student': ['C', 'D'],
            'correct': ['A', 'B'],
            'marks': 2,
            'expected_marks': 0,
            'expected_status': 'has_wrong'
        },
        
        # EDGE CASES
        {
            'name': 'Edge Case - No Selection',
            'student': [],
            'correct': ['A', 'B'],
            'marks': 2,
            'expected_marks': 0,
            'expected_status': 'no_selection'
        },
        {
            'name': 'Edge Case - Fractional Marks',
            'student': ['A'],
            'correct': ['A', 'B', 'C'],
            'marks': 2,
            'expected_marks': 0.67,  # 1/3 * 2 = 0.67 (rounded)
            'expected_status': 'partially_correct'
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {test['name']}")
        print(f"   Student: {test['student']}")
        print(f"   Correct: {test['correct']}")
        print(f"   Total Marks: {test['marks']}")
        
        result = calculate_partial_marks(test['student'], test['correct'], test['marks'])
        
        # Check marks
        marks_match = abs(result['marks_awarded'] - test['expected_marks']) < 0.01
        
        # Check status
        if test['expected_status'] == 'fully_correct':
            status_match = result['is_fully_correct']
        elif test['expected_status'] == 'partially_correct':
            status_match = result['is_partially_correct']
        elif test['expected_status'] == 'has_wrong':
            status_match = result['has_wrong_options']
        elif test['expected_status'] == 'no_selection':
            status_match = not any([result['is_fully_correct'], result['is_partially_correct'], result['has_wrong_options']])
        else:
            status_match = False
        
        if marks_match and status_match:
            print(f"   ✅ PASSED: {result['marks_awarded']} marks - {result['explanation']}")
            passed += 1
        else:
            print(f"   ❌ FAILED:")
            print(f"      Expected: {test['expected_marks']} marks, {test['expected_status']}")
            print(f"      Got: {result['marks_awarded']} marks")
            print(f"      Status: fully_correct={result['is_fully_correct']}, partial={result['is_partially_correct']}, wrong={result['has_wrong_options']}")
            print(f"      Explanation: {result['explanation']}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"🎯 TEST RESULTS: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Partial marking system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return failed == 0

def test_real_world_examples():
    """Test with real-world examples"""
    
    print(f"\n{'='*60}")
    print("🌍 REAL-WORLD EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            'scenario': 'Student gets half the multiple-choice question right',
            'student': ['A'],
            'correct': ['A', 'B'],
            'marks': 2,
            'explanation': 'Should get 1 mark (50% of 2 marks)'
        },
        {
            'scenario': 'Student includes wrong option with correct ones',
            'student': ['A', 'B', 'C'],
            'correct': ['A', 'B'],
            'marks': 2,
            'explanation': 'Should get 0 marks (wrong option included)'
        },
        {
            'scenario': 'Student gets 2 out of 3 correct options',
            'student': ['B', 'C'],
            'correct': ['A', 'B', 'C'],
            'marks': 3,
            'explanation': 'Should get 2 marks (2/3 of 3 marks)'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n📖 EXAMPLE {i}: {example['scenario']}")
        print(f"   Expected: {example['explanation']}")
        
        result = calculate_partial_marks(example['student'], example['correct'], example['marks'])
        
        print(f"   Result: {result['marks_awarded']} marks - {result['explanation']}")
        
        if result['is_fully_correct']:
            print(f"   Status: ✅ Fully Correct")
        elif result['is_partially_correct']:
            print(f"   Status: 🟡 Partially Correct")
        elif result['has_wrong_options']:
            print(f"   Status: ❌ Has Wrong Options")
        else:
            print(f"   Status: ❓ Not Answered")

if __name__ == "__main__":
    success = test_partial_marking()
    test_real_world_examples()
    
    print(f"\n🎯 PARTIAL MARKING SYSTEM: {'✅ READY' if success else '❌ NEEDS FIXES'}")
