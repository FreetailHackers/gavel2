ANNOTATOR_ID = "annotator_id"
TELEMETRY_URL = ""

# Socket events
CONNECT = "connected"

ANNOTATOR_INSERTED = "annotator.inserted"
ANNOTATOR_UPDATED = "annotator.updated"
ANNOTATOR_DELETED = "annotator.deleted"

ITEM_INSERTED = "item.inserted"
ITEM_UPDATED = "item.updated"
ITEM_DELETED = "item.deleted"

FLAG_INSERTED = "flag.inserted"
FLAG_UPDATED = "flag.updated"
FLAG_DELETED = "flag.deleted"

SETTING_INSERTED = "setting.inserted"
SETTING_UPDATED = "setting.updated"
SETTING_DELETED = "setting.deleted"

SESSION_UPDATED = "session.updated"

# Setting
# keys
SETTING_CLOSED = "closed"  # boolean
SETTING_STOP_QUEUE = "queued"  # boolean
# values
SETTING_TRUE = "true"
SETTING_FALSE = "false"

# Defaults
# these can be overridden via the config file
DEFAULT_WELCOME_MESSAGE = """
Welcome to Gavel.

**Please read this important message carefully before continuing.**

Gavel is a fully automated expo judging system that both tells you where to go
and collects your votes.

The system is based on the model of pairwise comparison. You'll start off by
looking at a single submission, and then for every submission after that,
you'll decide whether it's better or worse than the one you looked at
**immediately beforehand**.

If at any point, you can't find a particular submission, you can click the
'Skip' button and you will be assigned a new project. **Please don't skip
unless absolutely necessary.**

Gavel makes it really simple for you to submit votes, but please think hard
before you vote. **Once you make a decision, you can't take it back**.
""".strip()

DEFAULT_EMAIL_SUBJECT = "Welcome to Gavel!"

DEFAULT_EMAIL_BODY = """
Hi {name},

Welcome to Gavel, the online expo judging system. This email contains your
magic link to the judging system.

DO NOT SHARE this email with others, as it contains your personal magic link.

To access the system, visit {link}.

Once you're in, please take the time to read the welcome message and
instructions before continuing.
""".strip()

DEFAULT_CLOSED_MESSAGE = """
Gavel judging is currently closed. If judging is still happening in person, try refreshing the page.
""".strip()

DEFAULT_CLOSING_MESSAGE = """
Gavel judging is in the process of shutting down. Please wait.
""".strip()

DEFAULT_DISABLED_MESSAGE = """
Your account is currently disabled. Reload the page to try again.
""".strip()

DEFAULT_LOGGED_OUT_MESSAGE = """
You are currently logged out. Open your magic link to get started.
""".strip()

DEFAULT_WAIT_MESSAGE = """
Wow, you've visited all the projects presented in this expo. Thank you so much for your effort. From this point, follow any post-expo instructions event staff have provided for judges.
""".strip()
