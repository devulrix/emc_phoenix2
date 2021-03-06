# load settings file
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import os
from django.core.mail import send_mail

from .forms import ContactForm, ContactFormSignedIn

import json

# Create your views here.
def home(request):

    if 'CF_INSTANCE_INDEX' in os.environ:
        CF_INSTANCE_INDEX = os.environ['CF_INSTANCE_INDEX']
    else:
        CF_INSTANCE_INDEX = 999

    if "VCAP_APPLICATION" in os.environ:
        application_name = json.loads(os.environ['VCAP_APPLICATION'])['application_name']
    else:
        application_name = "local"

    title = "Welcome on instance %s using app %s" %(CF_INSTANCE_INDEX, application_name)
    context = {
        "title": title,
        "index": CF_INSTANCE_INDEX,
    }

    return render(request, "home.html", context)

def contact(request):
    title = "Contact:"
    if request.user.is_authenticated():
        form = ContactFormSignedIn(request.POST or None)
    else:
        form = ContactForm(request.POST or None)

    context = {
        "contact": 'active',
        "title": title,
        "form": form,
    }
    if form.is_valid():
        form_email = form.cleaned_data.get("email")
        form_message = form.cleaned_data.get("message")
        form_full_name = form.cleaned_data.get("full_name")
        from_email = form_email

        subject = 'Site contact form'

        to_email = [settings.EMAIL_HOST_USER]
        contact_message = "%s: %s via %s" %(form_full_name, form_message, form_email)
        some_html_message = """
        <h1>This message was send to you from %s:</h1>
        %s
        """ %(form_full_name, form_message)
        # send asynchronous
        send_mail(subject,
                    contact_message,
                    from_email,
                    to_email,
                    html_message = some_html_message,
                    fail_silently = False)
        context = {
            "contact": 'active',
            "title": "Thank You!",
        }

    return render(request, "contact.html", context)

from .tasks import prime_number
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def primes(request):

    if request.method == 'GET':
        searchrange = 3
        tasks = 1
        if 'range' in request.GET:
            try:
                searchrange = int(request.GET.get('range'))
            except ValueError:
                searchrange = 3
        if 'tasks' in request.GET:
            try:
                tasks = int(request.GET.get('tasks'))
            except ValueError:
                tasks = 1
        if tasks < 1:
            tasks = 1
        if searchrange < 3:
            searchrange = 3

        if searchrange > 500000:
            searchrange = 500000

        if (searchrange/tasks) > 100000:
            searchrange = 100000
            tasks = 5

        window = int(searchrange / tasks)
        low = 0
        high = window

        for n in range(0, tasks):
            if high > searchrange:
                high = searchrange
            prime_number.delay(low,high)
            low += window
            high += window

    context = {
        "title": "Primes:",
        "range": searchrange,
        "tasks": tasks,
    }
    return render(request, "primes.html", context)
