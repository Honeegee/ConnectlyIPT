```mermaid
erDiagram
    User ||--o{ Post : "creates"
    User ||--o{ Like : "gives"
    User ||--o{ Comment : "writes"
    User }o--o{ User : "follows/is followed by"
    UserFollow }|--|| User : "has follower"
    UserFollow }|--|| User : "has followed"
    
    Post }|--|| User : "belongs to"
    Post ||--o{ Like : "receives"
    Post ||--o{ Comment : "has"
    
    Comment }|--|| User : "written by"
    Comment }|--|| Post : "belongs to"
    
    Like }|--|| User : "given by"
    Like }|--|| Post : "received by"
    
    User {
        int id PK
        string username
        string email
        string password
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime date_joined
        datetime last_login
        string first_name
        string last_name
    }
    
    Post {
        int id PK
        int author_id FK
        string title
        string content
        string post_type
        jsonb metadata
        datetime created_at
    }
    
    Like {
        int id PK
        int user_id FK
        int post_id FK
        datetime created_at
    }
    
    Comment {
        int id PK
        int author_id FK
        int post_id FK
        string text
        datetime created_at
    }
    
    UserFollow {
        int id PK
        int follower_id FK
        int followed_id FK
        datetime created_at
    }
