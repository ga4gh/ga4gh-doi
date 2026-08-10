# GA4GH DOI Service

The GA4GH DOI Service allows users to register GA4GH DOIs (standards, conference, articles, grants,
posted content, reports) and submit them to Crossref.

## Setup

1. **Create a virtual environment** (recommended)
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root. 

   ```
   # Database - either set DATABASE_URL, or the individual DB_* vars below
   DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/doi_db
   # DB_HOST=localhost
   # DB_PORT=5432
   # DB_NAME=doi_db
   # DB_USER=user
   # DB_PASSWORD=password

   # Crossref deposit credentials (used to submit approved batches)
   EMAIL=your-email@example.org
   PASSWORD=your-password

   # SMTP (used to send registration/approval notification emails)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

4. **Set up the database schema**

   Database changes are managed with [Liquibase](https://www.liquibase.com/).
   Update `liquibase/liquibase.properties` with your database URL/credentials,
   then from the `liquibase/` directory run:
   ```
   liquibase update
   ```

## Running the app

```
python -m src.main
```

Or, equivalently:
```
uvicorn src.main:app --reload
```

The app will be available at [http://localhost:8000](http://localhost:8000).
