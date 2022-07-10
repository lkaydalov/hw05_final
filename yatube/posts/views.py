from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .utils import get_page


@cache_page(20, key_prefix="index_page")
def index(request):
    """Забирает из баззы данных и возвращает на главную
    страницу информацию о последних постах на сайте,
    а также ссылки на записи групп постов.
    """
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    context = get_page(posts, request)

    return render(request, template, context)


def group_posts(request, slug):
    """Забирает из баззы данных информацию о постах,
    относящихся к определённой группе, заголовок и
    описание группы и возвращает на страницу последние записи.
    """
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('author', 'group')
    context = {
        'group': group,
    }
    context.update(get_page(posts, request))

    return render(request, template, context)


def profile(request, username):
    """Отображает информацию о профиле пользовалтеля."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    user = request.user
    following = user.is_authenticated and author.following.exists(
    ) and user.follower.exists()

    template = 'posts/profile.html'
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page(posts, request))

    return render(request, template, context)


def post_detail(request, post_id):
    """Отображает информацию о деталях конкретного поста пользователя."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post__pk=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Позволяет создать новый пост и сохраняет его в базу данных."""
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Позволяет отредактировать уже существующий пост."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id
    )
    if post.author != request.user:

        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )

    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect('posts:post_detail', post_id)

    return render(request, 'posts/create_post.html', {
        'post': post, 'form': form, 'is_edit': True,
    })


@login_required
def add_comment(request, post_id):
    """Добавляем комментарии к постам."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Позволяет отслеживать избранных авторов."""
    posts = Post.objects.filter(author__following__user=request.user)
    context = get_page(posts, request)

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Позволяет подписаться на автора."""
    author = get_object_or_404(User, username=username)
    if (
        request.user == author
        or Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    ):

        return redirect('posts:profile', username=username)

    Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Позволяет отписаться от автора."""
    Follow.objects.filter(
        user=request.user, author__username=username
    ).delete()

    return redirect('posts:profile', username=username)
