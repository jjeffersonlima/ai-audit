# Directive: Data Collection

## Goal
Gather comprehensive documentation and technical details about the AI system being audited.

## Inputs Requested from User
- **Client Profile**: Basic info (Name, Site, Description) stored in `Client Context/Client_Profile.md`.
- **Sales Call Transcripts**: Stored in `Meeting Transcripts/Sales Calls/`.
- **Discovery Call Transcripts**: Stored in `Meeting Transcripts/Discovery Calls/`.
- **Process Mapping Call Transcripts**: Stored in `Meeting Transcripts/Process Mapping Calls/`.
- **Kickoff Form Responses**: Structured data from the initial questionnaire (CSV/JSON). Stored in `Process Documentation/Onboarding Responses/`. See `directives/onboarding_data_legend.md` for schema.
- **Process Notes & Documents**: Stored in `Process Documentation/`. Create role-specific subfolders as needed (e.g., `Process Notes (SDRs)/`).
- Existing documentation (technical specs, privacy policies).

**Important:** When a call produces both a transcript and a document (e.g., process mapping sessions), store the transcript in `Meeting Transcripts/` and the resulting document in `Process Documentation/`. Analysis is most valuable when you can match the transcript with its corresponding document.

## Tools to Use
- `execution/data_collector.py` (when implemented) to fetch external data or process uploaded files.
- **Prompts**:
    - `prompts/discovery_context.md`: Use to structure the initial conversation and gather context.
    - `prompts/discovery_interview_questions.md`: Use to generate guided questions for specific roles.

## Output
- A structured `.tmp/data_package.json` containing:
    - `system_overview`: General description.
    - `technical_stack`: Models, frameworks, infrastructure.
    - `data_integrity`: Source and quality analysis.
    - `compliance_context`: Relevant regulations (e.g., GDPR, EU AI Act).

## Edge Cases
- **Missing Data**: If critical info is missing, the orchestrator must flag it and ask the user.
- **Unstructured Files**: Use LLM to parse and extract key info into the JSON structure.
