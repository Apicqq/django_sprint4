from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, Http404
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (CreateView,
                                  DeleteView,
                                  DetailView,
                                  ListView,
                                  UpdateView,
                                  )
from django.views.generic.list import MultipleObjectMixin

from blog.forms import PostForm, CommentForm, UserForm, RegistrateForm
from blog.models import Category, Post, Comment, User


class PostUpdateMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post,
                                     pk=kwargs['pk'],
                                     )
        if (not self.request.user.is_authenticated
                or instance.author != self.request.user):
            return redirect('blog:post_detail', pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateMixin:
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'pk': comment.post.pk})


class BlogListView(ListView):
    model = Post
    queryset = Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        Q(is_published=True)
        & Q(pub_date__lte=now())
        & Q(category__is_published=True)
    ).prefetch_related('comments').annotate(comment_count=Count('comments'))
    paginate_by = 10
    template_name = 'blog/index.html'
    ordering = ('-pub_date',)


class BlogCategoryView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'])
        return context

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug'])
        return category.posts.filter(
            Q(is_published=True)
            & Q(pub_date__lte=now())
            & Q(category__is_published=True)
        ).order_by('-pub_date').prefetch_related('comments').annotate(
            comment_count=Count('comments'))


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.username = self.request.user
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post,
                                     pk=kwargs['pk'],
                                     )
        if (instance.author != self.request.user
                and (not instance.is_published
                     or not instance.category.is_published
                     or instance.pub_date >= now())):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, PostUpdateMixin, UpdateView):
    pass


class PostDeleteView(LoginRequiredMixin, PostUpdateMixin, DeleteView):
    success_url = reverse_lazy('blog:index')


class UserDetailView(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        profile = get_object_or_404(
            self.model,
            username=self.kwargs['username'])
        if (not self.request.user.is_authenticated
                or self.request.user != profile):
            object_list = Post.objects.filter(
                author=profile,
                is_published=True,
                category__is_published=True,
                pub_date__lte=now()
            ).select_related(
                'category',
                'author',
                'location'
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
            context = super(UserDetailView, self).get_context_data(
                object_list=object_list,
                profile=profile, **kwargs
            )
        else:
            object_list = Post.objects.filter(
                author=profile,
            ).select_related(
                'category',
                'author',
                'location'
            ).annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date')
            context = super(UserDetailView, self).get_context_data(
                object_list=object_list,
                profile=profile, **kwargs
            )
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(User, username=request.user)
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    posts = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.posts = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.posts
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentUpdateMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentUpdateMixin, DeleteView):
    pass


class SignUpView(CreateView):
    form_class = RegistrateForm
    success_url = reverse_lazy('blog:index')
    template_name = 'registration/registration_form.html'
