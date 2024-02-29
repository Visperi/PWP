# Meetings notes

## Meeting 1.
* **DATE:** 31.1.2024
* **ASSISTANTS:** Mika Oja

### Minutes
- Concept diagram goes too deep into the technical implementation and practicalities.
- Motivation and concepts not clear enough 

### Action points
- Concept diagram needs to be reworked to better represent the relations between the concepts. 
- Better specify the concepts and motivations of the project.




## Meeting 2.
* **DATE:** 14.2.2024
* **ASSISTANTS:** Mika Oja

### Minutes
- Database files are not needed in the repository. Lovelace and wiki requirements are not perfectly in sync, and 
Lovelace criteria should be followed
- Timestamps in databases could use DateTime type instead of raw epoch integers, as they have native support between 
Python and sqlite databases, and can be easier to handle
- Cascade behavior in databases may not work as expected, because foreign key behavior is not defined in models 
`Match` and `Player`. Without having bidirectional foreign key definition between `MatchPlayerRelation` and models 
cascade may work in raw SQLite commands but not in Flask-SQLAlchemy.

### Action points
- Remove database files from the repository (Done)
- Change timestamp type in `Match` model to DateTime type (Done)
- Define foreign key behavior also in `Match` and `Player` models to correct cascade behavior




## Meeting 3.
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Meeting 4.
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Midterm meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




## Final meeting
* **DATE:**
* **ASSISTANTS:**

### Minutes
*Summary of what was discussed during the meeting*

### Action points
*List here the actions points discussed with assistants*




