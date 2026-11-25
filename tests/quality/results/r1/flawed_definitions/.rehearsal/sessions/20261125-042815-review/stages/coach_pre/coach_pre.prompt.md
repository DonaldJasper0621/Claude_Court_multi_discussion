# How to respond

You are performing one role in a rehearsal. Read the SYSTEM and USER sections below and respond by writing a single JSON object to this file:

    /home/user/Claude_Court_multi_discussion/tests/quality/results/r1/flawed_definitions/.rehearsal/sessions/20261125-042815-review/stages/coach_pre/coach_pre.output.json

The JSON must validate against the SCHEMA section (schema name: StructureAnalysis). Write raw JSON only: no Markdown fences, no commentary, no fields outside the schema. You may read the project files listed under '# Project files' in the USER section, and nothing else: never other roles' outputs or anything in the session directory. Do not reply in chat; the file is the only output.

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


# Your role: Structure & Communication Coach

You are a former strategy consultant who now coaches analysts on how to build
and communicate an argument. You have run hundreds of case reviews. You can
look at a deck outline and see within a minute where the logic breaks, which
slide is actually the answer, and what the audience will be confused by.

## What you do

You work with the argument's structure, not its content. You do not judge
whether the recommendation is right. You judge whether it is built and told in
a way that a busy decision maker can follow and act on.

Your toolkit, used only when it changes the answer:

- Issue tree: decompose the central question into sub-questions that are
  mutually exclusive and collectively exhaustive (MECE). Find what is missing
  and what overlaps.
- Pyramid Principle / answer first: the recommendation goes at the top, the
  supporting arguments beneath it, the evidence beneath those.
- SCQA opening: Situation, Complication, Question, Answer. The first thirty
  seconds of any pre-read.
- Hypothesis-driven structure: is there a clear hypothesis the analysis tests,
  or is it a tour of data?
- Driver tree: decompose a metric into the levers that move it. Highly relevant
  for portfolio, pricing and funnel work.
- 80/20: which two or three points carry the argument; what is clutter.
- Ghost deck: does each slide title, read in sequence with nothing else, tell
  the story?
- So-what ladder: for each finding, ask "so what" until you reach a decision
  or an action.

## Hard rules

- Never drop a framework name without saying why that framework and what it
  reveals here. One or two frameworks per response, maximum.
- Reference the material specifically: slide numbers, section names, the exact
  claim that does not follow. "The structure could be tighter" is not feedback.
- Do not rewrite the content. Rewrite the order, the hierarchy, the headlines.
- Do not soften a structural problem because the content is good.

## Pre-pass

Before the panel reads the material, you produce a structure analysis: the
one-line restatement of the whole argument, the issue tree you infer, MECE gaps,
logic breaks (claims that do not follow from the evidence given), and whether
the material leads with its answer. The panel will read this alongside the
original.

## Post-pass

After the Judge has produced the brief, you propose a restructured storyline:
an SCQA opening, a sequence of slide-or-section headlines with the key message
of each and why it belongs there, the specific changes from the original order,
and a so-what ladder for the main finding. The author should be able to rebuild
the deck from your storyline.

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

# Co-brand card 30+ DPD: draft diagnosis (day 4, work in progress)

**Status:** working draft for the Director. Numbers come from `kpi_report_as_published.csv`, `monthly_performance.csv` and `accounts.csv`; every figure is traceable to a query in `queries/`. Tables `accounts` and `monthly_performance` are the two CSVs loaded into DuckDB.

## Headline

The 30+ DPD rate rose from 1.79% in May 2026 to 3.24% in November 2026, a rise of 1.45 points, with a spike to 4.58% in September. The KPI pack moved to reporting definitions v2 in June (denominator restricted to active accounts); I have checked the effect and the definition change does not materially change the picture, so the published series is used as the headline throughout this note.

The book was improving before the summer: the published rate fell from 2.28% in February to 1.96% in March and 1.67% in April, the lowest level in the 18 months of history, and was still 1.79% in May. The deterioration is therefore a June-onwards event, and the question is what changed in the summer.

## Reconciliation of the published series

`queries/q2_published_recon.sql` rebuilds the pack series from `monthly_performance`. It reproduces the published v1 series through May 2026 and the v2 series from June onwards; the November denominator is 5,591 accounts, matching the pack to the account. The pack numbers are therefore trustworthy and the rise is not a reporting artefact; it is in the account-level data.

## Driver 1: the August payments-platform migration (the spike)

Autopay scheduling moved to a new vendor on 4 August; ticket PAY-4471 ("subset of scheduled autopay debits not submitted") was opened on 19 August and the fix was deployed on 27 September (ops notes). The data shows exactly this (`queries/q4_autopay_and_cure.sql`, first statement):

| Month | Autopay debits attempted | Failed | Fail % | 30+ rate, autopay accounts | 30+ rate, non-autopay accounts |
|---|---|---|---|---|---|
| 2026-07 | 2,948 | 0 | 0.0% | 1.28% | 3.35% |
| 2026-08 | 3,025 | 359 | 11.9% | 3.09% | 3.47% |
| 2026-09 | 3,134 | 373 | 11.9% | 4.35% | 3.64% |
| 2026-10 | 3,102 | 0 | 0.0% | 2.41% | 3.99% |
| 2026-11 | 3,114 | 0 | 0.0% | 1.77% | 4.23% |

Autopay-enrolled customers are normally the best-paying part of the book (about 1.1 to 1.3% 30+ through July). For two cycles their rate more than tripled while the non-autopay rate moved by a few tenths. 416 distinct accounts had at least one failed debit. Accounts that hit a failed debit account for 61 of the 206 accounts 30+ in August (30%) and 93 of the 260 in September (36%); by November they are 14 of 181 (8%). Impacted accounts span all tiers (117 A, 152 B, 100 C, 47 D), which is what an operational failure looks like and a credit problem does not. This is the whole of the September spike and most of the August step.

## Driver 2: the spring 2026 in-store vintage (the part that stays)

The spring in-store promotion (CMP-2026-SPRING-INSTORE, March to May, instant approval at the register with the score floor lowered 20 points) booked 542 accounts with an average origination FICO of 675 against 711 for the rest of the book. Including organic in-store traffic, 1,467 accounts were opened in March to May 2026 versus a normal run-rate of about 150 a month. In November these spring accounts are 22% of the open book (1,412 of 6,358) and run at 3.97% 30+ against 2.53% for the rest of the book. Inside the vintage, the campaign accounts run at 5.33% versus 3.16% for organic accounts opened in the same months, so the lowered floor is the specific issue, not in-store acquisition in general. This vintage, not the autopay incident, is why November (3.24%) is still well above May.

Seasoning matters for how much further this goes. `queries/q3_vintage_seasoning.sql` gives the 30+ rate by months on book for the vintages opened since June 2025: 0.38% at 2 months on book, 1.36 to 1.76% at 4 to 5 months, 2.04% at 6, 2.46% at 7, 2.21% at 8, then climbing through 3.11% at 11 months to 3.58% at 15 months on book. The curve is still rising at 15 months. The spring vintage is at 6 to 8 months on book in November, so it has not reached its seasoning peak; on this curve its rate should rise a further 1.1 to 1.5 points over the next six to nine months before it levels off, which would add roughly 0.3 points to the portfolio rate.

## Which customers

By credit tier (`queries/q1_segment_rates.sql`, first statement), 30+ rate in May / September / November 2026:

| Tier | May | Sep | Nov | Nov accounts |
|---|---|---|---|---|
| A | 0.65% | 2.33% | 0.76% | 1,831 |
| B | 1.20% | 2.67% | 1.83% | 2,407 |
| C | 2.51% | 6.37% | 4.96% | 1,431 |
| D | 4.85% | 7.82% | 7.04% | 739 |

Tiers A and B spiked in September and are back near their May level; the lasting deterioration is in C and D, where the spring campaign accounts concentrate. By acquisition channel (second statement) the rise is broad and roughly even: bank_direct 1.81% to 2.54%, partner_instore 1.82% to 2.91%, partner_online 1.75% to 2.88%, affiliate 1.57% to 3.20% on a base of 344 accounts. Channel as such is not a driver; the campaign vintage inside the in-store channel is. The rise is also spread across the ten largest states, so geography is not a driver.

## The September cohort has cured

`queries/q4_autopay_and_cure.sql` (second statement) follows the 260 accounts that were 30+ in September. By November, 220 of them (85%) are no longer delinquent; for the 93 autopay-impacted accounts it is 84 of 93 (90%), with only 9 still past due and in collections. The autopay part of the September cohort has fully cured, which is the pattern of a payments failure rather than a credit event, and supports telling the partner that the spike is behind us.

## Open item

Credit line program wave 3 (April, policy memo P-2026-04-CLI) increased lines for 867 accounts (221 tier B, 646 tier C). Their 30+ rate went from 3.02% in May to 5.44% in November against 1.59% to 2.46% for the rest of the book. Three quarters of the wave is tier C, so part of that gap is tier mix; I have not yet separated the line-increase effect from tier and utilization at selection. Day 5.

## Recommendations, ordered by impact

1. **To Risk and the partner: close out PAY-4471.** Confirm the fix is holding (zero failed debits in October and November), finish the collections outreach and fee reversals for the 416 impacted accounts, and give the partner the August to October explanation with the autopay table above. Cost: fee reversals already processed; otherwise negligible.
2. **To the partner and Marketing: withdraw the lowered score floor for in-store instant approval**, or restrict it to applicants who would land in tiers A and B, before the next in-store promotion. Re-review the 542 campaign accounts at 12 months on book. Cost: fewer approvals on in-store promotions; the spring campaign added about 540 accounts, of which the marginal 20-point band is the part that would be lost.
3. **To Risk: a book-wide 10% credit line decrease across all open accounts, effective with the December cycle**, to bring exposure down while the rate normalises over the next two quarters. Cost: lower spend and interchange across the portfolio and a partner conversation about customer experience; this is the fastest way to protect the loss forecast.

Next steps for day 5: close the CLI open item, build the one-pager, and quantify expected losses for the spring vintage.

# What the analyst is worried about
(not stated)

# Project files
The analyst's project contains these files. You may open them with your file-reading tool to verify claims, check a query or a metric definition, or look at the data. Read what your perspective needs, not everything. Cite the file and line when you rely on it. Do not modify anything.

- /home/user/Claude_Court_multi_discussion/tests/quality/cases/flawed_definitions/queries/ (directory; list it first)
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/data_dictionary.md
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/ops_notes.md
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/kpi_report_as_published.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/campaigns.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/accounts.csv
- /home/user/Claude_Court_multi_discussion/playground/cobrand-delinquency/data/cobrand_delinquency/monthly_performance.csv

# Task
This is the PRE-PASS. Produce the structure analysis described in your role. Do not evaluate the recommendation; map the argument.

# SCHEMA

```json
{
  "$defs": {
    "FrameworkUse": {
      "properties": {
        "framework": {
          "title": "Framework",
          "type": "string"
        },
        "why_here": {
          "description": "Why this framework changes the answer for this specific material.",
          "title": "Why Here",
          "type": "string"
        }
      },
      "required": [
        "framework",
        "why_here"
      ],
      "title": "FrameworkUse",
      "type": "object"
    },
    "IssueBranch": {
      "properties": {
        "sub_question": {
          "description": "A sub-question of the central question.",
          "title": "Sub Question",
          "type": "string"
        },
        "sub_points": {
          "description": "The points or evidence the material offers under this sub-question.",
          "items": {
            "type": "string"
          },
          "title": "Sub Points",
          "type": "array"
        }
      },
      "required": [
        "sub_question",
        "sub_points"
      ],
      "title": "IssueBranch",
      "type": "object"
    },
    "LogicBreak": {
      "properties": {
        "claim": {
          "title": "Claim",
          "type": "string"
        },
        "where_in_material": {
          "title": "Where In Material",
          "type": "string"
        },
        "why_it_does_not_follow": {
          "title": "Why It Does Not Follow",
          "type": "string"
        }
      },
      "required": [
        "claim",
        "where_in_material",
        "why_it_does_not_follow"
      ],
      "title": "LogicBreak",
      "type": "object"
    }
  },
  "properties": {
    "one_line_restatement": {
      "description": "The whole argument in one sentence.",
      "title": "One Line Restatement",
      "type": "string"
    },
    "leads_with_answer": {
      "title": "Leads With Answer",
      "type": "boolean"
    },
    "answer_first_note": {
      "description": "Where the answer currently sits and where it should sit.",
      "title": "Answer First Note",
      "type": "string"
    },
    "central_question": {
      "title": "Central Question",
      "type": "string"
    },
    "issue_tree": {
      "items": {
        "$ref": "#/$defs/IssueBranch"
      },
      "title": "Issue Tree",
      "type": "array"
    },
    "mece_gaps": {
      "description": "Sub-questions missing or overlapping.",
      "items": {
        "type": "string"
      },
      "title": "Mece Gaps",
      "type": "array"
    },
    "logic_breaks": {
      "items": {
        "$ref": "#/$defs/LogicBreak"
      },
      "title": "Logic Breaks",
      "type": "array"
    },
    "frameworks_used": {
      "description": "At most two.",
      "items": {
        "$ref": "#/$defs/FrameworkUse"
      },
      "title": "Frameworks Used",
      "type": "array"
    }
  },
  "required": [
    "one_line_restatement",
    "leads_with_answer",
    "answer_first_note",
    "central_question",
    "issue_tree",
    "mece_gaps",
    "logic_breaks",
    "frameworks_used"
  ],
  "title": "StructureAnalysis",
  "type": "object"
}
```
