```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant API as Backend API
    participant Google as Google OAuth
    participant DB as Database
    participant Email as Email Service

    %% Google OAuth Flow
    alt Google OAuth Authentication
        Client->>API: 1. Request OAuth URL
        API-->>Client: 2. Return Google OAuth URL
        Client->>Google: 3. Redirect to Google login
        Google-->>Client: 4. Return authorization code
        Client->>API: 5. Send authorization code
        API->>Google: 6. Exchange code for tokens
        Google-->>API: 7. Return access & ID tokens
        
        API->>API: 8. Verify token & extract user info
        API->>DB: 9. Check if user exists
        DB-->>API: 10. User status
        
        alt New User
            API->>DB: 11a. Create new user
            API->>Email: 11b. Send welcome email
        else Existing User
            API->>DB: 11c. Update last login
        end
        
        API->>DB: 12. Create/Update Django session
        API->>DB: 13. Log authentication event
        API-->>Client: 14. Return JWT + user data
        
        alt Error Handling
            Google-->>Client: E1. OAuth cancelled
            Google-->>API: E2. Invalid code
            API-->>Client: E3. Account creation failed
        end
    end

    %% Traditional Login Flow
    alt Traditional Authentication
        Client->>API: 1. Send username/password
        API->>API: 2. Validate input format
        
        alt Valid Input
            API->>DB: 3. django.contrib.auth.authenticate
            DB-->>API: 4. User data
            
            alt Success
                API->>DB: 5a. Create Django session
                API->>DB: 5b. Update last login
                API-->>Client: 6. Return JWT + user data
            else Invalid Credentials
                API-->>Client: 7. Auth error (401)
            end
        else Invalid Input
            API-->>Client: 8. Validation error (400)
        end
    end

    %% Password Reset Flow
    alt Password Reset
        Client->>API: 1. Request password reset
        API->>DB: 2. Verify email exists
        API->>DB: 3. Generate reset token using Django's PasswordResetTokenGenerator
        API->>Email: 4. Send reset email
        Email-->>Client: 5. Reset link
        
        Client->>API: 6. Submit new password with token
        API->>DB: 7. Verify reset token
        API->>DB: 8. Update password
        API-->>Client: 9. Confirmation
    end

    %% JWT Refresh
    alt Token Refresh
        Client->>API: 1. Request token refresh
        API->>DB: 2. Validate refresh token
        alt Valid Token
            API->>DB: 3a. Generate new access token
            API-->>Client: 4a. New access token
        else Invalid Token
            API-->>Client: 3b. Invalid token error
        end
    end

    %% Logout Flow
    alt Logout
        Client->>API: 1. Logout request
        API->>DB: 2. Invalidate Django session
        API->>DB: 3. Log logout event
        API-->>Client: 4. Logout success
    end