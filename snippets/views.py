from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.views.decorators.http import require_safe, require_http_methods, require_POST
from snippets.models import Snippet, Comment
from snippets.forms import SnippetForm, CommentForm


@require_safe
def top(request):
    snippets = Snippet.objects.all()
    context = {'snippets': snippets}
    return render(request, 'snippets/top.html', context)


@login_required
@require_http_methods(['GET', 'POST', 'HEAD'])
def snippet_new(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.created_by = request.user
            snippet.save()
            return redirect(snippet_detail, snippet_id=snippet.pk)
    else:
        form = SnippetForm()
    return render(request, 'snippets/snippet_new.html', {'form': form})


@login_required
def snippet_edit(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    if snippet.created_by_id != request.user.id:
        return HttpResponseForbidden("このスニペットの編集は許可されていません。")

    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', snippet_id=snippet_id)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/snippet_edit.html', {'form': form})


@login_required
def snippet_delete(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    if snippet.created_by_id != request.user.id:
        return HttpResponseForbidden("このスニペットの削除は許可されていません。")

    if request.method == 'POST':
        snippet.delete()
    else:
        form = SnippetForm(instance=snippet)
        return render(request, 'snippets/snippet_delete.html', {'form': form, 'snippet': snippet})
    return redirect(top)


def snippet_detail(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    comments = list(Comment.objects.filter(commented_to=snippet_id))
    comment_form = CommentForm()
    return render(request, 'snippets/snippet_detail.html', {
        'snippet': snippet,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
@require_POST
def comment_new(request, snippet_id):
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.commented_to = snippet
        comment.commented_by = request.user
        comment.save()
    return redirect(snippet_detail, snippet_id=snippet_id)
    # return render(request, 'snippets/snippet_new.html', {'form': form})

# from django.contrib import messages
# @login_required
# def comment_new(request, snippet_id):
#     snippet = get_object_or_404(Snippet, pk=snippet_id)

#     form = CommentForm(request.POST)
#     if form.is_valid():
#         comment = form.save(commit=False)
#         comment.commented_to = snippet
#         comment.commented_by = request.user
#         comment.save()
#         messages.add_message(request, messages.SUCCESS,
#                              "コメントを投稿しました。")
#     else:
#         messages.add_message(request, messages.ERROR,
#                              "コメントの投稿に失敗しました。")
#     return redirect('snippet_detail', snippet_id=snippet_id)

# @login_required
# def comment_delete(request, snippet_id):
#     snippet = get_object_or_404(Snippet, pk=snippet_id)
#     if snippet.created_by_id != request.user.id:
#         return HttpResponseForbidden("このスニペットの編集は許可されていません。")

#     if request.method == 'POST':
#         snippet.delete()
#     return redirect(top)
