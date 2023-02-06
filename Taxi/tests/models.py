import datetime
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.core.validators import MinValueValidator

from compendium import s3
from compendium.models.models import CustomUser


class FilterByBaseGroupManagerMixin(models.Manager):
    def filter_base_group(self, base_group):
        """
        Args:
            base_group (Group): Group model instance.
        """
        return (
            self.get_queryset()
            .filter(
                models.Q(base_groups=base_group)
                | models.Q(created_by__groups__name=base_group),
            )
            .distinct()
        )


class NotArchivedManager(FilterByBaseGroupManagerMixin):
    """
    Filter for getting only active (not archived) Tests.
    """

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=True)


class ArchivedManager(FilterByBaseGroupManagerMixin):
    """
    Filter only archived Tests.
    """

    def get_queryset(self):
        return super().get_queryset().filter(archived_at__isnull=False)


class Test(models.Model):
    """
    Test model.
    """

    STATUS_NEW = 'new'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_ARCHIVE = 'archive'

    title = models.CharField(max_length=200, help_text='Название теста')
    title_en = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True,
        help_text='Название теста на английском',
    )
    description = models.CharField(
        max_length=300,
        default=None,
        blank=True,
        null=True,
        help_text='Описание теста',
    )
    description_en = models.CharField(
        max_length=300,
        default=None,
        blank=True,
        null=True,
        help_text='Описание теста на английском',
    )

    get_random_num = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=None,
        blank=True,
        null=True,
        help_text='Количество случайных вопросов в тесте',
    )

    time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Время на прохождение теста в минутах',
    )

    published_at = models.DateField(help_text='Дата публикации теста')
    published_until = models.DateField(help_text='Дата конца публикации теста')

    is_english_version = models.BooleanField(
        default=False, help_text='Возможность создания вопросов на английском',
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text='Дата создания теста',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
        help_text='Дата обновления теста',
    )
    archived_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text='Дата архивирования теста',
    )

    created_by = models.ForeignKey(
        CustomUser,
        related_name='user_created_test',
        on_delete=models.DO_NOTHING,
        help_text='Кто создал тест',
    )
    archived_by = models.ForeignKey(
        CustomUser,
        related_name='user_archived_test',
        on_delete=models.DO_NOTHING,
        default=None,
        blank=True,
        null=True,
        help_text='Кто заархивировал тест',
    )

    reward = models.BooleanField(
        default=True, help_text='Награждать за прохождение теста?',
    )

    base_groups = models.ManyToManyField(
        Group,
        blank=True,
        default=None,
        limit_choices_to={
            'name__startswith': CustomUser.BASE_GROUPS_STARTSWITH,
        },
        related_name='base_groups',
        help_text='Доступность теста для базовых групп',
    )

    all_objects = models.Manager()
    objects = NotArchivedManager()
    archived_objects = ArchivedManager()

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        return '"{}", ID: {}'.format(self.title, self.pk)

    def delete_test_question_images(self):
        """
        Remove all question images recursively.
        """
        s3.delete_folder('tests/test_{}'.format(self.pk))

    @property
    def is_active(self):
        """
        Is Test is published.

        Returns:
            boll: True if Test is published, False otherwise.
        """
        return (
            self.published_at
            <= datetime.datetime.date(timezone.now())
            < self.published_until
        )

    @property
    def is_archived(self):
        """
        Is Test is archived.

        Returns:
            boll: True if Test is archived, False otherwise.
        """
        return self.archived_at is not None and self.archived_by is not None

    @property
    def text_status(self):
        """
        Text status of Test.
        """
        result = self.STATUS_NEW

        if self.is_active:
            result = self.STATUS_ACTIVE
        elif self.published_until <= datetime.datetime.date(timezone.now()):
            result = self.STATUS_EXPIRED

        if self.is_archived:
            result = self.STATUS_ARCHIVE

        return result

    @property
    def questions_total(self):
        """
        Number of questions.
        """
        return self.questionanswer_set.count()

    def total_assigned(self, among_agents=None):
        """
        Number of users on whom test is assigned.

        Args:
            among_agents (QuerySet): List of Agents.
        """

        if among_agents is not None:
            return self.testlogs_set.filter(user__in=among_agents).count()
        else:
            return self.testlogs_set.count()

    def total_assigned_answered(self, among_agents=None):
        """
        Number of users who already answered the test.

        Args:
            among_agents (QuerySet): List of Agents.
        """
        if among_agents is not None:
            return self.testlogs_set.filter(
                answered_date__isnull=False, user__in=among_agents,
            ).count()
        else:
            return self.testlogs_set.filter(
                answered_date__isnull=False,
            ).count()

    def answered_percent(self, among_agents=None):
        """
        Percent of answered assigned tests.

        Args:
            among_agents (QuerySet): List of Agents.
        """
        try:
            if among_agents is not None:
                return round(
                    self.total_assigned_answered(among_agents)
                    * 100
                    / self.total_assigned(among_agents),
                )
            else:
                return round(
                    self.total_assigned_answered()
                    * 100
                    / self.total_assigned(),
                )
        except ZeroDivisionError:
            return 0

    def avg_answered(self, among_agents=None):
        """
        Average Test results.

        Args:
            among_agents (QuerySet): List of Agents.
        """
        if among_agents is not None:
            qs = self.testlogs_set.filter(
                user_result__isnull=False, user__in=among_agents,
            )
        else:
            qs = self.testlogs_set.filter(user_result__isnull=False)

        qs = qs.aggregate(models.Avg('user_result'))

        return (
            round(qs.get('user_result__avg'))
            if qs.get('user_result__avg')
            else 0
        )

    def get_dump(self):
        """
        Dumped Test data with questions and answers.

        Returns:
            None|dict: Dict with data, None if Test is not published.
        """
        result = None

        if self.is_active:
            result = {
                'title': self.title,
                'title_en': self.title_en,
                'time': self.time,
                'with_en_version': self.is_english_version,
                'published_at': self.published_at.strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
                'published_until': self.published_until.strftime(
                    '%Y-%m-%d %H:%M:%S',
                ),
            }
            if self.get_random_num:
                question_list = (
                    QuestionAnswer.get_questions_with_answers_for_test(
                        self, self.get_random_num,
                    )
                )
            else:
                question_list = (
                    QuestionAnswer.get_questions_with_answers_for_test(self)
                )

            result['questions'] = question_list

        return result

    @staticmethod
    def mark_archived():
        """
        Tests those "published_until" ended 7 days ago marks as archived.

        Returns:
            Number of updated items.
        """
        # Tests with "published_until" date lte this date can be moved to archive.
        date = timezone.now() - datetime.timedelta(days=7)
        return Test.objects.filter(published_until__lte=date).update(
            archived_at=timezone.now(),
        )


def question_default_structure():
    return {'q_ru': '', 'q_en': '', 'q_img': '', 'without_correct': False}


def answers_default_structure():
    return [{'answer_ru': '', 'answer_en': '', 'is_correct': ''}]


class QuestionAnswer(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        help_text='Тест к которому относится вопрос',
    )

    question = JSONField(
        default=question_default_structure, help_text='Вопрос теста',
    )

    answers = JSONField(
        default=answers_default_structure,
        help_text='Список ответов на вопрос',
    )

    @property
    def question_image_url(self):
        """
        Image url.

        Returns:
            str: Url to the image, an empty string if the image is not set.
        """
        result = ''

        if self.question.get('q_img'):
            result = '/s3-api/{}'.format(self.question['q_img'])

        return result

    class Meta:
        verbose_name = 'Вопрос - ответ'
        verbose_name_plural = 'Вопросы - ответы'

    def delete_question(self):
        """
        Delete model and image from filesystem.
        """

        image = self.question.get('q_img')

        self.delete()

        if image:
            s3.delete_file(image)

    @staticmethod
    def get_questions_with_answers_for_test(test, rand_num=None):
        """
        Get questions and answers for given Test.

        Args:
            test (Test): Test model instance.
            rand_num (int): If not None, questions result will be decreased for this number
            and these questions will be randomly selected.
        Returns:
            list: Empty list if there are no results. Otherwise, list of dictionaries.
        """
        result = []

        if rand_num:
            qs = test.questionanswer_set.all().order_by('?')[:rand_num]
        else:
            qs = test.questionanswer_set.all()

        for question in qs:
            result.append(
                {
                    'id': question.pk,
                    'question': question.question,
                    'answers': question.answers,
                },
            )

        return result


class PublishedTestLogsManager(models.Manager):
    """
    Add to QS conditions where NOW between published_at and published_until.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                test__published_at__lte=timezone.now(),
                test__published_until__gt=timezone.now(),
            )
        )


class TestLogs(models.Model):
    """Assigned on users tests, results."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        help_text='Пользователь, на которого назначен тест',
    )
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, help_text='Назначить тест',
    )

    dump_test = JSONField(help_text='Дамп теста')
    user_answers = JSONField(
        blank=True, null=True, default=None, help_text='Ответы',
    )
    user_result = models.PositiveSmallIntegerField(
        blank=True, null=True, default=None, help_text='Результат',
    )
    assigned_date = models.DateTimeField(
        auto_now_add=True, help_text='Дата и время назначения теста',
    )
    started_date = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        help_text='Дата и время начала сдачи теста',
    )
    answered_date = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        help_text='Дата и время сдачи теста',
    )
    answered_number = models.PositiveSmallIntegerField(
        default=0, help_text='Количество прохождений теста',
    )

    objects = models.Manager()
    published_objects = PublishedTestLogsManager()

    class Meta:
        unique_together = ('user', 'test')

        verbose_name = 'Назначенный тест'
        verbose_name_plural = 'Назначенные тесты'

    @property
    def time_left_to_submit_answer(self):
        """
        How much time left for user to submit answers of Test.

        Returns:
            float: Seconds with microseconds, for example "880.156658".
        """
        result = None
        if self.started_date:
            time_left = (
                self.started_date + timezone.timedelta(minutes=self.test.time)
            ) - timezone.now()
            result = time_left.total_seconds()

        return result

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        super(TestLogs, self).save()

    @staticmethod
    def get_active_assigned_on_user(user):
        """
        Active, not answered tests.
        """

        return TestLogs.published_objects.filter(
            user=user, answered_date__isnull=True,
        )

    @staticmethod
    def get_avg_result_by_user(user, for_last_15_tests=False):
        """
        Average Test result.
        """

        qs = TestLogs.objects.filter(user=user)

        if for_last_15_tests:
            qs = qs.order_by('-answered_date')
            qs = qs[:15]

        qs = qs.aggregate(models.Avg('user_result'))

        return (
            round(qs.get('user_result__avg'))
            if qs.get('user_result__avg')
            else 0
        )

    @staticmethod
    def get_last_answered_test_results_by_user(user, last_num=15):
        """
        List with last test results.
        """
        result = []

        qs = TestLogs.objects.filter(
            user=user, user_result__isnull=False,
        ).order_by('-answered_date')[:last_num]

        if qs:
            result = list(qs.values_list('user_result', flat=True))
            result.reverse()

        return result

    def calculate_result(self, answers_dict):
        """
        Calculate the result of solving test.

        Args:
            answers_dict(dict): Dict where keys are Question IDs and values are dict with lists of answers and results.
                example structure:
                    {
                    "<question_id>": {
                            "answer": [{option_1}, {option_n}],
                            "is_correct": <None|True|False>
                        }
                    }

        Returns:
            int: Percentage of correct answers.
        """

        test_questions = self.dump_test.get('questions')

        answers_dict_for_results = answers_dict.copy()
        correct_answers_num = 0
        for test_question in test_questions:
            test_question_id = str(test_question['id'])
            answer_data = answers_dict.get(test_question_id, {})
            answer = answer_data.get('answer', [])

            if not answer and not test_question['question'].get(
                    'without_correct',
            ):
                answers_dict_for_results[test_question_id] = {
                    'answer': [],
                    'is_correct': False,
                }
                continue

            correct_answer_num_for_this_question = sum(
                bool(i['is_correct']) for i in test_question['answers']
            )
            if correct_answer_num_for_this_question != len(answer):
                answers_dict_for_results[test_question_id][
                    'is_correct'
                ] = False
                continue

            # Below a situation when a question without a correct answer and user did not answer on it.
            # So we can immediately add +1 to corrects answers.
            if test_question['question'].get('without_correct') and not len(
                    answer,
            ):
                correct_answers_num += 1
                answers_dict_for_results[test_question_id] = {
                    'answer': [],
                    'is_correct': True,
                }
                continue

            answer_is_correct = False
            for test_answer in test_question['answers']:
                if test_answer['is_correct']:
                    for answer_part in answer:
                        if (
                                test_answer['answer_ru'] == answer_part['a_ru']
                                and test_answer['answer_en']
                                == answer_part['a_en']
                        ):
                            answer_is_correct = True
                        else:
                            answer_is_correct = False
                            answers_dict_for_results[test_question_id][
                                'is_correct'
                            ] = False
                            continue

            if answer_is_correct:
                correct_answers_num += 1
                answers_dict_for_results[test_question_id]['is_correct'] = True

        self.user_answers = answers_dict_for_results
        self.user_result = round(
            correct_answers_num * 100 / len(test_questions),
        )

        return

    @staticmethod
    def get_not_answered_tests(days_num=1):
        """
        Search for not answered assigned Tests those publication ends soon.

        Args:
            days_num (int): Number of days before end of Test publishing for notify user about not answered Test.

        Returns:
            QuerySet: Queryset with TestLogs.
        """

        date = timezone.now() + datetime.timedelta(days=days_num)

        return TestLogs.published_objects.filter(
            answered_date__isnull=True, test__published_until__lte=date,
        )

    @staticmethod
    def get_answered_tests_by_user(user):
        """
        Search for answered assigned Tests.

        Args:
            user (CustomUser): User object.

        Returns:
            QuerySet: Queryset with TestLogs.
        """

        return TestLogs.objects.filter(user=user, user_result__isnull=False)

    @staticmethod
    def get_not_answered_and_expired():
        """
        Search for assigned not answered tests with publication date that is over.

        Returns:
            QuerySet: Queryset with TestLogs.
        """

        date = timezone.now()

        return TestLogs.objects.filter(
            test__published_until__lt=date, user_result__isnull=True,
        )

    @staticmethod
    def get_avg_results_by_users(
            user_ids, s_date=None, e_date=None, for_last_15_tests=False,
    ):
        """
        Average tests results by users and dates or for 15 last results.

        Args:
            user_ids (list): List with CustomUser IDs.
            s_date (date): Date from.
            e_date (date): Date until.
            for_last_15_tests (bool): If True average counts for last 15 answers, False by default.

        Returns:
            QuerySet: QuerySet with data.
        """
        result = []

        qs = TestLogs.objects.using('slave').filter(user_id__in=user_ids)

        if for_last_15_tests:
            ids_qs = qs.order_by('-answered_date')
            ids_qs = ids_qs[:15]

            ids = ids_qs.values_list('pk', flat=True)
            # "ids" = already filtered last 15 results.
            if ids:
                result = (
                    qs.filter(id__in=ids)
                    .values('user__username')
                    .annotate(models.Avg('user_result'))
                )
        elif s_date and e_date:
            result = (
                qs.filter(answered_date__gte=s_date, answered_date__lte=e_date)
                .values('user__username')
                .annotate(models.Avg('user_result'))
            )
        else:
            result = qs.values('user__username').annotate(
                models.Avg('user_result'),
            )

        return result
