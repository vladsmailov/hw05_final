from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class Login(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/login.html'


class PasswordChangeView(LoginRequiredMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_form.html'

    def get_success_url(self):
        return redirect(PasswordChangeDoneView)


class PasswordChangeDoneView(LoginRequiredMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_done.html'


class PasswordResetView(LoginRequiredMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_form.html'

    def get_success_url(self):
        return redirect(PasswordResetDoneView)


class PasswordResetDoneView(LoginRequiredMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_done.html'


class PasswordResetConfirmView(LoginRequiredMixin, CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_confirm.html'


class PasswordResetCompleteView(LoginRequiredMixin, CreateView):
    form_class = CreateView
    template_name = 'users/password_reset_complete.html'
