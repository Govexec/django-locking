# encoding: utf-8

from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType

from locking.models import Lock
from locking import settings as _s


class LockableAdmin(admin.ModelAdmin):

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js',
            _s.STATIC_URL + 'locking/js/jquery.url.packed.js',
            _s.ADMIN_URL + "ajax/variables.js",
            _s.STATIC_URL + "locking/js/admin.locking.js?v=1"
        )
        css = {"all": (_s.STATIC_URL + 'locking/css/locking.css',)}

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super(LockableAdmin, self).get_form(request, obj, *args, **kwargs)
        form.request = request
        form.obj = obj
        return form

    def changelist_view(self, request, extra_context=None):
        # we need the request objects in a few places where it's usually not present,
        # so we're tacking it on to the LockableAdmin class
        self.request = request
        return super(LockableAdmin, self).changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change, *args, **kwargs):

        super(LockableAdmin, self).save_model(request, obj, form, change, *args, **kwargs)

        try:
            # object creation doesn't need/have locking in place
            content_type = ContentType.objects.get_for_model(obj)
            obj = Lock.objects.get(entry_id=obj.id,
                                   app=content_type.app_label,
                                   model=content_type.model)
            obj.unlock_for(request.user)
            obj.save()
        except:
            pass

    def get_lock_for_admin(self_obj, obj):
        '''
        returns the locking status along with a nice icon for the admin
        interface use in admin list display like so:
        list_display = ['title', 'get_lock_for_admin']
        '''

        locked_by = ''
        multi_lock = ''
        output = str(obj.id)
        content_type = ContentType.objects.get_for_model(obj)

        try:
            lock = Lock.objects.get(entry_id=obj.id,
                                    app=content_type.app_label,
                                    model=content_type.model)
            locked_by = lock.locked_by.username
        except Lock.MultipleObjectsReturned:
            locks = Lock.objects.filter(entry_id=obj.id,
                                        app=content_type.app_label,
                                        model=content_type.model).order_by('-_locked_at')
            lock = locks[0]
            locked_by = locks[0].locked_by.username
            for username in set(lock.locked_by.username for lock in locks) - set([locked_by]):
                multi_lock += '<div>%s</div>' % username
        except Lock.DoesNotExist:
            return ''

        if lock.is_locked:
            seconds_remaining = lock.lock_seconds_remaining
            minutes_remaining = seconds_remaining / 60
            locked_until = _("Still locked for %s more minute(s) by %s.") \
                % (minutes_remaining, lock.locked_by)
            if self_obj.request.user == lock.locked_by:
                locked_until_self = _(
                    "You have a lock on this content for %s more minute(s)."
                ) % (minutes_remaining)
                locked_until = '''
                    <img src="%slocking/img/page_edit.png"
                    title="%s" />''' % (_s.STATIC_URL, locked_until_self)
            else:
                locked_until_self = _(
                    "Still locked for %s more minute(s) by %s."
                ) % (minutes_remaining, lock.locked_by)
                locked_until = '''
                    <img src="%slocking/img/lock.png" title="%s" />'''\
                    % (_s.STATIC_URL, locked_until)
            full_name = "%s %s" % (
                lock.locked_by.first_name, lock.locked_by.last_name)
            return u'''<a href="#" id=%s class="lock-status locked" title="Locked By: %s">%s%s</a>%s''' % (output, full_name, locked_until, " " + locked_by, multi_lock)
        else:
            return ''

    get_lock_for_admin.allow_tags = True
    get_lock_for_admin.short_description = 'Lock'
