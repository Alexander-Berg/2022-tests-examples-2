import os
import json
import base64
import xlrd
import xlwt
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, crypto
from django.utils.translation import gettext_lazy as _, gettext
from django.views.decorators.http import require_http_methods, require_GET
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse

from compendium import s3

from compendium.calculates import get_config_
from compendium.decorators import (
    access_to_assign_test_or_403,
    access_to_create_test_or_403,
    require_any_group,
)
from compendium.models import Notification
from compendium.models.models import (
    billing_logs,
    Cabinets,
    CustomUser,
    experience_logs,
    Virtual_cabinet,
)
from compendium.views import (
    data_every_page,
    error_403,
    error_404,
    error_500,
    message_info,
    __get_cabinet_agents,
)

from .models import Test, TestLogs, QuestionAnswer
from .forms import (
    ArchivedTestsDateRange,
    AssignTestForm,
    AssignTestOnCabinetForm,
    TestForm,
    TestQuestionAnswerForm,
)

import logging
logger = logging.getLogger(__name__)


@require_http_methods(['GET', 'POST'])
def solve_test(request, test_id):
    """
    Solve the test action.
    """
    user = CustomUser.objects.get(pk=request.user.pk)

    response_data = {'data_every_page': data_every_page(request)}

    try:
        assigned_test = TestLogs.published_objects.get(pk=test_id, user=user)

        if assigned_test.answered_date:
            return message_info(
                request, _('Notification'), _('You already passed this test.'),
            )

        response_data['test'] = assigned_test
    except TestLogs.DoesNotExist:
        return error_403(request)

    if request.method == 'POST':
        if (
                assigned_test.time_left_to_submit_answer + 3 >= 0
        ):  # 3 sec is just for insurance

            answer_dict = {}
            for param in request.POST:
                if param.startswith('q_'):
                    encoded_question_id = param[2:]
                    encoding = 'utf-8'
                    question_id = str(
                        base64.b64decode(bytes(encoded_question_id, encoding)),
                        encoding,
                    )

                    try:
                        answer_dict[question_id] = {
                            'answer': [
                                json.loads(item)
                                for item in request.POST.getlist(param)
                            ],
                            'is_correct': None,
                        }
                    except ValueError:
                        continue

            assigned_test.calculate_result(answer_dict)
        else:
            assigned_test.user_result = 0

        assigned_test.answered_date = timezone.now()

        try:
            assigned_test.answered_number += 1
            assigned_test.save()

            if assigned_test.user_result == 100:
                message = _('Good one mate!')
            else:
                message = (
                    _(
                        'Test passed with a score of {}%. Be attentive the next time!',
                    ).format(
                        assigned_test.user_result
                        if assigned_test.user_result
                        else 0,
                    )
                )

            Notification(login=user, text=message, type='verify').save()

            tests_config = get_config_('TESTS_REWARD')
            if assigned_test.test.reward and assigned_test.user_result == 100:
                if (
                        assigned_test.answered_number == 1
                ):  # It means that agent passed the test at first time.
                    billing_comment = 'Прохождение теста'
                    billing_logs(
                        user=user,
                        operation=tests_config['coins_amount'],
                        comment=billing_comment,
                    ).save()

                    reward_coins = tests_config['coins_amount']
                else:
                    reward_coins = None

                reward_message = render_to_string(
                    'chunks/reward_notification.html',
                    {'coins': reward_coins, 'exp': tests_config['exp_amount']},
                )

                experience_logs.add_experience(
                    user, tests_config['exp_amount'], 'Прохождение теста',
                )

                Notification(
                    login=user, text=reward_message, type='verify',
                ).save()

            CustomUser.objects.filter(pk=user.pk).update(
                avg_knowledge=TestLogs.get_avg_result_by_user(user),
            )

            return redirect('/')
        except TestLogs:
            result = render(request, 'solve_test.html', response_data)
    else:
        if not assigned_test.started_date:
            assigned_test.started_date = timezone.now()
            assigned_test.save()

            response_data['test'] = assigned_test

        result = render(request, 'solve_test.html', response_data)

    return result


def get_user_tests(request):
    """
    Tests, assigned on user
    """
    agent = CustomUser.objects.get(pk=request.user.pk)
    active_tests = TestLogs.get_active_assigned_on_user(agent)

    tests_config = get_config_('TESTS_REWARD')

    response_data = {
        'active_tests': active_tests,
        'reward_coins': (
            tests_config.get('coins_amount', 0) if tests_config else None
        ),
        'reward_exp': (
            tests_config.get('exp_amount', 0) if tests_config else None
        ),
    }

    return render_to_string('user_tests.html', response_data)


def list_tests(request):
    """
    List of tests.
    """
    if request.path_info.endswith('/all'):
        qs = Test.objects.filter_base_group(request.user_base_group).all()
    else:
        qs = Test.objects.filter(created_by__pk=request.user.pk)

    tests = qs.order_by('-id')

    return render(
        request,
        'list.html',
        {'tests': tests, 'data_every_page': data_every_page(request)},
    )


def list_tests_cabinet(request):
    """
    List of test cards for cabinets.
    """
    cabinet_agents = __get_cabinet_agents(request)

    assigned_tests = TestLogs.objects.filter(
        user_id__in=cabinet_agents.values_list('pk', flat=True),
    )

    tests = Test.objects.filter(
        id__in=assigned_tests.values_list('test', flat=True),
    ).order_by('-id')

    tests = tests

    response_data = {
        'tests': tests,
        'cabinet_agents': cabinet_agents,
        'data_every_page': data_every_page(request),
    }

    return render(
        request, 'compendium_support/cabinet/tests.html', response_data,
    )


@access_to_create_test_or_403()
def archive_test(request, test_id):
    """
    Mark Test as archived.
    """
    try:
        test = Test.objects.filter_base_group(request.user_base_group).get(
            pk=test_id,
        )
        test.archived_at = timezone.now()

        user = CustomUser.objects.get(pk=request.user.pk)
        test.archived_by = user

        test.save()
        return redirect(reverse('tests:list'))
    except Test:
        return error_404(request)


def archive(request):
    """
    Archived tests.
    """
    response_data = {'data_every_page': data_every_page(request)}

    form = ArchivedTestsDateRange(request.GET)
    if not form.is_valid():
        default_range = {
            'date_from': timezone.now().date(),
            'date_until': timezone.now().date() + timezone.timedelta(days=31),
        }
        form = ArchivedTestsDateRange(default_range)

    form.is_valid()

    response_data['form'] = form

    tests = (
        Test.archived_objects.filter_base_group(request.user_base_group)
        .filter(
            archived_at__gte=form.cleaned_data['date_from'],
            archived_at__lte=form.cleaned_data['date_until'],
        )
        .order_by('-archived_at')
    )
    response_data['tests'] = tests

    page = 1

    if 'page' in request.GET:
        page = int(request.GET.get('page'))

    paginator = Paginator(tests, 10)
    if page > paginator.num_pages or page < 1:
        if request.is_ajax():
            return JsonResponse(
                status=404,
                data={'status': 'false', 'message': 'Такой страницы нет'},
            )
        else:
            return message_info(request, '404', 'Такой страницы нету')

    response_data['pages'] = paginator.num_pages
    response_data['tests'] = paginator.page(page)

    if request.is_ajax():
        json_result = render_to_string(
            'chunks/test_list.html', {'tests': response_data['tests']},
        )

        next_page = page + 1

        response = JsonResponse(
            status=200, data={'details': json_result, 'next_page': next_page},
        )
    else:
        response = render(request, 'archive.html', response_data)

    return response


@access_to_create_test_or_403()
@require_http_methods(['GET', 'POST'])
def edit_test(request, test_id):
    """
    Update existed Test.
    """

    try:
        test = Test.objects.filter_base_group(request.user_base_group).get(
            pk=test_id,
        )
    except Test.DoesNotExist:
        return error_404(request)

    tests_config = get_config_('TESTS_REWARD')

    response_data = {
        'data_every_page': data_every_page(request),
        'is_reward_available': (
            True if tests_config and tests_config.get('is_active') else False
        ),
    }

    if request.method == 'POST':
        reward_was_checked = test.reward

        form = TestForm(request.POST, instance=test)

        if form.is_valid():

            if (
                    not response_data['is_reward_available']
                    and form.cleaned_data.get('reward')
                    and not reward_was_checked
            ):
                test.reward = False

            form.save()

            result = redirect(reverse('tests:list'))
        else:
            response_data['form'] = form
            result = render(request, 'create-edit_test.html', response_data)
    else:
        response_data['form'] = TestForm(instance=test)

        result = render(request, 'create-edit_test.html', response_data)

    return result


@access_to_create_test_or_403()
@require_http_methods(['GET', 'POST'])
def create_test(request):
    """
    Create new test.
    """

    response_data = {
        'data_every_page': data_every_page(request),
        'is_reward_available': False,
    }

    tests_config = get_config_('TESTS_REWARD')

    if tests_config and tests_config.get('is_active'):
        response_data['is_reward_available'] = True

    if request.method == 'GET':
        response_data['form'] = TestForm(
            reward_is_active=response_data['is_reward_available'],
        )
        result = render(request, 'create-edit_test.html', response_data)
    else:
        form = TestForm(request.POST)

        if form.is_valid():
            new_test = form.save(commit=False)

            if new_test.reward and not response_data['is_reward_available']:
                new_test.reward = False

            user = CustomUser.objects.get(id=request.user.id)
            new_test.created_by = user
            new_test.save()

            result = redirect(
                reverse('tests:create-questions', args=(new_test.pk,)),
            )
        else:
            response_data['form'] = form
            result = render(request, 'create-edit_test.html', response_data)

    return result


@access_to_create_test_or_403()
@require_http_methods(['GET', 'POST'])
def create_questions(request, test_id):
    """
    Create question or edit the test.
    """
    response_data = {'data_every_page': data_every_page(request)}

    try:
        test = Test.objects.filter_base_group(request.user_base_group).get(
            id=test_id,
        )
        response_data['test'] = test
    except Test.DoesNotExist:
        test = None

    if test:
        response_data['questions'] = QuestionAnswer.objects.filter(
            test=test,
        ).order_by('-id')

    if request.method == 'POST' and test:

        form = TestQuestionAnswerForm(
            data=request.POST,
            files=request.FILES,
            with_english=test.is_english_version,
        )

        if form.is_valid():
            question_answer = QuestionAnswer()
            question_answer.test = test

            # process question
            image_path = ''
            if 'q_img' in request.FILES:
                try:
                    q_img = request.FILES['q_img']

                    image_ext = os.path.splitext(q_img.name)[-1]
                    new_image_name = '{}{}'.format(
                        crypto.get_random_string(), image_ext,
                    )

                    filename = 'tests/test_{}/{}'.format(
                        test.id, new_image_name,
                    )

                    s3.upload_image(request.FILES['q_img'], filename)

                    image_path = filename
                except IndexError:
                    return error_403(request)

            question_answer.question = {
                'q_ru': form.cleaned_data['q_ru'],
                'q_en': form.cleaned_data.get('q_en', ''),
                'q_img': image_path,
                'without_correct': False,
            }

            # process answers
            is_set_correct_answer = False
            answers_list = []
            for item in form.cleaned_data:
                if item.startswith('a_'):
                    if 'ru' in item:
                        num = item[5:]

                        answer_ru = form.cleaned_data['a_ru_{}'.format(num)]
                        answer_en = form.cleaned_data.get(
                            'a_en_{}'.format(num), '',
                        )

                        # replace " on ”
                        if '"' in answer_ru:
                            answer_ru = answer_ru.replace('"', '”')
                        if '"' in answer_en:
                            answer_en = answer_en.replace('"', '”')

                        if not answer_ru and not answer_en:
                            continue

                        answer_correct = request.POST.get(
                            'a_correct_{}'.format(num),
                        )

                        if answer_correct:
                            is_set_correct_answer = True

                        answers_list.append(
                            {
                                'answer_ru': answer_ru,
                                'answer_en': answer_en,
                                'is_correct': bool(answer_correct),
                            },
                        )

                        continue

            question_answer.answers = answers_list

            try:
                if not is_set_correct_answer:
                    question_answer.question['without_correct'] = True

                question_answer.save()
            except:
                s3.delete_file(image_path)

            result = redirect(
                reverse('tests:create-questions', args=(test.id,)),
            )
        else:
            response_data['form'] = form
            result = render(request, 'create_questions.html', response_data)
    elif request.method == 'GET' and test:
        form = TestQuestionAnswerForm(with_english=test.is_english_version)
        response_data['form'] = form
        result = render(request, 'create_questions.html', response_data)

    else:
        result = error_404(request)

    return result


@access_to_create_test_or_403()
def delete_question(request, question_id):
    """
    Delete question and redirect to create-questions page.
    """

    try:
        q = QuestionAnswer.objects.get(id=question_id)
        if Test.objects.filter_base_group(request.user_base_group).get(
                pk=q.test.id,
        ):
            q.delete_question()

        return redirect(reverse('tests:create-questions', args=(q.test.id,)))
    except QuestionAnswer.DoesNotExist:
        return error_404(request)
    except Test.DoesNotExist:
        return error_403(request)


@access_to_assign_test_or_403()
@require_http_methods(['GET', 'POST'])
def bulk_test_assign(request, test_id):
    """
    Assign Test on user logins from file.
    """

    response_data = {'data_every_page': data_every_page(request)}

    try:
        test = Test.objects.filter_base_group(request.user_base_group).get(
            pk=test_id,
        )
        if not test.is_active:
            return redirect(reverse('tests:list'))
        response_data['test'] = test
    except Test.DoesNotExist:
        return error_404(request)

    if request.method == 'POST':
        if not test.questionanswer_set.all():
            return message_info(
                request, _('Error'), _('You cannot assign on empty test'),
            )

        form = AssignTestForm(request.POST, request.FILES)
        file = request.FILES['assign_file']

        if form.is_valid():
            try:
                wb = xlrd.open_workbook(file_contents=file.read())
            except xlrd.XLRDError:
                return error_500(request)

            test_base_groups = test.base_groups.all()

            worksheet = wb.sheet_by_index(0)
            for row_num in range(worksheet.nrows):
                try:
                    user_login = worksheet.row_values(row_num)[0]
                    if test_base_groups:
                        user = CustomUser.objects.get(
                            groups__in=test_base_groups,
                            username=user_login.strip(),
                        )
                    else:
                        user = CustomUser.objects.get(
                            username=user_login.strip(),
                        )

                    test_log = TestLogs()
                    test_log.test = test
                    test_log.user = user
                    test_log.dump_test = test.get_dump()

                    test_log.save()
                except CustomUser.DoesNotExist:
                    continue
                except IntegrityError:
                    continue

            Notification(
                login=response_data['data_every_page']['agent'],
                text=_('Test was assigned on users'),
            ).save()

            result = redirect(reverse('tests:list'))
        else:
            response_data['form'] = form
            result = render(request, 'assign-test.html', response_data)
    else:
        form = AssignTestForm()
        response_data['form'] = form

        assign_cabinet_form = AssignTestOnCabinetForm()
        response_data['assign_cabinet_form'] = assign_cabinet_form

        result = render(request, 'assign-test.html', response_data)

    return result


@access_to_assign_test_or_403()
@require_http_methods(['POST'])
def bulk_test_assign_cabinet(request, test_id):
    """
    Assign Test on users from cabinet.
    """

    try:
        test = Test.objects.filter_base_group(request.user_base_group).get(
            pk=test_id,
        )
        if not test.is_active:
            raise Test.DoesNotExist
    except Test.DoesNotExist:
        return error_404(request)

    user = CustomUser.objects.get(pk=request.user)

    form = AssignTestOnCabinetForm(request.POST)

    if form.is_valid():
        try:
            cabinet = Cabinets.objects.get(pk=form.cleaned_data['cabinet'])
        except Cabinets.DoesNotExist:
            return error_403(request)

        for virtual_cabinet_user in Virtual_cabinet.objects.filter(
                cabinet=cabinet,
        ):
            try:
                agent = CustomUser.objects.get(pk=virtual_cabinet_user.user_to)

                test_log = TestLogs()
                test_log.test = test
                test_log.user = agent
                test_log.dump_test = test.get_dump()
                test_log.save()
            except CustomUser.DoesNotExist:
                continue
            except IntegrityError:
                continue

        Notification(login=user, text=_('Test was assigned on users')).save()

        result = redirect(reverse('tests:list'))
    else:
        result = redirect(reverse('tests:assign-test'), args=(test.id,))

    return result


@require_any_group(['Доступ к кабинетам'])
def get_statistic_cabinet(request, test_id):
    cabinet_agents = __get_cabinet_agents(request)
    return get_statistic(request, test_id, cabinet_agents)


@require_any_group(['Доступ к созданию тестов', 'Доступ к кабинетам'])
def get_statistic(request, test_id, among_agents=None):
    """
    Download file with Test statistic.
    """

    try:
        test = Test.all_objects.get(pk=test_id)
    except Test.DoesNotExist:
        return error_404(request)

    wb = xlwt.Workbook()
    sh = wb.add_sheet('Test ID {}'.format(test.pk))

    style = xlwt.XFStyle()

    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font

    sh.write(0, 1, gettext('Last name'), style)
    sh.write(0, 2, gettext('Name'), style)

    column_num = 3
    list_of_all_test_question_ids = []
    for question in test.questionanswer_set.all().order_by('pk'):
        list_of_all_test_question_ids.append(question.pk)

        sh.write(0, column_num, question.question.get('q_ru'), style)
        column_num += 1
        sh.write(0, column_num, gettext('Answer'), style)
        column_num += 1

    sh.write(0, column_num, gettext('Result'), style)

    if among_agents is not None:
        test_logs = test.testlogs_set.filter(user__in=among_agents).all()
    else:
        test_logs = test.testlogs_set.all()

    answer_num = 1
    for answered_test in test_logs:
        sh.write(answer_num, 0, answered_test.user.username, style)
        sh.write(answer_num, 1, answered_test.user.last_name, style)
        sh.write(answer_num, 2, answered_test.user.first_name, style)

        answer_column_num = 3
        for question_id in list_of_all_test_question_ids:

            user_answer_result = ''
            user_answer = ''
            if (
                    answered_test.user_answers
                    and answered_test.user_answers.get(str(question_id))
            ):
                answers_list = []
                if answered_test.user_answers[str(question_id)]['answer']:
                    for each_answer in answered_test.user_answers[
                            str(question_id)
                    ]['answer']:
                        answers_list.append(each_answer.get('a_ru'))

                user_answer = '\r\n'.join(answers_list)

                user_answer_result = '0'
                if answered_test.user_answers[str(question_id)]['is_correct']:
                    user_answer_result = '100'

            sh.write(answer_num, answer_column_num, user_answer_result)
            answer_column_num += 1
            sh.write(answer_num, answer_column_num, user_answer)
            answer_column_num += 1

        sh.write(
            answer_num,
            answer_column_num,
            answered_test.user_result
            if answered_test.user_result is not None
            else '-',
            style,
        )

        answer_num += 1

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response[
        'Content-Disposition'
    ] = 'attachment; filename=test_{}_statistic.xls'.format(test.pk)

    wb.save(response)

    return response


@require_GET
def details(request):
    response_data = {'data_every_page': data_every_page(request)}

    if request.GET.get('login'):
        try:
            user = CustomUser.objects.get(username=request.GET['login'])
        except CustomUser.DoesNotExist:
            return error_404(request)
    else:
        user = response_data['data_every_page'].get('agent')

    tests = TestLogs.get_answered_tests_by_user(user=user).order_by(
        '-answered_date',
    )

    page = 1
    if 'page' in request.GET:
        if not request.is_ajax():
            return error_403(request)
        page = int(request.GET.get('page'))

    paginator = Paginator(tests, 25)
    if page > paginator.num_pages or page < 1:
        if request.is_ajax():
            return JsonResponse(
                status=404,
                data={'status': 'false', 'message': 'Такой страницы нет'},
            )
        else:
            return message_info(request, '404', 'Такой страницы нету')

    response_data['pages'] = paginator.num_pages
    response_data['tests'] = paginator.page(page)

    if request.is_ajax():
        json_result = render_to_string(
            'chunks/details_test_card.html', {'tests': response_data['tests']},
        )

        next_page = page + 1

        response = JsonResponse(
            status=200, data={'details': json_result, 'next_page': next_page},
        )
    else:
        response = render(request, 'details.html', response_data)

    return response
