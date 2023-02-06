import copy
import typing


def get_dict_copy_with_edit_items(
        dict_: typing.Dict[str, typing.Any],
        update_items: typing.Dict[str, typing.Any] = None,
        deleted_keys: typing.List[str] = None,
):
    """
    Copy dict, add new items and delete keys
    May working with nested dicts (keys are separated by a dot)

    :param dict_:
    :param update_items:
    :param deleted_keys:
    :return:
    """
    update_items = update_items or {}
    deleted_keys = deleted_keys or []
    assert not set(update_items) & set(deleted_keys)

    new_dict = copy.deepcopy(dict_)

    # Add new key-value to new_dict
    for key_to_set, value in update_items.items():
        nested_keys = key_to_set.split('.')
        obj_set_to: typing.Union[typing.Dict, typing.Any] = new_dict
        for key in nested_keys[:-1]:
            obj_set_to = obj_set_to.get(key)
            if not isinstance(obj_set_to, dict):
                raise TypeError(f'An object with key {key} is not a dict')
        obj_set_to[nested_keys[-1]] = value

    # Delete key from new_dict
    for key_to_remove in deleted_keys:
        nested_keys = key_to_remove.split('.')
        obj_deleted_from: typing.Union[typing.Dict, typing.Any] = new_dict
        for key in nested_keys[:-1]:
            obj_deleted_from = obj_deleted_from.get(key)
            if not isinstance(obj_deleted_from, dict):
                raise TypeError(f'An object with key {key} is not a dict')
        del obj_deleted_from[nested_keys[-1]]
    return new_dict
