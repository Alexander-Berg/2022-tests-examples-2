# pylint: disable=no-member
import argparse
import time

import google.protobuf.text_format as proto_text
import grpc
import kikimr.core.protos.flat_scheme_op_pb2 as flat_scheme_op
import kikimr.core.protos.grpc_pb2_grpc as grpc_server
import kikimr.core.protos.msgbus_pb2 as msgbus


RETRY_SLEEP_TIME = 0.1  # 100ms
RETRIES_COUNT = 100  # max wait 10s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True)
    parser.add_argument('--grpc-port', required=True, type=int)
    parser.add_argument('--profile-path', required=True)
    args = parser.parse_args()

    server = '{}:{}'.format(args.host, args.grpc_port)
    channel = grpc.insecure_channel(server)
    server_stub = grpc_server.TGRpcServerStub(channel)

    add_config_item(
        server_stub, 'TableServiceConfig { UseSessionBusyStatus: true }',
    )

    bind_storage_pools(server_stub, 'local', {'dynamic_storage_pool:1': 'hdd'})

    with open(args.profile_path, 'r') as profile:
        add_config_item(server_stub, profile.read())


def perform_request_safe(server_stub, request, method):
    try:
        getattr(server_stub, method)(request)
        return True
    except:  # noqa pylint: disable=bare-except
        return False


def perform_request(server_stub, request, method):
    retries = 0
    while True:
        done = perform_request_safe(server_stub, request, method)
        if done:
            break
        retries += 1
        if retries > RETRIES_COUNT:
            raise RuntimeError(
                'Cannot perform YDB gRPC operation: {}'.format(method),
            )
        time.sleep(RETRY_SLEEP_TIME)


def bind_storage_pools(server_stub, domain_name, spools):
    request = msgbus.TSchemeOperation()
    scheme_transaction = request.Transaction
    scheme_operation = scheme_transaction.ModifyScheme
    scheme_operation.WorkingDir = '/'
    scheme_operation.OperationType = flat_scheme_op.ESchemeOpAlterSubDomain
    domain_description = scheme_operation.SubDomain
    domain_description.Name = domain_name
    for name, kind in spools.items():
        domain_description.StoragePools.add(Name=name, Kind=kind)
    perform_request(server_stub, request, 'SchemeOperation')


def add_config_item(server_stub, config):
    request = msgbus.TConsoleRequest()
    action = request.ConfigureRequest.Actions.add()
    item = action.AddConfigItem.ConfigItem
    proto_text.Parse(config, item.Config)
    perform_request(server_stub, request, 'ConsoleRequest')


if __name__ == '__main__':
    main()
