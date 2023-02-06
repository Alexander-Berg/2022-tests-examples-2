# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import SelectiveMixin


class SandboxCiWeb4TestTask(SelectiveMixin):
    """
    Абстрактная базовая таска для hermione-тестов Серпа (serp/web4)
    """
    project_name = 'web4'
