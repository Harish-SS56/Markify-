@app.route('/api/confirm-submission', methods=['POST'])
def confirm_submission():
    """Confirm and save student submission after teacher verification"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        paper_id = data.get('paper_id')
        roll_number = data.get('roll_number')
        section = data.get('section')
        student_name = data.get('student_name', '')
        answers = data.get('answers', [])
        
        if not paper_id or not roll_number or not answers:
            return jsonify({"error": "Missing required data"}), 400
        
        # Save submission and calculate results
        result = save_student_submission(paper_id, roll_number, section, student_name, answers)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "message": "Answer sheet submitted successfully",
            "submission_id": result['submission_id'],
            "roll_number": roll_number,
            "section": section,
            "extracted_answers": f"{len(answers)} answers processed"
        })
        
    except Exception as e:
        return jsonify({"error": f"Confirmation failed: {str(e)}"}), 500
