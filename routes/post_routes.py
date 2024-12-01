from flask import request, jsonify
from app import app
from app.services.data_service import load_data
from app.utils.pagination import paginate_data
from datetime import datetime

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = load_data()
    post_data = request.get_json()
    
    # Validate required fields
    required_fields = ['userId', 'title', 'content', 'postType']
    for field in required_fields:
        if field not in post_data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate post type
    valid_types = ['QUESTION', 'DISCUSSION', 'ANNOUNCEMENT', 'REVIEW']
    if post_data['postType'].upper() not in valid_types:
        return jsonify({'error': 'Invalid post type'}), 400
    
    # Validate that user exists
    user = next((user for user in data['users'] if user['userId'] == post_data['userId']), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Validate that user is active
    if user['status'] != 'ACTIVE':
        return jsonify({'error': 'User account is not active'}), 403
    
    new_post = {
        'postId': str(len(data['posts']) + 1),
        'userId': post_data['userId'],
        'title': post_data['title'],
        'content': post_data['content'],
        'postType': post_data['postType'].upper(),
        'tags': post_data.get('tags', []),
        'status': 'ACTIVE',
        'createdAt': datetime.now().isoformat(),
        'updatedAt': datetime.now().isoformat(),
        'viewCount': 0,
        'commentCount': 0,
        'reactionCount': 0
    }
    
    data['posts'].append(new_post)
    # In a real application, you would save to database here
    
    return jsonify(new_post), 201

@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    data = load_data()
    
    post = next((post for post in data['posts'] 
                 if post['postId'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Increment view count
    post['viewCount'] += 1
        
    return jsonify(post)

@app.route('/api/posts/<post_id>', methods=['PATCH'])
def update_post(post_id):
    data = load_data()
    update_data = request.get_json()
    
    post = next((post for post in data['posts'] 
                 if post['postId'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Prevent updates to critical fields
    protected_fields = ['postId', 'userId', 'createdAt', 'commentCount', 'reactionCount', 'viewCount']
    invalid_updates = [field for field in update_data if field in protected_fields]
    if invalid_updates:
        return jsonify({'error': f'Cannot update protected fields: {invalid_updates}'}), 400
    
    # Validate post type if being updated
    if 'postType' in update_data:
        valid_types = ['QUESTION', 'DISCUSSION', 'ANNOUNCEMENT', 'REVIEW']
        if update_data['postType'].upper() not in valid_types:
            return jsonify({'error': 'Invalid post type'}), 400
        update_data['postType'] = update_data['postType'].upper()
    
    # Update allowed fields
    for key, value in update_data.items():
        if key in post:
            post[key] = value
    
    post['updatedAt'] = datetime.now().isoformat()
    # In a real application, you would save to database here
    
    return jsonify(post)

@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = load_data()
    
    post = next((post for post in data['posts'] 
                 if post['postId'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Check if post is already deleted
    if post['status'] == 'DELETED':
        return jsonify({'error': 'Post is already deleted'}), 400
    
    # Soft delete - update status to deleted
    post['status'] = 'DELETED'
    post['updatedAt'] = datetime.now().isoformat()
    # In a real application, you would save to database here
    
    return jsonify({'message': 'Post deleted successfully'})

@app.route('/api/posts/<post_id>/comments', methods=['POST', 'GET', 'PATCH', 'DELETE'])
def handle_post_comments(post_id):
    data = load_data()
    
    # Check if post exists
    post = next((post for post in data['posts'] 
                 if post['postId'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Check if post is deleted
    if post['status'] == 'DELETED':
        return jsonify({'error': 'Cannot interact with deleted post'}), 400

    if request.method == 'GET':
        begin = int(request.args.get('begin', 1))
        count = int(request.args.get('count', 10))

        filtered_comments = [comment for comment in data['comments']
                           if comment['postId'] == post_id and comment['status'] == 'ACTIVE']

        comments_page, total_count = paginate_data(filtered_comments, begin, count)

        return jsonify({
            'comments': comments_page,
            'totalCount': total_count,
            'currentPage': begin,
            'pageSize': count
        })

    elif request.method == 'POST':
        comment_data = request.get_json()
        
        # Validate required fields
        required_fields = ['userId', 'content']
        for field in required_fields:
            if field not in comment_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        # Validate that user exists and is active
        user = next((user for user in data['users'] if user['userId'] == comment_data['userId']), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user['status'] != 'ACTIVE':
            return jsonify({'error': 'User account is not active'}), 403
        
        new_comment = {
            'commentId': str(len(data['comments']) + 1),
            'postId': post_id,
            'userId': comment_data['userId'],
            'content': comment_data['content'],
            'status': 'ACTIVE',
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }
        
        data['comments'].append(new_comment)
        post['commentCount'] += 1
        # In a real application, you would save to database here
        
        return jsonify(new_comment), 201

@app.route('/api/posts/<post_id>/reactions', methods=['POST', 'GET', 'DELETE'])
def handle_post_reactions(post_id):
    data = load_data()
    
    # Check if post exists
    post = next((post for post in data['posts'] 
                 if post['postId'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    # Check if post is deleted
    if post['status'] == 'DELETED':
        return jsonify({'error': 'Cannot interact with deleted post'}), 400

    if request.method == 'GET':
        reaction_type = request.args.get('type', '').upper()
        begin = int(request.args.get('begin', 1))
        count = int(request.args.get('count', 10))

        filtered_reactions = [reaction for reaction in data['reactions']
                            if reaction['postId'] == post_id and
                            (not reaction_type or reaction['reactionType'] == reaction_type)]

        reactions_page, total_count = paginate_data(filtered_reactions, begin, count)

        return jsonify({
            'reactions': reactions_page,
            'totalCount': total_count,
            'currentPage': begin,
            'pageSize': count
        })

    elif request.method == 'POST':
        reaction_data = request.get_json()
        
        # Validate required fields
        required_fields = ['userId', 'reactionType']
        for field in required_fields:
            if field not in reaction_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate reaction type
        valid_types = ['LIKE', 'LOVE', 'HELPFUL', 'INSIGHTFUL']
        if reaction_data['reactionType'].upper() not in valid_types:
            return jsonify({'error': 'Invalid reaction type'}), 400
            
        # Validate that user exists and is active
        user = next((user for user in data['users'] if user['userId'] == reaction_data['userId']), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user['status'] != 'ACTIVE':
            return jsonify({'error': 'User account is not active'}), 403
        
        # Check for existing reaction from same user
        existing_reaction = next((reaction for reaction in data['reactions']
                                if reaction['postId'] == post_id and
                                reaction['userId'] == reaction_data['userId']), None)
        if existing_reaction:
            return jsonify({'error': 'User has already reacted to this post'}), 400
        
        new_reaction = {
            'reactionId': str(len(data['reactions']) + 1),
            'postId': post_id,
            'userId': reaction_data['userId'],
            'reactionType': reaction_data['reactionType'].upper(),
            'createdAt': datetime.now().isoformat()
        }
        
        data['reactions'].append(new_reaction)
        post['reactionCount'] += 1
        # In a real application, you would save to database here
        
        return jsonify(new_reaction), 201

    elif request.method == 'DELETE':
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
            
        # Validate that user exists and is active
        user = next((user for user in data['users'] if user['userId'] == user_id), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        if user['status'] != 'ACTIVE':
            return jsonify({'error': 'User account is not active'}), 403
        
        reaction = next((reaction for reaction in data['reactions']
                        if reaction['postId'] == post_id and
                        reaction['userId'] == user_id), None)
        if not reaction:
            return jsonify({'error': 'Reaction not found'}), 404
        
        # Remove reaction
        data['reactions'].remove(reaction)
        post['reactionCount'] -= 1
        # In a real application, you would save to database here
        
        return jsonify({'message': 'Reaction removed successfully'})

@app.route('/api/posts', methods=['GET'])
def get_posts():
    data = load_data()
    status = request.args.get('status', '').upper()
    post_type = request.args.get('postType', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_posts = [post for post in data['posts']
                     if (not status or post['status'] == status) and
                     (not post_type or post['postType'] == post_type)]

    posts_page, total_count = paginate_data(filtered_posts, begin, count)

    return jsonify({
        'posts': posts_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })