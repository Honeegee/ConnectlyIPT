# API CRUD Interaction Flow Diagram

```mermaid
flowchart TD
    %% Main Layers
    Client[Client]
    ClientBrowser["Client Browser or Postman"]
    API_Layer[API Layer]
    RequestReceived[Request Received]
    ValidateRequest[Validate Request]
    SecurityMiddleware["Security Middleware: Token\nValidation & Permissions"]
    CRUD_Layer[CRUD Logic Layer]
    Utility_Layer[Utility Layer]
    SingletonLogger[Singleton Logger]
    FactoryPattern["Factory Pattern for\nObject Creation"]
    Data_Layer[Data Layer]
    Database["Database (SQL)"]
    
    %% Flow connections
    Client --> ClientBrowser
    ClientBrowser -- "HTTPS Request" --> RequestReceived
    RequestReceived -- "Input Validation" --> ValidateRequest
    ValidateRequest -- "Valid Request" --> SecurityMiddleware
    ValidateRequest -- "Invalid Input" --> SingletonLogger
    ValidateRequest -- "Log Validation Results" --> SingletonLogger
    SecurityMiddleware -- "Unauthorized" --> ClientBrowser
    SecurityMiddleware -- "Log Security Events" --> SingletonLogger
    SecurityMiddleware -- "Authorized Request" --> CRUD_Layer
    CRUD_Layer -- "Log CRUD Events" --> SingletonLogger
    CRUD_Layer -- "Create Object via Factory" --> FactoryPattern
    CRUD_Layer -- "Perform CRUD Operation" --> Database
    CRUD_Layer -- "CRUD Error" --> SingletonLogger
    CRUD_Layer -- "Response Data" --> ClientBrowser
    
    %% Defining subgraphs
    subgraph Client
        ClientBrowser
    end
    
    subgraph API_Layer
        RequestReceived
        ValidateRequest
        SecurityMiddleware
    end
    
    subgraph CRUD_Layer
        %% Authentication Endpoints
        subgraph AuthEndpoints[Authentication Endpoints]
            Auth1["/api/login/ (POST)"]
            Auth2["/api/logout/ (GET)"]
            Auth3["/api/register/ (POST)"]
            Auth4["/social-auth/google-oauth2/ (GET, POST)"]
        end
        
        %% User Management
        subgraph UserEndpoints[User Management]
            User1["/api/users/ (GET, POST)"]
            User2["/api/users/{id}/ (GET, PUT, DELETE)"]
            User3["/api/users/{username}/profile/ (GET, POST)"]
            User4["/api/users/{username}/posts/ (GET)"]
        end
        
        %% Social Features
        subgraph SocialEndpoints[Following System]
            Social1["/api/users/{username}/follow/ (POST)"]
            Social2["/api/users/{username}/follow/ (DELETE)"]
            Social3["/api/users/{username}/followers/ (GET)"]
            Social4["/api/users/{username}/following/ (GET)"]
        end
        
        %% Post Management
        subgraph PostEndpoints[Post Management]
            Post1["/api/posts/ (GET, POST)"]
            Post2["/api/posts/{id}/ (GET, PUT, DELETE)"]
            Post3["/api/feed/ (GET)"]
            Post4["/api/posts/{id}/like/ (POST, DELETE)"]
            Post5["/api/posts/{id}/likes/ (GET)"]
        end
        
        %% Comment Management
        subgraph CommentEndpoints[Comment Management]
            Comment1["/api/comments/ (GET, POST)"]
            Comment2["/api/comments/{id}/ (GET, PUT, DELETE)"]
            Comment3["/api/posts/{id}/comments/ (GET, POST)"]
        end
        
        %% Post Types
        subgraph PostTypes[Post Types]
            Type1["Text Post"]
            Type2["Image Post"]
            Type3["Video Post"]
        end
        
        %% Feed Filters
        subgraph FeedFilters[Feed Filters]
            Filter1["show_followed"]
            Filter2["show_liked"]
            Filter3["post_type"]
        end
    end
    
    subgraph Utility_Layer
        SingletonLogger
        FactoryPattern
    end
    
    subgraph Data_Layer
        Database
    end
