from __future__ import print_function

import logging

import time
import urlparse
import requests
import simplejson as json
import itertools
import pprint
import yaml

DC = {
    'vla': {
        'yp': 'https://vla.yp.yandex.net:8443',
        'vmproxy': 'https://vmproxy.vla-swat.yandex-team.ru',
    },
    'man': {
        'yp': 'https://man.yp.yandex.net:8443',
        'vmproxy': 'https://vmproxy.man-swat.yandex-team.ru',
    },
    'sas': {
        'yp': 'https://sas.yp.yandex.net:8443',
        'vmproxy': 'https://vmproxy.sas-swat.yandex-team.ru',
    },
    'test': {
        'yp': 'https://sas-test.yp.yandex.net:8443',
        'vmproxy': 'https://dev-vmproxy.n.yandex-team.ru'
    },
    'myt': {
        'yp': 'https://myt.yp.yandex.net:8443',
        'vmproxy': 'https://vmproxy.myt-swat.yandex-team.ru',
    },
    'iva': {
        'yp': 'https://iva.yp.yandex.net:8443',
        'vmproxy': 'https://vmproxy.iva-swat.yandex-team.ru',
    },
}


def check_dc(dc):
    if dc not in DC:
        raise Exception('Unknown dc "%s", allowed are: %r' % (dc, DC.keys()))
    return True


class YpClient(object):
    def __init__(self, dc, token):
        check_dc(dc)

        self.dc = dc
        self.yp_oauth_token = token

    def send_request(self, request, url):
        return requests.post(
            url, data=json.dumps(request),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'OAuth %s' % (self.yp_oauth_token,)
            }
        )

    def check_result(self, result):
        if result.status_code != 200:
            logging.warning('yp request failed with code: %d', result.status_code)
            logging.debug('response headers: %r', result.headers)

            if 'x-yt-response-message' in result.headers:
                raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'],))
            else:
                raise Exception('YP request error (status code %d)' % (result.status_code,))

    def get_object(self, object_type, object_id, selectors):
        request = {
            'object_type': object_type,
            'filter': {
                'query': '[/meta/id] = "%s"' % (object_id,),
            },
            'selector': {
                'paths': selectors
            }
        }

        url = '%s/ObjectService/SelectObjects' % (DC[self.dc]['yp'],)

        result = self.send_request(request, url)
        self.check_result(result)

        return result

    def request_eviction(self, object_id):
        request = {
            'object_type': 'pod',
            'object_id': object_id,
            'set_updates': [
                {
                    'path': '/control/request_eviction',
                    'value': {'message': 'Acknowledged by evacuate'}
                },
            ]
        }
        url = '%s/ObjectService/UpdateObject' % (DC[self.dc]['yp'],)

        result = self.send_request(request, url)
        self.check_result(result)

        return True

    def acknowledge_eviction(self, object_type, object_id, resources):
        request = {
            'object_type': object_type,
            'object_id': object_id,
            'set_updates': [
                {
                    'path': '/control/acknowledge_eviction',
                    'value': {'message': 'Acknowledged by evacuate'}
                },
                {
                    'path': '/spec/iss/instances/0/entity/instance/resources',
                    'value': resources
                },
            ]
        }

        url = '%s/ObjectService/UpdateObject' % (DC[self.dc]['yp'],)

        result = self.send_request(request, url)
        self.check_result(result)

        return True


def get_pods_for_eviction(dc, yp_oauth_token, production=False):
    check_dc(dc)

    if production:
        query = '[/labels/deploy_engine] = "QYP" and [/status/eviction/state] = "requested"'
    else:
        query = '[/labels/deploy_engine] = "QYP" and [/labels/qyp/eviction/force] = true'

    return select_pods(
        dc, yp_oauth_token,
        query,
        filter_node_status=True
    )


def get_pod_eviction_label(dc, yp_oauth_token, pod_id, path='', base_path='/labels/qyp/eviction'):
    check_dc(dc)

    request = {
        'object_type': 'pod',
        'filter': {
            'query': '[/meta/id] = "%s"' % (pod_id, ),
        },
        'selector': {
            'paths': [
                '%s%s' % (base_path, path)
            ]
        }
    }

    url = '%s/ObjectService/SelectObjects' % (DC[dc]['yp'], )
    result = requests.post(
        url, data=json.dumps(request),
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'OAuth %s' % (yp_oauth_token, )
        }
    )

    if result.status_code != 200:
        logging.warning('yp request failed with code: %d', result.status_code)
        logging.debug('response headers: %r', result.headers)

        if 'x-yt-response-message' in result.headers:
            raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'], ))
        else:
            raise Exception('YP request error (status code %d)' % (result.status_code, ))

    result = result.json()

    assert 'results' in result, 'Unable to find pod in YP'
    assert len(result['results']) == 1, 'Unable to find pod in YP'
    assert len(result['results'][0]['values']) == 1, 'Unable to find pod labels in YP'

    label = result['results'][0]['values'][0]

    return label


def update_pod_eviction_label(dc, yp_oauth_token, pod_id, value, path='', base_path='/labels/qyp/eviction'):
    check_dc(dc)

    request = {
        'object_type': 'pod',
        'object_id': pod_id,
        'set_updates': [{
            'path': '%s%s' % (base_path, path),
            'value': value
        }]
    }

    url = '%s/ObjectService/UpdateObject' % (DC[dc]['yp'], )

    result = requests.post(
        url, data=json.dumps(request),
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'OAuth %s' % (yp_oauth_token, )
        }
    )

    if result.status_code != 200:
        logging.warning('yp request failed with code: %d', result.status_code)
        logging.debug('response headers: %r', result.headers)

        if 'x-yt-response-message' in result.headers:
            raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'], ))
        else:
            raise Exception('YP request error (status code %d)' % (result.status_code, ))

    return True


def init_qyp_eviction_label(dc, yp_oauth_token, pod_id):
    check_dc(dc)

    for base in ('/labels/qyp', '/labels/qyp/eviction'):
        dct = get_pod_eviction_label(dc, yp_oauth_token, pod_id, base_path=base)
        if dct is None:
            update_pod_eviction_label(dc, yp_oauth_token, pod_id, {}, base_path=base)


def select_pods(dc, yp_oauth_token, query, filter_node_status=False):
    check_dc(dc)

    request = {
        'object_type': 'pod',
        'filter': {
            'query': query
        },
        'selector': {
            'paths': [
                '/meta/id',                     # 0
                '/meta/pod_set_id',             # 1
                '/status/dns',                  # 2
                '/status/scheduling/node_id',   # 3
                '/status/eviction',             # 4
                '/status/ip6_address_allocations',  # 5
                '/labels',                      # 6
                '/annotations',                 # 7
                '/spec/ip6_address_requests',   # 8
                '/spec/resource_requests',      # 9
                '/spec/disk_volume_requests',   # 10
                '/spec/iss/instances/0/properties',  # 11
            ]
        }
    }

    url = '%s/ObjectService/SelectObjects' % (DC[dc]['yp'], )
    result = requests.post(
        url, data=json.dumps(request),
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'OAuth %s' % (yp_oauth_token, )
        }
    )

    if result.status_code != 200:
        logging.warning('yp request failed with code: %d', result.status_code)
        logging.debug('response headers: %r', result.headers)

        if 'x-yt-response-message' in result.headers:
            raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'], ))
        else:
            raise Exception('YP request error (status code %d)' % (result.status_code, ))

    pods_for_eviction = []

    json_result = result.json()

    if 'results' not in json_result:
        # No pods for eviction as of now
        return pods_for_eviction

    for item in json_result['results']:
        disk_volumes = item['values'][10]
        requested_volume = None
        for volume in disk_volumes:
            if volume.get('labels', {}).get('mount_path', None) == '/qemu-persistent':
                requested_volume = volume
                break

        network_ids = set()
        net_requests = item['values'][8]
        for net in net_requests:
            if net.get('labels', {}).get('owner', None) == 'vm':
                network_ids.add(net['network_id'])

        assert len(network_ids) == 1
        network_id = network_ids.pop()

        # Detect nat64 if it is set in iss properties
        iss_properties = item['values'][11]
        use_nat64 = False

        for iss_prop in iss_properties:
            if iss_prop['key'] == 'USE_NAT64':
                assert iss_prop['value'] == 'true'
                use_nat64 = True
                break

        # Detect tun v4/v6 if pod has internet address allocation
        address_allocations = item['values'][5]
        use_tun64 = False
        for addressinfo in address_allocations:
            if addressinfo['vlan_id'] == 'backbone':
                if addressinfo.get('internet_address', None):
                    use_tun64 = True
                    break

        pods_for_eviction.append({
            'id': item['values'][0],
            'pod_set_id': item['values'][1],
            'fqdn': [
                item['values'][2]['transient_fqdn'],
                item['values'][2]['persistent_fqdn']
            ],
            'node_id': item['values'][3],
            'eviction': item['values'][4],
            'labels': item['values'][6],
            'owners': {
                'users': item['values'][7]['owners']['logins'],
                'groups': item['values'][7]['owners']['groups']
            },
            'requests': {
                'net': {'network_id': network_id},
                'resource': item['values'][9],
                'disk_volume': requested_volume,
            },
            'use_nat64': use_nat64,
            'use_tun64': use_tun64,
        })

    skip_pods_node_not_in_maintenance = set()

    if filter_node_status:
        nodes_for_eviction = set(pod['node_id'] for pod in pods_for_eviction)
        prepare_maintenance_nodes = set()

        for node in nodes_for_eviction:
            request = {
                'object_type': 'node',
                'filter': {
                    'query': '[/meta/id] = "%s"' % (node, )
                },
                'selector': {
                    'paths': ['/status/hfsm/state']
                }
            }

            url = '%s/ObjectService/SelectObjects' % (DC[dc]['yp'], )
            result = requests.post(
                url, data=json.dumps(request),
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'OAuth %s' % (yp_oauth_token, )
                }
            )

            if result.status_code != 200:
                logging.warning('yp request failed with code: %d', result.status_code)
                logging.debug('response headers: %r', result.headers)

                if 'x-yt-response-message' in result.headers:
                    raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'], ))
                else:
                    raise Exception('YP request error (status code %d)' % (result.status_code, ))

            results = result.json()
            if not results:
                logging.info('Unable to find hfsm state for node "%s" (no result)', node)
                continue

            status = result.json()['results'][0]['values'][0]

            if status != 'prepare_maintenance':
                logging.info('Status of node "%s" is not prepare_maintenance (got "%s"), skipping', node, status)
            else:
                logging.info('Node "%s" has real status "%s"', node, status)
                prepare_maintenance_nodes.add(node)

        for idx, pod in reversed(list(enumerate(pods_for_eviction))):
            if pod['labels'].get('qyp', {}).get('eviction', {}).get('force', False):
                # If eviction was forced -- dont check last update time and prepare maintenance on node
                continue

            if pod['eviction']['last_updated'] > (time.time() - 86400) * (10 ** 6):
                # Do not queue evacuation if eviction request was made less than 24h ago
                # QEMUKVM-622
                logging.info(
                    'Skip "%s" pod eviction: eviction last_updated time is less than 24h ago (%ds ago)',
                    pod['id'], int(time.time() - pod['eviction']['last_updated'] / (10 ** 6))
                )
                del pods_for_eviction[idx]
            else:
                logging.info(
                    'Pod "%s" eviction last_update time is %ds ago',
                    pod['id'], int(time.time() - pod['eviction']['last_updated'] / (10 ** 6))
                )

            if pod['node_id'] not in prepare_maintenance_nodes:
                skip_pods_node_not_in_maintenance.add(pod['id'])

                logging.info(
                    'Maybe skip "%s" pod eviction: node "%s" is not in prepare_maintenance state',
                    pod['id'], pod['node_id']
                )

                # Cant delete pod from pods_for_eviction right here, because we will also check
                # node segment and ignore prepare_maintenance for default segment

    pods_by_pod_set_id = {}
    for pod in pods_for_eviction:
        pods_by_pod_set_id.setdefault(pod['pod_set_id'], []).append(pod)

    skip_pods_no_podset = set()

    for pod_set_id, pods_in_pod_set in pods_by_pod_set_id.iteritems():
        request = {
            'object_type': 'pod_set',
            'filter': {
                'query': '[/meta/id] = "%s"' % (pod_set_id, ),
            },
            'selector': {
                'paths': [
                    '/spec/account_id',
                    '/spec/node_segment_id'
                ]
            }
        }

        url = '%s/ObjectService/SelectObjects' % (DC[dc]['yp'], )
        result = requests.post(
            url, data=json.dumps(request),
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'OAuth %s' % (yp_oauth_token, )
            }
        )

        if result.status_code != 200:
            logging.warning('yp request for pod_set "%s" failed with code: %d', pod_set_id, result.status_code)
            logging.debug('response headers: %r', result.headers)

            if 'x-yt-response-message' in result.headers:
                raise Exception('YP Error: %s' % (result.headers['x-yt-response-message'], ))
            else:
                raise Exception('YP request error (status code %d)' % (result.status_code, ))

        results = result.json()

        if not results:
            logging.info('Unable to find podset "%s", skipping %d pods', pod_set_id, len(pods_in_pod_set))
            for pod in pods_in_pod_set:
                skip_pods_no_podset.add(pod['id'])
            continue

        account_id = results['results'][0]['values'][0]
        node_segment = results['results'][0]['values'][1]

        for pod in pods_in_pod_set:
            pod['account_id'] = account_id
            pod['node_segment'] = node_segment

            if node_segment == 'default':
                # Do not check node==prepare_maintenance for default segment
                # QEMUKVM-582
                skip_pods_node_not_in_maintenance.discard(pod['id'])

    for idx, pod in reversed(list(enumerate(pods_for_eviction))):
        if pod['id'] in skip_pods_no_podset:
            logging.debug('%s: skip (no podset)', pod['id'])
            del pods_for_eviction[idx]
        elif pod['id'] in skip_pods_node_not_in_maintenance:
            logging.debug('%s: skip (node not in prepare_maintenance - %s)', pod['id'], pod['node_id'])
            del pods_for_eviction[idx]

    return pods_for_eviction


def vmproxy_api_call(url, data, oauth_token, extended=False):
    response = requests.post(
        url, data=json.dumps(data),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'OAuth %s' % (oauth_token, )
        }
    )

    if response.headers.get('Content-Type', '') == 'application/json':
        result = json.loads(response.text)
    else:
        result = response.text

    if response.status_code != 200:
        logging.error('vmproxy request fail with code %d', response.status_code)
        logging.error('vmproxy output')
        logging.error(response.text)
        logging.error('vmproxy headers:')
        logging.error(pprint.pformat(response.headers))

        if not extended:
            return False
        else:
            return False, response.status_code, result

    if extended:
        return True, response.status_code, result
    else:
        return result


def vmproxy_get_status(dc, pod_id, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    status_url = urlparse.urljoin(base_url, '/api/GetStatus/')
    return vmproxy_api_call(status_url, {'vm_id': {'pod_id': pod_id}}, vmproxy_oauth_token, extended)


def vmproxy_list_backups(dc, pod_id, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    backups_url = urlparse.urljoin(base_url, '/api/ListBackup/')
    return vmproxy_api_call(backups_url, {'vm_id': pod_id}, vmproxy_oauth_token, extended)


def vmproxy_deallocate_vm(dc, pod_id, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    deallocate_url = urlparse.urljoin(base_url, '/api/DeallocateVm/')
    return vmproxy_api_call(deallocate_url, {'id': pod_id}, vmproxy_oauth_token, extended)


def vmproxy_create_vm(dc, spec, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    createvm_url = urlparse.urljoin(base_url, '/api/CreateVm/')
    return vmproxy_api_call(createvm_url, spec, vmproxy_oauth_token, extended)


def vmproxy_create_vm_with_retries(dc, spec, vmproxy_oauth_token, max_wait):
    status_code = -1
    deadline = time.time() + max_wait

    while time.time() < deadline:
        done, status_code, result = vmproxy_create_vm(dc, spec, vmproxy_oauth_token, extended=True)
        message = result.get('message', 'unknown') if isinstance(result, dict) else None

        if not done:
            logging.debug(
                'CreateVm failed with status code %r and message %r, will try again in 5 secs (for %d secs more)',
                status_code, message, int(deadline - time.time())
            )

            time.sleep(5)
        else:
            break
    else:
        raise Exception('Unable to create new vm: last CreateVm status code was %r' % (status_code, ))


def vmproxy_update_vm(dc, spec, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    updatevm_url = urlparse.urljoin(base_url, '/api/UpdateVm/')
    return vmproxy_api_call(updatevm_url, spec, vmproxy_oauth_token, extended)


def vmproxy_stop_vm(dc, podid, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    action_url = urlparse.urljoin(base_url, '/api/MakeAction/')
    return vmproxy_api_call(action_url, {'vm_id': {'pod_id': podid}, 'action': 5}, vmproxy_oauth_token, extended)


def vmproxy_get_vmspec(dc, podid, vmproxy_oauth_token, extended=False):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    listvm_url = urlparse.urljoin(base_url, '/api/ListYpVm/')
    result, status_code, response = vmproxy_api_call(
        listvm_url, {'query': {'name': podid}},
        vmproxy_oauth_token, extended=True
    )
    if not result:
        if not extended:
            return result
        return result, status_code, response

    for vm in response.get('vms', []):
        if vm['meta']['id'] == podid:
            break
    else:
        if not extended:
            return False
        return False, status_code, response

    if extended:
        return True, status_code, vm
    else:
        return vm


def make_vbox_backup_sandbox_task(dc, pod_id, vmproxy_oauth_token):
    check_dc(dc)
    base_url = DC[dc]['vmproxy']
    create_backup_url = urlparse.urljoin(base_url, '/api/BackupVm/')

    vm_state = vmproxy_get_status(dc, pod_id, vmproxy_oauth_token)
    backups = vmproxy_list_backups(dc, pod_id, vmproxy_oauth_token)

    if vm_state['state']['type'] == 'STOPPED':
        vm_state_generation = vm_state['state']['generation']
    else:
        vm_state_generation = None

    backups = backups.get('backups', [])
    if backups:
        last_backup_info = backups[-1]
    else:
        last_backup_info = None

    if last_backup_info:
        prev_sandbox_task = last_backup_info['spec']['sandboxTaskId']
        prev_backup_generation = last_backup_info['spec']['generation']
    else:
        prev_sandbox_task = None
        prev_backup_generation = None

    try:
        prev_sandbox_task = int(prev_sandbox_task)
    except Exception:
        prev_sandbox_task = None

    if vm_state_generation is not None and vm_state_generation == prev_backup_generation and prev_sandbox_task:
        # VM is stopped and has same generation as latest backup, just wait for current task if needed
        logging.debug('Current vm is stopped and state generation is %r', vm_state_generation)
        logging.debug('Last backup generation is the same generation %r', prev_backup_generation)
        logging.debug('No need to schedule new backup task, will use old instead (#%d)', prev_sandbox_task)

        return prev_sandbox_task

    logging.debug(
        'Vm generation does not match last backup (%s != %s), will need to create new',
        vm_state_generation, prev_backup_generation
    )

    deadline = time.time() + 60

    while time.time() < deadline:
        result, status_code, response_json = vmproxy_api_call(
            create_backup_url, {'vm_id': {'pod_id': pod_id}}, vmproxy_oauth_token, extended=True
        )
        if status_code == 400:
            reason = 'unknown'
            try:
                if 'message' in response_json:
                    reason = response_json['message']
            except Exception:
                pass

            if 'already in progress' in reason:
                try:
                    logging.debug('backup already in progress, will try to grab current backup sandbox task id')
                    return int(last_backup_info['spec']['sandboxTaskId'])
                except Exception:
                    pass

            raise Exception('Unable to schedule vmproxy backup (reason: %s)' % (reason, ))

        elif not result:  # this will be False unless api returned HTTP 200 OK
            time.sleep(5)
            if time.time() >= deadline:
                raise Exception('Unable to schedule vmproxy backup (last http api status code: %r)' % (status_code, ))
            continue

        else:
            logging.info('New backup scheduled (got 200 OK)')
            break

    while True:
        vm_state = vmproxy_get_status(dc, pod_id, vmproxy_oauth_token)

        if not vm_state:
            raise Exception('Unable to get vm state (empty result)')

        backups = vmproxy_list_backups(dc, pod_id, vmproxy_oauth_token)
        backups = backups.get('backups', [])

        if backups:
            last_backup_info = backups[-1]
        else:
            last_backup_info = None

        if last_backup_info:
            sandbox_task = last_backup_info['spec']['sandboxTaskId']
        else:
            sandbox_task = None

        try:
            sandbox_task = int(sandbox_task)
        except Exception:
            sandbox_task = None

        if sandbox_task == prev_sandbox_task:
            logging.debug('Sandbox task didnt changed yet in vmproxy, waiting')
            time.sleep(5)
            continue

        logging.debug('New backup sandbox task found #%d', sandbox_task)
        return sandbox_task


def generate_new_vm_spec(vmspec, vm_state, resid):
    vmspec['meta'].pop('version', None)

    try:
        accessInfo = {
            'vncPassword': vm_state['config']['accessInfo']['vncPassword']
        }
    except Exception as ex:
        logging.warning('Unable to preserve accessInfo: %s', str(ex))
        accessInfo = {}

    vmspec['config'] = {
        'accessInfo': accessInfo,
        'autorun': vm_state['config']['autorun'],
        'disk': {
            'deltaSize': 0,
            'resource': {'rbTorrent': resid},
            'type': 1,  # 0 - qcow2, 1 - raw (qcow2 wo delta)
            'path': '/',
        },
        'id': 'empty',
        'mem': vm_state['config']['mem'],
        'type': 0 if vm_state['config']['type'] == 'LINUX' else 1,  # 0 - linux, 1 - windows
        'vcpu': vm_state['config']['vcpu'],
    }

    return vmspec


def get_qnotifier_tvm_ticket(secret, src, dst):
    import ticket_parser2
    import ticket_parser2.api.v1

    ts = int(time.time())

    tvm_keys = requests.get(
        'https://tvm-api.yandex.net/2/keys?lib_version=%s' % (ticket_parser2.__version__, )
    ).content

    svc_ctx = ticket_parser2.api.v1.ServiceContext(src, secret, tvm_keys)

    ticket_response = requests.post(
        'https://tvm-api.yandex.net/2/ticket/',
        data={
            'grant_type': 'client_credentials',
            'src': src,
            'dst': dst,
            'ts': ts,
            'sign': svc_ctx.sign(ts, dst)
        }
    ).json()

    ticket_for_dst = ticket_response[str(dst)]['ticket']
    return ticket_for_dst


class QnotifierNotAuthorized(Exception):
    pass


def notify_usergroups(tvm_ticket, users, groups, tags, subject, message):
    if not tvm_ticket:
        raise QnotifierNotAuthorized()

    next_is_group = object()
    is_group = False

    for item in itertools.chain(users, [next_is_group], groups):
        if item is next_is_group:
            is_group = True
            continue

        response = requests.post(
            'https://qnotifier.yandex-team.ru/subscriptions/%s' % (item if not is_group else 'group:%s' % (item, ), ),
            headers={
                'X-Ya-Service-Ticket': tvm_ticket,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            data=json.dumps({
                'tags': tags,
                'options': {}
            })
        )

        if response.status_code in (401, 403):
            raise QnotifierNotAuthorized()

        if response.status_code == 500:  # seems to be ok, we need to log response headers + content for debug
            logging.warning('qnotifier subscribe returned HTTP500')
            logging.warning('headers: %r', response.headers)
            logging.warning('content: %r', response.content)
            raise Exception('Got HTTP500 during notification subscribtion')

        assert response.status_code in (204, 402), \
            'Invalid qnotifier response (code %d), was trying to subscribe %s (group: %s)' % (
                response.status_code, item, is_group
            )

    response = requests.post(
        'https://qnotifier.yandex-team.ru/events/',
        headers={
            'X-Ya-Service-Ticket': tvm_ticket,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        data=json.dumps({
            'tags': tags,
            'message': message,
            'extra': {
                'subject': subject,
                'from_email': 'QYP <noreply@qyp.yandex-team.ru>'
            }
        })
    )

    if response.status_code == 500:  # seems to be ok, we need to log response headers + content for debug
        logging.warning('qnotifier subscribe returned HTTP500')
        logging.warning('headers: %r', response.headers)
        logging.warning('content: %r', response.content)
        raise Exception('Got HTTP500 during notification')

    assert response.status_code == 204, 'Unable to notify: status code %d' % (response.status_code, )


QNOTIFIER_TVM_TICKET = None


def notify_usergroups_autotvm((secret, dst, src), (notify_args)):
    global QNOTIFIER_TVM_TICKET

    for i in range(1, 11):
        try:
            try:
                notify_usergroups(QNOTIFIER_TVM_TICKET, *notify_args)
                return True
            except QnotifierNotAuthorized:
                QNOTIFIER_TVM_TICKET = get_qnotifier_tvm_ticket(secret, dst, src)
                notify_usergroups(QNOTIFIER_TVM_TICKET, *notify_args)
                return True
        except Exception as ex:
            logging.warning('Unable to notify: %s', str(ex))
            time.sleep(i*3)

    return False


def eviction_notify(tvm_info, tags, sb_task_id, steps, podinfo, step_details):
    # steps: [(name, None|0|1), ...]

    total_steps = len(steps)
    everything_ok = True

    for idx, (step_info, active) in enumerate(steps):
        if active is not None:
            current_step = idx + 1
            if not active:  # False
                everything_ok = False
            break
    else:
        current_step = 1

    subject = 'QYP: machine "%s" evacuation %s [%d/%d]' % (
        podinfo['id'],
        'in progress' if everything_ok else 'failed',
        current_step, total_steps
    )

    message = [
        '(This is automatic message, do not reply)',
        '',
        'We are evacuating your QYP machine "{machine_id}" (fqdn: {fqdn_fixed} => {fqdn}), because it has '  # nobr
        'set eviction=requested and underlying node "{node_id}" is in "prepare_maintenance" state.'.format(
            machine_id=podinfo['id'],
            node_id=podinfo['node_id'],
            fqdn=podinfo['fqdn'][0],
            fqdn_fixed=podinfo['fqdn'][1]
        ),
        '',
        'Whole process consist %d steps:' % (total_steps, ),
    ]

    for idx, (step_info, active) in enumerate(steps):
        step_no = idx + 1
        step_msg = '  %d. %-40s' % (idx + 1, step_info)

        if active is None and step_no < current_step:
            step_msg += '<<< DONE'

        if active is not None:
            if active:
                if step_no == len(steps):
                    step_msg += '<<< DONE'  # last step
                else:
                    step_msg += '<<< WE ARE HERE'
            else:
                step_msg += '<<< FAIL!'

        message.append(step_msg)

    if step_details:
        message += [
            '',
            'Step %d details:' % (current_step, ),
        ] + ['  %s' % line for line in step_details]

    message += [
        '',
        'Sandbox task responsive for full evacuation process (and sender of this message):',
        'https://sandbox.yandex-team.ru/task/%d/view' % (sb_task_id, ),
        '',
        'Have a nice day!',
        '',
        '--',
        'rA3eJIbKuH (qyp evacuator service)'
    ]

    full_message = '\n'.join(message)

    return notify_usergroups_autotvm(
        tvm_info, (
            podinfo['owners']['users'], podinfo['owners']['groups'], tags,
            subject, full_message
        )
    )


def format_dict(dct, indent=3, level=0, no_indent_first=False):
    return yaml.safe_dump(dct, default_flow_style=False, indent=indent, allow_unicode=True, encoding='utf-8')
