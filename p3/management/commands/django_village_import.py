# -*- coding: UTF-8 -*-
import csv
import random
from conference import models as cmodels
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from p3 import models as pmodels


class Command(BaseCommand):
    """
    """

    def handle(self, *args, **options):
        try:
            fname = args[0]
        except IndexError:
            raise CommandError("csv file not specified")

        with file(fname) as f:
            with transaction.commit_on_success():
                self.insert_data(csv.DictReader(f))

    def insert_data(self, reader):
        for line in reader:
            line["first_name"], line["last_name"] = line["author"].split(" ", 1)
            p = self.retrieve_profile(line)
            spk = self.mark_as_speaker(p)
            result = self.add_talk(spk, line)
            print line["author"], "-", line["proposal_title"],
            if result:
                print "[added]"
            else:
                print "[skipped]"

    def retrieve_profile(self, data):
        try:
            return cmodels.AttendeeProfile.objects.get(user__email=data["email"])
        except cmodels.AttendeeProfile.DoesNotExist:
            pass

        try:
            # l'utente potrebbe lo stesso esistere? in teoria no, ma già che ci siamo...
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            user = User(
                email=data["email"],
                username=self.new_username(data))
            user.set_unusable_password()
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.save()

        p = cmodels.AttendeeProfile.objects.getOrCreateForUser(user)
        p.setBio(data["author_bio"], language="en")
        # I profili che importiamo sono tutti degli speaker, e questi devono avere il profilo visibile
        p.visibility = "p"
        p.save()
        return p

    def new_username(self, data):
        return "{}{}{}".format(
            data["first_name"][0],
            data["last_name"][0],
            str(random.randint(0, 100000)))

    def mark_as_speaker(self, profile):
        if profile.visibility != "p":
            profile.visibility = "p"
            profile.save()

        try:
            speaker = cmodels.Speaker.objects.get(user=profile.user)
        except cmodels.Speaker.DoesNotExist:
            speaker = cmodels.Speaker.objects.create(user=profile.user)
            pmodels.SpeakerConference.objects.create(speaker=speaker)

        return speaker

    def add_talk(self, speaker, data):
        try:
            cmodels.Talk.objects.get(
                title=data["proposal_title"],
                conference=settings.CONFERENCE_CONFERENCE,
                talkspeaker__speaker=speaker)
        except cmodels.Talk.DoesNotExist:
            pass
        else:
            return False

        t = cmodels.Talk.objects.createFromTitle(
            title=data["proposal_title"],
            conference=settings.CONFERENCE_CONFERENCE,
            speaker=speaker,
            duration=30,
            language="en"
        )
        pmodels.P3Talk.objects.create(talk=t, sub_community="django")
        return True
