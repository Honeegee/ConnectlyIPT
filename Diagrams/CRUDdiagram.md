```mermaid
flowchart TD
    Client(("Client"))
    
    %% Authentication Layer
    subgraph Auth["Authentication"]
        direction LR
        Login["/auth/login/ (POST)"]
        Logout["/auth/logout/ (POST)"]
        Register["/auth/register/ (POST)"]
        GoogleOAuth["/auth/google/ (GET, POST)"]
        VerifyToken["/auth/verify/ (POST)"]
    end
    
    %% Core Entity Groups with better layout
    subgraph CoreEntities["Core Entities"]
        direction LR
        
        subgraph Users["User Management"]
            direction TB
            UserListCreate["/users/ (GET, POST)"]
            UserDetail["/users/:id/ (GET, PUT, DELETE)"]
            UserProfile["/users/:id/profile/ (GET, PUT)"]
        end
        
        subgraph Posts["Post Management"]
            direction TB
            PostListCreate["/posts/ (GET, POST)"]
            PostDetail["/posts/:id/ (GET, PUT, DELETE)"]
            NewsFeed["/posts/feed/ (GET)"]
        end
        
        subgraph Comments["Comment Management"]
            direction TB
            CommentListCreate["/comments/ (GET, POST)"]
            CommentDetail["/comments/:id/ (GET, PUT, DELETE)"]
            PostComments["/posts/:id/comments/ (GET)"]
        end
        
        subgraph Likes["Like Management"]
            direction TB
            PostLike["/posts/:id/like/ (POST, DELETE)"]
            CommentLike["/comments/:id/like/ (POST, DELETE)"]
            UserLikes["/users/:id/likes/ (GET)"]
        end
    end
    
    %% Social Features
    subgraph SocialFeatures["Social Features"]
        direction LR
        
        subgraph Following["Following System"]
            direction TB
            UserFollows["/users/:id/follows/ (GET)"]
            UserFollowers["/users/:id/followers/ (GET)"]
            FollowUser["/users/:id/follow/ (POST, DELETE)"]
        end
        
        subgraph Search["Search Features"]
            direction TB
            UserSearch["/users/search/ (GET)"]
            PostSearch["/posts/search/ (GET)"]
            ContentSearch["/search/ (GET)"]
        end
    end
    
    %% Administrative Features
    subgraph AdminSection["Administrative Controls"]
        direction LR
        
        subgraph AdminPanel["Admin Panel"]
            direction TB
            AdminDashboard["/admin/ (Full CRUD)"]
            UserManagement["/admin/users/"]
            ContentModeration["/admin/moderation/"]
        end
        
        subgraph PrivacySecurity["Privacy & Security"]
            direction TB
            UserPrivacySettings["/users/:id/privacy/ (GET, PUT)"]
            RBACEndpoint["/roles/ (GET, POST, PUT)"]
            PermissionCheck["/permissions/check/ (POST)"]
        end
    end
    
    %% Main Flow Connections
    Client --> Auth
    Auth --> CoreEntities
    Auth --> SocialFeatures
    Auth --> AdminSection
    
    %% Entity Relationships
    CoreEntities --> SocialFeatures
    CoreEntities --> AdminSection
    
    %% HTTP Method Legend
    subgraph Legend["HTTP Methods"]
        direction LR
        GetOp["GET - Read"]
        PostOp["POST - Create"]
        PutOp["PUT - Update"]
        DeleteOp["DELETE - Remove"]
    end
    
    %% Styling
    classDef client fill:#f5f5f5,stroke:#333,stroke-width:2px
    classDef auth fill:#cff,stroke:#333,stroke-width:2px
    classDef users fill:#f9f,stroke:#333,stroke-width:2px
    classDef posts fill:#ccf,stroke:#333,stroke-width:2px
    classDef comments fill:#fcf,stroke:#333,stroke-width:2px
    classDef likes fill:#ffc,stroke:#333,stroke-width:2px
    classDef following fill:#dfd,stroke:#333,stroke-width:2px
    classDef search fill:#ffe,stroke:#333,stroke-width:2px
    classDef admin fill:#eee,stroke:#333,stroke-width:2px
    classDef privacy fill:#fdd,stroke:#333,stroke-width:2px
    classDef legend fill:#fff,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
    
    class Client client
    class Login,Logout,Register,GoogleOAuth,VerifyToken auth
    class UserListCreate,UserDetail,UserProfile users
    class PostListCreate,PostDetail,NewsFeed posts
    class CommentListCreate,CommentDetail,PostComments comments
    class PostLike,CommentLike,UserLikes likes
    class UserFollows,UserFollowers,FollowUser following
    class UserSearch,PostSearch,ContentSearch search
    class AdminDashboard,UserManagement,ContentModeration admin
    class UserPrivacySettings,RBACEndpoint,PermissionCheck privacy
    class GetOp,PostOp,PutOp,DeleteOp legend