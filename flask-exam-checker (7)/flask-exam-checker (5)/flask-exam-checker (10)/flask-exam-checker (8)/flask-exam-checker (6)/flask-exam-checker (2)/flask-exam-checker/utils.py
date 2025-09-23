import re
from datetime import datetime

def clean_option(option):
    """Clean and standardize option format"""
    if not option:
        return None
    
    # Convert to uppercase and remove extra spaces
    option = str(option).upper().strip()
    
    # Handle different option formats
    if option in ['1', 'A']:
        return 'A'
    elif option in ['2', 'B']:
        return 'B'
    elif option in ['3', 'C']:
        return 'C'
    elif option in ['4', 'D']:
        return 'D'
    elif option in ['A', 'B', 'C', 'D']:
        return option
    else:
        # Try to extract letter from string like "(A)" or "A)"
        match = re.search(r'[ABCD]', option)
        if match:
            return match.group()
    
    return option  # Return as-is if no pattern matches

def validate_roll_number(roll_number):
    """Validate and clean roll number"""
    if not roll_number:
        return None
    
    # Remove extra spaces and convert to string
    roll_number = str(roll_number).strip()
    
    # Basic validation - should contain alphanumeric characters
    if re.match(r'^[A-Za-z0-9\-_]+$', roll_number):
        return roll_number.upper()
    
    return None

def calculate_percentage(correct, total):
    """Calculate percentage with proper rounding"""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 2)

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_image_file(file):
    """Validate uploaded image file"""
    if not file:
        return False
    
    if file.filename == '':
        return False
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check file size (max 10MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        return False
    
    return True

def extract_marks_from_text(text):
    """Extract marks from text patterns like 'marks-2', 'marks=3', '[2]', etc."""
    if not text:
        return 1
    
    text = str(text).lower().strip()
    
    # Enhanced patterns for marks extraction including handwritten variations
    patterns = [
        r'marks?[-=:\s]+(\d+(?:\.\d+)?)',  # marks-2, marks=3, marks:3, marks 2, mark 1.5
        r'(\d+(?:\.\d+)?)\s*marks?',       # 2 marks, 3marks, 1.5 mark
        r'mar\s*[-=:\s]*(\d+(?:\.\d+)?)',  # mar 2, mar-3, mar:1.5
        r'max\s*[-=:\s]*(\d+(?:\.\d+)?)',  # max 4, max-3, max:2.5
        r'\[(\d+(?:\.\d+)?)\]',            # [2], [3], [1.5]
        r'\((\d+(?:\.\d+)?)\)',            # (2), (3), (1.5)
        r'(\d+(?:\.\d+)?)\s*pts?',         # 2pts, 3pt, 1.5pts
        r'(\d+(?:\.\d+)?)\s*points?',      # 2 points, 3 point, 1.5 points
        r'worth\s+(\d+(?:\.\d+)?)',        # worth 2, worth 3, worth 1.5
        r'(\d+(?:\.\d+)?)\s*m\b',          # 2m, 3m, 1.5m
        r'^(\d+(?:\.\d+)?)$',              # Just a number by itself like "3" or "1.5"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                marks = float(match.group(1))
                return int(marks) if marks == int(marks) else marks  # Return int if whole number, float otherwise
            except (ValueError, IndexError):
                continue
    
    return 1  # Default to 1 mark if no pattern matches

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Replace unsafe characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename

def clean_multiple_options(options_str):
    """Clean and standardize multiple options format"""
    if not options_str:
        return []
    
    # Handle different input formats
    if isinstance(options_str, list):
        options = options_str
    elif isinstance(options_str, str):
        # Split by common delimiters
        options = re.split(r'[,;\s]+', options_str.strip())
    else:
        options = [str(options_str)]
    
    # Clean each option
    cleaned_options = []
    for option in options:
        cleaned = clean_option(option)
        if cleaned and cleaned not in cleaned_options:
            cleaned_options.append(cleaned)
    
    return sorted(cleaned_options)  # Sort for consistent comparison

def validate_multiple_options(student_options, correct_options):
    """
    Validate student's multiple options against correct answers using strict marking
    Returns True only if student selected ALL correct options and NO wrong options
    """
    if not isinstance(student_options, list):
        student_options = clean_multiple_options(student_options)
    if not isinstance(correct_options, list):
        correct_options = clean_multiple_options(correct_options)
    
    # Clean and sort both lists for comparison
    student_set = set(clean_multiple_options(student_options))
    correct_set = set(clean_multiple_options(correct_options))
    
    # Strict marking: must match exactly (all correct, no extra)
    return student_set == correct_set

def calculate_partial_marks(student_options, correct_options, total_marks):
    """
    Calculate marks using partial marking system:
    - If student selects ONLY correct options (subset), award proportional marks
    - If student selects ANY wrong option, award 0 marks
    - If student selects ALL correct options, award full marks
    
    Args:
        student_options: List of student's selected options
        correct_options: List of correct options
        total_marks: Total marks for the question
    
    Returns:
        dict: {
            'marks_awarded': float,
            'is_fully_correct': bool,
            'is_partially_correct': bool,
            'has_wrong_options': bool,
            'explanation': str
        }
    """
    if not isinstance(student_options, list):
        student_options = clean_multiple_options(student_options)
    if not isinstance(correct_options, list):
        correct_options = clean_multiple_options(correct_options)
    
    # Clean and convert to sets for comparison
    student_set = set(clean_multiple_options(student_options))
    correct_set = set(clean_multiple_options(correct_options))
    
    # Handle empty selections
    if not student_set:
        return {
            'marks_awarded': 0,
            'is_fully_correct': False,
            'is_partially_correct': False,
            'has_wrong_options': False,
            'explanation': 'No options selected'
        }
    
    if not correct_set:
        return {
            'marks_awarded': 0,
            'is_fully_correct': False,
            'is_partially_correct': False,
            'has_wrong_options': True,
            'explanation': 'No correct options defined'
        }
    
    # Check for wrong options (student selected options not in correct set)
    wrong_options = student_set - correct_set
    correct_selected = student_set & correct_set  # Intersection: correct options selected by student
    
    # RULE 1: If student selected ANY wrong option → 0 marks
    if wrong_options:
        return {
            'marks_awarded': 0,
            'is_fully_correct': False,
            'is_partially_correct': False,
            'has_wrong_options': True,
            'explanation': f'Selected wrong option(s): {", ".join(sorted(wrong_options))}'
        }
    
    # RULE 2: Student selected ONLY correct options (no wrong ones)
    # Check if it's a subset of correct options
    if student_set.issubset(correct_set):
        # RULE 2a: Student selected ALL correct options → Full marks
        if student_set == correct_set:
            return {
                'marks_awarded': total_marks,
                'is_fully_correct': True,
                'is_partially_correct': False,
                'has_wrong_options': False,
                'explanation': 'All correct options selected'
            }
        
        # RULE 2b: Student selected SOME correct options (but not all) → Partial marks
        else:
            # Calculate proportional marks
            proportion = len(correct_selected) / len(correct_set)
            partial_marks = round(total_marks * proportion, 2)
            
            missing_options = correct_set - student_set
            
            return {
                'marks_awarded': partial_marks,
                'is_fully_correct': False,
                'is_partially_correct': True,
                'has_wrong_options': False,
                'explanation': f'Partial marks: {len(correct_selected)}/{len(correct_set)} correct options. Missing: {", ".join(sorted(missing_options))}'
            }
    
    # This shouldn't happen given the logic above, but just in case
    return {
        'marks_awarded': 0,
        'is_fully_correct': False,
        'is_partially_correct': False,
        'has_wrong_options': True,
        'explanation': 'Unexpected error in marking calculation'
    }

def parse_options_string(options_str):
    """Parse options string from various formats like 'A,B', 'A B C', 'A;B;C' etc."""
    if not options_str:
        return []
    
    # Handle array-like strings from database
    if options_str.startswith('{') and options_str.endswith('}'):
        # PostgreSQL array format: {A,B,C}
        options_str = options_str[1:-1]  # Remove braces
    
    # Split by various delimiters
    options = re.split(r'[,;\s]+', str(options_str).strip())
    
    # Clean and filter empty options
    return [clean_option(opt) for opt in options if opt.strip()]
