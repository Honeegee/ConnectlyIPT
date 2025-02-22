# API CRUD Interaction Flow Diagram

```mermaid
graph LR
    %% Nodes Definition
    Browser[Client Browser or Postman]
    Request[Request Received]
    Validate[Input Validation]
    Security[Security Middleware: Token & Permissions]
    UserCRUD[User Operations]
    PostCRUD[Post Operations]
    CommentCRUD[Comment Operations]
    ProfileCRUD[Profile Operations]
    Login[Login Request]
    Token[Token Generation]
    DB[(Database SQL/NoSQL)]
    Logger[Singleton Logger]
    Factory[Factory Pattern]

    %% Subgraphs
    subgraph Client
        Browser
    end

    subgraph API_Layer
        Request
        Validate
        Security
        
        subgraph CRUD_Logic
            subgraph Users_API
                UserCRUD -->|GET /users| U1[List Users]
                UserCRUD -->|POST /users| U2[Create User]
                UserCRUD -->|GET /users/:id| U3[Get User]
                UserCRUD -->|PUT /users/:id| U4[Update User]
                UserCRUD -->|DELETE /users/:id| U5[Delete User]
            end

            subgraph Posts_API
                PostCRUD -->|GET /posts| P1[List Posts]
                PostCRUD -->|POST /posts| P2[Create Post]
                PostCRUD -->|GET /posts/:id| P3[Get Post]
                PostCRUD -->|PUT /posts/:id| P4[Update Post]
                PostCRUD -->|DELETE /posts/:id| P5[Delete Post]
                PostCRUD -->|GET /feed| P6[News Feed]
                PostCRUD -->|POST /posts/:id/like| P7[Like Post]
                PostCRUD -->|DELETE /posts/:id/like| P8[Unlike Post]
            end

            subgraph Comments_API
                CommentCRUD -->|GET /comments| C1[List Comments]
                CommentCRUD -->|POST /comments| C2[Create Comment]
                CommentCRUD -->|GET /comments/:id| C3[Get Comment]
                CommentCRUD -->|PUT /comments/:id| C4[Update Comment]
                CommentCRUD -->|DELETE /comments/:id| C5[Delete Comment]
                CommentCRUD -->|GET /posts/:id/comments| C6[Post Comments]
                CommentCRUD -->|POST /posts/:id/comments| C7[Add Comment]
            end

            subgraph Profiles_API
                ProfileCRUD -->|GET /profiles/me| PR1[My Profile]
                ProfileCRUD -->|GET /profiles/:username| PR2[User Profile]
                ProfileCRUD -->|POST /profiles/:username| PR3[Update Profile]
                ProfileCRUD -->|GET /profiles/:username/posts| PR4[User Posts]
                ProfileCRUD -->|POST /profiles/:username/follow| PR5[Follow]
                ProfileCRUD -->|DELETE /profiles/:username/unfollow| PR6[Unfollow]
            end
        end
    end

    %% Main Flow
    Browser -->|HTTPS Request| Request
    Request --> Validate
    Validate -->|Valid Request| Security
    Validate -->|Invalid Input| Logger
    
    Security -->|Unauthorized| Browser
    Security -->|Authorized Request| CRUD_Logic

    %% Auth Flow
    Login -->|POST /api/login| Token
    Token -->|POST /api/token| Security

    %% Data Layer Flow
    UserCRUD --> DB
    PostCRUD --> DB
    CommentCRUD --> DB
    ProfileCRUD --> DB

    %% Factory Pattern
    Factory --> UserCRUD
    Factory --> PostCRUD
    Factory --> CommentCRUD
    Factory --> ProfileCRUD

    %% Logging Flow
    UserCRUD -->|Log Operations| Logger
    PostCRUD -->|Log Operations| Logger
    CommentCRUD -->|Log Operations| Logger
    ProfileCRUD -->|Log Operations| Logger

    %% Response Flow
    DB -->|Response Data| CRUD_Logic
    CRUD_Logic -->|Send Response| Browser

    %% Styling
    classDef clientNode fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    classDef middleware fill:#bbf,stroke:#333,stroke-width:2px,color:#000
    classDef operation fill:#dfd,stroke:#333,stroke-width:1px,color:#000
    classDef database fill:#fdd,stroke:#333,stroke-width:2px,color:#000
    classDef utility fill:#dff,stroke:#333,stroke-width:1px,color:#000
    classDef endpoint fill:#efe,stroke:#333,stroke-width:1px,color:#000

    class Browser clientNode
    class Security,Validate middleware
    class UserCRUD,PostCRUD,CommentCRUD,ProfileCRUD operation
    class DB database
    class Logger,Factory utility
    class U1,U2,U3,U4,U5,P1,P2,P3,P4,P5,P6,P7,P8,C1,C2,C3,C4,C5,C6,C7,PR1,PR2,PR3,PR4,PR5,PR6 endpoint

```

## API Endpoints Summary

### Authentication
- `POST /api/login/` - User login
- `POST /api/token/` - Obtain authentication token

### Users
- `GET /api/users/` - List all users
- `POST /api/users/` - Create new user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create new post
- `GET /api/posts/{id}/` - Get post details
- `PUT /api/posts/{id}/` - Update post
- `DELETE /api/posts/{id}/` - Delete post
- `POST /api/posts/{id}/like/` - Like a post
- `DELETE /api/posts/{id}/like/` - Unlike a post
- `GET /api/feed/` - Get personalized news feed

### Comments
- `GET /api/comments/` - List all comments
- `POST /api/comments/` - Create new comment
- `GET /api/comments/{id}/` - Get comment details
- `PUT /api/comments/{id}/` - Update comment
- `DELETE /api/comments/{id}/` - Delete comment
- `GET /api/posts/{id}/comments/` - Get comments for a post
- `POST /api/posts/{id}/comments/` - Add comment to a post

### Profiles
- `GET /api/profiles/me/` - Get own profile
- `GET /api/profiles/{username}/` - Get user profile
- `POST /api/profiles/{username}/` - Update profile
- `GET /api/profiles/{username}/posts/` - Get user's posts
- `POST /api/profiles/{username}/follow/` - Follow user
- `DELETE /api/profiles/{username}/unfollow/` - Unfollow user
