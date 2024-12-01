# User Routes Testing Documentation

## 1. Get Users
### Basic Request
```http
GET http://localhost:8080/api/users?role=landlord&begin=1&count=10
```
### Request Parameters
- `role`: landlord
- `begin`: 1 (page number)
- `count`: 10 (items per page)

### Sample Response
```json
{
    "users": [
        {
            "userId": "2",
            "username": "jsmith",
            "firstName": "John",
            "lastName": "Smith",
            "email": "jsmith@email.com",
            "role": "LANDLORD",
            "phoneNumber": "555-0102",
            "status": "ACTIVE",
            "isVerified": true
        }
    ],
    "totalCount": 1,
    "currentPage": 1,
    "pageSize": 10
}
```

## 2. Create User
### Request
```http
POST http://localhost:8080/api/users
```

### Request Body
```json
{
    "username": "newlandlord",
    "password": "securepass123",
    "role": "LANDLORD",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@email.com",
    "phoneNumber": "555-0123",
    "campusAffiliation": "Downtown Campus",
    "profilePictureUrl": "https://example.com/profile.jpg"
}
```

### Sample Response
```json
{
    "userId": "5",
    "username": "newlandlord",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@email.com",
    "role": "LANDLORD",
    "phoneNumber": "555-0123",
    "campusAffiliation": "Downtown Campus",
    "profilePictureUrl": "https://example.com/profile.jpg",
    "status": "ACTIVE",
    "isVerified": false,
    "createdAt": "2024-03-20T10:30:00",
    "lastLogin": null,
    "tokenBalance": 0
}
```

## 3. Get User by ID
### Request
```http
GET http://localhost:8080/api/users/5
```

### Sample Response
```json
{
    "userId": "5",
    "username": "newlandlord",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@email.com",
    "role": "LANDLORD",
    "phoneNumber": "555-0123",
    "status": "ACTIVE"
}
```

## 4. Update User
### Request
```http
PATCH http://localhost:8080/api/users/5
```

### Request Body
```json
{
    "phoneNumber": "555-9999",
    "campusAffiliation": "Updated Campus"
}
```

### Sample Response
```json
{
    "userId": "5",
    "username": "newlandlord",
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@email.com",
    "role": "LANDLORD",
    "phoneNumber": "555-9999",
    "campusAffiliation": "Updated Campus",
    "status": "ACTIVE"
}
```

## 5. Delete User
### Request
```http
DELETE http://localhost:8080/api/users/5
```

### Sample Response
```json
{
    "message": "User deactivated successfully"
}
```

## 6. User Profile Operations

### 6.1 Get User Profile
#### Request
```http
GET http://localhost:8080/api/users/5/profile
```

#### Sample Response
```json
{
    "profileId": "5",
    "userId": "5",
    "bio": "Experienced landlord with multiple properties",
    "preferences": {
        "contactMethod": "email",
        "notificationSettings": {
            "email": true,
            "sms": false
        }
    },
    "createdAt": "2024-03-20T10:35:00",
    "updatedAt": "2024-03-20T10:35:00"
}
```

### 6.2 Create User Profile
#### Request
```http
POST http://localhost:8080/api/users/5/profile
```

#### Request Body
```json
{
    "bio": "Experienced landlord with multiple properties",
    "preferences": {
        "contactMethod": "email",
        "notificationSettings": {
            "email": true,
            "sms": false
        }
    }
}
```

#### Sample Response
```json
{
    "profileId": "5",
    "userId": "5",
    "bio": "Experienced landlord with multiple properties",
    "preferences": {
        "contactMethod": "email",
        "notificationSettings": {
            "email": true,
            "sms": false
        }
    },
    "createdAt": "2024-03-20T10:35:00",
    "updatedAt": "2024-03-20T10:35:00"
}
```

### 6.3 Update User Profile
#### Request
```http
PATCH http://localhost:8080/api/users/5/profile
```

#### Request Body
```json
{
    "bio": "Updated bio information",
    "preferences": {
        "contactMethod": "sms",
        "notificationSettings": {
            "email": true,
            "sms": true
        }
    }
}
```

#### Sample Response
```json
{
    "profileId": "5",
    "userId": "5",
    "bio": "Updated bio information",
    "preferences": {
        "contactMethod": "sms",
        "notificationSettings": {
            "email": true,
            "sms": true
        }
    },
    "createdAt": "2024-03-20T10:35:00",
    "updatedAt": "2024-03-20T10:40:00"
}
```

## 7. Property Reviews

### 7.1 Get Property Reviews
#### Request
```http
GET http://localhost:8080/api/properties/prop789/reviews
```

#### Sample Response
```json
{
    "reviews": [
        {
            "reviewId": "review123",
            "propertyId": "prop789",
            "userId": "12345",
            "rating": 4.5,
            "comment": "Great location and amenities",
            "createdAt": "2024-03-15T09:00:00Z",
            "status": "ACTIVE"
        },
        {
            "reviewId": "review124",
            "propertyId": "prop789",
            "userId": "12346",
            "rating": 4.0,
            "comment": "Clean and well-maintained",
            "createdAt": "2024-03-16T10:00:00Z",
            "status": "ACTIVE"
        }
    ]
}
```

### 7.2 Create Property Review
#### Request
```http
POST http://localhost:8080/api/properties/prop789/reviews
```

#### Request Body
```json
{
    "userId": "12345",
    "rating": 4.5,
    "comment": "Great location and amenities"
}
```

#### Sample Response
```json
{
    "reviewId": "review125",
    "propertyId": "prop789",
    "userId": "12345",
    "rating": 4.5,
    "comment": "Great location and amenities",
    "createdAt": "2024-03-20T10:30:00Z",
    "status": "ACTIVE"
}
```

## 8. Property Amenities

### 8.1 Get Property Amenities
#### Request
```http
GET http://localhost:8080/api/properties/prop789/amenities
```

#### Sample Response
```json
{
    "amenityId": "amen123",
    "propertyId": "prop789",
    "features": [
        "Swimming Pool",
        "Gym",
        "Study Room",
        "Laundry"
    ],
    "utilities": [
        "Water",
        "Electricity",
        "Internet"
    ],
    "parking": {
        "type": "Covered",
        "spots": 50,
        "includedInRent": true
    },
    "createdAt": "2024-02-01T08:00:00Z",
    "updatedAt": "2024-02-01T08:00:00Z"
}
```

### 8.2 Create Property Amenities
#### Request
```http
POST http://localhost:8080/api/properties/prop789/amenities
```

#### Request Body
```json
{
    "features": [
        "Swimming Pool",
        "Gym",
        "Study Room",
        "Laundry"
    ],
    "utilities": [
        "Water",
        "Electricity",
        "Internet"
    ],
    "parking": {
        "type": "Covered",
        "spots": 50,
        "includedInRent": true
    }
}
```

#### Sample Response
```json
{
    "amenityId": "amen124",
    "propertyId": "prop789",
    "features": [
        "Swimming Pool",
        "Gym",
        "Study Room",
        "Laundry"
    ],
    "utilities": [
        "Water",
        "Electricity",
        "Internet"
    ],
    "parking": {
        "type": "Covered",
        "spots": 50,
        "includedInRent": true
    },
    "createdAt": "2024-03-20T10:30:00Z",
    "updatedAt": "2024-03-20T10:30:00Z"
}
```

### 8.3 Update Property Amenities
#### Request
```http
PATCH http://localhost:8080/api/properties/prop789/amenities
```

#### Request Body
```json
{
    "features": [
        "Swimming Pool",
        "Gym",
        "Study Room",
        "Laundry",
        "Basketball Court"
    ],
    "utilities": [
        "Water",
        "Electricity",
        "Internet",
        "Gas"
    ]
}
```

#### Sample Response
```json
{
    "amenityId": "amen124",
    "propertyId": "prop789",
    "features": [
        "Swimming Pool",
        "Gym",
        "Study Room",
        "Laundry",
        "Basketball Court"
    ],
    "utilities": [
        "Water",
        "Electricity",
        "Internet",
        "Gas"
    ],
    "parking": {
        "type": "Covered",
        "spots": 50,
        "includedInRent": true
    },
    "createdAt": "2024-03-20T10:30:00Z",
    "updatedAt": "2024-03-20T10:35:00Z"
}
```

