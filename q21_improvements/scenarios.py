# Area: Q21 Eval Pipeline
# PRD: q21_improvements/improvement_plan.md
"""
Ground-truth game scenarios for offline simulation.
All opening sentences are authentic verbatim Hebrew strings sourced directly 
from the Q21G League course booklet via PyMuPDF extraction.
"""

SCENARIO_1 = {
    "name": "The Non-Arbitrary Line Limit",
    "book_name": "Q21G League Final Project",
    "book_hint": "A coding constraint whose precise threshold mirrors psychological research on human attention span boundaries",
    "association_word": "memory",
    "actual_association_word": "chunk",
    "opening_sentence": "מגבלת150שורות לקובץ היא לא מספר שרירותי.",
    "warmup_answer": "7",
}

SCENARIO_2 = {
    "name": "Prompt Engineering Principles",
    "book_name": "Q21G League Final Project",
    "book_hint": "A systemic method involving three core principles: atomicity, scientific comparison, and structured formatting.",
    "association_word": "rules",
    "actual_association_word": "atom",
    "opening_sentence": "פרק זה הציג שיטה מערכתית לתכנון פרומפטים. שלושה עקרונות מרכזיים:",
    "warmup_answer": "7",
}

SCENARIO_3 = {
    "name": "Gmail API Constraints",
    "book_name": "Q21G League Final Project",
    "book_hint": "Constraints on the free tier of the async transport layer, capping daily message volume to prevent abuse.",
    "association_word": "limits",
    "actual_association_word": "quota",
    "opening_sentence": "חשוב להכיר את מגבלותGmail APIלפני המימוש: חשבון חינמי מוגבל ל-",
    "warmup_answer": "7",
}

SCENARIO_4 = {
    "name": "Agent Interaction Patterns",
    "book_name": "Q21G League Final Project",
    "book_hint": "A flow diagram or section outlining how distinct entities — League Manager, Log Server, Referee, and Players — communicate.",
    "association_word": "diagram",
    "actual_association_word": "audit",
    "opening_sentence": "איור5מציג את התקשורת בין הסוכנים.",
    "warmup_answer": "7",
}

SCENARIO_5 = {
    "name": "Model Context Protocol",
    "book_name": "AI Agents with Model Context Protocol",
    "book_hint": "A standard communication protocol developed by Anthropic to create a uniform interface between AI agents and external tools.",
    "association_word": "standard",
    "actual_association_word": "interface",
    "opening_sentence": "MCPהוא פרוטוקול תקשורת שפותח על ידיAnthropicבמטרה ליצור ממשק אחיד בין",
    "warmup_answer": "7",
}

ALL_SCENARIOS = [SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4, SCENARIO_5]
