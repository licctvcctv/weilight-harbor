# Weilight Harbor — User Document (Draft)

**Course:** COMP3030J Web Development, University College Dublin, 2025/2026
**Group:** 14
**Live deployment:** http://csi6220-2-vm3.ucd.ie
**Document version:** Week 11 draft

> Target page budget (Overleaf, 11pt, 2.5cm margins, ≤10 pages):
> Introduction ≤1, Regular User 2–3, Certified User 2–3, Administrator 2–3, FAQ ≤1.

This document is written for the three end-user roles supported by Weilight Harbor. Screenshots will be inserted before final submission; for now each section names the page, the URL and the visible controls so the reader can follow along on the live site.

---

## 1. Getting Started  *(≤1 page)*

### 1.1 What is Weilight Harbor?
Weilight Harbor (微光港湾) is a charity and mutual-aid platform for the families and caregivers of seriously ill patients. It combines a moderated community, an anonymous after-dark confession space, a private journaling area, a verified crowdfunding module, and an interactive map for arranging temporary respite help.

### 1.2 Browser and Device Support
- Recommended desktop browsers: latest Chrome, Firefox, Safari, or Edge.
- Mobile: iOS Safari ≥16, Android Chrome ≥120.
- A network connection is required to reach the live VM.

### 1.3 Visiting the Site
Open http://csi6220-2-vm3.ucd.ie in a browser. The landing page introduces the platform; the navigation bar at the top lets you move between modules, switch language (中 / EN), and log in.

### 1.4 Test Accounts (assignment evaluation only)
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator |
| `limei` | `test123` | Certified Family |
| `zhangwei` | `test123` | Regular User |

A complete table is in Appendix A.

### 1.5 Switching Language
Use the **中 / EN** toggle on the left of the navigation bar. The choice is remembered for the rest of your session and across visits on the same browser.

---

## 2. Regular User  *(2–3 pages)*

A *regular user* is anyone who has registered without applying for caregiver certification. They can browse, donate, post in the community, comment, and use the night confession panel.

### 2.1 Registering and Logging In
1. Click **Join the Harbor** in the top right of any page → form at `/auth/register`.
2. Fill in username, email or phone, password (≥6 characters), and confirm password.
3. Submit. You will be redirected to the login page; sign in with your credentials.
4. Forgot your password? Click **Forgot password?** on the login page (UI only in the current build).

### 2.2 Browsing the Community  (`/community/`)
- The left 70 % of the page shows the post feed; the right 30 % is the **Night Confessions** panel.
- Filter posts by the category pills near the top (e.g. *Emotional Support*, *Daily Life*, *Medical Info*, *Good News*, *Resources*).
- Sort by **Latest**, **Most Empathised**, or **Hot** using the tab selector.
- Click a post card to open the full detail page.

### 2.3 Reacting and Commenting on a Post
- The empathy button (heart icon) is labelled "I feel the same" and toggles your reaction. Each user can react once per post.
- Comments appear chronologically; click **Reply** under a comment to thread.
- You can mark your comment **Anonymous** with the checkbox above the comment box.

### 2.4 Writing a Post (`/community/create`)
1. Click **New Post** in the community navigation.
2. Choose at least one category, optionally add a title (≤50 chars), write your content, attach up to 9 images.
3. Toggle **Post anonymously** if you prefer; your username and avatar will be hidden.
4. Click **Publish**. If your text contains words flagged as sensitive, you will be warned and may be redirected to a crisis hotline.

### 2.5 Night Confessions
- The panel is **active 21:00 – 06:00 server local time** (UTC on the VM).
- Outside that window the panel is dimmed with a countdown.
- During active hours you can write a confession (anonymous, capped length) or send a "hug" reaction to an existing one.
- If your text mentions self-harm or crisis keywords, a crisis hotline modal will appear before submission.

### 2.6 Viewing and Donating to a Crowdfunding Campaign
1. Open `/crowdfunding/`.
2. Filter or search for a campaign.
3. Click a campaign card to open the detail page.
4. The right-hand sticky panel shows progress and the **Donate** button. Choose a preset amount or enter a custom value.
5. Optionally write a public message and tick **Anonymous** to hide your name from the donor list.
6. Confirm. The progress bar animates and a thank-you toast appears. *(Donations are simulated for the assignment.)*

### 2.7 Personal Centre
- **Profile** (`/user/profile`) — overview of your activity.
- **Edit profile** (`/user/edit`) — name, phone, email, avatar, bio.
- **History** (`/user/history`) — paginated tabs for your Posts, Campaigns, Donations and Respite Requests.
- **Settings** (`/user/settings`) — change password.
- **Apply for certification** (`/user/certification`) — see Section 3.1.

### 2.8 Logging Out
Click your avatar in the top right → **Logout**. Logout is sent as a POST so it cannot be triggered from a malicious link.

---

## 3. Certified Family / Volunteer  *(2–3 pages)*

A certified user is a regular user whose caregiver/volunteer status has been approved by an administrator. Certified users keep all the regular-user capabilities and additionally gain access to crowdfunding creation, the journal, and the respite map's create/accept actions.

### 3.1 Applying for Certification
1. Open the avatar menu → **Apply Certification** (or `/user/certification`).
2. Choose **Family** or **Volunteer**.
3. Fill in your real name, ID number, relationship to the patient, and patient details (name, illness, hospital, diagnosis date).
4. Upload a primary proof document (PDF / JPG / PNG). Optionally upload up to three additional supporting documents.
5. Submit. Your application enters a queue with status **Pending**; an admin will approve or reject within 24–48 hours.
6. Track status at `/user/certification/status`. If rejected, the rejection reason is shown and you can re-apply.

### 3.2 Starting a Crowdfunding Campaign  (`/crowdfunding/create`)
1. From the crowdfunding page, click **Start a Campaign**.
2. If you are not yet certified, the page redirects to the certification application.
3. Provide title, story, target amount, deadline, category, cover image, patient photo and a payment QR placeholder.
4. Click **Submit for Review**. Status becomes **Pending**; once approved by an admin, your campaign appears in the public listing.

### 3.3 Receiving Donations
- The campaign detail page shows real-time progress, donor count and a donor list (with anonymous donations rendered as "Anonymous Caregiver").
- When `current_amount ≥ funding_goal` a **Fully Funded** badge is shown and the donate button is greyed out.

### 3.4 Life Journal
- Open `/journal/` for your private timeline. Only you can see your entries.
- **New entry** — pick a date, a mood emoji, write your text, attach up to 9 photos.
- **Edit / Delete** — available from any entry detail page (soft delete preserves the row).
- **Filters** — choose a year and month to focus the timeline.
- **Annual Film** — once you have at least 10 entries in a year, an *Annual Film* button unlocks; it plays a full-screen Ken-Burns slideshow of up to 12 highlights.

### 3.5 Respite Station — Posting and Accepting
1. Open `/respite/`. The map centres on Dublin by default; allow location access for a closer view.
2. Click **I need a break** to post a service request, or **I can lend equipment** to post an equipment offer.
3. Fill the form: title, time window, address (auto-filled if location is allowed), special notes, contact preference.
4. Your pin appears on the map (orange = service, green = equipment) with a pulsing animation while pending.
5. Other certified users can click your pin and **Accept**. You cannot accept your own request.
6. After the activity is over, the original requester clicks **Confirm Completed** to close the request.

### 3.6 Profile Visibility
Certified users display a verification badge next to their name across the platform. This is shown in posts, comments, donations, and respite pins.

---

## 4. Administrator  *(2–3 pages)*

Administrators see an additional **Admin** entry in the user-menu dropdown that links to `/admin/`. The admin panel is a Layui-based interface inherited from Pear-Admin-Flask, extended with three custom review pages.

### 4.1 Logging In as an Administrator
Use the seeded `admin` / `admin123` account on the standard `/auth/login` page. After signing in, your avatar dropdown shows **Admin Panel**, opening `/admin/` in a new tab.

### 4.2 Dashboard
The admin dashboard shows summary cards (pending counts) and a left-hand sidebar with sections:
- **Certification Reviews** — `/admin/certification/`
- **Campaign Reviews** — `/admin/campaign-review/`
- **Community Moderation** — `/admin/community/`
- **User Management** — inherited from the base panel
- **Roles & Powers** — inherited from the base panel
- **Operation Log** — inherited audit log

### 4.3 Reviewing Certification Applications
1. Open **Certification Reviews**.
2. The table lists applicants oldest first; filter by status if needed.
3. Click **Review** on a row to see all uploaded documents (clickable to enlarge), the applicant profile, and a history of any prior applications.
4. Pick one of:
   - **Approve** — confirms the certification; the applicant is granted certified status immediately.
   - **Reject** — requires a reason; shown to the applicant on their status page.
   - **Request More Info** — sends a note back to the applicant; status remains Pending.
5. Every action is logged to the operation log table.

### 4.4 Reviewing Crowdfunding Campaigns
1. Open **Campaign Reviews**.
2. Click a campaign to open the review pane: cover image, story, payment QR, target amount and any patient documents.
3. **Approve** to publish the campaign; **Reject** with a reason. The campaign creator sees the decision on their personal centre.

### 4.5 Moderating Community Posts
1. Open **Community Moderation**.
2. Filter by status (auto, hidden, pending) or search by author / keyword.
3. For each post you can:
   - **Approve** — leave it visible.
   - **Hide** — keep the data but remove it from the public feed; the author sees a "hidden by moderator" notice.
   - **Delete** — soft-delete (sets `delete_at`); reversible by direct database operation only.

### 4.6 User and Role Management
The base Pear-Admin-Flask **User Management** and **Role / Power** pages remain available for managing accounts, freezing users, or editing the RBAC matrix. New roles or permissions should follow the existing dictionary structure.

### 4.7 Audit Log
Every action wrapped in the `@authorize("…", log=True)` decorator writes a row to the operation log, including the operator, the resource code, and a timestamp. Use it to review who approved or rejected what.

---

## 5. Frequently Asked Questions  *(≤1 page)*

**Q1. The Night Confessions panel is dimmed — is the feature broken?**
No. It is intentionally only active between 21:00 and 06:00 (VM local time, UTC).

**Q2. Why does the **Donate** button do nothing for my campaign?**
The campaign is probably already fully funded, or your account is not signed in. The button is greyed out in both cases.

**Q3. I uploaded a document but the page says "valid proof document required".**
The file may exceed the size limit, or have a non-permitted extension. Allowed types are PDF, JPG, JPEG, PNG (and the equivalents declared in `ALLOWED_DOC_EXTS`).

**Q4. Why can my friend not see my journal entries?**
The journal is private by design. All journal queries filter by `user_id == current_user.id`; no one but you, including administrators, can read your entries through the public site.

**Q5. I cannot start a campaign — the page tells me to "apply for certification".**
Crowdfunding requires verified caregiver/volunteer status. Submit a certification application (Section 3.1) and wait for admin approval (24–48 hours).

**Q6. The map does not centre on my location.**
The browser blocked the location prompt or no permission was granted. The map falls back to Dublin city centre. You can pan/zoom manually.

**Q7. Where do I report a bug?**
For the assignment evaluation, please email the group contact listed on the cover of the system document, or open an issue at https://github.com/licctvcctv/weilight-harbor/issues.

---

## Appendix A — Test Accounts (full list)

| Username | Password | Role | Notes |
|---|---|---|---|
| `admin` | `admin123` | Administrator | Full admin access |
| `limei` | `test123` | Certified Family | ALS caregiver, has campaigns |
| `zhangwei` | `test123` | Regular User | Donor profile, tech background |
| `wangfang` | `test123` | Certified Volunteer | Retired nurse |
| `chenyun` | `test123` | Certified Family | Alzheimer's caregiver |
| `liuyang` | `test123` | Regular User | Has a pending certification |
| `sunli` | `test123` | Certified Family | Pediatric cancer caregiver |
| `zhaojing` | `test123` | Certified Volunteer | Social worker |

## Appendix B — Glossary
- **Certified user** — a regular user whose caregiver or volunteer status has been approved by an administrator.
- **Empathy reaction** — the like equivalent on this platform, labelled "I feel the same" (我也是).
- **Night Confessions** — the time-gated, anonymous after-dark panel.
- **Annual Film** — a full-screen slideshow synthesised from a user's journal entries.
- **Respite** — a temporary break from caregiving responsibilities.
