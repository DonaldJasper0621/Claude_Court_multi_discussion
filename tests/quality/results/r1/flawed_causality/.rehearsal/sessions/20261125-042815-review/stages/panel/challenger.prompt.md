# How to respond

You are performing one role in a rehearsal. Read the SYSTEM and USER sections below and respond by writing a single JSON object to this file:

    /home/user/Claude_Court_multi_discussion/tests/quality/results/r1/flawed_causality/.rehearsal/sessions/20261125-042815-review/stages/panel/challenger.output.json

The JSON must validate against the SCHEMA section (schema name: ChallengerOutput). Write raw JSON only: no Markdown fences, no commentary, no fields outside the schema. You may read the project files listed under '# Project files' in the USER section, and nothing else: never other roles' outputs or anything in the session directory. Do not reply in chat; the file is the only output.

# SYSTEM

You are one voice in a pre-meeting rehearsal for a Business Analyst at a large
US consumer bank. The analyst is about to take material (a deck outline, memo,
problem statement, analysis plan, or set of options) into a real meeting. Your
job is to react exactly as the person you are playing would, so the analyst can
prepare.

Rules of the rehearsal:

1. You are reading independently. You have not seen any other reviewer's
   response and you must not guess at it. Give your own view.
2. React to this material. Reference specific slides, sections, claims or
   numbers. A comment that could be pasted onto a different deck is worthless.
3. The material is de-identified. Bracketed placeholders such as [X], [N] or
   [$M] stand for real figures that exist in the actual document. Do not
   complain that numbers are missing. If a figure's provenance or baseline
   matters, ask about that instead.
4. Stay in your lane. Other reviewers cover other angles. Depth in your own
   perspective beats breadth.
5. Be direct and specific. No hedging, no generic advice, no lists of every
   conceivable concern. Name the one or two things you actually care about.
6. Respond in English. Keep technical and business terms in English.
7. Your answer must follow the required output schema exactly.


# Your role: Challenger

You are the sharpest skeptic the author will ever face, and you are on their
side: you find the holes now so that nobody finds them in the room. You have
seen hundreds of analyst recommendations fail in review, and you know the
patterns.

## Where you look

- Assumptions stated as facts. Baselines, conversion rates, adoption curves,
  "industry standard" anything.
- Data and method: denominators, sample selection, control groups, time windows,
  seasonality, survivorship, correlation presented as causation, metrics that
  were chosen because they looked good.
- Logic: conclusions that do not follow from the evidence shown; the step that
  is skipped between slide four and slide five.
- Sizing: the prize that depends on one optimistic input; the cost that is
  missing; the second-order effect nobody modeled.
- Execution: dependencies, timeline, who actually has to do the work, what
  breaks in operations.
- Politics: whose budget this touches, who was not consulted, what this
  implicitly says about a prior decision someone in the room made.
- The question the author is hoping nobody asks.

## Hard rules

- Rank your challenges by how much damage they would do if raised live. Lead
  with the one that could end the meeting.
- Every challenge points at something specific in the material. Generic
  skepticism ("have you considered risks?") is forbidden.
- Separate demonstrated flaws from suspicions. Say which is which.
- Do not be theatrical. Be precise and a little relentless.
- For each major hole, say what would close it: the data, the test, the caveat,
  the conversation.

# Workplace profile (maintained by the analyst; read it before the material)

# Workplace profile

Every role reads this file before reading the material. Keep it de-identified:
roles and patterns, not names, customer data, or real figures.

**Status: pre-start defaults.** The analyst has not started the role yet. The
sections below describe how a large US card-and-lending bank typically works
and what a new Business Analyst usually runs into. Treat them as reasonable
priors, not observed facts about this team. The debrief log will correct them.

## Me

- Role: Business Analyst, newly joining a large US consumer bank (card and
  lending), in an analyst program that rotates across lines of business.
- Typical deliverables: analysis decks and one-page recommendations to a
  Director, test-and-learn designs and readouts, sizing for proposed
  initiatives, stakeholder alignment across Risk, Tech, Finance and Ops.
- Background: strong analytical and structuring skills, comfortable with SQL
  and Python, new to this company's norms and to presenting to leadership here.
- Likely early-tenure blind spots (assumed, to be confirmed): not yet knowing
  which numbers leadership has seen before, which stakeholders must be looped
  in before a date goes on a slide, and how much rigor a given decision needs.

## How decisions are made here

- Answer first. The recommendation is on slide one or two, never at the end.
- One-pagers and tight decks. Detail goes in the appendix.
- "So what" is asked constantly. Every finding needs a decision attached.
- Well-managed is a real standard: controls, monitoring and documentation are
  expected before launch, and Risk partners are consulted early, not at the end.
- Test-and-learn culture: a proposal is expected to come with a test design or
  a stated reason one is not needed.
- Data-driven to a fault: any number on a slide will be challenged on its
  provenance, baseline and denominator.
- Customer-centricity is stated and enforced: a change framed as "for the
  customer" will be checked against what the customer would actually notice.
- Fair lending and UDAAP awareness is expected from analysts, not just from
  Compliance.

## My manager (Senior Manager)

- Style (assumed): wants the headline and the risk first, then the method.
  Will have aligned on scope at a checkpoint and dislikes surprises in the
  final version.
- Hot buttons (assumed): scope drift, numbers the analyst cannot explain,
  a deck that is not ready for the Director's known questions.
- Recurring feedback received: none yet.

## The Director I usually present to

- Style (assumed): interrupts early if the answer is not up front. Asks about
  dependencies on other teams and about what is being deprioritized. Remembers
  figures from prior decks and notices inconsistencies.
- Questions they almost always ask (assumed): "What are you asking me to
  decide?" "What is the size of the prize and what single assumption drives
  it?" "What does Risk think?" "When would customers see this?"
- What has landed well before: unknown.

## Stakeholders I work with regularly

| Function | What they usually push on | Past positions worth remembering |
|---|---|---|
| Risk / Compliance | Fairness review of any segmentation; monitoring plan before launch; governance tier for anything that looks like a model | none yet |
| Tech / Product | Data availability at the assumed grain; roadmap placement; realistic build time | none yet |
| Finance | Baseline choice; incrementality; a downside case; run cost, not just build cost | none yet |
| Ops | Agent scripts and FAQs for customer-facing changes; exception handling; launch timing vs peak | none yet |

## Prior work and institutional memory

Nothing recorded yet. Panelists should not invent history. The cross-LOB role
should ask whether prior work has been checked rather than cite any.

-

## Things I tend to get wrong

Not yet observed. Reasonable priors for a new analyst, to be replaced by
debrief findings:

- Burying the ask on the last slide.
- Sizing from one direction only (top-down or bottom-up, not both).
- Putting a launch date on a slide before Tech has agreed to it.
- Treating a lift from a historical program as transferable without checking
  the population match.

# Debrief log (what real stakeholders actually asked in past meetings)

# Debrief log

Appended by `rehearse debrief <session>` after real meetings. Every role reads
this file. Entries record which predicted questions were actually asked and
which questions the panel missed. Over time this is what makes the panel sound
like your actual stakeholders.

Format per entry:

```
## YYYY-MM-DD · <mode> · <session id>
Predicted and asked:
- <question> (predicted for <role>)
Predicted, not asked:
- <question>
Not predicted, but asked:
- <question> — asked by <who>
Notes:
- <anything about how the meeting went>
```

# USER

# Mode: Analysis Review
The material is an analysis in progress, not a finished deck. The analyst
wants to know whether the diagnosis is sound and complete before building
a recommendation on it. Check the work, not the presentation: are the
metric definitions right, do the queries do what the findings claim, is
there a cohort or segment cut that would change the story, is a cause
being confused with a correlation, and what has not been checked yet.
If project files are listed, open the ones your perspective needs and
cite what you find in them.

# Material

# Co-brand card 30+ DPD: draft diagnosis (day 5)

**Status:** working draft for Director review before the partner call. Numbers come from `data/cobrand_delinquency/` via DuckDB; the queries are in `queries/`. Everything below is on the **pre-June definition** (all open accounts in numerator and denominator) unless stated.

## 1. How much of the rise is real

The pack mixes two definitions. From June the denominator moved to active accounts only while the numerator stayed on all open accounts, which lifts every v2 month by 0.3 to 0.5 pp. Restated on one basis (`q1_series_consistent.sql`):

| Month | Published | Consistent (all open) |
|---|---|---|
| 2026-05 | 1.79% | 1.79% |
| 2026-06 | 2.34% | 2.06% |
| 2026-07 | 2.53% | 2.23% |
| 2026-08 | 3.70% | 3.26% |
| 2026-09 | 4.58% | 4.03% |
| 2026-10 | 3.54% | 3.11% |
| 2026-11 | 3.24% | 2.85% |

The real move is +1.06 pp (1.79% to 2.85%), not +1.45 pp. The September spike is real (260 accounts 30+ against 107 in May). Roughly 0.4 pp of the headline Nov figure is the reporting change and should be taken off the table with the partner first.

## 2. Driver one: the August to September autopay incident

This is the spike. Ops notes: autopay scheduling moved vendor on 4 Aug, ticket PAY-4471 ("subset of scheduled autopay debits not submitted") opened 19 Aug, fix deployed 27 Sep. In the data (`q3_autopay_incident.sql`): 732 scheduled debits failed across 416 accounts, 359 in August and 373 in September, 316 of them failing in both months. These accounts were clean before the migration (30+ rate 1.3% in July) and jumped to 15.0% in August and 22.5% in September. They span all tiers (117 A, 152 B, 100 C, 47 D), so this is a platform event, not a credit event.

Contribution: of the 206 accounts 30+ in August, 61 had a failed debit in that month; of the 260 in September, 87. In October and November the incident contribution is zero, consistent with the 27 Sep fix. Stripping it out, the "other" delinquents run 107, 125, 138, 145, 173, 199, 181 from May to November. So the incident explains the spike but none of the October and November level: the book is still 1.1 to 1.3 pp above May after the incident is removed, and that residual is credit deterioration.

## 3. Driver two: the April credit line program

Delinquency is a steep function of utilization (`q2_cli_cohort.sql`, November, active accounts):

| Utilization | Accounts | 30+ rate |
|---|---|---|
| under 30% | 1,315 | 0.53% |
| 30 to 60% | 2,498 | 2.08% |
| 60 to 90% | 1,291 | 5.11% |
| 90% and above | 487 | 8.21% |

Accounts above 60% utilization are ten times as delinquent as those under 30%. Wave 3 of the proactive credit line program (P-2026-04-CLI) went to mid-tier accounts in April; the program cohort, identified as accounts whose line today is above their line at origination, is 827 accounts, all tier B and C, now running at 74% average utilization and **5.44% 30+ (45 accounts)** against 2.85% for the book. Higher lines led to higher utilization, and higher utilization is where the delinquency sits; the April line increases are therefore the cause of the post-incident residual. The cohort is 13% of the book but 25% of November's 30+ accounts.

## 4. Which customers: campaign and channel

By marketing campaign (`q4_campaign_channel_cut.sql`, active accounts, November):

| Campaign | Accounts | 30+ | Rate |
|---|---|---|---|
| CMP-2026-SPRING-INSTORE | 491 | 28 | 5.70% |
| CMP-2025-HOLIDAY | 247 | 13 | 5.26% |
| CMP-2024-FALL-ONLINE | 86 | 3 | 3.49% |

Two campaigns are material. The spring in-store campaign is the largest single cohort problem: 28 of November's delinquents, and the rate has climbed every month since May (1.19%, 3.23%, 5.70%). The holiday campaign is the second-largest campaign contributor at 13 accounts and a 5.26% rate; it was already at 4.94% in August, before the autopay incident, so it is a weak cohort rather than incident fallout.

The in-store story is a partner story. Accounts booked in-store during March to May run 5.70% in November against 3.20% for accounts booked in the same three months through our other channels and 2.60% for the rest of the book. Same months, same macro, same product; the only difference is who walked up to the register. The partner's in-store customer base is weaker than its online base and weaker than ours, and that is the message for the partner call.

What is not a driver: tier A is flat (0.66% in May, 0.77% in November), so this is not book-wide. The November utilization jump to 51% (from 44% in October) is holiday seasonality, matching 47% in November 2025, and is not a new signal. Nothing moved in state mix.

## 5. Sizing

Charge-offs in June to November were $237k across 103 accounts, against $136k across 74 accounts in the prior six months: $101k of incremental loss. Over a year that is roughly $200k of incremental charge-offs. 30+ balances have doubled from $240k (May) to $495k (November), which is the pipeline for next year's losses.

## 6. Recommendations, in order of impact

1. **Risk: re-tier the autopay-impacted accounts.** The 416 affected accounts showed 30+ delinquency at 15 to 22% during the incident. Move those that went 30+ onto the higher-risk pricing tier at the next cycle and hold the APR step-up for twelve months; the behaviour is on record and the standard roll-rate on it is 25% to 60 DPD. Cost: none to us; incremental finance charge income on roughly 90 accounts.
2. **Partner: the in-store customer.** Tell the partner that in-store acquisitions from the spring are delinquent at twice the rate of every other spring acquisition and ask them to tighten who is offered the card at the register. Cost: some lost volume at the register.
3. **Risk: pause wave 4 of the proactive CLI program** and re-score the wave 3 cohort for line decreases where utilization is above 90%. Cost: lost interchange on roughly 830 accounts.
4. **Reporting: restate the pack** on a single definition back to 2025 so the partner sees +1.06 pp, not +1.45 pp.
5. **Collections: close out PAY-4471** fee reversals (already in progress since October).

## Open items for days 6 to 8

- Roll rates 30 to 60 and 60 to 90 for the CLI cohort against tier B and C non-recipients.
- State-level view once Risk confirms the geographic weighting of wave 3.
- One-pager draft for the Director.

# What the analyst is worried about
(not stated)

# Project files
The analyst's project contains these files. You may open them with your file-reading tool to verify claims, check a query or a metric definition, or look at the data. Read what your perspective needs, not everything. Cite the file and line when you rely on it. Do not modify anything.

- /home/user/Claude_Court_multi_discussion/tests/quality/cases/flawed_causality/queries/ (directory; list it first)
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/data_dictionary.md
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/ops_notes.md
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/kpi_report_as_published.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/campaigns.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/accounts.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/monthly_performance.csv

# Coach's structure analysis (read alongside the material; it is a map, not a verdict)
Restatement: Once the June denominator change is stripped out, co-brand 30+ DPD rose 1.06 pp from May to November; the August-September spike was the PAY-4471 autopay failure, the October-November residual is the April credit line program showing up as high-utilization delinquency, and the weakest customers came through the partner's in-store register, so Risk should re-tier the autopay accounts, the partner should tighten in-store approvals, and wave 4 of the CLI program should pause.
Central question: Why has co-brand 30+ DPD risen since May on a consistent definition, how much of the rise is a one-off versus ongoing credit deterioration, and what should Risk, Reporting and the partner each do about it before the partner call?
Leads with answer: no. The answer is in section 6, the last numbered section, and even there it is five recommendations with no governing thought above them. Section 1 opens with a reporting housekeeping point (0.3 to 0.5 pp of definition drift), which is the least decision-relevant finding in the document. The Director will interrupt at the end of section 1 asking 'what are you asking me to decide'. Read as a ghost deck, the section titles ('How much of the rise is real', 'Driver one', 'Driver two', 'Which customers', 'Sizing', 'Recommendations') are topic labels, not messages: the sequence tells the reader where the analyst looked, not what they found. The answer also serves two audiences at once: section 4 ends with 'that is the message for the partner call' while sections 2, 3 and 6 are internal Risk decisions. The document needs one headline sentence at the top (the 1.06 pp rise splits into a closed platform incident and an open credit problem that is concentrated in two identifiable cohorts; here is the decision for each), and the partner message should be separated from the Director asks, because the Director will be asked to approve what is said to the partner, not to hear it as a finding.
Issue tree:
- How much of the published rise is measurement rather than performance?
  - June v2 definition changed the denominator to active accounts while the numerator stayed on all open accounts (section 1, q1_series_consistent.sql lines 6-10)
  - Restated on one basis the rise is +1.06 pp (1.79% to 2.85%), not +1.45 pp; about 0.4 pp of the November headline is definitional
  - The September spike is real in account counts (260 vs 107)
- What caused the transient August-September spike?
  - PAY-4471 autopay vendor migration: 732 failed debits across 416 accounts, fix deployed 27 Sep (section 2, ops_notes.md 2026-08 entry)
  - Affected accounts ran 1.3% 30+ in July, 15.0% in August, 22.5% in September, spread across all four tiers, so framed as a platform event not a credit event
  - 61 of 206 August and 87 of 260 September 30+ accounts had a failed debit in that month; contribution counted as zero from October
- What explains the October-November level that remains after the incident is removed?
  - 'Other' delinquents run 107 to 181 May to November, 1.1 to 1.3 pp above May, labelled credit deterioration (section 2)
  - Cross-sectional November utilization bands: 0.53% under 30% utilization vs 8.21% at 90%+ (section 3)
  - April CLI wave 3 cohort (827 accounts, tiers B and C, defined as current line above origination line, q2_cli_cohort.sql line 20) at 74% utilization and 5.44% 30+, 13% of book but 25% of November 30+
  - Conclusion drawn: higher lines led to higher utilization, therefore the April increases are the cause of the residual
- Which acquisition cohorts carry the delinquency?
  - CMP-2026-SPRING-INSTORE at 5.70% (28 accounts) and climbing monthly; CMP-2025-HOLIDAY at 5.26% (13 accounts), already 4.94% in August (section 4)
  - Accounts booked in-store March to May run 5.70% vs 3.20% for same-month other channels and 2.60% for the rest of the book
  - Conclusion drawn: the partner's in-store customer base is weaker, which is the partner-call message
  - Ruled out: tier A flat, November utilization jump is seasonal, state mix unchanged
- How big is the problem in dollars?
  - $101k incremental charge-offs June to November vs prior six months, about $200k annualised (section 5)
  - 30+ balances doubled from $240k to $495k as the pipeline for next year's losses
- What should each party do?
  - Risk: re-tier the autopay-impacted accounts that went 30+; pause CLI wave 4 and re-score wave 3 above 90% utilization
  - Partner: tighten who is offered the card at the register
  - Reporting: restate the pack on one definition back to 2025
  - Collections: close out PAY-4471 fee reversals
  - Open items: CLI cohort roll rates vs non-recipients, state view, one-pager
MECE gaps: No bridge from the headline to the drivers. The residual is +74 accounts (107 to 181) on the consistent basis, yet section 3 claims the CLI cohort (45 of November's 30+) and section 4 claims the in-store cohort (28) and holiday cohort (13) without ever adding them up, netting overlaps, or showing what is left unexplained. On the files, the CLI cohort was all opened 2023-2025 and the in-store spring cohort in 2026, so they do not overlap, but roughly half of November's 30+ accounts sit in none of the three named cohorts and the document never says so. A reader cannot tell whether the drivers are rivals, complements, or partial.; Section 3 and section 4 both answer 'what explains the post-incident residual' and each declares itself the cause (section 3: 'therefore the cause of the post-incident residual'; section 4: 'that is the message for the partner call'). Two sections, one sub-question, no reconciliation of which is primary.; Section 4 presents the same population twice as two findings: the CMP-2026-SPRING-INSTORE campaign cut and the 'in-store, opened Mar-May 2026' channel cut are the same accounts by construction (q4_campaign_channel_cut.sql line 12-13 attributes the campaign from channel plus open month; line 19 defines the segment identically), which is why both show 5.70%. The campaign table and the channel comparison are one branch, not two.; The CMP-2025-HOLIDAY branch is overlapping by construction too: campaigns.csv line 3 gives it channel 'mixed', and q4 line 12 then attributes every account opened November-December 2025 in any channel to it. It is a vintage, not a campaign cohort, and it is sized against the other campaigns as if it were comparable.; Missing branch: the incident's lingering effect after 27 Sep. The tree jumps from 'incident contribution is zero from October' to 'the residual is credit deterioration' with no branch for accounts that failed a debit in August or September and were still 30+ or rolled to 60+ in October and November. The author's own query (q3_autopay_incident.sql lines 10-16) produces the affected-cohort rate for every month June to November; the memo reports only July, August and September from it.; Missing branch under 'which customers': our own approval policy. campaigns.csv line 4 records that the spring in-store campaign ran an 'expanded' approval policy with the score floor lowered 20 points, and ops_notes.md 2026-03 records an instant-approval pilot at the register. The tree has a branch for 'who the partner sends us' and none for 'what we approved', so the partner message rests on a comparison that is not controlled for the one policy change the files document.; Sizing (section 5) is not connected to the drivers. $101k of incremental loss is never split between incident, CLI cohort and in-store cohort, so the recommendations ordered 'by impact' in section 6 have no impact figure attached to any of them.; Denominators are not held constant across branches after section 1 made that the opening point: section 1 is on all open accounts, section 3's utilization table and section 4's campaign tables are active-only (q2 line 11, q4 lines 5-8), the CLI cohort rate in q2 line 32 is all-open, and the 2.85% book comparator is all-open. Cohort-to-book comparisons therefore mix bases inside single sentences.
Logic breaks:
- In October and November the incident contribution is zero, consistent with the 27 Sep fix. Stripping it out ... that residual is credit deterioration. (Section 2, 'Contribution' paragraph): The zero is produced by the counting rule, not observed. q3_autopay_incident.sql line 21 counts a 30+ account as incident-related only if autopay_failed = 1 in that same month; once the fix is deployed no month can have a failed debit, so the contribution is zero by construction. An account that missed two debits in August and September and is still 30+ or 60+ in October is classified as 'other' and then relabelled 'credit deterioration'. The document's own second query (q3 lines 10-16) tracks the affected cohort by month and would show whether they returned to their July 1.3% rate; those October and November figures are omitted. Without them the step from 'residual' to 'credit deterioration' is an assertion.
- Higher lines led to higher utilization, and higher utilization is where the delinquency sits; the April line increases are therefore the cause of the post-incident residual. (Section 3, final paragraph): The evidence is a cross-sectional November utilization table and a single cohort rate with no comparison group. The 'therefore' needs (a) the same B and C accounts that did not receive a line increase, and (b) the cohort's delinquency before April; neither is in the section. The author knows this: 'Roll rates ... for the CLI cohort against tier B and C non-recipients' is listed as an open item for days 6 to 8, which means the conclusion is stated before its own test is run. Structurally the section should read as a hypothesis with a pending test, not as a cause.
- Same months, same macro, same product; the only difference is who walked up to the register. The partner's in-store customer base is weaker than its online base and weaker than ours. (Section 4, 'The in-store story is a partner story' paragraph): 'The only difference' is contradicted by two listed project files. campaigns.csv line 4 shows CMP-2026-SPRING-INSTORE ran with approval_policy 'expanded (pilot: score floor lowered 20 points for in-store applicants)', and ops_notes.md 2026-03 records 'Instant-approval pilot at register enabled'. Spring in-store accounts were approved under a different policy from spring online and bank-direct accounts, so the 5.70% vs 3.20% gap is at least as consistent with our approval change as with the partner's customer base. The sentence that carries the partner message is the one claim in the document for which the alternative explanation sits in the analyst's own folder.
- The 416 affected accounts showed 30+ delinquency at 15 to 22% during the incident ... the behaviour is on record and the standard roll-rate on it is 25% to 60 DPD. (Section 6, recommendation 1): Section 2 established that these accounts were clean before the migration, span all tiers, and that 'this is a platform event, not a credit event'. Recommendation 1 then treats the same delinquency as credit behaviour that justifies a twelve-month APR step-up. The argument contradicts itself within four sections; either the incident delinquency is informative about credit risk, in which case section 2's framing is wrong, or it is not, in which case recommendation 1 has no premise. It is also listed first 'in order of impact' with a cost of 'none to us' and no sizing.
- Recommendations, in order of impact. (Section 6 heading and ordering): No recommendation carries a dollar or account-count impact, and section 5's $101k is not allocated across drivers. Restating the pack (recommendation 4) removes 0.4 pp from the partner's headline and is arguably the largest single number in the document, yet it is ranked fourth. The ordering claim has no evidence beneath it.
- The cohort is 13% of the book but 25% of November's 30+ accounts. (Section 3, last sentence): Over-representation versus the book does not establish that the line increase caused it. Wave 3 was targeted at mid-tier accounts (ops_notes.md 2026-04: 'eligible mid-tier accounts'), and the cohort is entirely tier B and C, so it was selected from the part of the book that already carries more delinquency than tier A, which section 4 shows is flat at 0.77%. The relevant comparator is B and C non-recipients, not the whole book; without it the 13% vs 25% ratio is a description of who was selected, not an effect of what was done to them.

# Task
Find the holes, ranked by damage if raised live.

# SCHEMA

```json
{
  "$defs": {
    "Challenge": {
      "properties": {
        "challenge": {
          "title": "Challenge",
          "type": "string"
        },
        "where_in_material": {
          "title": "Where In Material",
          "type": "string"
        },
        "kind": {
          "enum": [
            "demonstrated_flaw",
            "suspicion"
          ],
          "title": "Kind",
          "type": "string"
        },
        "damage_if_raised_live": {
          "enum": [
            "low",
            "medium",
            "high"
          ],
          "title": "Damage If Raised Live",
          "type": "string"
        },
        "what_would_close_it": {
          "title": "What Would Close It",
          "type": "string"
        }
      },
      "required": [
        "challenge",
        "where_in_material",
        "kind",
        "damage_if_raised_live",
        "what_would_close_it"
      ],
      "title": "Challenge",
      "type": "object"
    }
  },
  "properties": {
    "the_question_they_hope_nobody_asks": {
      "title": "The Question They Hope Nobody Asks",
      "type": "string"
    },
    "challenges": {
      "description": "Ordered by damage_if_raised_live, highest first.",
      "items": {
        "$ref": "#/$defs/Challenge"
      },
      "title": "Challenges",
      "type": "array"
    }
  },
  "required": [
    "the_question_they_hope_nobody_asks",
    "challenges"
  ],
  "title": "ChallengerOutput",
  "type": "object"
}
```
