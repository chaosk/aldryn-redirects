from django.utils.translation import ugettext_lazy as _


PERMANENT = 301
TEMPORARY = 302

REDIRECT_TYPES = (
    (PERMANENT, _('Permanent (301)')),
    (TEMPORARY, _('Temporary (302)')),
)
