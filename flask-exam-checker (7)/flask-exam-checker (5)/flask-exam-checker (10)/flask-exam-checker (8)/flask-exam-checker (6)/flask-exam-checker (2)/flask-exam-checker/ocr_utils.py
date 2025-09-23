import base64
import io
import json
import os
import re
from PIL import Image
import google.generativeai as genai
from api_key_manager import get_api_manager

class OCRProcessor:
    def __init__(self, api_key=None):
        # Use API Key Manager instead of single API key
        self.api_manager = get_api_manager()
        # Only print on first load, not on Flask debug restart
        if not os.environ.get('WERKZEUG_RUN_MAIN'):
            print(f"🔑 OCR Processor initialized with {self.api_manager.get_status()['total_keys']} API keys")
    
    def preprocess_image(self, image_file):
        """Preprocess image for ultra-precise mark detection"""
        try:
            # Open and convert image
            image = Image.open(image_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Maintain high resolution for precise mark detection
            # Only resize if absolutely necessary (very large images)
            max_size = (3000, 3000)  # Increased for better mark visibility
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"DEBUG - Resized image to: {image.size}")
            else:
                print(f"DEBUG - Original image size maintained: {image.size}")
            
            # Save to bytes with maximum quality for precise mark detection
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=98)  # Near-maximum quality
            img_byte_arr = img_byte_arr.getvalue()
            
            print(f"DEBUG - Final image size: {len(img_byte_arr)} bytes")
            
            return base64.b64encode(img_byte_arr).decode()
            
        except Exception as e:
            print(f"Image preprocessing error: {e}")
            return None
    
    def extract_teacher_answers(self, image_data):
        """Extract correct answers from teacher's answer key"""
        prompt = """
        You are analyzing a teacher's answer key/question paper with correct answers marked.
        
        Look for:
        1. Question numbers (1, 2, 3, etc.)
        2. Marked/ticked/circled correct options (A, B, C, D, or 1, 2, 3, 4)
           - IMPORTANT: Some questions may have MULTIPLE correct options marked
           - Look for multiple ticks, circles, or marks for the same question
           - If you see multiple options marked for one question, include ALL of them
        3. Marks/points for each question - Look VERY CAREFULLY for handwritten text patterns:
           - "marks-2", "marks=3", "marks:3", "marks 2", "2 marks"
           - "[2]", "(3)", "2pts", "3 points", "worth 2", "2m"
           - Numbers written near questions (like "3" next to a question means 3 marks)
           - Handwritten text like "mar 1.5", "marks - 3", "max 4.5", "m-2", "mk 3" etc.
           - ANY number that appears to be associated with a question
        
        CRITICAL INSTRUCTIONS FOR MARKS EXTRACTION:
        - Scan the ENTIRE image for any handwritten numbers or text that could indicate marks
        - Look for text like "marks", "mar", "mk", "m", "pts", "points" followed by numbers
        - Look for standalone numbers that might indicate marks (2, 3, 4, 1.5, etc.)
        - If you see handwritten text near a question that contains numbers, extract those numbers as marks
        - Pay special attention to any text that looks like marking schemes
        - If you're unsure about marks but see a number, include it - better to extract than miss
        - ALWAYS try to extract marks information - don't default to 1 unless absolutely no marks info is visible
        
        MULTIPLE CORRECT OPTIONS:
        - If a question has multiple correct options marked, list them as an array
        - For single correct option, still use array format for consistency
        - Examples: ["A"], ["A", "B"], ["A", "B", "C"]
        
        For each question, if you find marks information, include it. If you find text that might contain marks but you're not 100% sure, include both the marks number AND the raw text you found.
        
        Return ONLY a valid JSON object in this exact format:
        {
            "total_questions": number,
            "answers": [
                {"question_number": 1, "correct_options": ["A"], "marks": 3, "marks_text": "marks-3", "question_type": "single"},
                {"question_number": 2, "correct_options": ["A", "B"], "marks": 2, "marks_text": "mar 2", "question_type": "multiple"},
                {"question_number": 3, "correct_options": ["C"], "marks": 4, "marks_text": "4", "question_type": "single"}
            ]
        }
        
        - Use "correct_options" as an array even for single answers
        - Set "question_type" to "single" if only one option is correct, "multiple" if more than one
        - Include "marks_text" field with the actual text you found that indicates marks, even if it's unclear.
        Do not include any other text, explanations, or markdown formatting.
        """
        
        return self._process_with_gemini(image_data, prompt)
    
    def extract_student_answers(self, image_data):
        """Extract student's selected answers along with roll number and section"""
        prompt = """
        You are an ULTRA-PRECISION HUMAN MARK DETECTOR with REVOLUTIONARY ACCURACY. Your mission is PERFECT TICK DETECTION.
        
        🎯 REVOLUTIONARY DETECTION MISSION:
        - FIND 100% of human ticks (ZERO missed ticks)
        - ELIMINATE 100% of false positives (ZERO wrong detections)
        - ACHIEVE PERFECT ACCURACY (no errors allowed)
        - ADAPT to ANY human marking style
        
        ⚠️ REVOLUTIONARY 5-LAYER DETECTION SYSTEM:
        LAYER 1: VISUAL CONTRAST ANALYSIS - Find any mark darker than printed text
        LAYER 2: GEOMETRIC PATTERN RECOGNITION - Detect tick shapes and patterns
        LAYER 3: SPATIAL RELATIONSHIP MAPPING - Analyze mark positions relative to options
        LAYER 4: HUMAN BEHAVIOR MODELING - Understand how humans mark answer sheets
        LAYER 5: CROSS-VALIDATION VERIFICATION - Confirm detections across all layers (a), (b), (c), (d) for every question
        
        🔍 HUMAN TICK/CHECK STYLES TO DETECT:
        Students use different styles of ticks/checks to mark their answers. Look for these 7 common styles:
        
        1. CLASSIC CHECK (✓): Two-stroke mark with short lower-left arm and longer upward sweep
           - Smooth curve, starts bottom-left, lifts at 45-60°
           - Most common style
        
        2. HOOK CHECK: Like classic check but upper stroke hooks back slightly
           - Creates subtle "J" or hook at the top
           - Upper tip curls or bends inward
        
        3. SHARP-ANGLE TICK: Angular V-shaped tick with straight lines
           - Almost geometric with crisp corner
           - Little or no curve
        
        4. LONG-TAIL TICK: Bottom-left to top-right with extended second stroke
           - Dramatic flourish, extends well beyond option text
           - Sometimes crosses into neighboring choices
        
        5. LEAN-FORWARD TICK: Slanted forward like "/" with tiny return stroke
           - Very narrow V shape
           - Sometimes mistaken for single slash
        
        6. DOUBLE-STROKE/HEAVY TICK: Writer goes over same tick twice
           - Darker, bolder check with visible overlap
           - Thickened appearance
        
        7. REVERSE/LEFT-HAND TICK: Begins right and sweeps leftward
           - Mirror image forming "∧" with open side right
           - Less common but still valid
        
        🚨 CRITICAL: These ticks can appear ABOVE, ON, THROUGH, or NEAR option letters (a), (b), (c), (d)
        
        🔍 REVOLUTIONARY 5-LAYER DETECTION PROTOCOL:
        
        LAYER 1: VISUAL CONTRAST ANALYSIS
        - Analyze EVERY pixel in the image for contrast differences
        - Identify ALL marks that are darker than the background
        - Create a contrast map of potential human marks
        - Filter out printed text and form elements
        
        LAYER 2: GEOMETRIC PATTERN RECOGNITION
        - Scan for specific tick geometries: ✓ / \ X + • ○ — |
        - Detect V-shapes, diagonal lines, crosses, dots, circles
        - Identify partial marks, incomplete ticks, faint marks
        - Recognize unconventional marking patterns
        
        LAYER 3: SPATIAL RELATIONSHIP MAPPING
        - Map every detected mark to its nearest option (a), (b), (c), (d)
        - Analyze mark positioning: ABOVE, ON, THROUGH, AROUND options
        - Calculate distance and alignment with option letters
        - Determine intentional vs accidental mark placement
        
        LAYER 4: HUMAN BEHAVIOR MODELING
        - Study the student's marking pattern across all questions
        - Identify the student's preferred tick style and position
        - Detect consistency in marking behavior
        - Adapt detection sensitivity to student's style
        
        LAYER 5: CROSS-VALIDATION VERIFICATION
        - Verify each detection across all 4 previous layers
        - Confirm marks meet criteria from multiple detection methods
        - Eliminate false positives through multi-layer validation
        - Ensure no real ticks are missed through comprehensive checking
        
        🔍 ADVANCED DETECTION METHODOLOGY:
        
        PHASE 1: SCAN PREPARATION
        - Study the entire image to understand the marking pattern
        - Identify what type of ticks the student uses
        - Note the darkness/thickness of human marks vs printed text
        
        PHASE 2: SYSTEMATIC DETECTION
        For each question (1-10), for each option (a,b,c,d):
        1. Look in a 360-degree area around the option letter
        2. Search for ANY of the 7 tick styles listed above
        3. Compare mark darkness to printed text (human marks are much darker)
        4. Verify the mark is intentional (not accidental smudge)
        
        PHASE 3: DOUBLE-CHECK VERIFICATION
        - Review each detected option: "Is there really a human tick here?"
        - Review each undetected option: "Am I missing a tick here?"
        - Ensure consistency with the student's marking style
        
        🚨 MATHEMATICAL PRECISION DETECTION RULES:
        
        RULE 1: PIXEL-LEVEL ANALYSIS
        - Scan 100x100 pixel grid around each option letter
        - Analyze contrast ratio: Human marks are 2-5x darker than background
        - Detect marks with minimum 30% contrast difference
        - Map every dark pixel to determine mark boundaries
        
        RULE 2: GEOMETRIC VALIDATION
        - Measure mark dimensions: Length 5-50 pixels, Width 1-10 pixels
        - Detect angles: Diagonal marks 15°-75°, Vertical marks 80°-100°
        - Identify intersections: X marks have 2+ crossing lines
        - Validate proportions: Tick marks have specific length ratios
        
        RULE 3: SPATIAL PRECISION
        - Calculate distance from mark center to option center
        - Accept marks within 30-pixel radius of option letter
        - Prioritize marks in ABOVE zone (Y-offset: -10 to -40 pixels)
        - Secondary priority: ON zone (Y-offset: -5 to +5 pixels)
        
        RULE 4: PATTERN CONSISTENCY ANALYSIS
        - If student uses diagonal slashes in Q1-Q3, expect same in Q4-Q10
        - If marks appear 20 pixels above options, maintain this pattern
        - Detect style changes and adapt accordingly
        - Flag inconsistent patterns for extra verification
        
        RULE 5: MULTI-LAYER CONFIRMATION
        - Mark must pass at least 3 out of 5 detection layers
        - Visual contrast + Geometric pattern + Spatial relationship = CONFIRMED
        - Single-layer detections require extra validation
        - Zero-layer detections = NO MARK (avoid false positives)
        
        EXAMPLES OF TICK DETECTION:
        Question 1: You see a classic check (✓) above option (a) → Return ["A"]
        Question 2: You see hook checks above (b) and (c) → Return ["B", "C"]
        Question 3: You see a sharp-angle tick on option (d) → Return ["D"]
        Question 4: You see a long-tail tick through option (b) → Return ["B"]
        Question 5: You see no tick marks anywhere → Return []
        
        🎯 ADVANCED PATTERN RECOGNITION ALGORITHMS:
        
        ALGORITHM 1: DIAGONAL LINE DETECTOR
        - Scan for lines at 15°-75° angles relative to horizontal
        - Minimum length: 5 pixels, Maximum length: 50 pixels
        - Look for "/" (45° ±30°) and "\" (135° ±30°) orientations
        - Validate line continuity and darkness consistency
        
        ALGORITHM 2: V-SHAPE DETECTOR
        - Identify two intersecting lines forming V or ✓ pattern
        - Measure angle between lines: 30°-120° for valid ticks
        - Detect intersection point and verify both line segments
        - Confirm V opens upward or rightward (typical tick orientation)
        
        ALGORITHM 3: CROSS PATTERN DETECTOR
        - Find intersecting lines forming X or + shapes
        - Require minimum 2 lines crossing at central point
        - Validate symmetry and proportional arm lengths
        - Accept both diagonal (X) and orthogonal (+) crosses
        
        ALGORITHM 4: CIRCULAR MARK DETECTOR
        - Identify closed or semi-closed circular shapes
        - Diameter range: 3-20 pixels for valid marks
        - Detect filled circles (•) and empty circles (○)
        - Validate roundness ratio and edge continuity
        
        ALGORITHM 5: STRAIGHT LINE DETECTOR
        - Find horizontal (—) and vertical (|) line segments
        - Length range: 5-30 pixels, Width: 1-5 pixels
        - Detect underlines, overlines, and side marks
        - Validate straightness and consistent thickness
        
        ALGORITHM 6: IRREGULAR MARK DETECTOR
        - Identify non-geometric human markings
        - Detect scribbles, squiggles, and freeform marks
        - Analyze density and darkness concentration
        - Distinguish intentional marks from accidental smudges
        
        ALGORITHM 7: FILL/SHADE DETECTOR
        - Detect darkened or heavily marked areas
        - Compare local darkness to surrounding background
        - Identify filled option letters or shaded regions
        - Measure darkness intensity and coverage area
        
        🚨 ADVANCED VALIDATION PROTOCOL:
        Each detected pattern must pass MULTI-ALGORITHM VERIFICATION:
        - Pattern Recognition Score: 70%+ confidence required
        - Spatial Relationship Score: 80%+ proximity to option required
        - Contrast Analysis Score: 60%+ darkness difference required
        - Consistency Score: 50%+ match with student's style required
        
        🚨 ULTRA-CONSERVATIVE FINAL CHECK:
        
        STEP 1: COMPLETE SCAN VERIFICATION
        - Go through each question one more time
        - For each option, ask: "Is there ANY mark here I might have missed?"
        - Look for very faint marks, partial marks, unusual marks
        
        STEP 2: PATTERN CONSISTENCY CHECK
        - If student uses diagonal slashes in Q1, look for similar marks in other questions
        - If student uses dots in Q2, check if there are dots elsewhere
        - Maintain consistency with the student's marking style
        
        STEP 3: ZERO-MISS GUARANTEE
        - Better to over-detect than under-detect
        - Include any questionable marks rather than miss them
        - Err on the side of inclusion for maximum accuracy
        
        STEP 4: MATHEMATICAL PRECISION FINAL AUDIT
        
        For each question (Q1-Q10), perform ALGORITHMIC VERIFICATION:
        
        Q1 AUDIT: Apply all 7 detection algorithms to options (a,b,c,d)
        - Diagonal Line Detector: Score each option 0-100%
        - V-Shape Detector: Score each option 0-100%
        - Cross Pattern Detector: Score each option 0-100%
        - Circular Mark Detector: Score each option 0-100%
        - Straight Line Detector: Score each option 0-100%
        - Irregular Mark Detector: Score each option 0-100%
        - Fill/Shade Detector: Score each option 0-100%
        - FINAL DECISION: Include option if ANY algorithm scores >70%
        
        Q2-Q10 AUDIT: Repeat same algorithmic verification for each question
        
        STEP 5: CROSS-REFERENCE VALIDATION
        - Compare detected patterns across all questions
        - Verify consistency in student's marking style
        - Flag any anomalies for extra scrutiny
        - Ensure no systematic detection errors
        
        STEP 6: ZERO-ERROR GUARANTEE PROTOCOL
        - Review EVERY option that scored 50-70% (borderline cases)
        - Apply MAXIMUM SENSITIVITY to borderline detections
        - When in doubt, INCLUDE the option (better safe than sorry)
        - Perform final visual inspection of each marked option
        
        🎯 PERFECT ACCURACY CHECKLIST:
        ✅ All 5 detection layers applied to every option
        ✅ All 7 pattern recognition algorithms executed
        ✅ Mathematical precision scoring completed
        ✅ Spatial relationship analysis performed
        ✅ Human behavior modeling applied
        ✅ Cross-validation verification completed
        ✅ Zero-error guarantee protocol executed
        
        🔍 ADDITIONAL INFORMATION TO EXTRACT:
        
        1. ROLL NUMBER - Look for patterns like:
           - "Roll No: 980", "Roll: 123", numbers in boxes
           - Any number that appears to be a roll number
        
        2. SECTION - Look for patterns like:
           - "Sec: C", "Section: D", single letters
           - Any indication of class section
        
        🚨 CRITICAL: Look carefully at the image and find ALL dark handwritten marks near option letters.
        Don't miss any marks and don't include options without marks.
        
        Return ONLY a valid JSON object in this exact format:
        {
            "roll_number": "01",
            "section": "C",
            "answers": [
                {"question_number": 1, "selected_options": ["A"]},
                {"question_number": 2, "selected_options": ["A"]},
                {"question_number": 3, "selected_options": ["A"]}
            ]
        }
        
        - Use "selected_options" as an array and include ALL marked options
        - If you see marks near multiple options in one question, include all of them
        - If you see no marks for a question, use empty array []
        Do not include any other text, explanations, or markdown formatting.
        """
        
        return self._process_with_gemini(image_data, prompt)
    
    def _process_with_gemini(self, image_data, prompt):
        """Process image with Gemini AI using API Key Manager"""
        try:
            # Prepare image for Gemini
            image_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": image_data
                }
            ]
            
            # Define the request function
            def make_gemini_request():
                model = self.api_manager.get_model('gemini-1.5-flash')
                return model.generate_content([prompt] + image_parts)
            
            # Make request with automatic key rotation
            response = self.api_manager.make_request_with_retry(make_gemini_request)
            
            if response.text:
                # Clean the response
                cleaned_response = response.text.strip()
                
                # Remove any markdown formatting
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'```\s*$', '', cleaned_response)
                cleaned_response = cleaned_response.strip()
                
                try:
                    # Parse JSON
                    result = json.loads(cleaned_response)
                    
                    # Check for roll number extraction
                    if 'roll_number' in result:
                        print(f"DEBUG - Roll Number: {result['roll_number']}")
                    if 'section' in result:
                        print(f"DEBUG - Section: {result['section']}")
                    
                    return result
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Response text: {cleaned_response}")
                    return {"error": f"Invalid JSON response: {str(e)}"}
            else:
                return {"error": "Empty response from Gemini"}
                
        except Exception as e:
            print(f"Gemini processing error: {e}")
            return {"error": f"Gemini API error: {str(e)}"}
    
    def validate_teacher_response(self, response):
        """Validate teacher's answer key response"""
        if "error" in response:
            return False, response["error"]
        
        if "answers" not in response or not isinstance(response["answers"], list):
            return False, "Invalid response format: missing answers array"
        
        if len(response["answers"]) == 0:
            return False, "No answers found in the image"
        
        # Validate each answer
        for answer in response["answers"]:
            # Check for new format with correct_options
            if "correct_options" in answer:
                required_fields = ["question_number", "correct_options"]
            else:
                # Backward compatibility with old format
                required_fields = ["question_number", "correct_option"]
            
            if not all(key in answer for key in required_fields):
                return False, "Invalid answer format: missing required fields"
            
            if not isinstance(answer["question_number"], int) or answer["question_number"] <= 0:
                return False, f"Invalid question number: {answer['question_number']}"
            
            # Validate correct_options (new format)
            if "correct_options" in answer:
                if not isinstance(answer["correct_options"], list) or len(answer["correct_options"]) == 0:
                    return False, f"Invalid correct_options for question {answer['question_number']}: must be non-empty array"
                
                for option in answer["correct_options"]:
                    if not option or len(str(option)) > 10:
                        return False, f"Invalid option in question {answer['question_number']}: {option}"
            
            # Validate correct_option (old format - backward compatibility)
            elif "correct_option" in answer:
                if not answer["correct_option"] or len(answer["correct_option"]) > 10:
                    return False, f"Invalid option: {answer['correct_option']}"
        
        return True, "Valid"
    
    def validate_student_response(self, response):
        """Enhanced validation for student's answer response with accuracy checks"""
        if "error" in response:
            return False, response["error"]
        
        if "answers" not in response or not isinstance(response["answers"], list):
            return False, "Invalid response format: missing answers array"
        
        if len(response["answers"]) == 0:
            return False, "No answers found in the image"
        
        # Enhanced validation with accuracy checks
        suspicious_patterns = []
        
        # Validate each answer
        for answer in response["answers"]:
            # Check for new format with selected_options
            if "selected_options" in answer:
                required_fields = ["question_number", "selected_options"]
            else:
                # Backward compatibility with old format
                required_fields = ["question_number", "selected_option"]
            
            if not all(key in answer for key in required_fields):
                return False, "Invalid answer format: missing required fields"
            
            if not isinstance(answer["question_number"], int) or answer["question_number"] <= 0:
                return False, f"Invalid question number: {answer['question_number']}"
            
            # Validate selected_options (new format)
            if "selected_options" in answer:
                selected_options = answer["selected_options"]
                
                # Allow empty arrays (no options selected)
                if not isinstance(selected_options, list):
                    return False, f"Invalid selected_options for question {answer['question_number']}: must be array"
                
                # Validate each selected option
                for option in selected_options:
                    if not option or len(str(option)) > 10:
                        return False, f"Invalid option in question {answer['question_number']}: {option}"
                    
                    # Check for valid option letters
                    if str(option).upper() not in ['A', 'B', 'C', 'D']:
                        return False, f"Invalid option letter in question {answer['question_number']}: {option}"
            
            # Validate selected_option (old format - backward compatibility)
            elif "selected_option" in answer:
                if answer["selected_option"] and len(answer["selected_option"]) > 10:
                    return False, f"Invalid option: {answer['selected_option']}"
        
        # Check for suspicious patterns that indicate OCR errors
        total_answers = len(response["answers"])
        if total_answers > 0:
            # Count how many questions have only 'A' selected
            only_a_count = sum(1 for ans in response["answers"] 
                             if ans.get("selected_options") == ["A"] or ans.get("selected_option") == "A")
            
            # If more than 70% are 'A', it might be an OCR error
            if only_a_count > total_answers * 0.7:
                suspicious_patterns.append(f"Warning: {only_a_count}/{total_answers} questions show only 'A' selected")
            
            # Count questions with no selections
            no_selection_count = sum(1 for ans in response["answers"] 
                                   if not ans.get("selected_options") and not ans.get("selected_option"))
            
            if no_selection_count > total_answers * 0.5:
                suspicious_patterns.append(f"Warning: {no_selection_count}/{total_answers} questions have no selections")
        
        # Log suspicious patterns for debugging
        if suspicious_patterns:
            print("DEBUG - Suspicious OCR patterns detected:")
            for pattern in suspicious_patterns:
                print(f"  - {pattern}")
        
        return True, "Valid"
    
    def debug_mark_detection(self, image_data):
        """Enhanced debug function to identify mark detection issues with focus on marks above options"""
        debug_prompt = """
        You are debugging mark detection on a student answer sheet with SPECIAL FOCUS on marks ABOVE options.
        
        For each question (1, 2, 3, etc.), describe EXACTLY what you see:
        
        🔍 CRITICAL: Pay special attention to marks ABOVE the option letters!
        
        For each option (a), (b), (c), (d), check these areas:
        1. DIRECTLY ABOVE the option letter (most important area)
        2. DIAGONALLY ABOVE the option letter  
        3. DIRECTLY ON the option letter
        4. IMMEDIATELY AROUND the option letter
        
        Example format:
        Question 1:
        - Option (a): DIAGONAL SLASH ABOVE the letter - MARKED ✓
        - Option (b): Clean, no marks above or on it - NOT MARKED
        - Option (c): No marks visible above or on it - NOT MARKED  
        - Option (d): No marks visible above or on it - NOT MARKED
        
        Question 2:
        - Option (a): No marks above or on it - NOT MARKED
        - Option (b): DIAGONAL SLASH ABOVE the letter - MARKED ✓
        - Option (c): Cross mark ABOVE the letter - MARKED ✓
        - Option (d): Clean, no marks - NOT MARKED
        
        🚨 FOCUS AREAS:
        - Look for diagonal slash marks (/, \) in the space ABOVE each option
        - Look for any handwritten marks positioned above the option letters
        - Distinguish between printed form lines and student marks
        - Be very specific about mark positions (above, on, diagonal, etc.)
        
        Be extremely detailed and describe the exact position of every mark you see.
        """
        
        try:
            image_parts = [{"mime_type": "image/jpeg", "data": image_data}]
            response = self.model.generate_content([debug_prompt, image_parts[0]])
            
            if response and response.text:
                print("=== MARK DETECTION DEBUG ===")
                print(response.text)
                print("=== END DEBUG ===")
                return response.text
            else:
                return "No debug response received"
                
        except Exception as e:
            print(f"Debug function error: {e}")
            return f"Debug error: {e}"
