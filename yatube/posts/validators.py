from django import forms


def clean_text(text):
    if text == '':
        raise forms.ValidationError(
            'Кажется, ты забыл, зачем зашёл на страницу. Пиши пост',
            params={'text': text},
        )
