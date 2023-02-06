from django.contrib import admin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

from compendium.models.models import CustomUser
from tests.models import Test, TestLogs, QuestionAnswer


class TestAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', 'archived_at', 'archived_by')
    list_display = (
        'title',
        'title_en',
        'is_english_version',
        'published_at',
        'published_until',
        'is_archived',
    )

    def is_archived(self, obj):
        return bool(obj.archived_at)

    is_archived.boolean = True
    is_archived.short_description = 'archived'

    def save_model(self, request, obj, form, change):

        if (
                not change
        ):  # "change" == False -> "add" == True -> new model will be added
            user = CustomUser.objects.get(id=request.user.id)
            obj.created_by = user

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        """
        Add some addition functionality.
        Args:
            request: Request.
            obj (Test): Test model instance.
        """

        obj.delete_test_question_images()

        super().delete_model(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions


class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('test', 'question_ru', 'question_en', 'question_img')

    @staticmethod
    def question_ru(obj):
        return obj.question.get('q_ru')

    @staticmethod
    def question_en(obj):
        return obj.question.get('q_en')

    @staticmethod
    def question_img(obj):
        return obj.question.get('q_img')


class AssignedDateAllValuesFieldListFilter(admin.AllValuesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(
            field, request, params, model, model_admin, field_path,
        )

        queryset = model_admin.get_queryset(request)

        if request.GET.get('q'):
            search_key = request.GET.get('q').strip()
            # filtered queryset is queryset result after search
            filtered_qs = queryset.filter(
                Q(user__username__icontains=search_key)
                | Q(test__title__icontains=search_key),
            )
            if filtered_qs:
                queryset = filtered_qs

        self.lookup_choices = (
            queryset.distinct()
            .order_by(field.name)
            .values_list(field.name, flat=True)
        )


class TestLogsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'test',
        'assigned_date',
        'answered_date',
        'user_result',
        'is_archived',
    )

    search_fields = (
        'user__username',
        'test__title',
    )  # "assigned_date" filter based on these fields.

    readonly_fields = (
        'dump_test',
        'user_result',
        'user_answers',
        'assigned_date',
        'started_date',
        'answered_date',
        'answered_number',
    )

    list_filter = (('assigned_date', AssignedDateAllValuesFieldListFilter),)

    def is_archived(self, obj):
        return bool(obj.test.archived_at)

    is_archived.boolean = True
    is_archived.short_description = 'archived'

    def save_model(self, request, obj, form, change):
        """
        Add some functionality before save.
        """

        if (
                not change
        ):  # "change" == False -> "add" == True -> new model will be added
            if not obj.test.is_active:
                message = 'Нельзя назначить неактивный тест'
                self.message_user(request, '%s.' % message, level=40)
                return redirect(reverse('admin:index'))

            obj.dump_test = obj.test.get_dump()

        super().save_model(request, obj, form, change)

    def get_actions(self, request):
        actions = super().get_actions(request)

        actions['cancel_selected_test'] = (
            self.cancel_selected_test,
            'cancel_selected_test',
            'Аннулировать выбранные %(verbose_name_plural)s',
        )

        return actions

    def cancel_selected_test(self, test_logs_admin, request, queryset):

        updated_number = 0
        not_updated_id_list = []
        for test_log in queryset:
            if test_log.test.is_active and not test_log.test.is_archived:
                test_log.user_answers = None
                test_log.user_result = None
                test_log.started_date = None
                test_log.answered_date = None
                test_log.dump_test = test_log.test.get_dump()
                test_log.save()
                updated_number += 1
            else:
                not_updated_id_list.append(str(test_log.pk))

        if updated_number:
            message = 'Аннулированных результатов тестов: %s' % updated_number
            self.message_user(request, '%s.' % message)

        if not_updated_id_list:
            message = (
                'Нельзя аннулировать результаты неактивных тестов. Список ID: {}'.format(
                    ', '.join(not_updated_id_list),
                )
            )
            self.message_user(request, '%s.' % message, level=40)


admin.site.register(Test, TestAdmin)
admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
admin.site.register(TestLogs, TestLogsAdmin)
