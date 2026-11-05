"""Output contracts for every role, plus the persisted session record.

Every role answers through structured outputs against one of these models, so
the report renderer never parses free text.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]


# --------------------------------------------------------------------------- #
# Coach pre-pass
# --------------------------------------------------------------------------- #


class IssueBranch(BaseModel):
    sub_question: str = Field(description="A sub-question of the central question.")
    sub_points: list[str] = Field(description="The points or evidence the material offers under this sub-question.")


class LogicBreak(BaseModel):
    claim: str
    where_in_material: str
    why_it_does_not_follow: str


class FrameworkUse(BaseModel):
    framework: str
    why_here: str = Field(description="Why this framework changes the answer for this specific material.")


class StructureAnalysis(BaseModel):
    one_line_restatement: str = Field(description="The whole argument in one sentence.")
    leads_with_answer: bool
    answer_first_note: str = Field(description="Where the answer currently sits and where it should sit.")
    central_question: str
    issue_tree: list[IssueBranch]
    mece_gaps: list[str] = Field(description="Sub-questions missing or overlapping.")
    logic_breaks: list[LogicBreak]
    frameworks_used: list[FrameworkUse] = Field(description="At most two.")


# --------------------------------------------------------------------------- #
# Advocate and Challenger
# --------------------------------------------------------------------------- #


class Strength(BaseModel):
    strength: str
    where_in_material: str


class Rebuttal(BaseModel):
    objection: str
    rebuttal: str
    supported_by_material: bool = Field(description="False if the rebuttal needs evidence the material does not contain.")
    evidence_needed: str = Field(description="Empty if supported_by_material is true.")


class AdvocateOutput(BaseModel):
    strongest_case: str = Field(description="One sentence a Director would repeat to a VP.")
    undersold_strengths: list[Strength]
    lead_with: str = Field(description="What to say in the first minute of the meeting.")
    objections_and_rebuttals: list[Rebuttal]


class Challenge(BaseModel):
    challenge: str
    where_in_material: str
    kind: Literal["demonstrated_flaw", "suspicion"]
    damage_if_raised_live: Severity
    what_would_close_it: str


class ChallengerOutput(BaseModel):
    the_question_they_hope_nobody_asks: str
    challenges: list[Challenge] = Field(description="Ordered by damage_if_raised_live, highest first.")


# --------------------------------------------------------------------------- #
# Panelists
# --------------------------------------------------------------------------- #


class Concern(BaseModel):
    concern: str
    where_in_material: str
    severity: Severity


class PanelistOutput(BaseModel):
    one_line_reaction: str
    stance: Literal["supportive", "neutral", "skeptical", "blocking"]
    top_concerns: list[Concern] = Field(description="One or two concerns, the ones you actually care about.")
    the_question: str = Field(description="The one thing you would say aloud in the meeting.")
    what_would_make_me_say_yes: str


# --------------------------------------------------------------------------- #
# Judge
# --------------------------------------------------------------------------- #


class LikelyQuestion(BaseModel):
    question: str
    asked_by: str
    why_they_ask: str
    suggested_answer: str = Field(description="Sayable in under thirty seconds.")


class Dissent(BaseModel):
    topic: str
    positions: list[str]
    root_cause: str


class JudgeBrief(BaseModel):
    verdict: Literal["go", "revise", "no_go"]
    headline: str = Field(description="One sentence, answer first.")
    decision: str = Field(description="In decide mode: the option chosen and why. Otherwise empty.")
    must_fix_before_sending: list[str]
    likely_questions: list[LikelyQuestion]
    consensus: list[str]
    dissent: list[Dissent]
    blind_spots: list[str] = Field(description="Things nobody on the panel raised but should have.")
    next_steps: list[str]


# --------------------------------------------------------------------------- #
# Coach post-pass
# --------------------------------------------------------------------------- #


class SCQA(BaseModel):
    situation: str
    complication: str
    question: str
    answer: str


class StorylineItem(BaseModel):
    title: str = Field(description="Slide or section headline, written as the message itself.")
    key_message: str
    why_here: str


class Storyline(BaseModel):
    one_line_restatement: str
    opening_scqa: SCQA
    recommended_storyline: list[StorylineItem]
    changes_from_original: list[str]
    so_what_ladder: list[str] = Field(description="Finding, then successive so-whats, ending in a decision or action.")
    frameworks_used: list[FrameworkUse] = Field(description="At most two.")


# --------------------------------------------------------------------------- #
# Session record
# --------------------------------------------------------------------------- #


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0

    def add(self, other: "Usage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cache_read_input_tokens += other.cache_read_input_tokens
        self.cache_creation_input_tokens += other.cache_creation_input_tokens


class CallMeta(BaseModel):
    role_id: str
    model: str
    seconds: float
    usage: Usage
    error: Optional[str] = None


class PanelistResult(BaseModel):
    role_id: str
    role_name: str
    output: Optional[PanelistOutput] = None
    error: Optional[str] = None


class DebriefAnswer(BaseModel):
    question: str
    predicted_for: str
    asked: bool


class Debrief(BaseModel):
    recorded_at: str
    outcome_in_room: str
    predicted: list[DebriefAnswer]
    unpredicted: list[str]
    notes: str


class Session(BaseModel):
    id: str
    created_at: str
    mode: str
    mode_title: str
    input_text: str
    worry: Optional[str] = None
    panel_ids: list[str]
    mock: bool = False
    output_language: str = "en"

    structure: Optional[StructureAnalysis] = None
    advocate: Optional[AdvocateOutput] = None
    challenger: Optional[ChallengerOutput] = None
    panel: list[PanelistResult] = Field(default_factory=list)
    judge: Optional[JudgeBrief] = None
    storyline: Optional[Storyline] = None

    calls: list[CallMeta] = Field(default_factory=list)
    errors: dict[str, str] = Field(default_factory=dict)
    debrief: Optional[Debrief] = None

    def total_usage(self) -> Usage:
        total = Usage()
        for call in self.calls:
            total.add(call.usage)
        return total
