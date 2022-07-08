from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Отображает шаблон с информацией об авторе проекта."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Отображает шаблон с информацией о технологиях проекта."""

    template_name = 'about/tech.html'
