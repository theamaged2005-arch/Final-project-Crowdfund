import difflib
import re

from .models import FAQ

FALLBACK_ANSWER = (
    "Sorry, I'm not sure about that. You can browse projects from the homepage, "
    "or contact the project creator directly from the project page. "
    "Try asking me about registering, donating, creating a project, or comments."
)


def _tokenize(text):
    return set(re.findall(r'\w+', text.lower()))


def get_answer(user_message):
    """Very small offline 'AI' agent: scores every active FAQ against the
    user's message using keyword overlap + fuzzy text similarity, and
    returns the best match (or a fallback if nothing scores well enough).
    """
    user_tokens = _tokenize(user_message)
    if not user_tokens:
        return FALLBACK_ANSWER

    best_score = 0.0
    best_faq = None

    for faq in FAQ.objects.filter(is_active=True):
        score = 0.0

        # 1) keyword overlap - strongest signal
        for kw in faq.keyword_list():
            kw_tokens = _tokenize(kw)
            if kw_tokens and kw_tokens.issubset(user_tokens):
                score += 2.0
            elif kw in user_message.lower():
                score += 1.5

        # 2) fuzzy similarity against the question itself - catches typos/rephrasing
        similarity = difflib.SequenceMatcher(None, user_message.lower(), faq.question.lower()).ratio()
        score += similarity

        if score > best_score:
            best_score = score
            best_faq = faq

    if best_faq and best_score >= 1.0:
        return best_faq.answer
    return FALLBACK_ANSWER