import argparse
from xml.etree import ElementTree

FASTCGI_SOCKET = '/tmp/tests-{project}@@WORKER_SUFFIX@@.sock'
FASTCGI_PIDFILE = 'testenv/{project}@@WORKER_SUFFIX@@.pid'
FASTCGI_MONGO_MAP = {
    'mongo-archive': 'archive',
    'mongo-communications': 'communications',
    'mongo-corp': 'corp',
    'mongo-localizations': 'localizations',
    'mongo-minor': 'noncritical',
    'mongo-subventions': 'subvention_reasons',
    'mongo-parks': 'parks',
    'mongo-taxi': 'taxi',
    'mongo-gprstimings': 'gprstimings',
    'mongo-logs': 'logs',
    'mongo-user-communication': 'user_communication',
    'mongo-users': 'users',
    'mongo-phones_confirms': 'phones_confirms',
    'mongo-misc': 'misc',
    'mongo-geofence': 'geofence',
    'mongo-orderhistory': 'orderhistory',
    'mongo-drivers': 'drivers',
    'mongo-cars': 'cars',
}

# Force console logger
XML_LOGGER_PATCH = """
<patch>
  <append path="./components/component[@name='logger-component']">
    <output>console</output>
  </append>
</patch>
"""

XML_TESTS_CONTORL_PATCH = """
<patch>
  <append path="./components">
    <component name="tests-control" type="{component_name}:tests-control">
      <mockserver>http://@@MOCKSERVER@@/</mockserver>
      <testpoint_url>http://@@MOCKSERVER@@/testpoint</testpoint_url>
      <testpoint_timeout_ms>60000</testpoint_timeout_ms>
      <httpclient_timeout_ms>60000</httpclient_timeout_ms>
      <cache_update_disabled>1</cache_update_disabled>
    </component>
  </append>
  <append path="./handlers">
    <handler url="/tests/control" pool="work_pool" id="tests-control">
      <component name="tests-control"/>
    </handler>
  </append>
</patch>
"""

XML_YT_COMPONENT_PATCH = """
<patch>
  <append path="./components/component[@name='yt-component']">
    <yt_clusters>yt-test</yt_clusters>
    <yt_clusters>yt-repl</yt_clusters>
  </append>
</patch>
"""

# List of projects that require yt-component
PROJECTS_WITH_YT_COMPONENT = (
    'taxi-chat',
    'taxi-archive-api',
    'taxi-driver-protocol',
    'taxi-promotions',
    'taxi-protocol-external-api',
    'taxi-protocol',
    'taxi-feedback',
)

XML_LOGBROKERTEST_COMPONENT_PATCH = """
<patch>
  <append path="./components">
    <component
        name="lb-consumer-test" type="{component_name}:lb-consumer-test">
      <testpoint_url>@@MOCKSERVER@@/testpoint</testpoint_url>
      <testpoint_timeout_ms>60000</testpoint_timeout_ms>
    </component>
  </append>
  <append path="./handlers">
    <handler url="/logbroker/test/.*" pool="work_pool" id="lb-consumer-test">
      <component name="lb-consumer-test"/>
    </handler>
  </append>
</patch>
"""

XML_CONFIGS_SERVICE_TIMEOUT_PATCH = """
<patch>
  <append path="./components/component[@name='config']">
    <timeout_ms>5000</timeout_ms>
  </append>
</patch>
"""

# List of projects that require logbroker test handler + component
PROJECTS_WITH_LOGBROKERTEST_COMPONENT = ('taxi-graph',)


def _apply_patch(tree, patch_str):
    patch = ElementTree.fromstring(patch_str)
    for patch_node in patch:
        if patch_node.tag == 'append':
            node = tree.find(patch_node.attrib['path'])
            assert node is not None, 'patch:' + patch_str
            for patch in patch_node:
                node.insert(0, patch)
    return tree


def patch_module_path(tree, alias, path):
    is_set = False
    for node in tree.findall('./modules/module[@name=\'%s\']' % alias):
        node.attrib['path'] = path
        is_set = True
    if not is_set:
        raise RuntimeError('No module with name %s found' % alias)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project', help='Project name', default='taxi-protocol',
    )
    parser.add_argument(
        '--secdist-path',
        help='Path to secdist file',
        default='configs/secdist.json',
    )
    parser.add_argument(
        '--fastcgi-module',
        help='Path to fastcgi module',
        default='build/protocol/lib/libyandex-taxi-protocol-cxx.so',
    )
    parser.add_argument(
        '--fastcgi-module-alias', help='Module alias within fastcgi config',
    )
    parser.add_argument(
        '--configs-fallback-path',
        help='Path to configs service fallback',
        default='build/common/generated/fallback/configs.json',
    )
    parser.add_argument('--build-path', help='Path to current build directory')
    parser.add_argument('input', help='Source fastcgi.conf')
    parser.add_argument('output', help='Patched fastcgi.conf')
    args = parser.parse_args()

    tree = ElementTree.parse(args.input)

    # Use random port for monitor
    for node in tree.findall('./daemon/monitor_port'):
        node.text = '0'
    for node in tree.findall('./daemon/endpoint/socket'):
        node.text = FASTCGI_SOCKET.format(project=args.project)
    for node in tree.findall('./daemon/pidfile'):
        node.text = FASTCGI_PIDFILE.format(project=args.project)

    if args.fastcgi_module_alias:
        fastcgi_alias = args.fastcgi_module_alias
    else:
        fastcgi_alias = args.project

    patch_module_path(tree, fastcgi_alias, args.fastcgi_module)

    for node in tree.findall(
            './components/component[@name=\'secdist\']/config',
    ):
        node.text = args.secdist_path
    for node in tree.findall('./components/component/secdist'):
        node.text = args.secdist_path
    configs_fallback = './components/component[@name=\'config\']/fallback_path'
    for node in tree.findall(configs_fallback):
        node.text = args.configs_fallback_path
    configs_caches_fallback = (
        './components/component[@name=\'caches\']/fallback_path'
    )
    for node in tree.findall(configs_caches_fallback):
        node.text = args.configs_fallback_path
    if tree.find('./components/component[@name=\'config\']'):
        tree = _apply_patch(tree, XML_CONFIGS_SERVICE_TIMEOUT_PATCH)
    for node in tree.findall(
            './components/component[@type=\'taxi-protocol:mongo-client\']',
    ):
        for child in node:
            node.remove(child)
        child = ElementTree.Element('dbalias')
        child.text = FASTCGI_MONGO_MAP[node.attrib['name']]
        node.append(child)

    # Disable graphite client
    for node in tree.findall(
            './components/component[@name=\'graphite-client\']/port',
    ):
        node.text = '0'

    tree = _apply_patch(
        tree, XML_LOGGER_PATCH.format(component_name=args.project),
    )

    tree = _apply_patch(
        tree, XML_TESTS_CONTORL_PATCH.format(component_name=fastcgi_alias),
    )

    if args.project in PROJECTS_WITH_YT_COMPONENT:
        tree = _apply_patch(tree, XML_YT_COMPONENT_PATCH)

    if args.project in PROJECTS_WITH_LOGBROKERTEST_COMPONENT:
        tree = _apply_patch(
            tree,
            XML_LOGBROKERTEST_COMPONENT_PATCH.format(
                component_name=fastcgi_alias,
            ),
        )

    tree.write(args.output)


if __name__ == '__main__':
    main()
