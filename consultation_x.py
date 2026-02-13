"""
ConsultationX - AI-Powered Consultation Training Tool
=====================================================
Backend framework for simulating consultative phone calls
and scoring team performance.

Owner: Shawn Hernandez (Proof by Shawn Hernandez)
Created: 2026-02-13

Designed for:
- Project Management team training
- Sales team training
- Consultative selling skill development

How it works:
1. User selects a scenario (e.g. "New client inquiry", "Upset client", "Upsell opportunity")
2. AI plays the role of the client with a hidden persona + goals
3. User responds in real-time via text (voice later)
4. AI evaluates the full conversation and generates a Consultation Score (0-100)
5. Breakdown by category: Solution Finding, Speed, Efficiency, Communication, Empathy, Closing
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple
from enum import Enum
from datetime import datetime
import json


# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class TeamRole(Enum):
    """Which team the trainee belongs to."""
    PROJECT_MANAGER = "Project Manager"
    SALES = "Sales"


class ScenarioCategory(Enum):
    """Types of consultation scenarios."""
    NEW_CLIENT_INQUIRY = "New Client Inquiry"
    UPSET_CLIENT = "Upset Client"
    UPSELL_OPPORTUNITY = "Upsell Opportunity"
    SCHEDULING_CONFLICT = "Scheduling Conflict"
    SCOPE_CHANGE = "Scope Change"
    BUDGET_OBJECTION = "Budget Objection"
    COMPETITOR_COMPARISON = "Competitor Comparison"
    RUSH_REQUEST = "Rush Request"
    QUALITY_COMPLAINT = "Quality Complaint"
    FOLLOW_UP_CLOSE = "Follow-Up Close"


class Difficulty(Enum):
    """How tough the simulated client is."""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ScoreCategory(Enum):
    """Categories for scoring the consultation."""
    SOLUTION_FINDING = "Solution Finding"
    SPEED = "Speed & Responsiveness"
    EFFICIENCY = "Efficiency"
    COMMUNICATION = "Communication"
    EMPATHY = "Empathy & Rapport"
    CLOSING = "Closing & Next Steps"


# Score tier thresholds
SCORE_TIERS = {
    (90, 100): {"tier": "A+", "label": "Elite Closer"},
    (80, 89):  {"tier": "A",  "label": "Strong Performer"},
    (70, 79):  {"tier": "B",  "label": "Solid"},
    (60, 69):  {"tier": "C",  "label": "Needs Improvement"},
    (0, 59):   {"tier": "D",  "label": "Needs Training"},
}


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ClientPersona:
    """The simulated client's personality and hidden goals."""
    name: str
    company: str
    personality: str  # e.g. "impatient", "detail-oriented", "friendly but indecisive"
    hidden_goal: str  # what the client actually wants (trainee must uncover this)
    pain_points: List[str]
    budget_range: Optional[str] = None
    objections: List[str] = field(default_factory=list)
    deal_breakers: List[str] = field(default_factory=list)


@dataclass
class Scenario:
    """A training scenario definition."""
    id: str
    title: str
    category: ScenarioCategory
    team_role: TeamRole
    difficulty: Difficulty
    description: str
    client_persona: ClientPersona
    success_criteria: List[str]
    max_turns: int = 20  # conversation limit
    time_limit_seconds: int = 600  # 10 minutes


@dataclass
class Message:
    """A single message in the consultation conversation."""
    role: str  # "client" or "trainee"
    content: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CategoryScore:
    """Score for a single evaluation category."""
    category: ScoreCategory
    score: int  # 0-100
    feedback: str


@dataclass
class ConsultationResult:
    """Final evaluation of a completed consultation."""
    overall_score: int  # 0-100
    tier: str
    tier_label: str
    category_scores: List[CategoryScore]
    strengths: List[str]
    improvements: List[str]
    key_moments: List[str]  # notable good/bad moments from the conversation
    client_satisfaction: int  # 0-100 how happy the simulated client would be
    deal_outcome: str  # "closed", "lost", "follow-up needed"
    summary: str


@dataclass
class ConsultationSession:
    """A full training session."""
    session_id: str
    user_email: str
    user_name: str
    team_role: TeamRole
    scenario: Scenario
    messages: List[Message] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    result: Optional[ConsultationResult] = None
    is_complete: bool = False

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()

    def add_message(self, role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def get_turn_count(self) -> int:
        return len([m for m in self.messages if m.role == "trainee"])

    def is_over_limit(self) -> bool:
        return self.get_turn_count() >= self.scenario.max_turns

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# SCENARIO LIBRARY
# ============================================================

# Pre-built scenarios for both teams

PM_SCENARIOS = [
    Scenario(
        id="pm_upset_reshoot",
        title="The Angry Reshoot Request",
        category=ScenarioCategory.QUALITY_COMPLAINT,
        team_role=TeamRole.PROJECT_MANAGER,
        difficulty=Difficulty.HARD,
        description="A real estate agent is furious about photo quality from yesterday's shoot. They want a full reshoot for free, today.",
        client_persona=ClientPersona(
            name="Karen Mitchell",
            company="Compass Real Estate",
            personality="Impatient, confrontational, but ultimately reasonable if you show empathy first",
            hidden_goal="Wants to feel heard more than anything. Would accept a partial reshoot if you acknowledge the issue.",
            pain_points=["Photos are dark", "Listing goes live tomorrow", "Paid premium price"],
            objections=["I paid for premium quality", "My clients expect better", "I'll go to your competitor"],
            deal_breakers=["Being told it's not a big deal", "Long wait times for resolution"],
        ),
        success_criteria=[
            "Acknowledge the issue without being defensive",
            "Ask specific questions about which photos need fixing",
            "Offer a concrete solution with a timeline",
            "Retain the client relationship",
        ],
    ),
    Scenario(
        id="pm_schedule_conflict",
        title="Double-Booked Shoot Day",
        category=ScenarioCategory.SCHEDULING_CONFLICT,
        team_role=TeamRole.PROJECT_MANAGER,
        difficulty=Difficulty.MEDIUM,
        description="Two high-value clients need shoots at overlapping times tomorrow. One is a repeat client, the other is new but big potential.",
        client_persona=ClientPersona(
            name="David Park",
            company="Keller Williams",
            personality="Friendly but firm. Values reliability above all.",
            hidden_goal="Flexible on time but needs to know you prioritize him. Would move to afternoon if asked respectfully.",
            pain_points=["Already rescheduled once", "Open house in 3 days"],
            objections=["I was told this time was confirmed", "My seller is getting anxious"],
        ),
        success_criteria=[
            "Be transparent about the conflict",
            "Offer alternative times proactively",
            "Make the client feel prioritized",
            "Secure a confirmed new time",
        ],
    ),
    Scenario(
        id="pm_scope_creep",
        title="The Expanding Scope",
        category=ScenarioCategory.SCOPE_CHANGE,
        team_role=TeamRole.PROJECT_MANAGER,
        difficulty=Difficulty.MEDIUM,
        description="Client booked a standard photo package but keeps asking for extras on-site (drone, video walkthrough, twilight). Need to manage expectations and upsell properly.",
        client_persona=ClientPersona(
            name="Jennifer Liu",
            company="Sotheby's International",
            personality="Enthusiastic, doesn't understand pricing, assumes everything is included",
            hidden_goal="Would happily pay more if the value is explained clearly. Budget isn't the issue — clarity is.",
            pain_points=["Luxury listing needs to look amazing", "Previous photographer did everything in one visit"],
            budget_range="$2,000-5,000",
            objections=["My last photographer included all of this", "At this price I expected more"],
        ),
        success_criteria=[
            "Explain what's included vs. add-ons clearly",
            "Position extras as upgrades, not upsells",
            "Get commitment on expanded scope with pricing",
            "Keep the energy positive",
        ],
    ),
    Scenario(
        id="pm_rush_request",
        title="The Last-Minute Rush",
        category=ScenarioCategory.RUSH_REQUEST,
        team_role=TeamRole.PROJECT_MANAGER,
        difficulty=Difficulty.EASY,
        description="Agent needs photos edited and delivered by tonight instead of the standard 24-hour turnaround. It's 2pm.",
        client_persona=ClientPersona(
            name="Mike Torres",
            company="eXp Realty",
            personality="Apologetic but desperate. Knows it's a big ask.",
            hidden_goal="Willing to pay rush fee. Just needs to know it's possible.",
            pain_points=["Listing appointment tomorrow morning", "Seller is impatient"],
            budget_range="Will pay rush fee",
        ),
        success_criteria=[
            "Assess feasibility honestly",
            "Quote rush fee clearly",
            "Set realistic delivery time",
            "Confirm the arrangement",
        ],
    ),
]

SALES_SCENARIOS = [
    Scenario(
        id="sales_new_inquiry",
        title="The Cold Lead",
        category=ScenarioCategory.NEW_CLIENT_INQUIRY,
        team_role=TeamRole.SALES,
        difficulty=Difficulty.MEDIUM,
        description="A new real estate agent found your website and wants pricing. They're shopping around and comparing 3 companies.",
        client_persona=ClientPersona(
            name="Sarah Chen",
            company="Independent Agent",
            personality="Analytical, price-conscious, asks a lot of questions",
            hidden_goal="Wants the best value, not the cheapest. Will choose quality if you prove ROI.",
            pain_points=["New to the area", "Previous photographer was unreliable", "Needs consistent quality"],
            budget_range="$200-400 per listing",
            objections=["Your competitor is cheaper", "I'm just starting out so budget is tight", "Can I try one shoot first?"],
        ),
        success_criteria=[
            "Ask about their business before quoting price",
            "Understand their volume potential",
            "Position value over price",
            "Get commitment to a trial shoot",
        ],
    ),
    Scenario(
        id="sales_budget_objection",
        title="The Price Pushback",
        category=ScenarioCategory.BUDGET_OBJECTION,
        team_role=TeamRole.SALES,
        difficulty=Difficulty.HARD,
        description="A mid-volume agent (8 listings/month) loves your quality but says your pricing is 30% higher than their current provider.",
        client_persona=ClientPersona(
            name="Robert Kim",
            company="Coldwell Banker",
            personality="Direct, numbers-driven, respects confidence",
            hidden_goal="Already unhappy with current provider's reliability. Would switch for same price or slightly more if turnaround is faster.",
            pain_points=["Current provider misses deadlines", "Inconsistent quality between photographers", "No single point of contact"],
            budget_range="$250-350 per listing",
            objections=["30% more is hard to justify", "I need to see the math", "What if quality isn't better?"],
            deal_breakers=["Arrogance", "Inability to discuss pricing openly"],
        ),
        success_criteria=[
            "Acknowledge the price difference honestly",
            "Uncover pain points with current provider",
            "Calculate the cost of missed deadlines and reshoots",
            "Offer a volume commitment with pricing",
            "Close with a specific next step",
        ],
    ),
    Scenario(
        id="sales_upsell",
        title="The Upgrade Conversation",
        category=ScenarioCategory.UPSELL_OPPORTUNITY,
        team_role=TeamRole.SALES,
        difficulty=Difficulty.EASY,
        description="An existing client who does photo-only wants to know about video and drone. They just got a luxury listing.",
        client_persona=ClientPersona(
            name="Amanda Foster",
            company="Compass",
            personality="Excited, trusts your team already, but needs justification for the spend",
            hidden_goal="Wants to impress the seller and win more luxury listings. Will buy the premium package if you connect it to her business growth.",
            pain_points=["First luxury listing", "Wants to stand out from other agents", "Seller expects high-end marketing"],
            budget_range="$1,500-3,000",
        ),
        success_criteria=[
            "Congratulate them on the luxury listing",
            "Connect premium services to their business goals",
            "Present package options (not just one price)",
            "Close with a booking date",
        ],
    ),
    Scenario(
        id="sales_competitor",
        title="The Competitor Switch",
        category=ScenarioCategory.COMPETITOR_COMPARISON,
        team_role=TeamRole.SALES,
        difficulty=Difficulty.HARD,
        description="A high-volume agent (15+ listings/month) is considering leaving your competitor. They had a bad experience but are cautious about switching.",
        client_persona=ClientPersona(
            name="James Wright",
            company="RE/MAX",
            personality="Skeptical, been burned before, needs proof not promises",
            hidden_goal="Wants a reliable partner, not just a vendor. Will commit to a 3-month trial if you offer a dedicated point of contact.",
            pain_points=["Competitor missed 3 shoots last month", "No consistency in photographer quality", "Can't reach anyone when there's a problem"],
            budget_range="$300-500 per listing",
            objections=["How do I know you won't do the same?", "I need a guarantee", "What happens when you're busy?"],
            deal_breakers=["Overpromising", "Not listening to concerns"],
        ),
        success_criteria=[
            "Listen more than you talk in the first half",
            "Ask about specific pain points, don't assume",
            "Offer proof (case studies, references, trial)",
            "Propose a structured trial with clear expectations",
            "Don't trash the competitor",
        ],
    ),
]

ALL_SCENARIOS = PM_SCENARIOS + SALES_SCENARIOS


def get_scenarios_by_role(role: TeamRole) -> List[Scenario]:
    """Get all scenarios for a given team role."""
    return [s for s in ALL_SCENARIOS if s.team_role == role]


def get_scenario_by_id(scenario_id: str) -> Optional[Scenario]:
    """Look up a specific scenario by ID."""
    for s in ALL_SCENARIOS:
        if s.id == scenario_id:
            return s
    return None


# ============================================================
# AI PROMPT BUILDERS
# ============================================================

def build_client_system_prompt(scenario: Scenario) -> str:
    """Build the system prompt for the AI playing the client role."""
    persona = scenario.client_persona
    return f"""You are playing the role of a client in a consultation training simulation.

CHARACTER:
- Name: {persona.name}
- Company: {persona.company}
- Personality: {persona.personality}

SCENARIO: {scenario.description}

YOUR HIDDEN GOAL (do NOT reveal this directly):
{persona.hidden_goal}

YOUR PAIN POINTS:
{chr(10).join(f'- {p}' for p in persona.pain_points)}

YOUR OBJECTIONS (use these naturally when appropriate):
{chr(10).join(f'- {o}' for o in persona.objections)}

{f"YOUR DEAL BREAKERS (if the trainee does any of these, become difficult):" + chr(10) + chr(10).join(f'- {d}' for d in persona.deal_breakers) if persona.deal_breakers else ""}

RULES:
1. Stay in character at all times
2. Start the conversation as the client would — you initiated this call/chat
3. Be realistic — don't make it too easy or too hard
4. React naturally to good consultation skills (warm up) and bad ones (get frustrated)
5. If the trainee uncovers your hidden goal, gradually become more cooperative
6. Keep responses conversational and concise (2-4 sentences typically)
7. Never break character or reveal you are AI
8. Difficulty level: {scenario.difficulty.value}
"""


def build_evaluator_system_prompt(scenario: Scenario) -> str:
    """Build the system prompt for the AI evaluating the conversation."""
    return f"""You are an expert consultation trainer evaluating a training conversation.

SCENARIO: {scenario.title}
- Category: {scenario.category.value}
- Team Role: {scenario.team_role.value}
- Difficulty: {scenario.difficulty.value}
- Description: {scenario.description}

CLIENT'S HIDDEN GOAL: {scenario.client_persona.hidden_goal}

SUCCESS CRITERIA:
{chr(10).join(f'- {c}' for c in scenario.success_criteria)}

Evaluate the trainee's performance and return a JSON object with this exact structure:
{{
    "overall_score": <0-100>,
    "category_scores": [
        {{"category": "Solution Finding", "score": <0-100>, "feedback": "<specific feedback>"}},
        {{"category": "Speed & Responsiveness", "score": <0-100>, "feedback": "<specific feedback>"}},
        {{"category": "Efficiency", "score": <0-100>, "feedback": "<specific feedback>"}},
        {{"category": "Communication", "score": <0-100>, "feedback": "<specific feedback>"}},
        {{"category": "Empathy & Rapport", "score": <0-100>, "feedback": "<specific feedback>"}},
        {{"category": "Closing & Next Steps", "score": <0-100>, "feedback": "<specific feedback>"}}
    ],
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
    "key_moments": ["<notable moment 1>", "<notable moment 2>"],
    "client_satisfaction": <0-100>,
    "deal_outcome": "<closed | lost | follow-up needed>",
    "summary": "<2-3 sentence overall assessment>"
}}

Be specific and reference actual moments from the conversation. Be fair but honest.
Score relative to the difficulty level — a perfect score on Hard should be truly exceptional.
"""


def build_conversation_for_api(session: ConsultationSession) -> List[Dict]:
    """Convert session messages to API message format."""
    messages = []
    for msg in session.messages:
        if msg.role == "client":
            messages.append({"role": "assistant", "content": msg.content})
        else:
            messages.append({"role": "user", "content": msg.content})
    return messages


# ============================================================
# SCORE HELPERS
# ============================================================

def get_tier(score: int) -> Tuple[str, str]:
    """Get tier letter and label from a score."""
    for (low, high), info in SCORE_TIERS.items():
        if low <= score <= high:
            return info["tier"], info["label"]
    return "D", "Needs Training"


def parse_evaluation_response(response_text: str, scenario: Scenario) -> ConsultationResult:
    """Parse the AI evaluator's JSON response into a ConsultationResult."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            raise ValueError("Could not parse evaluation response as JSON")

    overall = data.get("overall_score", 50)
    tier, tier_label = get_tier(overall)

    category_scores = []
    for cs in data.get("category_scores", []):
        try:
            cat = ScoreCategory(cs["category"])
        except ValueError:
            continue
        category_scores.append(CategoryScore(
            category=cat,
            score=cs.get("score", 50),
            feedback=cs.get("feedback", ""),
        ))

    return ConsultationResult(
        overall_score=overall,
        tier=tier,
        tier_label=tier_label,
        category_scores=category_scores,
        strengths=data.get("strengths", []),
        improvements=data.get("improvements", []),
        key_moments=data.get("key_moments", []),
        client_satisfaction=data.get("client_satisfaction", 50),
        deal_outcome=data.get("deal_outcome", "follow-up needed"),
        summary=data.get("summary", ""),
    )
