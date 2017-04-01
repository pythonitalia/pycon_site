# -*- coding: UTF-8 -*-
from django import forms
from django import http
from django.conf import settings
from django.conf.urls import url, patterns
from django.contrib import admin
from django.core import urlresolvers
from assopy import admin as aadmin
from assopy import models as amodels
from conference import admin as cadmin
from conference import models as cmodels
from conference import dataaccess as cdata
from conference import settings as csettings
from p3 import models
from p3 import dataaccess
from p3 import forms as pforms
# Add support for translations for some form or admin fields
from django.utils.translation import ugettext as _

_TICKET_CONFERENCE_COPY_FIELDS = ('shirt_size', 'python_experience', 'diet', 'tagline', 'days', 'badge_image')
def ticketConferenceForm():
    class _(forms.ModelForm):
        class Meta:
            model = models.TicketConference
    fields = _().fields

    class TicketConferenceForm(forms.ModelForm):
        shirt_size = fields['shirt_size']
        python_experience = fields['python_experience']
        diet = fields['diet']
        tagline = fields['tagline']
        days = fields['days']
        badge_image = fields['badge_image']

        class Meta:
            model = cmodels.Ticket

        def __init__(self, *args, **kw):
            if 'instance' in kw:
                o = kw['instance']

                try:
                    p3c = o.p3_conference
                except models.TicketConference.DoesNotExist:
                    p3c = None

                if p3c:
                    initial = kw.pop('initial', {})
                    for k in _TICKET_CONFERENCE_COPY_FIELDS:
                        initial[k] = getattr(p3c, k)
                    kw['initial'] = initial
            return super(TicketConferenceForm, self).__init__(*args, **kw)

    return TicketConferenceForm

class TicketConferenceAdmin(cadmin.TicketAdmin):
    list_display = cadmin.TicketAdmin.list_display + ('_order', '_assigned', '_tagline',)
    list_filter = cadmin.TicketAdmin.list_filter + ('orderitem__order___complete',)

    form = ticketConferenceForm()

    class Media:
        js = ('p5/j/jquery-flot/jquery.flot.js',)

    def _order(self, o):
        return o.orderitem.order.code

    def _assigned(self, o):
        if o.p3_conference:
            return o.p3_conference.assigned_to
        else:
            return ''

    def _tagline(self, o):
        try:
            p3c = o.p3_conference
        except models.TicketConference.DoesNotExist:
            return ''
        html = p3c.tagline
        if p3c.badge_image:
            i = ['<img src="%s" width="24" />' % p3c.badge_image.url] * p3c.python_experience
            html += '<br />' + ' '.join(i)
        return html
    _tagline.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.save()
        p3c = obj.p3_conference
        if p3c is None:
            p3c = models.TicketConference(ticket=obj)

        data = form.cleaned_data
        for k in _TICKET_CONFERENCE_COPY_FIELDS:
            setattr(p3c, k, data.get(k))
        p3c.save()

    def changelist_view(self, request, extra_context=None):
        if not request.GET:
            q = request.GET.copy()
            q['fare__conference'] = settings.CONFERENCE_CONFERENCE
            q['fare__ticket_type__exact'] = 'conference'
            q['orderitem__order___complete__exact'] = 1
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(TicketConferenceAdmin,self).changelist_view(request, extra_context=extra_context)

    def queryset(self, request):
        qs = super(TicketConferenceAdmin, self).queryset(request)
        qs = qs.select_related('orderitem__order', 'p3_conference', 'user', 'fare', )
        return qs

    def get_urls(self):
        urls = super(TicketConferenceAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^stats/data/$', self.admin_site.admin_view(self.stats_data), name='p3-ticket-stats-data'),
        )
        return my_urls + urls

    def stats_data(self, request):
        from conference.views import json_dumps
        from django.db.models import Q
        from collections import defaultdict
        from microblog.models import PostContent
        import datetime

        conferences = cmodels.Conference.objects\
            .exclude(code__startswith='ep')\
            .order_by('conference_start')

        output = {}
        for c in conferences:
            tickets = cmodels.Ticket.objects\
                .filter(fare__conference=c)\
                .filter(Q(orderitem__order___complete=True) | Q(orderitem__order__method__in=('bank', 'admin')))\
                .select_related('fare', 'orderitem__order')
            data = {
                'conference': defaultdict(lambda: 0),
                'partner': defaultdict(lambda: 0),
                'event': defaultdict(lambda: 0),
                'other': defaultdict(lambda: 0),
            }
            for t in tickets:
                tt = t.fare.ticket_type
                date = t.orderitem.order.created.date()
                offset = date - c.conference_start
                data[tt][offset.days] += 1

            for k, v in data.items():
                data[k] = sorted(v.items())


            dlimit = datetime.date(c.conference_start.year, 1, 1)
            deadlines = cmodels.DeadlineContent.objects\
                .filter(language='en')\
                .filter(deadline__date__lte=c.conference_start, deadline__date__gte=dlimit)\
                .select_related('deadline')\
                .order_by('deadline__date')
            markers = [ ((d.deadline.date - c.conference_start).days, 'CAL: ' + (d.headline or d.body)) for d in deadlines ]

            posts = PostContent.objects\
                .filter(language='en')\
                .filter(post__date__lte=c.conference_start, post__date__gte=dlimit)\
                .filter(post__status='P')\
                .select_related('post')\
                .order_by('post__date')
            markers += [ ((d.post.date.date() - c.conference_start).days, 'BLOG: ' + d.headline) for d in posts ]

            output[c.code] = {
                'data': data,
                'markers': markers,
            }

        return http.HttpResponse(json_dumps(output), 'text/javascript')

admin.site.unregister(cmodels.Ticket)
admin.site.register(cmodels.Ticket, TicketConferenceAdmin)

class SpeakerAdmin(cadmin.SpeakerAdmin):
    def queryset(self, request):
        # XXX: waiting to upgrade to django 1.4, I'm implementing
        # this bad hack filter to keep only speakers of current conference.
        qs = super(SpeakerAdmin, self).queryset(request)
        qs = qs.filter(user__in=(
            cmodels.TalkSpeaker.objects\
                .filter(talk__conference=settings.CONFERENCE_CONFERENCE)\
                .values('speaker')
        ))
        return qs
    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        sids = queryset.values_list('user', flat=True)
        profiles = dataaccess.profiles_data(sids)
        self._profiles = dict(zip(sids, profiles))
        return super(SpeakerAdmin, self).get_paginator(request, queryset, per_page, orphans, allow_empty_first_page)

    def _avatar(self, o):
        return '<img src="%s" height="32" />' % (self._profiles[o.user_id]['image'],)
    _avatar.allow_tags = True

admin.site.unregister(cmodels.Speaker)
admin.site.register(cmodels.Speaker, SpeakerAdmin)

from conference import forms as cforms

class TalkConferenceAdminForm(cadmin.TalkAdminForm):
    def __init__(self, *args, **kwargs):
        super(TalkConferenceAdminForm, self).__init__(*args, **kwargs)
        self.fields['tags'].required = False

class TalkConferenceAdmin(cadmin.TalkAdmin):
    multilingual_widget = cforms.MarkEditWidget
    form = TalkConferenceAdminForm

admin.site.unregister(cmodels.Talk)
admin.site.register(cmodels.Talk, TalkConferenceAdmin)

class DonationAdmin(admin.ModelAdmin):
    list_display = ('_name', 'date', 'amount')
    list_select_related = True
    search_fields = ('user__user__first_name', 'user__user__last_name', 'user__user__email')
    date_hierarchy = 'date'

    def _name(self, o):
        return o.user.name()
    _name.short_description = 'name'
    _name.admin_order_field = 'user__user__first_name'

admin.site.register(models.Donation, DonationAdmin)

class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('conference', 'booking_start', 'booking_end', 'minimum_night')

admin.site.register(models.HotelBooking, HotelBookingAdmin)

class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ('_conference', 'room_type', 'quantity', 'amount',)
    list_editable = ('quantity', 'amount',)
    list_filter = ('booking__conference',)
    list_select_related = True

    def _conference(self, o):
        return o.booking.conference_id

    def get_urls(self):
        urls = super(HotelRoomAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^tickets/$', self.admin_site.admin_view(self.ticket_list), name='p3-hotelrooms-tickets-data'),
        )
        return my_urls + urls

    def ticket_list(self, request):
        from conference.views import json_dumps
        day_ix = int(request.GET['day'])
        room_type = request.GET['type']
        rdays = models.TicketRoom.objects.reserved_days()
        day = rdays[day_ix]

        qs = models.TicketRoom.objects.valid_tickets()\
            .filter(room_type__room_type=room_type, checkin__lte=day, checkout__gte=day)\
            .select_related('ticket__user', 'ticket__orderitem__order')\
            .order_by('ticket__orderitem__order__created')

        output = []
        for row in qs:
            user = row.ticket.user
            order = row.ticket.orderitem.order
            name = u'{0} {1}'.format(user.first_name, user.last_name)
            if row.ticket.name and row.ticket.name != name:
                name = u'{0} ({1})'.format(row.ticket.name, name)
            output.append({
                'user': {
                    'id': user.id,
                    'name': name,
                },
                'order': {
                    'id': order.id,
                    'code': order.code,
                    'method': order.method,
                    'complete': order._complete,
                },
                'period': (row.checkin, row.checkout, row.checkout == day),
            })
        return http.HttpResponse(json_dumps(output), 'text/javascript')

admin.site.register(models.HotelRoom, HotelRoomAdmin)

class TicketRoomAdmin(admin.ModelAdmin):
    list_display = ('_user', '_room_type', 'ticket_type', 'checkin', 'checkout', '_order_code', '_order_date', '_order_confirmed')
    list_select_related = True
    search_fields = ('ticket__user__first_name', 'ticket__user__last_name', 'ticket__user__email', 'ticket__orderitem__order__code')
    raw_id_fields = ('ticket', )
    list_filter = ('room_type__room_type',)

    def _user(self, o):
        return o.ticket.user

    def _room_type(self, o):
        return o.room_type.get_room_type_display()

    def _order_code(self, o):
        return o.ticket.orderitem.order.code

    def _order_date(self, o):
        return o.ticket.orderitem.order.created

    def _order_confirmed(self, o):
        return o.ticket.orderitem.order._complete
    _order_confirmed.boolean = True

admin.site.register(models.TicketRoom, TicketRoomAdmin)

# Admin Manager for P3Talk Class

class P3TalkAdminForm(forms.ModelForm):
    class Meta:
        model = models.P3Talk
        fields = ['sub_community']

    # talk_url = forms.URLField(_('Talk'), required=False)
    talk_url = forms.ModelChoiceField(required=False, queryset=cmodels.Talk.objects.filter(
                                                        conference=settings.CONFERENCE_CONFERENCE))

    def __init__(self, *args, **kwargs):
        super(P3TalkAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['talk_url'].widget = pforms.HTMLAnchorWidget(title=self.instance.talk.title)
            self.fields['talk_url'].initial = str(urlresolvers.reverse('admin:conference_talk_change',
                                                                   args=(self.instance.talk.pk,)))



class P3TalkAdmin(admin.ModelAdmin):
    list_display = ('_title', '_conference', '_duration',
                    'sub_community', '_speakers',
                    '_status', '_slides', '_video')
    list_filter = ('talk__conference', 'talk__status', 'sub_community')
    ordering = ('-talk__conference', 'talk__title')
    search_fields = ('talk__title',)
    form = P3TalkAdminForm

    def _title(self, obj):
        return obj.talk.title
    _title.short_description = 'Talk Title'
    _title.admin_order_field = 'talk__title'

    def _conference(self, obj):
        return obj.talk.conference
    _conference.short_description = 'Conference'
    _conference.admin_order_field = 'talk__conference'

    def _duration(self, obj):
        return obj.talk.duration
    _duration.short_description = 'Duration'
    _duration.admin_order_field = 'talk__duration'

    def _status(self, obj):
        return obj.talk.status
    _status.short_description = 'Status'
    _status.admin_order_field = 'talk__conference'

    def _slides(self, obj):
        return bool(obj.talk.slides)
    _slides.boolean = True

    def _video(self, obj):
        return bool(obj.talk.video_type) and \
               (bool(obj.talk.video_url) or
                bool(obj.talk.video_file))
    _video.boolean = True

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        # Cloned
        # from conference.admin.TalkAdmin
        talks = cdata.talks_data(queryset.values_list('talk__id', flat=True))
        self.cached_talks = dict([(x['id'], x) for x in talks])
        sids = [s['id'] for t in talks for s in t['speakers']]
        profiles = cdata.profiles_data(sids)
        self.cached_profiles = dict([(x['id'], x) for x in profiles])
        return super(P3TalkAdmin, self).get_paginator(request, queryset, per_page,
                                                      orphans, allow_empty_first_page)

    def changelist_view(self, request, extra_context=None):
        """
        Cloned (and adapted) from conference.admin.TalkAdmin
        """
        if not request.GET.has_key('conference') and not request.GET.has_key('conference__exact'):
            q = request.GET.copy()
            q['talk__conference'] = csettings.CONFERENCE
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(P3TalkAdmin, self).changelist_view(request, extra_context=extra_context)

    def _speakers(self, obj):
        # Slightly adapted from conference.admin.TalkAdmin
        # (basically the same method!)
        # We may consider to remove this method from this model Admin
        # or some Refactoring is needed to remove this useless duplication
        data = self.cached_talks.get(obj.talk.id)
        output = []
        for x in data['speakers']:
            args = {
                'url': urlresolvers.reverse('admin:conference_speaker_change', args=(x['id'],)),
                'name': x['name'],
                'mail': self.cached_profiles[x['id']]['email'],
            }
            output.append(
                '<a href="%(url)s">%(name)s</a> (<a href="mailto:%(mail)s">mail</a>)' % args)
        return '<br />'.join(output)

    _speakers.allow_tags = True

admin.site.register(models.P3Talk, P3TalkAdmin)

class InvoiceAdmin(aadmin.InvoiceAdmin):
    """
    Specializzazione per gestire il download delle fatture generate con genro
    """

    def _invoice(self, i):
        if i.assopy_id:
            fake = not i.payment_date
            view = urlresolvers.reverse('genro-legacy-invoice', kwargs={'assopy_id': i.assopy_id})
            return '<a href="%s">View</a> %s' % (view, '[Not payed]' if fake else '')
        else:
            return super(InvoiceAdmin, self)._invoice(i)
    _invoice.allow_tags = True
    _invoice.short_description = 'Download'

admin.site.unregister(amodels.Invoice)
admin.site.register(amodels.Invoice, InvoiceAdmin)
