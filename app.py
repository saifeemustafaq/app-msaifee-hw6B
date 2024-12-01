# pip install Flask

from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)


# Load data from JSON file
def load_data():
    with open('sample_data.json', 'r') as file:
        return json.load(file)


def paginate_data(data_list, begin, count):
    # Convert begin to 0-based index
    start_idx = (begin - 1) if begin > 0 else 0
    end_idx = start_idx + count
    return data_list[start_idx:end_idx], len(data_list)


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


@app.route('/api/users/<landlord_id>/properties', methods=['GET'])
def get_landlord_properties(landlord_id):
    data = load_data()
    status = request.args.get('status', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_properties = [prop for prop in data['properties']
                           if prop['landlordId'] == landlord_id and
                           (not status or prop['status'] == status)]

    properties_page, total_count = paginate_data(filtered_properties, begin, count)

    return jsonify({
        'properties': properties_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })


@app.route('/api/properties/<property_id>/media', methods=['GET'])
def get_property_media(property_id):
    data = load_data()
    media_type = request.args.get('type', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_media = [media for media in data['mediaAssets']
                      if media['propertyId'] == property_id and
                      (not media_type or media['assetType'] == media_type)]

    media_page, total_count = paginate_data(filtered_media, begin, count)

    return jsonify({
        'mediaAssets': media_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })


@app.route('/api/posts', methods=['GET'])
def get_posts():
    data = load_data()
    post_type = request.args.get('type', '').upper()
    status = request.args.get('status', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_posts = [post for post in data['posts']
                      if (not post_type or post['postType'] == post_type) and
                      (not status or post['status'] == status)]

    posts_page, total_count = paginate_data(filtered_posts, begin, count)

    return jsonify({
        'posts': posts_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })


@app.route('/api/posts/<post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    data = load_data()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_comments = [comment for comment in data['comments']
                         if comment['postId'] == post_id]

    comments_page, total_count = paginate_data(filtered_comments, begin, count)

    return jsonify({
        'comments': comments_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })


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


@app.route('/api/users/<user_id>/activities', methods=['GET'])
def get_user_activities(user_id):
    data = load_data()
    activity_type = request.args.get('type', '').upper()
    begin = int(request.args.get('begin', 1))
    count = int(request.args.get('count', 10))

    filtered_activities = [activity for activity in data['tokenActivities']
                           if activity['userId'] == user_id and
                           (not activity_type or activity['activityType'] == activity_type)]

    activities_page, total_count = paginate_data(filtered_activities, begin, count)

    return jsonify({
        'activities': activities_page,
        'totalCount': total_count,
        'currentPage': begin,
        'pageSize': count
    })

if __name__ == '__main__':
    app.run(port=8080, debug=True)