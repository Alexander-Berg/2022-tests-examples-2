# -*- coding: utf-8 -*-

from optparse import make_option

from django.core.management.base import BaseCommand
from passport_grants_configurator.apps.core.models import (
    Environment,
    Namespace,
    NamespaceEnvironments,
)


class Command(BaseCommand):
    help = u'Добавляет окружение intranet testing к [blackbox, oauth]'
    option_list = BaseCommand.option_list + (
        make_option(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help=u'Удалить окружение intranet testing у [blackbox, oauth]',
        ),
    )

    def handle(self, *args, **options):

        environment = Environment.objects.get(name='intranet', type='testing')

        # У паспорта уже есть это окружение, исключаем его namespace
        names = ['blackbox', 'oauth']
        namespaces = [Namespace.objects.get(name=name) for name in names]

        if options['delete']:
            NamespaceEnvironments.objects.filter(namespace__in=namespaces, environment=environment).delete()
            print 'Deleted "intranet testing" from %s' % namespaces
            return

        for namespace in namespaces:
            name_env, is_created = NamespaceEnvironments.objects.get_or_create(
                environment=environment,
                namespace=namespace,
            )
            if is_created:
                name_env.save()

        print 'Added "intranet testing" to %s' % namespaces
