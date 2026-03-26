# Directive: Client Onboarding

## Goal
Initialize a new AI Audit engagement by creating a standardized directory structure and template files. This ensures consistency across all client projects.

## Desired Structure
The following structure must be created for every new client:

```
📁 [Client Name] - AI Audit
  ├── 📁 .tmp (intermediate data files)
  ├── 📁 Meeting Transcripts
  │     ├── 📁 Sales Calls
  │     ├── 📁 Discovery Calls
  │     └── 📁 Process Mapping Calls
  ├── 📁 Client Context
  │     └── 📄 Client_Profile.md
  ├── 📁 Process Documentation
  │     └── 📁 Onboarding Responses
  │           └── 📄 Pre-Discovery Questionnaire.md
  └── 📁 AI Audit (outputs)
        ├── 📄 Final Audit Report.md (Placeholder)
        └── 📄 VALUE Scoring Matrix.csv
```

**Notes on folder usage:**
- `Meeting Transcripts/` stores raw call transcripts, separated by call type.
- `Process Documentation/` stores documents, notes, and filled forms. Role-specific subfolders (e.g., `Process Notes (SDRs)/`) should be created as needed during the audit.
- `AI Audit/` centralizes all audit outputs (report, presentation, scoring matrix).
- When a call produces both a transcript and a document (e.g., process mapping), store the transcript in `Meeting Transcripts/` and the document in `Process Documentation/`. Analysis is most valuable when matching transcript + document.

## Tools to Use
- `execution/create_client_structure.py`

## Instructions
1. Get the `Client Name` from the user.
2. Run the structure generation script.
3. Confirm to the user that the environment is ready for data entry.
4. Guide the user on where to place each type of file (transcripts vs. documents).

## Edge Cases
- **Directory Exists**: If the folder already exists, the script should warn the user and NOT overwrite existing files unless explicitly forced.
- **Role-specific folders**: Create `Process Documentation/Process Notes ([Role])/` subfolders as roles are identified during the audit process.
