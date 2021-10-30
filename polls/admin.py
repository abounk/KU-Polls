from django.contrib import admin

from .models import Choice, Question


class ChoiceInline(admin.StackedInline):
    """ Limit the number of choices to be shown in a line. """
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """ Allow admin to edit poll questions. """

    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': [
         'pub_date', 'end_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'is_published')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
