from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from app.utils.pagination import paginate_data
from datetime import datetime

@app.route('/api/activities', methods=['GET'])
def get_activities():
    data = load_data()
    activity_type = request.args.get('type', '').upper()
    user_id = request.args.get('userId')
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_activities = [activity for activity in data['tokenActivities']
                         if (not activity_type or activity['activityType'] == activity_type) and
                         (not user_id or activity['userId'] == user_id)]

    activities_page, total_count = paginate_data(filtered_activities, begin, count)

    return jsonify({
        'activities': activities_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

@app.route('/api/activities/<activity_id>', methods=['GET'])
def get_activity(activity_id):
    data = load_data()
    
    activity = next((activity for activity in data['tokenActivities'] 
                    if activity['activityId'] == activity_id), None)
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
        
    return jsonify(activity)

@app.route('/api/users/<user_id>/activities', methods=['POST', 'GET'])
def handle_user_activities(user_id):
    if request.method == 'GET':
        return get_user_activities(user_id)
        
    data = load_data()
    activity_data = request.get_json()
    
    # Validate user exists and is active
    user = next((user for user in data['users'] if user['userId'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user['status'] != 'ACTIVE':
        return jsonify({'error': 'User account is not active'}), 403
    
    # Validate required fields
    required_fields = ['activityType', 'tokenAmount', 'description']
    for field in required_fields:
        if field not in activity_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate activity type
    valid_types = ['EARN', 'SPEND', 'REFUND']
    if activity_data['activityType'].upper() not in valid_types:
        return jsonify({'error': 'Invalid activity type'}), 400
    
    new_activity = {
        'activityId': str(len(data['tokenActivities']) + 1),
        'userId': user_id,
        'activityType': activity_data['activityType'].upper(),
        'tokenAmount': activity_data['tokenAmount'],
        'description': activity_data['description'],
        'createdAt': datetime.now().isoformat(),
        'status': 'COMPLETED'
    }
    
    # Update user's token balance
    if new_activity['activityType'] == 'EARN':
        user['tokenBalance'] += new_activity['tokenAmount']
    elif new_activity['activityType'] == 'SPEND':
        if user['tokenBalance'] < new_activity['tokenAmount']:
            return jsonify({'error': 'Insufficient token balance'}), 400
        user['tokenBalance'] -= new_activity['tokenAmount']
    elif new_activity['activityType'] == 'REFUND':
        user['tokenBalance'] += new_activity['tokenAmount']
    
    data['tokenActivities'].append(new_activity)
    return jsonify(new_activity), 201

@app.route('/api/students/<student_id>/property-match-scores', methods=['GET'])
def get_property_match_scores(student_id):
    data = load_data()
    
    # Validate student exists and is active
    student = next((user for user in data['users'] 
                   if user['userId'] == student_id and user['role'] == 'STUDENT'), None)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    if student['status'] != 'ACTIVE':
        return jsonify({'error': 'Student account is not active'}), 403
    
    # Get student preferences from profile
    profile = next((p for p in data['profiles'] if p['userId'] == student_id), None)
    if not profile:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Calculate match scores for available properties
    property_scores = []
    for prop in data['properties']:
        if prop['status'] != 'AVAILABLE':
            continue
            
        # Calculate property match score based on student preferences
        match_score = 0
        match_factors = []
        
        # Location matching
        if profile.get('preferredLocation') == prop.get('location'):
            match_score += 30
            match_factors.append('location')
            
        # Price matching - within budget
        if profile.get('maxBudget', 0) >= prop.get('monthlyRent', 0):
            match_score += 25
            match_factors.append('price')
            
        # Amenities matching
        student_amenities = set(profile.get('desiredAmenities', []))
        property_amenities = set(prop.get('amenities', []))
        matching_amenities = student_amenities.intersection(property_amenities)
        if matching_amenities:
            match_score += min(len(matching_amenities) * 5, 20)
            match_factors.append('amenities')
            
        # Room type matching
        if profile.get('preferredRoomType') == prop.get('roomType'):
            match_score += 25
            match_factors.append('room type')
            
        score = {
            'propertyId': prop['propertyId'],
            'matchScore': match_score,
            'matchFactors': match_factors
        }
        property_scores.append(score)
    
    # Sort by match score descending
    property_scores.sort(key=lambda x: x['matchScore'], reverse=True)
    
    return jsonify({
        'studentId': student_id,
        'propertyScores': property_scores
    })

@app.route('/api/students/<student_id>/roommate-compatibility', methods=['GET'])
def get_roommate_compatibility(student_id):
    data = load_data()
    
    # Validate student exists and is active
    student = next((user for user in data['users'] 
                   if user['userId'] == student_id and user['role'] == 'STUDENT'), None)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    if student['status'] != 'ACTIVE':
        return jsonify({'error': 'Student account is not active'}), 403
    
    # Get student preferences from profile
    profile = next((p for p in data['profiles'] if p['userId'] == student_id), None)
    if not profile:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Calculate compatibility with other students
    compatibility_scores = []
    for other_user in data['users']:
        if other_user['userId'] == student_id or other_user['role'] != 'STUDENT':
            continue
            
        other_profile = next((p for p in data['profiles'] if p['userId'] == other_user['userId']), None)
        if not other_profile:
            continue
            
        # Calculate compatibility score based on profile matching
        compatibility_score = 0
        compatibility_factors = []
        
        # Lifestyle matching
        if profile.get('lifestyle') == other_profile.get('lifestyle'):
            compatibility_score += 25
            compatibility_factors.append('lifestyle')
            
        # Study habits matching
        if profile.get('studyHabits') == other_profile.get('studyHabits'):
            compatibility_score += 20
            compatibility_factors.append('study habits')
            
        # Sleep schedule matching
        if profile.get('sleepSchedule') == other_profile.get('sleepSchedule'):
            compatibility_score += 15
            compatibility_factors.append('sleep schedule')
            
        # Interests matching
        student_interests = set(profile.get('interests', []))
        other_interests = set(other_profile.get('interests', []))
        matching_interests = student_interests.intersection(other_interests)
        if matching_interests:
            compatibility_score += min(len(matching_interests) * 5, 20)
            compatibility_factors.append('interests')
            
        # Cleanliness matching
        if profile.get('cleanlinessLevel') == other_profile.get('cleanlinessLevel'):
            compatibility_score += 20
            compatibility_factors.append('cleanliness')
            
        score = {
            'studentId': other_user['userId'],
            'compatibilityScore': compatibility_score,
            'compatibilityFactors': compatibility_factors
        }
        compatibility_scores.append(score)
    
    # Sort by compatibility score descending
    compatibility_scores.sort(key=lambda x: x['compatibilityScore'], reverse=True)
    
    return jsonify({
        'studentId': student_id,
        'compatibilityScores': compatibility_scores
    })