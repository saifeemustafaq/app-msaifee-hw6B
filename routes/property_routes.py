from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from app.utils.pagination import paginate_data
from datetime import datetime

@app.route('/api/properties', methods=['POST'])
def create_property():
    data = load_data()
    property_data = request.get_json()
    
    # Validate required fields
    required_fields = ['landlordId', 'propertyName', 'address', 'propertyType']
    for field in required_fields:
        if field not in property_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
            
    # Validate address fields
    required_address_fields = ['city', 'state', 'zipCode', 'country']
    if not all(field in property_data['address'] for field in required_address_fields):
        return jsonify({'error': 'Address must include city, state, zipCode, and country'}), 400
    
    # Validate property type
    valid_types = ['APARTMENT', 'HOUSE', 'STUDIO', 'SHARED_ROOM']
    if property_data['propertyType'].upper() not in valid_types:
        return jsonify({'error': 'Invalid property type'}), 400
    
    new_property = {
        'propertyId': str(len(data['properties']) + 1),
        'landlordId': property_data['landlordId'],
        'propertyName': property_data['propertyName'],
        'address': property_data['address'],
        'geolocation': property_data.get('geolocation', {'latitude': None, 'longitude': None}),
        'propertyType': property_data['propertyType'].upper(),
        'description': property_data.get('description', ''),
        'status': 'AVAILABLE',
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat()
    }
    
    data['properties'].append(new_property)
    # In a real application, you would save to database here
    
    return jsonify(new_property), 201

@app.route('/api/properties', methods=['GET'])
def get_properties():
    data = load_data()
    status = request.args.get('status', '').upper()
    property_type = request.args.get('propertyType', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_properties = [prop for prop in data['properties']
                         if (not status or prop['status'] == status) and
                         (not property_type or prop['propertyType'] == property_type)]

    properties_page, total_count = paginate_data(filtered_properties, begin, count)

    return jsonify({
        'properties': properties_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

@app.route('/api/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    data = load_data()
    
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404
        
    return jsonify(property_item)

@app.route('/api/properties/<property_id>', methods=['PATCH'])
def update_property(property_id):
    data = load_data()
    update_data = request.get_json()
    
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404
    
    # Prevent updates to critical fields
    protected_fields = ['propertyId', 'landlordId', 'createdAt']
    invalid_updates = [field for field in update_data if field in protected_fields]
    if invalid_updates:
        return jsonify({'error': f'Cannot update protected fields: {invalid_updates}'}), 400
    
    # Update allowed fields
    for key, value in update_data.items():
        if key in property_item:
            property_item[key] = value
    
    property_item['updatedAt'] = datetime.now().isoformat()
    # In a real application, you would save to database here
    
    return jsonify(property_item)

@app.route('/api/properties/<property_id>', methods=['DELETE'])
def delete_property(property_id):
    data = load_data()
    
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404
    
    # Soft delete - update status to unavailable
    property_item['status'] = 'UNAVAILABLE'
    property_item['updatedAt'] = datetime.now().isoformat()
    # In a real application, you would save to database here
    
    return jsonify({'message': 'Property marked as unavailable'})

@app.route('/api/properties/<property_id>/details', methods=['POST', 'GET', 'PATCH'])
def handle_property_details(property_id):
    data = load_data()
    
    # Check if property exists
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404

    if request.method == 'GET':
        details = next((detail for detail in data.get('property_details', [])
                       if detail['propertyId'] == property_id), None)
        if not details:
            return jsonify({'error': 'Property details not found'}), 404
        return jsonify(details)

    elif request.method == 'POST':
        details_data = request.get_json()
        
        # Check if details already exist
        if any(detail['propertyId'] == property_id for detail in data.get('property_details', [])):
            return jsonify({'error': 'Property details already exist'}), 400
            
        new_details = {
            'detailsId': str(len(data.get('property_details', [])) + 1),
            'propertyId': property_id,
            'amenities': details_data.get('amenities', []),
            'rules': details_data.get('rules', []),
            'utilities': details_data.get('utilities', []),
            'parking': details_data.get('parking', {}),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        if 'property_details' not in data:
            data['property_details'] = []
        data['property_details'].append(new_details)
        return jsonify(new_details), 201

    elif request.method == 'PATCH':
        update_data = request.get_json()
        details = next((detail for detail in data.get('property_details', [])
                       if detail['propertyId'] == property_id), None)
        if not details:
            return jsonify({'error': 'Property details not found'}), 404
            
        # Update allowed fields
        for key, value in update_data.items():
            if key not in ['detailsId', 'propertyId', 'createdAt']:
                details[key] = value
                
        details['updatedAt'] = datetime.now().isoformat()
        return jsonify(details)

@app.route('/api/properties/<property_id>/media', methods=['POST', 'GET', 'DELETE'])
def handle_property_media(property_id):
    data = load_data()
    
    # Check if property exists
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404

    if request.method == 'GET':
        media_items = [media for media in data.get('property_media', [])
                      if media['propertyId'] == property_id]
        return jsonify({'media': media_items})

    elif request.method == 'POST':
        media_data = request.get_json()
        
        new_media = {
            'mediaId': str(len(data.get('property_media', [])) + 1),
            'propertyId': property_id,
            'type': media_data.get('type', 'IMAGE'),
            'url': media_data['url'],
            'caption': media_data.get('caption', ''),
            'isPrimary': media_data.get('isPrimary', False),
            'createdAt': datetime.now().isoformat()
        }
        
        if 'property_media' not in data:
            data['property_media'] = []
        data['property_media'].append(new_media)
        return jsonify(new_media), 201

    elif request.method == 'DELETE':
        media_id = request.args.get('mediaId')
        if not media_id:
            return jsonify({'error': 'Media ID is required'}), 400
            
        media_list = data.get('property_media', [])
        media_item = next((media for media in media_list 
                          if media['mediaId'] == media_id and media['propertyId'] == property_id), None)
        if not media_item:
            return jsonify({'error': 'Media not found'}), 404
            
        media_list.remove(media_item)
        return jsonify({'message': 'Media deleted successfully'})

@app.route('/api/properties/<property_id>/listings', methods=['POST', 'GET', 'PATCH', 'DELETE'])
def handle_property_listings(property_id):
    data = load_data()
    
    # Check if property exists
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404

    if request.method == 'GET':
        listings = [listing for listing in data.get('property_listings', [])
                   if listing['propertyId'] == property_id]
        return jsonify({'listings': listings})

    elif request.method == 'POST':
        listing_data = request.get_json()
        
        new_listing = {
            'listingId': str(len(data.get('property_listings', [])) + 1),
            'propertyId': property_id,
            'title': listing_data['title'],
            'description': listing_data['description'],
            'price': listing_data['price'],
            'leaseTerms': listing_data.get('leaseTerms', {}),
            'availableFrom': listing_data['availableFrom'],
            'status': 'ACTIVE',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        if 'property_listings' not in data:
            data['property_listings'] = []
        data['property_listings'].append(new_listing)
        return jsonify(new_listing), 201

    elif request.method == 'PATCH':
        listing_id = request.args.get('listingId')
        if not listing_id:
            return jsonify({'error': 'Listing ID is required'}), 400
            
        update_data = request.get_json()
        listing = next((listing for listing in data.get('property_listings', [])
                       if listing['listingId'] == listing_id and listing['propertyId'] == property_id), None)
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
            
        # Update allowed fields
        for key, value in update_data.items():
            if key not in ['listingId', 'propertyId', 'createdAt']:
                listing[key] = value
                
        listing['updatedAt'] = datetime.now().isoformat()
        return jsonify(listing)

    elif request.method == 'DELETE':
        listing_id = request.args.get('listingId')
        if not listing_id:
            return jsonify({'error': 'Listing ID is required'}), 400
            
        listing = next((listing for listing in data.get('property_listings', [])
                       if listing['listingId'] == listing_id and listing['propertyId'] == property_id), None)
        if not listing:
            return jsonify({'error': 'Listing not found'}), 404
            
        listing['status'] = 'INACTIVE'
        listing['updatedAt'] = datetime.now().isoformat()
        return jsonify({'message': 'Listing deactivated successfully'})

@app.route('/api/users/<user_id>/properties', methods=['GET'])
def get_landlord_properties(user_id):
    data = load_data()
    
    # Verify user exists and is a landlord
    user = next((user for user in data['users'] 
                 if user['userId'] == user_id and user['role'] == 'LANDLORD'), None)
    if not user:
        return jsonify({'error': 'Landlord not found'}), 404
        
    # Get status filter from query params
    status = request.args.get('status', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    # Filter properties by landlord and status if provided
    filtered_properties = [prop for prop in data['properties']
                         if prop['landlordId'] == user_id and
                         (not status or prop['status'] == status)]

    # Paginate results
    properties_page, total_count = paginate_data(filtered_properties, begin, count)

    return jsonify({
        'properties': properties_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

@app.route('/api/properties/<property_id>/reviews', methods=['POST', 'GET'])
def handle_property_reviews(property_id):
    data = load_data()
    
    # Check if property exists
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404

    if request.method == 'GET':
        reviews = [review for review in data.get('property_reviews', [])
                  if review['propertyId'] == property_id]
        return jsonify({'reviews': reviews})

    elif request.method == 'POST':
        review_data = request.get_json()
        
        # Validate required fields
        if not all(key in review_data for key in ['userId', 'rating', 'comment']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        new_review = {
            'reviewId': str(len(data.get('property_reviews', [])) + 1),
            'propertyId': property_id,
            'userId': review_data['userId'],
            'rating': review_data['rating'],
            'comment': review_data['comment'],
            'createdAt': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
        
        if 'property_reviews' not in data:
            data['property_reviews'] = []
        data['property_reviews'].append(new_review)
        return jsonify(new_review), 201

@app.route('/api/properties/<property_id>/amenities', methods=['GET', 'POST', 'PATCH'])
def handle_property_amenities(property_id):
    data = load_data()
    
    # Check if property exists
    property_item = next((prop for prop in data['properties'] 
                         if prop['propertyId'] == property_id), None)
    if not property_item:
        return jsonify({'error': 'Property not found'}), 404

    if request.method == 'GET':
        amenities = next((amenity for amenity in data.get('property_amenities', [])
                         if amenity['propertyId'] == property_id), None)
        if not amenities:
            return jsonify({'error': 'Amenities not found'}), 404
        return jsonify(amenities)

    elif request.method == 'POST':
        amenities_data = request.get_json()
        
        new_amenities = {
            'amenityId': str(len(data.get('property_amenities', [])) + 1),
            'propertyId': property_id,
            'features': amenities_data.get('features', []),
            'utilities': amenities_data.get('utilities', []),
            'parking': amenities_data.get('parking', {}),
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        if 'property_amenities' not in data:
            data['property_amenities'] = []
        data['property_amenities'].append(new_amenities)
        return jsonify(new_amenities), 201

    elif request.method == 'PATCH':
        update_data = request.get_json()
        amenities = next((amenity for amenity in data.get('property_amenities', [])
                         if amenity['propertyId'] == property_id), None)
        if not amenities:
            return jsonify({'error': 'Amenities not found'}), 404
            
        for key, value in update_data.items():
            if key not in ['amenityId', 'propertyId', 'createdAt']:
                amenities[key] = value
                
        amenities['updatedAt'] = datetime.now().isoformat()
        return jsonify(amenities)