from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from app.utils.pagination import paginate_data
from datetime import datetime
import json

@app.route('/api/users', methods=['GET'])
def get_users():
    data = load_data()
    role = request.args.get('role', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_users = [user for user in data['users'] if user['role'] == role] if role else data['users']
    users_page, total_count = paginate_data(filtered_users, begin, count)

    return jsonify({
        'users': users_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = load_data()
    user_data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'password', 'role', 'firstName', 'lastName', 'email', 'phoneNumber']
    for field in required_fields:
        if field not in user_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Set default values for new user
    new_user = {
        'userId': str(len(data['users']) + 1),  # Simple ID generation
        'username': user_data['username'],
        'password': user_data['password'],  # Note: Should be hashed in production
        'role': user_data['role'].upper(),
        'isVerified': False,
        'firstName': user_data['firstName'],
        'lastName': user_data['lastName'],
        'email': user_data['email'],
        'phoneNumber': user_data['phoneNumber'],
        'campusAffiliation': user_data.get('campusAffiliation'),
        'profilePictureUrl': user_data.get('profilePictureUrl'),
        'createdAt': datetime.now().isoformat(),
        'lastLogin': None,
        'status': 'ACTIVE',
        'tokenBalance': 0
    }
    
    # Validate role
    valid_roles = ['STUDENT', 'ALUMNI', 'LANDLORD', 'ADMIN']
    if new_user['role'] not in valid_roles:
        return jsonify({'error': 'Invalid role specified'}), 400
    
    data['users'].append(new_user)
    # In a real application, you would save to database here
    
    return jsonify(new_user), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    data = load_data()
    
    user = next((user for user in data['users'] if user['userId'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify(user)

@app.route('/api/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        data = load_data()
        update_data = request.get_json()
        
        user = next((user for user in data['users'] if user['userId'] == user_id), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent updates to critical fields
        protected_fields = ['userId', 'createdAt', 'role']
        invalid_updates = [field for field in update_data if field in protected_fields]
        if invalid_updates:
            return jsonify({'error': f'Cannot update protected fields: {invalid_updates}'}), 400
        
        # Update allowed fields
        for key, value in update_data.items():
            if key in user:
                user[key] = value
        
        # Add last modified timestamp
        user['updatedAt'] = datetime.now().isoformat()
        
        return jsonify(user)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format in request body'}), 400

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    data = load_data()
    
    user = next((user for user in data['users'] if user['userId'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Soft delete - update status to inactive
    user['status'] = 'INACTIVE'
    # In a real application, you would save to database here
    
    return jsonify({'message': 'User deactivated successfully'})

# Additional user-related routes for profile and activities
@app.route('/api/users/<user_id>/profile', methods=['POST', 'GET', 'PATCH'])
def handle_user_profile(user_id):
    if request.method == 'GET':
        data = load_data()
        profile = next((profile for profile in data['profiles'] if profile['userId'] == user_id), None)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        return jsonify(profile)
    
    elif request.method == 'POST':
        data = load_data()
        profile_data = request.get_json()
        
        # Check if profile already exists
        existing_profile = next((p for p in data['profiles'] if p['userId'] == user_id), None)
        if existing_profile:
            return jsonify({'error': 'Profile already exists'}), 400
        
        # Validate required profile fields
        required_fields = ['bio', 'preferences']
        for field in required_fields:
            if field not in profile_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_profile = {
            'profileId': str(len(data['profiles']) + 1),
            'userId': user_id,
            **profile_data,
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        data['profiles'].append(new_profile)
        # In a real application, you would save to database here
        
        return jsonify(new_profile), 201
    
    elif request.method == 'PATCH':
        data = load_data()
        update_data = request.get_json()
        
        profile = next((p for p in data['profiles'] if p['userId'] == user_id), None)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        for key, value in update_data.items():
            if key in profile and key not in ['profileId', 'userId', 'createdAt']:
                profile[key] = value
        
        profile['updatedAt'] = datetime.now().isoformat()
        # In a real application, you would save to database here
        
        return jsonify(profile)