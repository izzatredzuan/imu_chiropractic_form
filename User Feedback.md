# Chiro Assessment System – Meeting Minutes & Change Requests

**Requested by:** Chow Kit Yee, Nashereena Kaur Dhillon

---

# Pending

- _No pending issue._

---

## Priority

- _No pending priority issue._

#### Enhancement Suggestions

- Allow forms to be saved as drafts before completion.
  - Drafts **must not** be eligible for sign-off until all required sections are completed.
- Archive logs by day.
- Consider adding AI-generated assessment summaries when exporting to PDF.

#### Bugs

- _No pending bugs._

---

## Questions for the Chiro Team

- _No pending questions._

---

# Completed

## Major

### 06 March 2026

- Split the original **Section 1** into two sections and merge the original **Sections 2 & 3** into one. ✅
- Add a **PDPA Consent** section to Section 1. ✅
- Add three new fields to Section 2:
  - Red Flags ✅
  - Yellow Flags ✅
  - Contraindications ✅
- Simplify the discharge process:
  - Only require **Discharge Reason** and **Remarks**. ✅
  - Only **Clinicians** and **Admins** can discharge patients. ✅
- Treatment Log now displays a list of completed S.O.A.P records and allows users to open each record. ✅
- S.O.A.P records require sign-off, and multiple S.O.A.P records can be created for a single assessment. ✅
- Add **Patient Re-Evaluation Form** and **Patient Complaint Form**, supporting multiple records per assessment. ✅

### 09 April 2026

#### S.O.A.P

- Next Appointment and Modalities are no longer mandatory. ✅
- Add a delete function for modalities if the S.O.A.P has not been signed off. ✅

#### Section 3

- Add a drawing area for **Range of Motion (RoM)** with text separated into three fields. ✅

#### Anatomy Marking

- S.O.A.P markers support notes. ✅
- Assessment Section 1 markers do not require notes. ✅

#### General

- Added remaining required fields after receiving specifications from the Chiro team. ✅
- Fixed UI issues for the **Undo** and **Clear** buttons in Section 1 signature. ✅

---

### 28 April 2026

- Add file upload support in **Treatment Plan**. ✅

#### Priority

- Add **Cohort** field for Student user creation. ✅

---

### 21 May 2026

#### Notes Page

- Add **Convert to PDF** functionality. ✅
- The S.O.A.P Notes page should include the description of each anatomy marker in the generated PDF. ✅

#### Section 1

- Add the new Consent section. ✅
- Update Phase 1 completion logic:
  - **Special Direction** is no longer mandatory. ✅
- Remove the anatomy marker instruction:
  - _"Left-click a marker to add/edit a note. Right-click to delete."_ ✅

#### Section 4

- Add **Intervention Approved** field. ✅

#### S.O.A.P

- Fixed assessment ID not being passed during creation. ✅

#### Notes

- Fixed anatomy marker details not displaying when clicking/holding a marker. ✅

#### Discharge

- Added sign-off section. ✅

---

### 28 May 2026

- Fixed `{% if assessment and request.user.profile.role in "clinician admin" %}` logic. ✅
- Updated outdated constants. ✅

---

### 12 June 2026

#### Assessment

- Fixed Section 4 becoming locked again after Section 3 sign-off. ✅

#### Section 1

- Updated the Consent section:
  - Added four consent checkboxes.
  - Added consent explanation.
  - Added initial consent section.
- Added **Patient Relationship** and **Interpreter** fields.
- Added name fields for **PDPA Consent** and **Patient Consent**. ✅

#### Section 3

- Added confirmation messages for **Save** and **Sign Off**. ✅

#### Treatment Plan

- Made Phases 1–3 optional instead of mandatory. ✅

#### General

- Changed all occurrences of **Orthopedic** to **Orthopaedic**. ✅

---

### 19 June 2026

#### New Consent Section

_(Located after Section 4 and before Treatment Plan)_

- Removed the PDPA Consent section from the application. ✅
- Moved all remaining consent sections to the new Consent page. ✅
- Updated Witness Relationship to refer to the attending staff instead of the patient. ✅

#### Consent & Submission Confirmation

- Updated the first name in:

  > "I, **\_\_**"

  to display the **Patient Consent Name** instead of the Witness Name. ✅

- Added an encrypted **IC** field to the Assessment model and displayed it in the consent confirmation. ✅

#### General

- Fixed the login page logo. ✅

---

### 24 June 2026

#### Consent

- Repurposed **Witness Relationship** into **Patient Consent Relationship**. ✅
- Added **Patient Consent IC** field. ✅

---

### 26 June 2026

- Changed **Section 4 Diagnosis** to support multiple dated comments (similar to Remarks). ✅
- Automated emails now include the application URL. ✅

---

### 29 June 2026

#### User Management

- Sync Employee/Student user profiles (Create/Update) from the IMU API. ✅
- Added Change Password page and functionality. ✅
- Added Forgot Password page and functionality. ✅

#### Enhancements

- Redirect users who are already logged in. ✅
- Prevent login for locked accounts. ✅
- Add Assessment filtering by year. ✅
- Add an edit function for **Section 4 – Diagnosis & Treatment Plan Remarks** in the future. ✅
- Create backup DB cron function that runs every week ✅

---

### Minor Improvements

- Clinicians can view all assessments. ✅
- Clinicians can assign any clinician. ✅
- Add a confirmation dialog before saving assessments. ✅
- Display **Last Updated By**. ✅
- Display **Last Updated Time**. ✅
- Add **Differential Diagnosis** and **Working Diagnosis** fields. ✅
- Make assessments read-only when viewed by clinicians who are not assigned to them. ✅
- Display patient details (Name & File Number) in every section. ✅
- Fixed login redirect issue. ✅
- Fixed clinicians and students being unable to save assessments. ✅
- Change button colours after student edits so clinicians know which sections require sign-off. ✅
- Add clinician filter for assigned assessments. ✅
- Add `file_number` field. ✅
- Update legend sequence. ✅
- Merge Date, Time and Updated By into a single column. ✅
- Move Section 5 to Part 2. ✅
- Restrict access until Section 4 is completed. ✅
- Simplify the workflow so clinicians only sign off sections edited by students. ✅
- Disable S.O.A.P creation if the assessment is not assigned to the current user. ✅
- Finalised Consent section layout and requirements. ✅
- Finalised Section 3 physical sign-off placement. ✅

#### Bugs

- Datatable sorting is incorrect. ✅

---

# Cancelled

## Bugs

- S.O.A.P could not be unsigned after clicking **Update S.O.A.P**. _(Resolved before cancellation.)_

## Cancelled Requests

- Require patient consent signature before assessment creation and again during the final assessment phase. ❌
- Allow multiple Evaluators to be selected. ❌
