# Whyvo Backend Clean

Clean FastAPI backend for Whyvo core product domains only.

## Included domains
- auth
- users
- profile
- contacts
- chats/messages
- updates/posts/comments/likes
- device tokens

## Excluded on purpose
- calls
- Agora
- payments
- marketplace
- farm/agri/livestock
- debug/test donor runtime

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## API prefix
- `/api/v1`

## Health
- `GET /`
