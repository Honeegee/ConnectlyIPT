# API CRUD Interaction Flow Diagram

```mermaid
flowchart TB
    %% Main components
    Browser["Client Browser"]
    
    %% API Gateway layer
    subgraph APIGateway["API Gateway"]
        direction TB
        Request["Request<br>Received"]
        Validate["Input<br>Validation"]
        Security["Security Middleware:<br>Token & Permissions"]
        Login["Login<br>Request"]
        Token["Token<br>Generation"]
    end
    
    %% Service layer
    subgraph Services["Service Layer"]
        direction TB
        Factory["Service<br>Factory"]
        
        subgraph UserService["User Service"]
            direction TB
            UserCRUD["User<br>Operations"]
        end
        
        subgraph PostService["Post Service"]
            direction TB
            PostCRUD["Post<br>Operations"] 
        end
        
        subgraph CommentService["Comment Service"]
            direction TB
            CommentCRUD["Comment<br>Operations"]
        end
        
        subgraph ProfileService["Profile Service"]
            direction TB
            ProfileCRUD["Profile<br>Operations"]
        end
    end
    
    %% Data layer
    subgraph DataLayer["Data Layer"]
        direction TB
        DB[("Database<br>SQL/NoSQL")]
        Logger["Singleton<br>Logger"]
    end
    
    %% Endpoint details
    subgraph UserEndpoints["User Endpoints"]
        direction LR
        U1["GET /users<br>List Users"]
        U2["POST /users<br>Create User"]
        U3["GET /users/:id<br>Get User"]
        U4["PUT /users/:id<br>Update User"]
        U5["DELETE /users/:id<br>Delete User"]
    end
    
    subgraph PostEndpoints["Post Endpoints"]
        direction LR
        P1["GET /posts<br>List Posts"]
        P2["POST /posts<br>Create Post"]
        P3["GET /posts/:id<br>Get Post"]
        P4["PUT /posts/:id<br>Update Post"]
        P5["DELETE /posts/:id<br>Delete Post"]
        P6["GET /feed<br>News Feed"]
        P7["POST /posts/:id/like<br>Like Post"]
        P8["DELETE /posts/:id/like<br>Unlike Post"]
    end
    
    subgraph CommentEndpoints["Comment Endpoints"]
        direction LR
        C1["GET /comments<br>List Comments"]
        C2["POST /comments<br>Create Comment"]
        C3["GET /comments/:id<br>Get Comment"]
        C4["PUT /comments/:id<br>Update Comment"]
        C5["DELETE /comments/:id<br>Delete Comment"]
        C6["GET /posts/:id/comments<br>Post Comments"]
        C7["POST /posts/:id/comments<br>Add Comment"]
    end
    
    subgraph ProfileEndpoints["Profile Endpoints"]
        direction LR
        PR1["GET /profiles/me<br>My Profile"]
        PR2["GET /profiles/:username<br>User Profile"]
        PR3["POST /profiles/:username<br>Update Profile"]
        PR4["GET /profiles/:username/posts<br>User Posts"]
        PR5["POST /profiles/:username/follow<br>Follow"]
        PR6["DELETE /profiles/:username/unfollow<br>Unfollow"]
    end
    
    %% Core flow connections
    Browser <-->|"HTTPS Request/Response"| APIGateway
    Request --> Validate
    Validate -->|"Valid Request"| Security
    Validate -->|"Invalid Input"| Logger
    Security -->|"Unauthorized"| Browser
    Security -->|"Authorized Request"| Factory
    
    %% Auth flow
    Login -->|"POST /api/login"| Token
    Token -->|"POST /api/token"| Security
    
    %% Factory pattern connections
    Factory --> UserService
    Factory --> PostService
    Factory --> CommentService
    Factory --> ProfileService
    
    %% Service to data layer connections
    UserCRUD <--> DB
    PostCRUD <--> DB
    CommentCRUD <--> DB
    ProfileCRUD <--> DB
    
    %% Logger connections
    UserCRUD -->|"Log<br>Operations"| Logger
    PostCRUD -->|"Log<br>Operations"| Logger
    CommentCRUD -->|"Log<br>Operations"| Logger
    ProfileCRUD -->|"Log<br>Operations"| Logger
    
    %% Connect services to endpoints
    UserCRUD --- UserEndpoints
    PostCRUD --- PostEndpoints
    CommentCRUD --- CommentEndpoints
    ProfileCRUD --- ProfileEndpoints
    
    %% Styling
    classDef clientNode fill:#f9f,stroke:#333,stroke-width:3px,color:#000
    classDef middleware fill:#bbf,stroke:#333,stroke-width:3px,color:#000
    classDef service fill:#dfd,stroke:#333,stroke-width:3px,color:#000
    classDef database fill:#fdd,stroke:#333,stroke-width:3px,color:#000
    classDef utility fill:#dff,stroke:#333,stroke-width:3px,color:#000
    classDef endpoint fill:#efe,stroke:#333,stroke-width:3px,color:#000
    classDef gateway fill:#ffd,stroke:#333,stroke-width:3px,color:#000
    classDef factory fill:#ffb,stroke:#333,stroke-width:3px,color:#000
    
    %% Apply classes
    class Browser clientNode
    class Security,Validate,Login,Token,Request middleware
    class UserCRUD,PostCRUD,CommentCRUD,ProfileCRUD service
    class DB database
    class Logger utility
    class Factory factory
    class APIGateway gateway
    class U1,U2,U3,U4,U5,P1,P2,P3,P4,P5,P6,P7,P8,C1,C2,C3,C4,C5,C6,C7,PR1,PR2,PR3,PR4,PR5,PR6 endpoint

        %% Enhanced arrow colors

    linkStyle 0 stroke:#9B59B6,stroke-width:3px
    linkStyle 1 stroke:#9B59B6,stroke-width:3px
    linkStyle 2 stroke:#9B59B6,stroke-width:3px
    linkStyle 3 stroke:#9B59B6,stroke-width:3px
    linkStyle 4 stroke:#9B59B6,stroke-width:3px
    linkStyle 5 stroke:#9B59B6,stroke-width:3px
    linkStyle 6 stroke:#9B59B6,stroke-width:3px
    linkStyle 7 stroke:#9B59B6,stroke-width:3px
    linkStyle 8 stroke:#9B59B6,stroke-width:3px
    linkStyle 9 stroke:#9B59B6,stroke-width:3px
    linkStyle 10 stroke:#9B59B6,stroke-width:3px
    linkStyle 11 stroke:#9B59B6,stroke-width:3px
    linkStyle 12 stroke:#9B59B6,stroke-width:3px
    linkStyle 13 stroke:#9B59B6,stroke-width:3px
    linkStyle 14 stroke:#9B59B6,stroke-width:3px
    linkStyle 15 stroke:#9B59B6,stroke-width:3px
    linkStyle 16 stroke:#9B59B6,stroke-width:3px
    linkStyle 17 stroke:#9B59B6,stroke-width:3px
    linkStyle 18 stroke:#9B59B6,stroke-width:3px
    linkStyle 19 stroke:#9B59B6,stroke-width:3px


