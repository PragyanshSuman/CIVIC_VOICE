# Database Schema

## Entity Relationship Diagram

```
┌─────────────────────┐
│       Users         │
├─────────────────────┤
│ id (UUID) PK        │
│ email (unique)      │
│ hashed_password     │
│ full_name           │
│ role (enum)         │
│ is_active           │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
┌──────▼──────────────┐
│     Problems        │
├─────────────────────┤
│ id (UUID) PK        │
│ title               │
│ description         │
│ category            │
│ status (enum)       │
│ latitude            │
│ longitude           │
│ address             │
│ image_url           │
│ user_id FK          │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
┌──────▼──────────────┐
│     Solutions       │
├─────────────────────┤
│ id (UUID) PK        │
│ title               │
│ description         │
│ problem_id FK       │
│ author_id FK        │
│ ai_score_feasibility│
│ ai_score_impact     │
│ ai_score_cost       │
│ overall_score       │
│ upvotes_count       │
│ downvotes_count     │
│ created_at          │
│ updated_at          │
└──────┬──────────────┘
       │
       │ 1:N
       │
┌──────▼──────────────┐
│       Votes         │
├─────────────────────┤
│ id (UUID) PK        │
│ user_id FK          │
│ solution_id FK      │
│ vote_type (enum)    │
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│     Comments        │
├─────────────────────┤
│ id (UUID) PK        │
│ content             │
│ user_id FK          │
│ problem_id FK       │
│ solution_id FK      │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│   Notifications     │
├─────────────────────┤
│ id (UUID) PK        │
│ user_id FK          │
│ title               │
│ message             │
│ is_read             │
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│ Government Response │
├─────────────────────┤
│ id (UUID) PK        │
│ problem_id FK       │
│ official_id FK      │
│ response_text       │
│ action_plan         │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Table Descriptions

### Users
Stores all platform users including citizens, government officials, and administrators.

**Indexes:**
- `email` (unique)
- `role`

**Enums:**
- `role`: citizen, government, admin

### Problems
Civic issues reported by citizens with geolocation data.

**Indexes:**
- `user_id`
- `category`
- `status`
- `latitude, longitude` (spatial index)

**Enums:**
- `status`: open, under_review, solved, rejected

### Solutions
Proposed solutions to problems with AI-generated scores.

**Indexes:**
- `problem_id`
- `author_id`
- `overall_score` (descending)

### Votes
User votes on solutions (upvote/downvote).

**Indexes:**
- `user_id, solution_id` (composite unique)

**Enums:**
- `vote_type`: upvote, downvote

### Comments
User comments on problems or solutions.

**Indexes:**
- `problem_id`
- `solution_id`
- `user_id`

### Notifications
User notifications for various events.

**Indexes:**
- `user_id, is_read`

### Government Response
Official responses from government authorities.

**Indexes:**
- `problem_id`
- `official_id`

## Relationships

- User → Problems (1:N)
- User → Solutions (1:N)
- User → Votes (1:N)
- User → Comments (1:N)
- Problem → Solutions (1:N)
- Problem → Comments (1:N)
- Solution → Votes (1:N)
- Solution → Comments (1:N)

## Migration Strategy

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Performance Considerations

1. **Indexing**: All foreign keys and frequently queried columns are indexed
2. **UUID Primary Keys**: Better for distributed systems
3. **Timestamps**: Automatic tracking with `created_at` and `updated_at`
4. **Soft Deletes**: Consider adding `deleted_at` for soft delete pattern
5. **Partitioning**: Consider table partitioning for large datasets (future)

## Data Integrity

- Foreign key constraints ensure referential integrity
- NOT NULL constraints on critical fields
- Unique constraints on email and composite keys
- Check constraints on enums
- Cascade deletes configured appropriately
