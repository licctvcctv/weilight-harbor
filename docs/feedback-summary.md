# Weilight Harbor Feedback Summary

## ER Diagram

The formal black-and-white Chen-style ER diagrams are available at:

- `docs/rendered/weilight-harbor-er-imagegen-bw.png` - raster diagram generated with imagegen
- `docs/weilight-harbor-er-chen.svg` - editable SVG version with verified entity and relationship labels

```mermaid
erDiagram
    ADMIN_USER {
        int id PK
        string username
        string realname
        string email
        string phone
        string user_type
        boolean is_certified
        string locale
        datetime create_at
    }

    ADMIN_ROLE {
        int id PK
        string name
        string code
        int enable
    }

    ADMIN_POWER {
        int id PK
        string name
        string code
        string url
        int parent_id
        int enable
    }

    ADMIN_USER_ROLE {
        int id PK
        int user_id FK
        int role_id FK
    }

    ADMIN_ROLE_POWER {
        int id PK
        int role_id FK
        int power_id FK
    }

    WL_CERTIFICATION {
        int id PK
        int user_id FK
        int reviewer_id FK
        string cert_type
        string real_name
        string patient_name
        string patient_illness
        string hospital_name
        string status
        string reject_reason
        datetime reviewed_at
    }

    WL_CAMPAIGN {
        int id PK
        int user_id FK
        int reviewer_id FK
        string title
        text description
        string category
        decimal funding_goal
        decimal current_amount
        string qr_code_url
        string status
        boolean is_fully_funded
        datetime create_at
    }

    WL_DONATION {
        int id PK
        int campaign_id FK
        int user_id FK
        decimal amount
        string message
        boolean is_anonymous
        datetime create_at
    }

    WL_POST {
        int id PK
        int user_id FK
        string title
        text content
        string category
        text images
        int view_count
        int like_count
        int comment_count
        boolean is_anonymous
        int status
        datetime create_at
    }

    WL_COMMENT {
        int id PK
        int post_id FK
        int user_id FK
        int parent_id FK
        text content
        datetime create_at
    }

    WL_POST_LIKE {
        int id PK
        int post_id FK
        int user_id FK
        datetime create_at
    }

    WL_JOURNAL_ENTRY {
        int id PK
        int user_id FK
        string title
        text content
        text images
        string mood
        date entry_date
        datetime create_at
    }

    WL_RESPITE_REQUEST {
        int id PK
        int user_id FK
        int acceptor_id FK
        string request_type
        string title
        text description
        string category
        string address
        float latitude
        float longitude
        string status
        datetime accepted_at
        datetime completed_at
    }

    WL_CONFESSION {
        int id PK
        text content
        string nickname
        string session_id
        int hug_count
        datetime create_at
    }

    WL_SENSITIVE_WORD {
        int id PK
        string word
        int severity
        datetime create_at
    }

    ADMIN_USER ||--o{ ADMIN_USER_ROLE : has
    ADMIN_ROLE ||--o{ ADMIN_USER_ROLE : assigned_to
    ADMIN_ROLE ||--o{ ADMIN_ROLE_POWER : grants
    ADMIN_POWER ||--o{ ADMIN_ROLE_POWER : included_in

    ADMIN_USER ||--o{ WL_CERTIFICATION : submits
    ADMIN_USER ||--o{ WL_CERTIFICATION : reviews
    ADMIN_USER ||--o{ WL_CAMPAIGN : creates
    ADMIN_USER ||--o{ WL_CAMPAIGN : reviews
    WL_CAMPAIGN ||--o{ WL_DONATION : receives
    ADMIN_USER ||--o{ WL_DONATION : makes

    ADMIN_USER ||--o{ WL_POST : publishes
    WL_POST ||--o{ WL_COMMENT : has
    ADMIN_USER ||--o{ WL_COMMENT : writes
    WL_COMMENT ||--o{ WL_COMMENT : replies
    WL_POST ||--o{ WL_POST_LIKE : liked_by
    ADMIN_USER ||--o{ WL_POST_LIKE : gives

    ADMIN_USER ||--o{ WL_JOURNAL_ENTRY : records
    ADMIN_USER ||--o{ WL_RESPITE_REQUEST : requests
    ADMIN_USER ||--o{ WL_RESPITE_REQUEST : accepts
```

## Modification Summary

1. Respite Station map display issue

   The map page originally loaded with a world-level view, so local respite station markers were not visible unless the user manually zoomed far out or adjusted the map. The map initialization was adjusted so the view fits the station marker bounds by default, making nearby respite requests visible immediately after entering the page.

2. Annual Film record display issue

   The annual film page previously truncated journal text before rendering the slide, which caused records to appear incomplete. The backend now passes the full journal content to the film page, and the slide text area supports internal scrolling for longer entries, so complete records can be viewed without breaking the full-screen film layout.

3. Donation page refresh and scrolling issue

   After completing a donation, the page could remain in an old modal state, leaving the page unable to scroll when the user returned or re-entered the campaign page. The donation modal lifecycle was corrected to use a single Bootstrap-compatible open/close flow, clean up modal backdrop and scroll-lock styles, and refresh the campaign detail page after a successful donation so the updated amount and donor count are shown correctly.
