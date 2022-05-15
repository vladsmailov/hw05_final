from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Страничка посвященная автору проекта'
        context['text'] = 'А это текст посвященный автору :)'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = (
            'Страничка посвященная технологии '
            'производства этой странички :)'
        )
        context['text'] = (
            'Здесь будет подробное описание '
            'проделанной работы... скоро'
        )
        return context
