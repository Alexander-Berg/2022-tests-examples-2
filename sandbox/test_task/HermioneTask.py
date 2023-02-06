# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseTask


class HermioneTask(BaseTask):
    """
    Класс используется в качестве родителя корневой таски hermione
    для того, чтобы избежать циклических зависимостей в PEERDIR
    """
