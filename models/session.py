from datetime import datetime

class WorkSession:
    def __init__(self, id, user_id, title, created_at, updated_at, current_section):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.current_section = current_section
    
    @classmethod
    def from_db_row(cls, row):
        """Create a WorkSession object from a database row"""
        if row:
            return cls(
                id=row['id'],
                user_id=row['user_id'],
                title=row['title'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                current_section=row['current_section']
            )
        return None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'current_section': self.current_section
        }