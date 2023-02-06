package configmock

import (
	yaml "gopkg.in/yaml.v2"

	"a.yandex-team.ru/noc/puncher/config"
)

var tcText = `
daemon:
  listen: :8080
  self_api_url: http://localhost:8080
  macrosd_url: http://localhost:8083
  usersd_url: http://localhost
  requestsd_url: http://localhost
  rulesd_url: http://localhost:8088

imported:
  listen: :8081
  period: 3600
  usersd_url: http://localhost
  rulesd_url: http://localhost:8088
  requestsd_url: http://localhost:8087
  macrosd_url: http://localhost:8083

exportd:
  listen: :8082
  period: 3600
  time_zone: Europe/Moscow
  cparser: /bin/false
  usersd_url: http://localhost
  rulesd_url: http://localhost:8088
  macrosd_url: http://localhost:8083
  cvs_checkout_dir: /tmp/cvs
  cvs_commit_dir: /tmp/cvs-write

macrosd:
  listen: :8083
  period: 600
  priority_dns_pool_limit: 4
  cvs_checkout_dir: /tmp/cvs-macrosd

startrek_watcher:
  listen: :8084
  usersd_url: http://localhost
  requestsd_url: http://localhost

usersd:
  listen: :8085
  period: 3600
  macrosd_url: http://localhost:8083
  rulesd_url: http://localhost:8088

requestsd:
  listen: :8087
  rpc_timeout: 500ms
  public_puncher_url: http://localhost
  time_zone: Europe/Moscow
  templates_dir: /tmp/templates
  rulesd_url: http://localhost:8088

rulesd:
  listen: :8088

rules_cauth:
  listen: :8086
  period: 300
  dns_max_attempts: 3
  usersd_url: http://localhost:8085
  rulesd_url: http://localhost:8088
  macrosd_url: http://localhost:8083
  cvs_checkout_dir: /tmp/cvs-cauth
  hbf_rules_url: http://man1-hbf3.yndx.net/dump-dummy-rules

rules_target: { path: rules }

data_targets:
  department: { path: department.inc }
  wiki: { path: wiki.inc }
  service: { path: service.inc }
  servicerole: { path: servicerole.inc }
  vpnuser: { path: vpnuser.inc }
  mobile: { path: mobile.inc }
  project: { path: project.inc }
  role: { path: role.inc }
  mdm: { path: mdm.inc }
  idm: { path: idm.inc }
  staffrole: { path: "staffrole.inc" }

bot:
  url: http://localhost/
  token: 123456

conductor:
  api_groups_url: http://localhost/
  api_groups_export_url: http://localhost/
  api_v1_url: http://localhost/
  group_url: http://localhost/
  token: 123456

calendar:
  base_url: http://localhost/
  timeout: 10s
  client_id: 123456

cauth:
  puncher_rules_url: http://localhost/
  dial_timeout: 2s
  tls_handshake_timeout: 2s
  timeout: 30s
  certificate_file: /nonexistent
  key_file: /nonexistent
  rules_path: cauth-rules

cms:
  groups_url: http://localhost/

cvs:
  cvsroot: /opt/CVSROOT
  identity_file: /nonexistent
  sections_dir: sections-test
  balancers_dir: balancers
  router_fw_dir: /noc/routers/fw-test
  dns_cache_file: /noc/routers/fw/router.dnscache.full
  rules_inc_path: /noc/balancers/iptables/rules.inc
  rt_sections_dir: /noc/routers/fw/sections/

dns:
  servers:
    - 127.0.0.1
  pool_limit: 20
  retry: 3
  dial_timeout: 2s
  read_timeout: 2s
  write_timeout: 2s

golem:
  get_all_resp_url: http://localhost/
  get_host_resp_url: http://localhost/
  object_search_url: http://localhost/
  hostinfo_url: http://localhost/

idm:
  system_url: http://localhost/
  api_url: http://localhost/
  dial_timeout: 2s
  tls_handshake_timeout: 2s
  timeout: 120s
  certificate_file: /nonexistent
  key_file: /nonexistent
  token: 123456

ldap:
  url: example.yandex.ru
  username: "CN=Puncher,DC=yandex,DC=ru"
  password: "qwerty"

mdm:
  username: puncher
  password: qwerty
  url: http://localhost/
  timeout: 30s

mongodb:
  hosts:
    - localhost
  direct: false
  database: puncher_test
  user: robot
  password: letmein
  pool_limit: 128

racktables:
  macros_url: http://localhost/
  search_url: http://localhost/
  macro_resp_url: http://localhost/
  golem_slb_list_url: http://localhost/
  nets_by_project_url: http://localhost/
  sections_url: http://localhost/
  vm_projects_url: http://localhost/

securityfw:
  url: svn+ssh://localhost/securityfw
  identity_file: /nonexistent
  data_dir: /tmp/securityfw

staff:
  api_v3_url: http://localhost/
  newhire_api_url: http://localhost/
  token: 123456
  retry: 3

startrek:
  api_v2_url: http://localhost/
  timeout: 30s
  queue: PUNCHER
  token: 123456

users:
  admin_users:
    - "%admin-user%"
  super_users:
    - "%super-user%"
  noc_users:
    - "%noc-user%"
`

func NewTestConfig() *config.Service {

	cs := &config.Service{}
	err := yaml.Unmarshal([]byte(tcText), cs)
	if err != nil {
		panic(err)
	}

	return cs
}
