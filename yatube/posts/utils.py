from django.core.paginator import Paginator

from .constants import POSTS_PER_PAGE


def get_page(posts, request):
    """Функция отдаёт количество постов на страницу, указанное
    в константе POSTS_PET_PAGE,
    paginator определяет количество записей на странице,
    page_number извлекает из URL номер запрошенной страницы,
    page_obj получает набор записей для страницы
    с запрошенным номером.
    """
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return {'page_obj': page_obj}
