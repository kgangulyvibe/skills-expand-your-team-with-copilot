"""
In-memory database configuration for Mergington High School API
"""

from argon2 import PasswordHasher

# In-memory storage
activities_data = {}
teachers_data = {}

# Mock collection classes to mimic MongoDB interface
class MockCollection:
    def __init__(self, data_dict):
        self.data = data_dict
    
    def find(self, query=None):
        if query is None:
            query = {}
        
        results = []
        for doc_id, doc in self.data.items():
            # Simple query matching
            match = True
            for key, value in query.items():
                if key == "schedule_details.days":
                    # Handle the $in operator for days
                    if "$in" in value:
                        days_to_match = value["$in"]
                        if "schedule_details" not in doc or "days" not in doc["schedule_details"]:
                            match = False
                            break
                        if not any(day in doc["schedule_details"]["days"] for day in days_to_match):
                            match = False
                            break
                elif key == "schedule_details.start_time":
                    # Handle $gte operator
                    if "$gte" in value:
                        min_time = value["$gte"]
                        if "schedule_details" not in doc or "start_time" not in doc["schedule_details"]:
                            match = False
                            break
                        if doc["schedule_details"]["start_time"] < min_time:
                            match = False
                            break
                elif key == "schedule_details.end_time":
                    # Handle $lte operator
                    if "$lte" in value:
                        max_time = value["$lte"]
                        if "schedule_details" not in doc or "end_time" not in doc["schedule_details"]:
                            match = False
                            break
                        if doc["schedule_details"]["end_time"] > max_time:
                            match = False
                            break
                else:
                    # Simple equality check
                    if key not in doc or doc[key] != value:
                        match = False
                        break
            
            if match:
                result = doc.copy()
                result["_id"] = doc_id
                results.append(result)
        
        return results
    
    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None
    
    def count_documents(self, query):
        return len(self.find(query))
    
    def insert_one(self, doc):
        doc_id = doc.pop("_id")
        self.data[doc_id] = doc
        return type('MockResult', (), {'inserted_id': doc_id})()
    
    def update_one(self, query, update):
        results = self.find(query)
        if results:
            doc_id = results[0]["_id"]
            doc = self.data[doc_id]
            
            # Handle $push operation
            if "$push" in update:
                for field, value in update["$push"].items():
                    if field not in doc:
                        doc[field] = []
                    doc[field].append(value)
            
            # Handle $pull operation
            if "$pull" in update:
                for field, value in update["$pull"].items():
                    if field in doc and isinstance(doc[field], list):
                        doc[field] = [item for item in doc[field] if item != value]
            
            return type('MockResult', (), {'modified_count': 1})()
        return type('MockResult', (), {'modified_count': 0})()
    
    def aggregate(self, pipeline):
        # Simple implementation for the days aggregation
        if len(pipeline) == 3 and "$unwind" in pipeline[0] and "$group" in pipeline[1]:
            days = set()
            for doc in self.data.values():
                if "schedule_details" in doc and "days" in doc["schedule_details"]:
                    days.update(doc["schedule_details"]["days"])
            return [{"_id": day} for day in sorted(days)]
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

