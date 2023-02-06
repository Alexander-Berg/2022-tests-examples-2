from sandbox.projects.release_machine.components.config_core.jg.cube.lib import internal as internal_cubes


class CloneTestenvDb(internal_cubes.ReleaseMachineInternalSandboxTaskCube):
    TASK = "projects/release_machine/clone_te_db"
    TYPE = "clone_te_db"
    NAME = "clone_te_db"
