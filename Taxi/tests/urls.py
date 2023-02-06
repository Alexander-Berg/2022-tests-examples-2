"""tests URL Configuration

"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.list_tests, name='list'),
    path('cabinet', views.list_tests_cabinet, name='cabinet-list'),
    path('all', views.list_tests, name='all'),
    path('create-test', views.create_test, name='create-test'),
    path('edit-test/<int:test_id>/', views.edit_test, name='edit-test'),
    path(
        'archive-test/<int:test_id>/', views.archive_test, name='archive-test',
    ),
    path(
        'create-questions/<int:test_id>/',
        views.create_questions,
        name='create-questions',
    ),
    path(
        'delete-question/<int:question_id>/',
        views.delete_question,
        name='delete-question',
    ),
    path(
        'assign-test/<int:test_id>/',
        views.bulk_test_assign,
        name='assign-test',
    ),
    path(
        'assign-test-cabinet/<int:test_id>/',
        views.bulk_test_assign_cabinet,
        name='assign-test-cabinet',
    ),
    path('archive', views.archive, name='archive'),
    path('statistics/<int:test_id>/', views.get_statistic, name='statistics'),
    path(
        'cabinet-statistics/<int:test_id>/',
        views.get_statistic_cabinet,
        name='cabinet-statistics',
    ),
    path('details', views.details, name='details'),
    path('solve-test/<int:test_id>/', views.solve_test, name='solve-test'),
]
