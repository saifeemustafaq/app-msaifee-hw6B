from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from app.utils.pagination import paginate_data
from datetime import datetime

@app.route('/api/applications', methods=['POST'])
def create_application():
    data = load_data()
    application_data = request.get_json()
    
    # Validate required fields
    required_fields = ['userId', 'propertyId', 'listingId', 'moveInDate', 'leaseDuration']
    for field in required_fields:
        if field not in application_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate that user exists and is active
    user = next((user for user in data['users'] if user['userId'] == application_data['userId']), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if user['status'] != 'ACTIVE':
        return jsonify({'error': 'User account is not active'}), 403
    
    # Validate that property and listing exist
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == application_data['propertyId']), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404
        
    listing = next((listing for listing in data.get('property_listings', [])
                   if listing['listingId'] == application_data['listingId'] and 
                   listing['propertyId'] == application_data['propertyId']), None)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    new_application = {
        'applicationId': str(len(data['applications']) + 1),
        'userId': application_data['userId'],
        'propertyId': application_data['propertyId'],
        'listingId': application_data['listingId'],
        'moveInDate': application_data['moveInDate'],
        'leaseDuration': application_data['leaseDuration'],
        'status': 'PENDING',
        'notes': application_data.get('notes', ''),
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    data['applications'].append(new_application)
    return jsonify(new_application), 201

@app.route('/api/applications', methods=['GET'])
def get_applications():
    data = load_data()
    status = request.args.get('status', '').upper()
    user_id = request.args.get('userId')
    property_id = request.args.get('propertyId')
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_applications = [app for app in data['applications']
                           if (not status or app['status'] == status) and
                           (not user_id or app['userId'] == user_id) and
                           (not property_id or app['propertyId'] == property_id)]

    applications_page, total_count = paginate_data(filtered_applications, begin, count)

    return jsonify({
        'applications': applications_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

@app.route('/api/applications/<application_id>', methods=['GET'])
def get_application(application_id):
    data = load_data()
    
    application = next((app for app in data['applications'] 
                       if app['applicationId'] == application_id), None)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
        
    return jsonify(application)

@app.route('/api/applications/<application_id>', methods=['PATCH'])
def update_application(application_id):
    data = load_data()
    update_data = request.get_json()
    
    application = next((app for app in data['applications'] 
                       if app['applicationId'] == application_id), None)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Prevent updates to critical fields
    protected_fields = ['applicationId', 'userId', 'propertyId', 'listingId', 'createdAt']
    invalid_updates = [field for field in update_data if field in protected_fields]
    if invalid_updates:
        return jsonify({'error': f'Cannot update protected fields: {invalid_updates}'}), 400
    
    # Validate status if being updated
    if 'status' in update_data:
        valid_statuses = ['PENDING', 'APPROVED', 'REJECTED', 'WITHDRAWN']
        if update_data['status'].upper() not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        update_data['status'] = update_data['status'].upper()
    
    # Update allowed fields
    for key, value in update_data.items():
        if key in application:
            application[key] = value
    
    application['updatedAt'] = datetime.now().isoformat()
    return jsonify(application)

@app.route('/api/applications/<application_id>', methods=['DELETE'])
def delete_application(application_id):
    data = load_data()
    
    application = next((app for app in data['applications'] 
                       if app['applicationId'] == application_id), None)
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Soft delete - update status to withdrawn
    application['status'] = 'WITHDRAWN'
    application['updatedAt'] = datetime.now().isoformat()
    
    return jsonify({'message': 'Application withdrawn successfully'})

@app.route('/api/applications/<application_id>/documents', methods=['POST', 'GET', 'PATCH', 'DELETE'])
def handle_application_documents(application_id):
    if request.method == 'GET':
        return get_application_documents(application_id)
    elif request.method == 'POST':
        return create_application_document(application_id)
    elif request.method == 'PATCH':
        return update_application_document(application_id)
    elif request.method == 'DELETE':
        return delete_application_document(application_id)

@app.route('/api/applications/<application_id>/documents', methods=['GET'])
def get_application_documents(application_id):
    data = load_data()
    doc_type = request.args.get('type', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_documents = [doc for doc in data['documents']
                          if doc['applicationId'] == application_id and
                          (not doc_type or doc['documentType'] == doc_type)]

    documents_page, total_count = paginate_data(filtered_documents, begin, count)

    return jsonify({
        'documents': documents_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

def create_application_document(application_id):
    data = load_data()
    document_data = request.get_json()
    
    # Validate required fields
    required_fields = ['documentType', 'documentUrl']
    for field in required_fields:
        if field not in document_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
            
    # Validate document type
    valid_types = ['IDENTIFICATION', 'PROOF_OF_INCOME', 'REFERENCE_LETTER', 'OTHER']
    if document_data['documentType'].upper() not in valid_types:
        return jsonify({'error': 'Invalid document type'}), 400
        
    new_document = {
        'documentId': str(len(data.get('documents', [])) + 1),
        'applicationId': application_id,
        'documentType': document_data['documentType'].upper(),
        'documentUrl': document_data['documentUrl'],
        'description': document_data.get('description', ''),
        'status': 'ACTIVE',
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    if 'documents' not in data:
        data['documents'] = []
    data['documents'].append(new_document)
    
    return jsonify(new_document), 201

def update_application_document(application_id):
    data = load_data()
    document_id = request.args.get('documentId')
    update_data = request.get_json()
    
    if not document_id:
        return jsonify({'error': 'Document ID is required'}), 400
        
    document = next((doc for doc in data.get('documents', [])
                    if doc['documentId'] == document_id and 
                    doc['applicationId'] == application_id), None)
                    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
        
    # Prevent updates to critical fields
    protected_fields = ['documentId', 'applicationId', 'createdAt']
    invalid_updates = [field for field in update_data if field in protected_fields]
    if invalid_updates:
        return jsonify({'error': f'Cannot update protected fields: {invalid_updates}'}), 400
        
    # Update allowed fields
    for key, value in update_data.items():
        if key in document:
            document[key] = value
            
    document['updatedAt'] = datetime.now().isoformat()
    return jsonify(document)

def delete_application_document(application_id):
    data = load_data()
    document_id = request.args.get('documentId')
    
    if not document_id:
        return jsonify({'error': 'Document ID is required'}), 400
        
    document = next((doc for doc in data.get('documents', [])
                    if doc['documentId'] == document_id and 
                    doc['applicationId'] == application_id), None)
                    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
        
    # Soft delete
    document['status'] = 'DELETED'
    document['updatedAt'] = datetime.now().isoformat()
    
    return jsonify({'message': 'Document deleted successfully'})