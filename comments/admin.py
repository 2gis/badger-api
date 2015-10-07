from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _, ungettext

from comments.models import Comment


class UsernameSearch(object):
    """The User object may not be auth.User, so we need to provide
    a mechanism for issuing the equivalent of a .filter(user__username=...)
    search in CommentAdmin.
    """
    def __str__(self):
        return 'user__%s' % get_user_model().USERNAME_FIELD


class CommentsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('content_type', 'object_pk')}),
        (_('Content'), {'fields': ('user', 'comment')}),
        (_('Metadata'), {'fields': ('submit_date',)}),
    )

    list_display = ('content_type', 'object_pk')
    list_filter = ('submit_date',)
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    raw_id_fields = ('user',)
    search_fields = ('comment', UsernameSearch())

    def _bulk_flag(self, request, queryset, action, done_message):
        """
        Flag, approve, or remove some comments from an admin action. Actually
        calls the `action` argument to perform the heavy lifting.
        """
        n_comments = 0
        for comment in queryset:
            action(request, comment)
            n_comments += 1

        msg = ungettext('1 comment was successfully {action}.',
                        '{count} comments were successfully {action}.',
                        n_comments)
        self.message_user(request, msg.format({
            'count': n_comments, 'action': done_message(n_comments)}))

admin.site.register(Comment, CommentsAdmin)
