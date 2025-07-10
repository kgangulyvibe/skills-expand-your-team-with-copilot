"""
In-memory database for Mergington High School API - for testing/development when MongoDB is not available
"""

from argon2 import PasswordHasher
from copy import deepcopy

# In-memory storage
activities_data = {}
teachers_data = {}

class MockCollection:
    def __init__(self, data_store):
        self.data_store = data_store
    
    def find(self, query=None):
        """Mock find method to return all documents matching query"""
        if query is None:
            query = {}
        
        results = []
        for doc_id, doc in self.data_store.items():
            doc_copy = deepcopy(doc)
            doc_copy['_id'] = doc_id
            
            # Simple query matching - check if all query fields match document
            matches = True
            for key, value in query.items():
                if key not in doc_copy:
                    matches = False
                    break
                    
                # Handle nested queries like schedule_details.days
                if '.' in key:
                    keys = key.split('.')
                    current_value = doc_copy
                    for k in keys:
                        if k in current_value:
                            current_value = current_value[k]
                        else:
                            matches = False
                            break
                    
                    if not matches:
                        break
                        
                    # Handle $in operator
                    if isinstance(value, dict) and '$in' in value:
                        if not any(item in current_value for item in value['$in']):
                            matches = False
                    # Handle $gte and $lte operators
                    elif isinstance(value, dict) and '$gte' in value:
                        if current_value < value['$gte']:
                            matches = False
                    elif isinstance(value, dict) and '$lte' in value:
                        if current_value > value['$lte']:
                            matches = False
                    else:
                        if current_value != value:
                            matches = False
                else:
                    if doc_copy[key] != value:
                        matches = False
                        break
            
            if matches:
                results.append(doc_copy)
        
        return results
    
    def find_one(self, query):
        """Mock find_one method"""
        results = self.find(query)
        return results[0] if results else None
    
    def count_documents(self, query):
        """Mock count_documents method"""
        return len(self.find(query))
    
    def insert_one(self, document):
        """Mock insert_one method"""
        doc_copy = deepcopy(document)
        doc_id = doc_copy.pop('_id')
        self.data_store[doc_id] = doc_copy
        return True
    
    def update_one(self, filter_query, update_query):
        """Mock update_one method"""
        doc = self.find_one(filter_query)
        if not doc:
            return type('Result', (), {'modified_count': 0})()
        
        doc_id = doc['_id']
        
        # Handle $push operation
        if '$push' in update_query:
            for field, value in update_query['$push'].items():
                if field in self.data_store[doc_id]:
                    self.data_store[doc_id][field].append(value)
                else:
                    self.data_store[doc_id][field] = [value]
        
        # Handle $pull operation
        if '$pull' in update_query:
            for field, value in update_query['$pull'].items():
                if field in self.data_store[doc_id] and value in self.data_store[doc_id][field]:
                    self.data_store[doc_id][field].remove(value)
        
        return type('Result', (), {'modified_count': 1})()
    
    def aggregate(self, pipeline):
        """Mock aggregate method for getting unique days"""
        # Simple implementation for getting unique days
        if len(pipeline) >= 2 and pipeline[0].get('$unwind') == '$schedule_details.days':
            unique_days = set()
            for doc in self.data_store.values():
                if 'schedule_details' in doc and 'days' in doc['schedule_details']:
                    for day in doc['schedule_details']['days']:
                        unique_days.add(day)
            
            return [{'_id': day} for day in sorted(unique_days)]
        
        return []

# Create mock collections
activities_collection = MockCollection(activities_data)
teachers_collection = MockCollection(teachers_data)

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
    else:
        # Add missing activities for existing database
        for name, details in initial_activities.items():
            if not activities_collection.find_one({"_id": name}):
                activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Manga Maniacs": {
        "description": "Dive into the incredible worlds of Japanese manga! From epic shonen adventures to heartwarming slice-of-life stories, discover amazing characters, stunning artwork, and mind-blowing plot twists. Share your favorite series, debate the best anime adaptations, and find your next obsession with fellow otaku!",
        "schedule": "Tuesdays, 7:00 PM - 8:30 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:30"
        },
        "max_participants": 15,
        "participants": []
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]