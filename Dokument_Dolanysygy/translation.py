from modeltranslation.translator import register, TranslationOptions
from .models import File,Hasabat

@register(File)
class NewsTranslationOptions(TranslationOptions):
    fields = ('mazmuny',)

@register(Hasabat)
class HasabatTranslationOptions(TranslationOptions):
    fields = ('ady',)
