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

   Update `liquibase/liquibase.properties` with your database URL/credentials,
   then from the `liquibase/` directory run:
   ```
   liquibase update
   ```

## Running the app

```
python -m src.main
```

The app will be available at [http://localhost:8000](http://localhost:8000).

## AI Disclosure

Artificial intelligence tools, including large language models (LLMs), were used in the development of this project to support clarifying technical concepts and generating code snippets. These tools served as an aid for idea refinement, debugging, and testing of the program. All AI-generated code was thoroughly reviewed, verified for correctness, and fully understood before being incorporated into this work. Responsibility for all final decisions, interpretations, and implementations remains solely with the contributors.