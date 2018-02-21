"""State machine for email address status.

All users start with email_status of UNINITIALIZED and update_freq of 'never'.
If user changes update freq to daily or weekly, or changes email address,
a confirmation email is sent out and status changes to WAIT_FOR_CONF.

WAIT_FOR_CONF: if a bounce message is received, goes to BOUNCED.  In fact,
any time a BOUNCE message is received, status goes to BOUNCED.  If no conf
email is received, stays in WAIT_FOR_CONF because there is nothing to move
it to the next state.  If conf email comes back but is too late, goes to
CONF_TIMED_OUT.

CONFIRMED_GOOD: if conf email comes back within the time window, then we
enter this state.  If in this state, user can receive update emails.

If user blanks out email field, goes back to UNINITIALIZED.

If user changes email field, goes to WAIT_FOR_CONF (and sends out conf email).

Changes to update freq does not affect email_status, except when the
email_status is UNINITIALIZED, update_freq is never, and email is not blank.
"""

from enum import Enum


class EmailStatus(Enum):
    UNINITIALIZED = 1
    WAIT_FOR_CONF = 2
    CONFIRMED_GOOD = 3
    CONF_TIMED_OUT = 4
    BOUNCED = 5
