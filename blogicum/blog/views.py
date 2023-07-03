from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import (CreateView,
                                  DeleteView,
                                  DetailView,
                                  ListView,
                                  UpdateView)
from django.views.generic.list import MultipleObjectMixin

from blog.forms import PostForm, CommentForm, UserForm
from blog.models import Category, Post, Comment, User
from blog.utils import PAGINATION_VALUE


def get_base_queryset():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    ).prefetch_related('comments').annotate(
        comment_count=Count('comments')).order_by('-pub_date')


class BlogListView(ListView):
    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_base_queryset().filter(
            Q(is_published=True)
            & Q(pub_date__lte=now())
            & Q(category__is_published=True)
        )  # По-моему, так будет ещё короче


class BlogCategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'])
        context['page_obj'] = Paginator(
            get_base_queryset().filter(
                Q(is_published=True)
                & Q(pub_date__lte=now())
                & Q(category__is_published=True,
                    category=context['category'])
            ), PAGINATION_VALUE).get_page(context['page_obj'])
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        if (self.get_object().author != self.request.user
                and not self.get_object().is_published):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:index')

    def delete(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(self.get_success_url())
        return super().delete(request)


class UserDetailView(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    paginate_by = PAGINATION_VALUE

    def get_context_data(self, **kwargs):
        profile = self.get_object()
        object_list = get_base_queryset().filter(author=profile)
        if self.request.user != profile:
            object_list = get_base_queryset().filter(
                author=profile,
                is_published=True,
                category__is_published=True,
                pub_date__lte=now())
            # Тесты проходят без фильтров по категории и времени публикации,
            # но это нелогично: сторонние пользователи не должны
            # видеть отложенные посты и посты из "распубликованных" категорий.
        context = super(UserDetailView, self).get_context_data(
            object_list=object_list,
            profile=profile, **kwargs)
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )

    def get_object(self, queryset=None):
        return self.model.objects.get(username=self.request.user.username)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CommentForm
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'

    def delete(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(self.get_success_url())
        return super().delete(request)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.get_object().post.pk})
