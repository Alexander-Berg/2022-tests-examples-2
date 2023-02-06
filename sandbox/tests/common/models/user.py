from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import user as user_controller


def register_user(user_login):  # type: (str) -> str
    user_controller.User.validated(user_login)
    return user_login


def register_robot(robot_login, robot_owners=None):  # type: (str, list[str] or None) -> str
    user_controller.User.validated(robot_login, True)
    if not robot_owners:
        robot_owners = []

    for robot_owner in robot_owners:
        ro = mapping.RobotOwner.objects.with_id(robot_owner)
        if ro is None:
            ro = mapping.RobotOwner(login=robot_owner, robots=[robot_login])
        else:
            ro.robots = sorted(set(ro.robots) | {robot_login})
        ro.save()
    return robot_login
