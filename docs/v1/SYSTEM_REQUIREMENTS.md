## Functional Requirements

### 1. Users

#### Types
    - Regular (Job Seeker)
    - Recruiter

#### Operations
    - Signup (email + password) with email verification token, then OAuth2 Bearer (JWT) for auth
    - Log in: Issue access and refresh tokens
    - Log out: Revoke the current refresh token; access tokens naturally expire
    - Refresh: Renew the access token and rotate the refresh token

#### Regular users can:
    - View own data
    - Search for jobs
        - By title
        - Filters: location, employment type, remote/hybrid, salary range, company, tags
    - Create applications
    - View own applications
    - Cancel own applications while status = 'submitted'
    - Update own applications while status = 'submitted' (fields: CV, cover letter)
    - Constraint: a candidate may submit at most one application per job

#### Recruiter users can:
    - Create jobs
    - View existing jobs associated with their company
    - Update active (active = not archived) jobs associated with their company
    - Archive jobs associated with their company
    - Delete jobs associated with their company
    - View applications associated with their company's jobs
    - Update application status for their company's jobs:
        - submitted → received
        - received → advanced | rejected

### 2. Jobs
    - Have a nonnegative number of vacancies

### 3. Applications
    - Have a status:
        - submitted
        - received
        - advanced
        - canceled
        - rejected

### 4. Companies
    - One recruiter user can belong to several companies

## Non-functional Requirements

1. Security: JWT auth, bcrypt password hashing, input validation
2. Rate Limiting: Through web server or managed solutions only
3. Infrastructure and Deployment: Docker, single VM