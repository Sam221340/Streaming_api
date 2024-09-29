from django.contrib import admin
from user.models import *

# Register your models here.
admin.site.register(User)
# admin.site.register(Blog)
admin.site.register(Roles)

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(MatchHighlight)
# admin.site.register(HighlightLike)
