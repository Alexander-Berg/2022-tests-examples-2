from __future__ import print_function

from taxi.core import async
from taxi.core import db
from taxi.internal import experiment_manager


RULE_NAME = 'card_tester'


@async.inline_callbacks
def main():
    yield _remove_experiment()
    yield _insert_experiment()


@async.inline_callbacks
def _remove_experiment():
    query = {
        '_id': experiment_manager.CONFIG_SET_USER_EXPERIMENTS,
    }
    update = {
        '$pull': {
            'rules': {
                'name': RULE_NAME,
            }
        }
    }
    result = yield db.static.update(query, update)
    print('remove', result)


@async.inline_callbacks
def _insert_experiment():
    query = {
        '_id': experiment_manager.CONFIG_SET_USER_EXPERIMENTS,
    }
    update = {
        '$push': {
            'rules': {
                'name': RULE_NAME,
                'user_id_last_digits': [
                    'b67b2cd656d64253afab25bc0ce4d707',
                    'd56f0ca9e075484db97f4351f175124b',
                    '4c93cd21e4b5403b96c6b1eabbf75634',
                    'a848f487bf8c499d8b6212ff38699b85',
                    'd15d4433136d4d8dbd69cf121149f591',
                    'dc957193ef7742c29daa202d8d41d1d6',
                    '27afa63815ad48b6b04e27c36b625049',
                    'dd6411d6e6a24e8192e26dfd677a3a1c',
                    'a323feb73c9d44a4844d093dbd6636c4',
                    'ab18b7102e4e41f1bfa21d575523ac30',
                    '04dc7c42582a477cb767d28b91aed68d',
                    '630cf5de967f4a419df0ec9ef9c92320',
                    '01708794f6964bbbacdd88ebcd432f26',
                    '8a121934f3c94e84ba38ec24ef03e5c0',
                    'f801d6dfd0ff4a318fb385eaa5a29ea2',
                    '26f67ea23c434f8c94c33df3ff346bd2',
                    '5d85a8ef943d4d4eada41ae8b96541ca',
                    '48e2af14543b49e4aaed7e741042434f',
                    'dd278ed36655431683b646263f691602',
                    '71f78ef6c48c48cb9717ec24f5c20e85',
                    '248cbe73a94e4c2eb93fa759e2c9f938',
                    '89f1c557cb124716a78db7df247d82bf',
                    '169fc4ff8dab4469a0e044f2dcee02bd',
                    '2d80b7e50b30470abfc2da04ad9038cb',
                    '440c7b817b8447c7b8f022a58ed6f649',
                    'ef07c8189413432d9c013054d9664324',
                    '7ba2857fd2c941718edbc802be561cf7',
                    '3d98886ccbc64b9b9c542de669a9bda6',
                    '9ed7fac9b4d04b60824e4d2d58083623',
                    'b662bcf6a5704b2f830b72593de6600a',
                    '329ff2817c17431abbb0ebc2541fa241',
                ]
            }
        }
    }
    result = yield db.static.update(query, update)
    print('insert', result)


if __name__ == '__main__':
    main()
