import logging

from kazoo.exceptions import NodeExistsError, NoNodeError

import metrika.admin.python.zooface.recursive_deleter.lib as lib


def execute_query(pg_client, query, result=False):
    cursor = pg_client.cursor()
    try:
        cursor.execute(query)
        if result:
            result = cursor.fetchall()
        else:
            result = None
    except Exception:
        pg_client.rollback()
        raise
    else:
        pg_client.commit()
    return result


def insert_task(pg_client, node: str):
    return execute_query(
        pg_client,
        f"""
        INSERT INTO tasks (created, "group", environment, node)
        VALUES (NOW(), 'recipe', 'testing', '{node}') RETURNING id
        """,
        result=True
    )[0]['id']


def cancel_task(pg_client, id: int):
    execute_query(pg_client, f"UPDATE tasks SET status = 'STOPPING' WHERE id = {id}")


def get_task(pg_client, id: int):
    return execute_query(pg_client, f"SELECT * FROM tasks WHERE id = {id}", result=True)[0]


def create_tree(helper: lib.DeleteHelper, tree, prefix='/'):
    for node, childs in tree.items():
        try:
            helper.zk_client.create(f'{prefix}/{node}')
        except NodeExistsError:
            pass

        create_tree(helper, childs, f'{prefix}/{node}')


def dump_tree(helper: lib.DeleteHelper, path):
    if path == '/':
        root = result = {}
    else:
        name = path.split('/')[-1]
        root = {name: {}}
        result = root[name]

    try:
        for child in helper.zk_client.get_children(path):
            result.update(dump_tree(helper, f'{path}/{child}'))
    except NoNodeError:
        return {}

    return root


class ApiMock:
    def __init__(self, pg_client):
        self.pg_client = pg_client

    def update_task(self, task, **fields):
        logging.debug('Updating task %s: %s', task, fields)
        if not get_task(self.pg_client, task['id']):
            raise Exception()
        for k, v in fields.items():
            task[k] = v
        execute_query(self.pg_client, "UPDATE tasks SET {} WHERE id = {}".format(
            ', '.join(f"{k}='{v}'" for k, v in fields.items()),
            task['id']
        ))

    def get_task(self, environment, group, task_id):
        return get_task(self.pg_client, task_id)

    def get_tasks(self, active=True):
        statuses = ['ENQUEUED', 'EXECUTING', 'STOPPING'] if active else ['STOPPING']
        statuses = ', '.join(f"'{status}'" for status in statuses)
        return execute_query(self.pg_client, f"SELECT * FROM tasks WHERE status in ({statuses})", result=True)
