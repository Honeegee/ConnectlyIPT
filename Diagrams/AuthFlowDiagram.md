# Authentication and Authorization Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant API as API Layer
    participant TS as TokenService
    participant P as Permissions
    participant DB as Database

    %% Login Flow
    C->>API: Submit Login Credentials
    API->>TS: Validate Credentials
    alt Valid Credentials
        TS-->>API: Credentials Valid
        API->>TS: Generate Token
        TS-->>API: Return Token
        API-->>C: Token Returned (Authorization Successful)
    else Invalid Credentials
        TS-->>API: Credentials Invalid
        API-->>C: 401 Unauthorized
    end

    %% API Request Flow
    C->>API: Send API Request with Token
    API->>TS: Validate Token (via Middleware)
    
    alt Valid Token
        TS-->>API: Token Valid
        API->>P: Check User Role/Access
        
        alt Access Granted
            P-->>API: Access Granted
            API->>DB: Execute Request
            DB-->>API: Return Data
            API-->>C: Authorized Response (200 OK)
        else Access Denied
            P-->>API: Access Denied
            API-->>C: 403 Forbidden
        end
        
    else Invalid Token
        TS-->>API: Token Invalid
        API-->>C: 401 Unauthorized
    end

    %% Google OAuth Flow
    Note over C,API: Google OAuth Flow
    C->>API: Google Sign In Request
    API->>TS: Validate Google Token
    
    alt Valid Google Email (@mmdc.mcl.edu.ph)
        TS-->>API: Email Domain Valid
        API->>DB: Get/Create User
        DB-->>API: User Data
        API->>TS: Generate Token
        TS-->>API: Return Token
        API-->>C: Token + User Data
    else Invalid Email Domain
        TS-->>API: Invalid Domain
        API-->>C: 401 Unauthorized
    end
```

## Authentication Flows

### Regular Authentication
1. User can authenticate through:
   - Login form (username/password)
   - Signup form (create new account)
2. After successful authentication:
   - Generate authentication token
   - Create user session
   - Return token and user data

### Google OAuth2 Authentication
1. User clicks Google Sign In button
2. Redirected to Google login page
3. After Google authentication:
   - Get Google OAuth2 token
   - Verify token on server
   - Check email domain (@mmdc.mcl.edu.ph only)
   - Get existing user or create new one
   - Generate authentication token
   - Create user session
   - Return token and user data

### Token Authentication (API)
1. Client includes token in Authorization header
2. Server verifies token for each API request
3. Grant or deny access based on token validity

### Session Authentication (Web)
1. Server creates session after authentication
2. Client receives session cookie
3. Client includes cookie in subsequent requests
4. Server verifies session for each web request
5. Grant or deny access based on session validity

## Security Measures

1. Password Requirements:
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character

2. Email Restrictions:
   - Google OAuth limited to @mmdc.mcl.edu.ph domain
   - Email verification required

3. Token Security:
   - Unique per user
   - Included in Authorization header
   - Required for all API endpoints (except login/signup)

4. Session Security:
   - Secure cookie flags
   - HTTPS only
   - Session timeout
