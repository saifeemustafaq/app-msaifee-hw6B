from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from datetime import datetime, timedelta
import uuid

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = load_data()
    credentials = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in credentials:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Find user by username
    user = next((user for user in data['users'] 
                 if user['username'] == credentials['username']), None)
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # In production, you would hash the password before comparing
    if user['password'] != credentials['password']:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if user is active
    if user['status'] != 'ACTIVE':
        return jsonify({'error': 'Account is not active'}), 403
    
    # Create new session
    new_session = {
        'sessionId': str(uuid.uuid4()),
        'userId': user['userId'],
        'createdAt': datetime.now().isoformat(),
        'expiresAt': (datetime.now() + timedelta(hours=24)).isoformat(),
        'status': 'ACTIVE'
    }
    
    # Add session to data
    if 'sessions' not in data:
        data['sessions'] = []
    data['sessions'].append(new_session)
    
    # Create response with user info and session
    response = {
        'user': {
            'userId': user['userId'],
            'username': user['username'],
            'role': user['role'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'email': user['email']
        },
        'session': {
            'sessionId': new_session['sessionId'],
            'expiresAt': new_session['expiresAt']
        }
    }
    
    return jsonify(response), 201

@app.route('/api/sessions', methods=['DELETE'])
def delete_session():
    data = load_data()
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    # Find session
    session = next((session for session in data.get('sessions', [])
                   if session['sessionId'] == session_id), None)
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Update session status
    session['status'] = 'INACTIVE'
    session['updatedAt'] = datetime.now().isoformat()
    
    return jsonify({'message': 'Session terminated successfully'})

# Helper function to validate session (can be used by other routes)
def validate_session(session_id):
    if not session_id:
        return None, ('Session ID is required', 400)
        
    data = load_data()
    session = next((session for session in data.get('sessions', [])
                   if session['sessionId'] == session_id), None)
    
    if not session:
        return None, ('Session not found', 404)
        
    if session['status'] != 'ACTIVE':
        return None, ('Session is not active', 401)
        
    if datetime.fromisoformat(session['expiresAt']) < datetime.now():
        session['status'] = 'EXPIRED'
        return None, ('Session has expired', 401)
        
    # Get associated user
    user = next((user for user in data['users'] if user['userId'] == session['userId']), None)
    if not user:
        return None, ('Associated user not found', 404)
        
    if user['status'] != 'ACTIVE':
        return None, ('User account is not active', 403)
        
    return session, None