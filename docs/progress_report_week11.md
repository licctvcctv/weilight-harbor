# Weilight Harbor — Progress Report (Week 11)

**Course:** COMP3030J Web Development, University College Dublin, 2025/2026
**Group:** 14
**Date:** Week 11
**Live deployment:** http://csi6220-2-vm3.ucd.ie
**Repository:** https://github.com/licctvcctv/weilight-harbor

---

## 1. Summary
Weilight Harbor is feature-complete for Week 11 submission. All five planned user-facing modules (Community, Crowdfunding, Life Journal, Respite Station, User Centre) plus the Admin moderation panel are deployed on the assigned UCD VM and reachable on the public URL above. Both Mandarin and English locales are supported end-to-end with 511 translated strings. Continuous deployment is wired up via GitHub Actions: a push to `main` triggers a workflow that hops through the UCD jump host (password + TOTP) into the VM, fast-forwards the working tree to the latest commit, runs `vm_update.sh`, and restarts Gunicorn.

This week we are submitting two PDF drafts (`14_system_draft.pdf`, `14_user_draft.pdf`) on Moodle and finalising peer-testing materials for Week 12.

## 2. Completed Since Week 10
- Bilingual admin panel (i18n on Layui pages).
- GitHub Actions deploy workflow with TOTP + jump-host expect script.
- Pagination fixes on the User Centre history page (`url_for(**{page_param: n})` instead of manual `&` concatenation).
- Sensitive-word severity tiers (warning vs crisis modal) hooked up across community and confessions.
- Seed data refresh: 8 users, 12 posts, 7 campaigns, 81 donations, 48 journal entries, 8 respite requests.
- Documentation: README expansion and Week 11 system / user draft documents.

## 3. Plan for Weeks 11 – 15
| Week | Focus | Deliverables |
|---|---|---|
| 11 | System & User document drafts | `14_system_draft.pdf`, `14_user_draft.pdf` on Moodle by Friday midnight |
| 12 | Peer testing | Run two test sessions; complete the two feedback forms (user + system) for the assigned groups; receive feedback from two groups |
| 13 | Final polish | Final system document (≤20 pages), final user document (≤10 pages); incorporate peer-testing feedback |
| 14 | Demo rehearsal | Internal dry-run; prepare slides; finalise per-member contribution table |
| 15 | Final demonstration and submission | Final demo, final code freeze, archive |

## 4. Outstanding Work
**Documentation**
- Replace placeholder names / percentages in the System Document Section 4 (Team Contribution).
- Insert real screenshots into the User Document.
- Add a 1-page generative-AI usage write-up to confirm wording with the team.

**Product polish**
- Finish forgot-password flow (UI exists; SMTP is not provisioned on the VM, decision: leave stubbed for the assignment scope).
- Tighten responsive breakpoints on the Respite map list panel.
- Seed at least one user with >10 entries in a year so the Annual Film button is visible to evaluators by default.

**Peer testing preparation (Week 12)**
- Prepare a one-page "test scenario" sheet with login credentials and 6 user journeys (register, post, donate, journal, respite request, admin review).
- Confirm the two feedback forms (user + system) are filled in for each of the two groups assigned to us.
- Reserve the test slot on the shared schedule.

## 5. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Jump host TOTP secret rotates before final submission | Low | High | Fall-back to manual `bash deploy.sh`; secret stored in GitHub Secrets and in the team password manager |
| VM disk fills due to uploads | Low | Medium | Static uploads bounded by extension allow-list; current usage is ≈40 % of 30 GB |
| SQLite write contention during demo | Low | Medium | Demo audience size is small; if needed switch to a single-worker Gunicorn for the demo |
| Late-binding peer-testing feedback | Medium | Low | Allocate Day 1 of Week 13 strictly to feedback ingestion |

## 6. Asks for the Tutor
1. Confirmation that the Week 11 cover sheet should follow the standard module template (no separate group cover required).
2. Confirmation that simulated donations are acceptable as "transaction" coverage in the System Document.
3. Indicative page weighting between Technical Implementation and AI Use sections in the rubric (we have budgeted 10–12 vs 1–2).

---
*Prepared by Group 14. The complete System and User drafts accompany this report under `docs/`.*
