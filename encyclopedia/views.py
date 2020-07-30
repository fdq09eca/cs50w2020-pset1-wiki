from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed
from django.urls import reverse
from django import forms
from django.shortcuts import render
import markdown2
import random
from . import util


class editForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label='')


class createForm(forms.Form):
    title = content = forms.CharField(label='Title')
    content = forms.CharField(widget=forms.Textarea, label='')


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def title(request, title):
    entry_content = util.get_entry(title)
    if entry_content:
        context = {
            "entry_html": markdown2.markdown(entry_content),
            "entry_title": title
        }
        return render(request, 'encyclopedia/title.html', context)
    return HttpResponseNotFound('<h1>Page not found</h1>')


def search(request):
    if request.method == 'POST':
        q = request.POST.get('q')
        titles = util.list_entries()
        result = [title for title in titles if title.lower().startswith(q.lower())]
        if len(result) == 1:
            return HttpResponseRedirect(reverse('title', kwargs={'title': result[0]}))
        elif len(result) > 1:
            return render(request, "encyclopedia/index.html", {"entries": result})
        else:
            return HttpResponseRedirect(reverse('index'))
    return HttpResponseNotAllowed("GET is not allowed")


def new_page(request):
    if request.method == 'GET':
        form = createForm()
        context = {'form': form}
        return render(request, "encyclopedia/create.html", context)

    elif request.method == 'POST':
        form = createForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            title = form.cleaned_data['title']
            if title in util.list_entries():
                context = {'form': form, 'error': True}
                return render(request, "encyclopedia/create.html", context)
            util.save_entry(title, content)
        return HttpResponseRedirect(reverse('index'))


def random_page(request):
    titles = util.list_entries()
    random_title = random.choice(titles)
    return HttpResponseRedirect(reverse('title', kwargs={'title': random_title}))


def edit(request, title):
    if request.method == 'GET':
        form = editForm({'content': util.get_entry(title)})
        context = {'form': form, 'entry_title': title}
        return render(request, 'encyclopedia/edit.html', context)
    elif request.method == 'POST':
        content = request.POST.get('content')
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('index'))
    return HttpResponseNotAllowed('GET and POST only')
