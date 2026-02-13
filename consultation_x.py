"""
ConsultationX - AI-Powered Consultation Training Tool
=====================================================
Backend framework for simulating consultative phone calls
and scoring team performance.

Owner: Shawn Hernandez (Proof by Shawn Hernandez)
Created: 2026-02-13

Architecture:
- Groq (Llama 3) = plays the client (fast, realistic conversation)
- Claude (Anthropic) = scores the conversation after it ends (smart, detailed)

Designed for:
- Project Management team training
- Sales team training
- Consultative selling skill development

How it works:
1. Trainee selects role (PM or Sales) and difficulty
2. System generates a randomized client (name, brokerage, scenario, personality)
3. Phone ring animation plays, call begins
4. Groq plays the client in real-time — fast responses feel like a real call
5. When the call ends, Claude analyzes the full transcript
6. Consultation Score (0-100) with category breakdown, strengths, and improvements
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Tuple
from enum import Enum
from datetime import datetime
import json
import random
import re
import hashlib


# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class TeamRole(Enum):
    PROJECT_MANAGER = "Project Manager"
    SALES = "Sales"


class ScenarioCategory(Enum):
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
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ScoreCategory(Enum):
    SOLUTION_FINDING = "Solution Finding"
    SPEED = "Speed & Responsiveness"
    EFFICIENCY = "Efficiency"
    COMMUNICATION = "Communication"
    EMPATHY = "Empathy & Rapport"
    CLOSING = "Closing & Next Steps"


SCORE_TIERS = {
    (90, 100): {"tier": "A+", "label": "Elite Closer"},
    (80, 89):  {"tier": "A",  "label": "Strong Performer"},
    (70, 79):  {"tier": "B",  "label": "Solid"},
    (60, 69):  {"tier": "C",  "label": "Needs Improvement"},
    (0, 59):   {"tier": "D",  "label": "Needs Training"},
}

# Groq model for client simulation (fast responses)
GROQ_MODEL = "llama-3.3-70b-versatile"

# Claude model for evaluation (smart scoring)
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"


# ============================================================
# RANDOMIZATION POOLS
# ============================================================

FIRST_NAMES = [
    "Sarah", "David", "Jennifer", "Mike", "Amanda", "Robert", "Karen",
    "James", "Lisa", "Marcus", "Rachel", "Tony", "Priya", "Chris",
    "Nicole", "Daniel", "Maria", "Kevin", "Ashley", "Brian", "Tina",
    "Steven", "Laura", "Jason", "Emily", "Carlos", "Stephanie", "Derek",
    "Angela", "Ryan", "Michelle", "Andre", "Katherine", "Eric", "Diana",
    "Patrick", "Samantha", "Victor", "Heather", "Nathan", "Teresa",
    "Alex", "Vanessa", "Greg", "Christina", "Tyler", "Rebecca", "Omar",
]

LAST_NAMES = [
    "Chen", "Park", "Mitchell", "Torres", "Foster", "Kim", "Wright",
    "Liu", "Johnson", "Patel", "Garcia", "Thompson", "Nakamura", "Lee",
    "Williams", "Rodriguez", "Brown", "Martinez", "Davis", "Wilson",
    "Anderson", "Taylor", "Thomas", "Jackson", "White", "Harris", "Clark",
    "Lewis", "Robinson", "Walker", "Young", "King", "Scott", "Green",
    "Adams", "Baker", "Hall", "Rivera", "Campbell", "Gonzalez", "Murphy",
    "Sharma", "O'Brien", "Reeves", "Hoffman", "Nguyen", "Sullivan",
]

BROKERAGES = [
    "Compass", "Keller Williams", "Coldwell Banker", "Sotheby's International",
    "RE/MAX", "eXp Realty", "Century 21", "Berkshire Hathaway HomeServices",
    "Douglas Elliman", "Redfin", "Side Real Estate", "Engel & Volkers",
    "The Agency", "Corcoran", "Christie's International", "Intero Real Estate",
    "Sereno", "Vanguard Properties", "Pacific Union", "Windermere",
]

PERSONALITIES = [
    "Impatient and direct — wants answers fast, doesn't like small talk",
    "Friendly and chatty — easy to talk to but hard to keep on track",
    "Analytical and detail-oriented — asks a lot of questions, needs data",
    "Skeptical and guarded — been burned before, needs proof not promises",
    "Enthusiastic but indecisive — loves everything but can't commit",
    "Passive-aggressive — says 'it's fine' but clearly isn't happy",
    "Confident and assertive — knows what they want, respects competence",
    "Apologetic and accommodating — doesn't want to be a bother",
    "Price-focused — everything comes back to cost",
    "Relationship-driven — values trust and personal connection over everything",
    "Busy and distracted — keeps cutting you off, checking other things",
    "New to real estate — doesn't know industry terms, needs hand-holding",
]

BAY_AREA_CITIES = [
    "San Francisco", "Oakland", "San Jose", "Palo Alto", "Walnut Creek",
    "Berkeley", "Fremont", "Pleasanton", "Danville", "Saratoga",
    "Los Gatos", "Menlo Park", "Atherton", "Hillsborough", "Tiburon",
    "Mill Valley", "San Mateo", "Burlingame", "Redwood City", "Mountain View",
    "Sunnyvale", "Campbell", "Cupertino", "Livermore", "Dublin",
    "San Ramon", "Lafayette", "Orinda", "Moraga", "Piedmont",
]

PROPERTY_TYPES = [
    "single-family home", "condo", "townhouse", "luxury estate",
    "multi-unit property", "new construction", "fixer-upper",
    "mid-century modern", "Victorian", "contemporary",
]

SQUARE_FOOTAGES = [
    "1,200", "1,500", "1,800", "2,000", "2,200", "2,500", "2,800",
    "3,000", "3,200", "3,500", "3,800", "4,000", "4,500", "5,000",
    "5,500", "6,000", "7,000", "8,000",
]

PRICE_RANGES = [
    "$800K", "$950K", "$1.1M", "$1.3M", "$1.5M", "$1.8M", "$2M",
    "$2.2M", "$2.5M", "$2.8M", "$3M", "$3.5M", "$4M", "$4.5M", "$5M",
]


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class ClientPersona:
    name: str
    company: str
    personality: str
    hidden_goal: str
    pain_points: List[str]
    budget_range: Optional[str] = None
    objections: List[str] = field(default_factory=list)
    deal_breakers: List[str] = field(default_factory=list)
    # Randomized property context
    city: str = ""
    property_type: str = ""
    square_footage: str = ""
    listing_price: str = ""


@dataclass
class Scenario:
    id: str
    title: str
    category: ScenarioCategory
    team_role: TeamRole
    difficulty: Difficulty
    description: str
    client_persona: ClientPersona
    success_criteria: List[str]
    opening_line: str = ""  # what the client says first when the "call" starts
    max_turns: int = 20
    time_limit_seconds: int = 600


@dataclass
class Message:
    role: str  # "client" or "trainee"
    content: str
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class CategoryScore:
    category: ScoreCategory
    score: int
    feedback: str


@dataclass
class ConsultationResult:
    overall_score: int
    tier: str
    tier_label: str
    category_scores: List[CategoryScore]
    strengths: List[str]
    improvements: List[str]
    key_moments: List[str]
    client_satisfaction: int
    deal_outcome: str
    summary: str


@dataclass
class ConsultationSession:
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
    elapsed_seconds: float = 0.0

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

    def end_call(self):
        self.is_complete = True
        self.completed_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# SCENARIO TEMPLATES (used for randomization)
# ============================================================

# Each template defines the structure — randomization fills in the details

PM_SCENARIO_TEMPLATES = [
    {
        "category": ScenarioCategory.QUALITY_COMPLAINT,
        "title_template": "The Angry Reshoot Request",
        "difficulty": Difficulty.HARD,
        "description_template": "{name} from {company} is furious about photo quality from yesterday's shoot at a {sqft} sq ft {property_type} in {city}. They want a full reshoot for free, today.",
        "hidden_goal": "Wants to feel heard more than anything. Would accept a partial reshoot if you acknowledge the issue and give a timeline.",
        "pain_points": ["Photos are too dark", "Listing goes live tomorrow", "Paid premium price", "Seller is already upset"],
        "objections": ["I paid for premium quality", "My clients expect better", "I'll go to your competitor", "This is unacceptable"],
        "deal_breakers": ["Being told it's not a big deal", "Long wait times for resolution", "Being put on hold"],
        "success_criteria": [
            "Acknowledge the issue without being defensive",
            "Ask specific questions about which photos need fixing",
            "Offer a concrete solution with a timeline",
            "Retain the client relationship",
        ],
        "opening_template": "Yeah, hi. This is {name} with {company}. I need to talk to someone about the photos from yesterday. They're terrible. The {property_type} in {city}? The photos are dark, the angles are wrong — I can't use these. My listing goes live tomorrow.",
    },
    {
        "category": ScenarioCategory.SCHEDULING_CONFLICT,
        "title_template": "Double-Booked Shoot Day",
        "difficulty": Difficulty.MEDIUM,
        "description_template": "{name} at {company} has a {sqft} sq ft {property_type} in {city} that needs to be shot tomorrow, but there's a scheduling conflict.",
        "hidden_goal": "Flexible on time but needs to know you prioritize them. Would move to afternoon if asked respectfully.",
        "pain_points": ["Already rescheduled once", "Open house in 3 days", "Seller is getting anxious"],
        "objections": ["I was told this time was confirmed", "My seller is getting anxious", "This can't happen again"],
        "deal_breakers": ["Being made to feel unimportant", "No clear resolution"],
        "success_criteria": [
            "Be transparent about the conflict",
            "Offer alternative times proactively",
            "Make the client feel prioritized",
            "Secure a confirmed new time",
        ],
        "opening_template": "Hey there, it's {name} from {company}. I'm calling about tomorrow's shoot for the {property_type} in {city}. We're still good for the morning slot, right? Because I already told my seller we'd have photos by end of day.",
    },
    {
        "category": ScenarioCategory.SCOPE_CHANGE,
        "title_template": "The Expanding Scope",
        "difficulty": Difficulty.MEDIUM,
        "description_template": "{name} from {company} booked a standard photo package for a {sqft} sq ft {property_type} listed at {price} in {city}, but keeps asking for extras — drone, video, twilight.",
        "hidden_goal": "Would happily pay more if the value is explained clearly. Budget isn't the issue — clarity is.",
        "pain_points": ["Luxury listing needs to look amazing", "Previous photographer did everything in one visit", "Seller expects high-end marketing"],
        "objections": ["My last photographer included all of this", "At this price I expected more", "Why is that extra?"],
        "deal_breakers": ["Making them feel cheap for asking", "Hidden fees"],
        "success_criteria": [
            "Explain what's included vs. add-ons clearly",
            "Position extras as upgrades, not upsells",
            "Get commitment on expanded scope with pricing",
            "Keep the energy positive",
        ],
        "opening_template": "Hi! This is {name} from {company}. I just booked the photo shoot for my listing in {city} — the {sqft} square foot {property_type}, listed at {price}. Quick question — that includes drone shots too, right? And maybe a video walkthrough?",
    },
    {
        "category": ScenarioCategory.RUSH_REQUEST,
        "title_template": "The Last-Minute Rush",
        "difficulty": Difficulty.EASY,
        "description_template": "{name} from {company} needs photos of a {sqft} sq ft {property_type} in {city} edited and delivered by tonight instead of the standard 24-hour turnaround.",
        "hidden_goal": "Willing to pay a rush fee. Just needs to know it's possible.",
        "pain_points": ["Listing appointment tomorrow morning", "Seller is impatient", "Already promised the seller"],
        "objections": ["Is there any way to speed this up?", "I'll pay extra if needed"],
        "deal_breakers": [],
        "success_criteria": [
            "Assess feasibility honestly",
            "Quote rush fee clearly",
            "Set realistic delivery time",
            "Confirm the arrangement",
        ],
        "opening_template": "Hey, this is {name} over at {company}. So I know this is a big ask, but any chance I could get the photos from today's shoot — the {property_type} in {city} — delivered by tonight? I've got a listing presentation first thing tomorrow morning and I really need them.",
    },
    {
        "category": ScenarioCategory.UPSET_CLIENT,
        "title_template": "The Missing Deliverables",
        "difficulty": Difficulty.HARD,
        "description_template": "{name} from {company} was promised a full media package for a {price} {property_type} in {city} and is missing the virtual tour and floor plan 48 hours later.",
        "hidden_goal": "Needs the deliverables ASAP but also wants a discount or credit for the delay. Will stay if you offer both speed and accountability.",
        "pain_points": ["Promised 24-hour delivery", "Seller is asking where the virtual tour is", "Paid for premium package"],
        "objections": ["I was promised 24 hours", "This is the second time this happened", "I need a credit for this"],
        "deal_breakers": ["Blaming the client", "Making excuses without solutions"],
        "success_criteria": [
            "Apologize sincerely without excuses",
            "Provide a specific delivery timeline for remaining items",
            "Offer a meaningful make-good (credit, free add-on)",
            "Follow up proactively",
        ],
        "opening_template": "Hi, {name} here from {company}. I'm calling because I'm still missing the virtual tour and floor plan for the {property_type} in {city}. It's been 48 hours. I paid for the premium package and I was told I'd have everything in 24 hours. My seller is asking me where the virtual tour is and I don't have an answer.",
    },
]

SALES_SCENARIO_TEMPLATES = [
    {
        "category": ScenarioCategory.NEW_CLIENT_INQUIRY,
        "title_template": "The Cold Lead",
        "difficulty": Difficulty.MEDIUM,
        "description_template": "{name} from {company} found your website and wants pricing for a {sqft} sq ft {property_type} in {city}. They're shopping around.",
        "hidden_goal": "Wants the best value, not the cheapest. Will choose quality if you prove ROI and turnaround time.",
        "pain_points": ["Previous photographer was unreliable", "Needs consistent quality", "Shopping 3 providers"],
        "objections": ["Your competitor is cheaper", "I'm comparing options", "Can I try one shoot first?", "What's your turnaround time?"],
        "deal_breakers": ["Being pushy", "Not answering questions directly"],
        "success_criteria": [
            "Ask about their business before quoting price",
            "Understand their volume potential",
            "Position value over price",
            "Get commitment to a trial shoot",
        ],
        "opening_template": "Hi, my name is {name}, I'm an agent with {company}. I found you guys online and I'm looking for a new real estate photographer. I've got a {sqft} square foot {property_type} coming up in {city} and I wanted to get pricing. What do you guys charge?",
    },
    {
        "category": ScenarioCategory.BUDGET_OBJECTION,
        "title_template": "The Price Pushback",
        "difficulty": Difficulty.HARD,
        "description_template": "{name} at {company} does 8 listings a month and loves your quality, but says you're 30% more expensive than their current provider.",
        "hidden_goal": "Already unhappy with current provider's reliability. Would switch for same price or slightly more if turnaround is faster and quality is consistent.",
        "pain_points": ["Current provider misses deadlines", "Inconsistent quality", "No single point of contact"],
        "objections": ["You're 30% more expensive", "I need to see the math", "What if quality isn't better?", "My current guy is fine, just not great"],
        "deal_breakers": ["Arrogance", "Inability to discuss pricing openly", "Talking down about competitors"],
        "success_criteria": [
            "Acknowledge the price difference honestly",
            "Uncover pain points with current provider",
            "Calculate the cost of missed deadlines and reshoots",
            "Offer a volume commitment with adjusted pricing",
            "Close with a specific next step",
        ],
        "opening_template": "Hey, it's {name} with {company}. So I got your pricing back and honestly, I love the portfolio. Your work is great. But you're like 30% more than what I'm paying now. I do about 8 listings a month so that adds up. Is there any flexibility there?",
    },
    {
        "category": ScenarioCategory.UPSELL_OPPORTUNITY,
        "title_template": "The Upgrade Conversation",
        "difficulty": Difficulty.EASY,
        "description_template": "{name} from {company} is an existing photo-only client who just landed a {price} luxury {property_type} in {city} and wants to know about video and drone.",
        "hidden_goal": "Wants to impress the seller and win more luxury listings. Will buy the premium package if you connect it to their business growth.",
        "pain_points": ["First luxury listing", "Wants to stand out", "Seller expects high-end marketing"],
        "objections": ["How much more is video?", "Is drone worth it?", "Will it actually make a difference?"],
        "deal_breakers": [],
        "success_criteria": [
            "Congratulate them on the luxury listing",
            "Connect premium services to their business goals",
            "Present package options (not just one price)",
            "Close with a booking date",
        ],
        "opening_template": "Hey! It's {name} over at {company}. So guess what — I just landed a huge listing. {price} {property_type} in {city}, {sqft} square feet. I want to go all out on this one. You guys do video and drone too, right? What would that look like?",
    },
    {
        "category": ScenarioCategory.COMPETITOR_COMPARISON,
        "title_template": "The Competitor Switch",
        "difficulty": Difficulty.HARD,
        "description_template": "{name} from {company} does 15+ listings a month and is considering leaving their current photographer after a series of problems.",
        "hidden_goal": "Wants a reliable partner, not just a vendor. Will commit to a 3-month trial if you offer a dedicated point of contact and consistent quality.",
        "pain_points": ["Current provider missed 3 shoots last month", "Different photographer every time", "Can't reach anyone when there's a problem"],
        "objections": ["How do I know you won't do the same?", "I need a guarantee", "What happens when you get busy?", "I've heard this before"],
        "deal_breakers": ["Overpromising", "Not listening", "Trash-talking the competitor"],
        "success_criteria": [
            "Listen more than you talk in the first half",
            "Ask about specific pain points — don't assume",
            "Offer proof (case studies, references, trial)",
            "Propose a structured trial with clear expectations",
            "Never trash the competitor",
        ],
        "opening_template": "Yeah hi, this is {name} from {company}. Someone on my team recommended you guys. I'm doing about 15 to 20 listings a month and I'm... honestly just frustrated with my current setup. I'm not even sure what I'm looking for exactly, I just know I need a change.",
    },
    {
        "category": ScenarioCategory.FOLLOW_UP_CLOSE,
        "title_template": "The Follow-Up That Went Cold",
        "difficulty": Difficulty.MEDIUM,
        "description_template": "{name} from {company} inquired 2 weeks ago about services for properties in {city} but never responded to your follow-up email. They're calling back now.",
        "hidden_goal": "Got busy and forgot. Still interested but now also got a quote from a competitor. Needs a reason to choose you today.",
        "pain_points": ["Too busy to respond", "Got a cheaper quote elsewhere", "Needs to make a decision this week"],
        "objections": ["Sorry I ghosted you", "I got another quote that's lower", "I need to decide today actually"],
        "deal_breakers": ["Guilt-tripping about not responding", "Being inflexible"],
        "success_criteria": [
            "Welcome them back warmly — no guilt trip",
            "Re-qualify their needs (may have changed)",
            "Address the competing quote without desperation",
            "Create urgency and close today",
        ],
        "opening_template": "Hey, this is {name} from {company}. I think we talked a couple weeks ago? Sorry I dropped off — things got crazy. Anyway, I've got a few listings coming up in {city} and I need to lock in a photographer like... this week. Are you guys still available?",
    },
]


# ============================================================
# RANDOM SCENARIO GENERATOR
# ============================================================

def generate_random_client() -> Dict:
    """Generate a random client identity."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return {
        "name": f"{first} {last}",
        "company": random.choice(BROKERAGES),
        "city": random.choice(BAY_AREA_CITIES),
        "property_type": random.choice(PROPERTY_TYPES),
        "sqft": random.choice(SQUARE_FOOTAGES),
        "price": random.choice(PRICE_RANGES),
        "personality": random.choice(PERSONALITIES),
    }


def generate_random_scenario(
    team_role: TeamRole,
    difficulty: Optional[Difficulty] = None,
) -> Scenario:
    """Generate a fully randomized scenario with a unique client."""

    # Pick template pool based on role
    if team_role == TeamRole.PROJECT_MANAGER:
        templates = PM_SCENARIO_TEMPLATES
    else:
        templates = SALES_SCENARIO_TEMPLATES

    # Filter by difficulty if specified
    if difficulty:
        filtered = [t for t in templates if t["difficulty"] == difficulty]
        if filtered:
            templates = filtered

    template = random.choice(templates)
    client = generate_random_client()

    # Override personality with template-appropriate one sometimes
    # (50% chance to use a contextually appropriate personality)
    if random.random() > 0.5:
        client["personality"] = random.choice(PERSONALITIES)

    # Build the fill dict
    fill = {
        "name": client["name"],
        "company": client["company"],
        "city": client["city"],
        "property_type": client["property_type"],
        "sqft": client["sqft"],
        "price": client["price"],
    }

    # Generate unique scenario ID
    scenario_id = hashlib.md5(
        f"{client['name']}{datetime.now().isoformat()}{random.random()}".encode()
    ).hexdigest()[:8]

    persona = ClientPersona(
        name=client["name"],
        company=client["company"],
        personality=client["personality"],
        hidden_goal=template["hidden_goal"],
        pain_points=template["pain_points"],
        budget_range=template.get("budget_range"),
        objections=template.get("objections", []),
        deal_breakers=template.get("deal_breakers", []),
        city=client["city"],
        property_type=client["property_type"],
        square_footage=client["sqft"],
        listing_price=client["price"],
    )

    # Build opening line with randomized details
    opening = template.get("opening_template", "")
    try:
        opening = opening.format(**fill)
    except KeyError:
        pass

    return Scenario(
        id=f"random_{scenario_id}",
        title=template["title_template"],
        category=template["category"],
        team_role=team_role,
        difficulty=template["difficulty"] if not difficulty else difficulty,
        description=template["description_template"].format(**fill),
        client_persona=persona,
        success_criteria=template["success_criteria"],
        opening_line=opening,
    )


# ============================================================
# AI PROMPT BUILDERS
# ============================================================

def build_client_system_prompt(scenario: Scenario) -> str:
    """Build the Groq system prompt for the AI playing the client."""
    persona = scenario.client_persona
    return f"""You are playing the role of a real estate client on a phone call. This is a training simulation but you must NEVER break character.

WHO YOU ARE:
- Name: {persona.name}
- Brokerage: {persona.company}
- Personality: {persona.personality}

THE SITUATION:
{scenario.description}

PROPERTY DETAILS:
- Location: {persona.city}
- Type: {persona.property_type}
- Size: {persona.square_footage} sq ft
- List Price: {persona.listing_price}

YOUR HIDDEN GOAL (never reveal this directly — the trainee must figure it out):
{persona.hidden_goal}

YOUR PAIN POINTS (bring these up naturally):
{chr(10).join(f'- {p}' for p in persona.pain_points)}

YOUR OBJECTIONS (use when appropriate, don't dump them all at once):
{chr(10).join(f'- {o}' for o in persona.objections)}

{f"THINGS THAT WILL MAKE YOU ANGRY (deal breakers):" + chr(10) + chr(10).join(f'- {d}' for d in persona.deal_breakers) if persona.deal_breakers else ""}

HOW TO BEHAVE:
1. You initiated this call. You're a real person, not a robot.
2. Talk like a real person on a phone call — casual, natural, with filler words sometimes
3. Keep responses to 2-4 sentences usually. This is a conversation, not a monologue.
4. If the trainee does a good job (asks smart questions, shows empathy), warm up gradually
5. If the trainee does a bad job (pushy, dismissive, robotic), get more difficult
6. Use your objections naturally — don't frontload them all
7. If they uncover your hidden goal, start moving toward resolution
8. You can end the call if things go really well ("Alright, let's do it") or really badly ("You know what, I think I'll call someone else")
9. NEVER say you are AI. NEVER break character. NEVER reference this being a simulation.
10. Difficulty: {scenario.difficulty.value} — {"be tough but fair" if scenario.difficulty == Difficulty.HARD else "be reasonable" if scenario.difficulty == Difficulty.MEDIUM else "be fairly easy to work with"}
"""


def build_evaluator_prompt(scenario: Scenario, messages: List[Message], elapsed_seconds: float) -> str:
    """Build the Claude evaluation prompt for scoring the conversation."""

    # Format the conversation transcript
    transcript_lines = []
    for msg in messages:
        speaker = scenario.client_persona.name if msg.role == "client" else "TRAINEE"
        transcript_lines.append(f"[{speaker}]: {msg.content}")
    transcript = "\n\n".join(transcript_lines)

    minutes = elapsed_seconds / 60

    return f"""You are an expert consultation trainer at a real estate marketing company called Aerial Canvas. You are evaluating a training call simulation.

SCENARIO: {scenario.title}
- Category: {scenario.category.value}
- Team Role: {scenario.team_role.value}
- Difficulty: {scenario.difficulty.value}
- Description: {scenario.description}

CLIENT PROFILE:
- Name: {scenario.client_persona.name}
- Brokerage: {scenario.client_persona.company}
- Personality: {scenario.client_persona.personality}
- Property: {scenario.client_persona.square_footage} sq ft {scenario.client_persona.property_type} in {scenario.client_persona.city}

CLIENT'S HIDDEN GOAL (trainee needed to uncover this):
{scenario.client_persona.hidden_goal}

SUCCESS CRITERIA:
{chr(10).join(f'- {c}' for c in scenario.success_criteria)}

CALL DURATION: {minutes:.1f} minutes
TOTAL EXCHANGES: {len(messages)} messages

--- FULL TRANSCRIPT ---

{transcript}

--- END TRANSCRIPT ---

Evaluate the trainee's performance. Be specific — reference actual quotes from the conversation.
Score relative to difficulty level. A perfect score on Hard should be truly exceptional.

Return a JSON object with this EXACT structure (no markdown, just raw JSON):
{{
    "overall_score": <0-100>,
    "category_scores": [
        {{"category": "Solution Finding", "score": <0-100>, "feedback": "<2-3 sentences referencing specific moments>"}},
        {{"category": "Speed & Responsiveness", "score": <0-100>, "feedback": "<2-3 sentences>"}},
        {{"category": "Efficiency", "score": <0-100>, "feedback": "<2-3 sentences>"}},
        {{"category": "Communication", "score": <0-100>, "feedback": "<2-3 sentences>"}},
        {{"category": "Empathy & Rapport", "score": <0-100>, "feedback": "<2-3 sentences>"}},
        {{"category": "Closing & Next Steps", "score": <0-100>, "feedback": "<2-3 sentences>"}}
    ],
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "improvements": ["<improvement 1>", "<improvement 2>", "<improvement 3>"],
    "key_moments": ["<describe a specific good or bad moment from the call>", "<another moment>"],
    "client_satisfaction": <0-100>,
    "deal_outcome": "<closed | lost | follow-up needed>",
    "summary": "<3-4 sentence overall assessment of the trainee's performance>"
}}"""


def build_conversation_for_groq(session: ConsultationSession) -> List[Dict]:
    """Convert session messages to Groq API format."""
    messages = [
        {"role": "system", "content": build_client_system_prompt(session.scenario)}
    ]
    for msg in session.messages:
        if msg.role == "client":
            messages.append({"role": "assistant", "content": msg.content})
        else:
            messages.append({"role": "user", "content": msg.content})
    return messages


# ============================================================
# GROQ CLIENT ENGINE
# ============================================================

class GroqClient:
    """Handles communication with Groq API for client simulation."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def get_client_response(self, session: ConsultationSession) -> str:
        """Get the next client response from Groq."""
        import requests

        messages = build_conversation_for_groq(session)

        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 300,
            },
            timeout=10,
        )

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.status_code} — {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def get_opening_line(self, scenario: Scenario) -> str:
        """Get the client's opening line — uses the pre-written one or generates one."""
        if scenario.opening_line:
            return scenario.opening_line

        # Fallback: generate with Groq
        import requests
        messages = [
            {"role": "system", "content": build_client_system_prompt(scenario)},
            {"role": "user", "content": "[The phone is ringing. You are the client. You initiated this call. Say your opening line.]"},
        ]

        response = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 200,
            },
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Hi, this is {scenario.client_persona.name} from {scenario.client_persona.company}. Do you have a minute?"


# ============================================================
# CLAUDE EVALUATOR ENGINE
# ============================================================

class ClaudeEvaluator:
    """Handles conversation evaluation via Claude API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def evaluate_session(self, session: ConsultationSession) -> ConsultationResult:
        """Send the full conversation to Claude for scoring."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        eval_prompt = build_evaluator_prompt(
            session.scenario,
            session.messages,
            session.elapsed_seconds,
        )

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": eval_prompt}],
        )

        response_text = response.content[0].text
        return parse_evaluation_response(response_text, session.scenario)


# ============================================================
# MAIN CONSULTATION ENGINE
# ============================================================

class ConsultationEngine:
    """Main engine that orchestrates the full consultation flow."""

    def __init__(self, groq_api_key: str, anthropic_api_key: str):
        self.groq = GroqClient(groq_api_key)
        self.evaluator = ClaudeEvaluator(anthropic_api_key)

    def start_session(
        self,
        user_email: str,
        user_name: str,
        team_role: TeamRole,
        difficulty: Optional[Difficulty] = None,
    ) -> ConsultationSession:
        """Start a new consultation training session with a random scenario."""
        scenario = generate_random_scenario(team_role, difficulty)

        session_id = hashlib.md5(
            f"{user_email}{datetime.now().isoformat()}{random.random()}".encode()
        ).hexdigest()[:12]

        session = ConsultationSession(
            session_id=session_id,
            user_email=user_email,
            user_name=user_name,
            team_role=team_role,
            scenario=scenario,
        )

        # Get client's opening line
        opening = self.groq.get_opening_line(scenario)
        session.add_message("client", opening)

        return session

    def send_response(self, session: ConsultationSession, trainee_message: str) -> str:
        """Send trainee's response and get the client's reply."""
        if session.is_complete:
            raise ValueError("Session is already complete")

        # Add trainee message
        session.add_message("trainee", trainee_message)

        # Check turn limit
        if session.is_over_limit():
            session.end_call()
            return "[Call ended — turn limit reached]"

        # Get client response from Groq
        client_response = self.groq.get_client_response(session)
        session.add_message("client", client_response)

        return client_response

    def end_and_evaluate(self, session: ConsultationSession) -> ConsultationResult:
        """End the call and get Claude's evaluation."""
        session.end_call()
        result = self.evaluator.evaluate_session(session)
        session.result = result
        return result


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
    """Parse Claude's JSON evaluation into a ConsultationResult."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(.*?)```', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Try to find raw JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                data = json.loads(json_match.group(0))
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
