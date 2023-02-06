tls: true
insecure: true
key: "/crt/server.key"
cert: "/crt/server.crt"
hosts:
  {{ FLEET_HOST }}:
    url: "https://{{ HEC_HOST }}:{{ HEC_PORT }}/services/collector"
    token: "{{ HEC_OSQUERY_TOKEN }}"
    enroll_secret: {{ ENROLL_SECRET }}
    insecure_enroll: true
