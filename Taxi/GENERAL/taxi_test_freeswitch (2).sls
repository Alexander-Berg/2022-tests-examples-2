yav:
  ssl_cert: 'sec-01cqs4xzyx552qjthmghakmkvh'
  templates:
    /etc/yandex/mrcp-proxy.key:
      template: 'just_secret_contents.tpl'
      owner: 'root:root'
      mode: '0400'
      secrets: 'sec-01cw6pwchwfh71prj6b924r0aa->SECRET'
    /etc/freeswitch/autoload_configs/ya_speechkit.conf.xml:
      template: 'taxi_freeswitch/ya-speechkit-conf.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01e45rx02njfm8xfah12rrrhvk->SK_API_KEY'
    /etc/yandex/octonode/config-admin.yml:
      template: 'taxi_freeswitch/config-admin.tpl'
      owner: 'root:www-data'
      mode: '0640'
      secrets:
        - sec-01dg2hh4rtbd5d0m6k7j0fwbr9->FREESWITCH_EVENT_SOCKET
        - sec-01dg4r8a9rkh8vnbb1197yg6nh->OCTONODE_MDS_S3
    /root/.fs_cli_conf:
      template: 'taxi_freeswitch/fs-cli.tpl'
      owner: 'root:root'
      mode: '0400'
      secrets: 'sec-01dg2hh4rtbd5d0m6k7j0fwbr9->FREESWITCH_EVENT_SOCKET'
    /etc/freeswitch/directory/default/nekrand.xml:
      template: 'taxi_freeswitch/directory/nekrand.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds5e8y0mvs4aqqkcwzc1nped->DIRECTORY_NEKRAND'
    /etc/freeswitch/sip_profiles/external-ipv6/cipt-iva-trunk.xml:
      template: 'taxi_freeswitch/gateways/cipt-iva-trunk.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/external-ipv6/cipt-myt-trunk.xml:
      template: 'taxi_freeswitch/gateways/cipt-myt-trunk.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/external/robot-uiscom-01.xml:
      template: 'taxi_freeswitch/gateways/robot-uiscom-01.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01efhmkm9ngq4pny6gggqxbast->ROBOT_UISCOM_01'
    /etc/freeswitch/sip_profiles/internal-ipv6/cipt-taxi-sbc1.xml:
      template: 'taxi_freeswitch/gateways/cipt-taxi-sbc1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/cipt-taxi-sbc2.xml:
      template: 'taxi_freeswitch/gateways/cipt-taxi-sbc2.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-m9-qapp1.xml:
      template: 'taxi_freeswitch/gateways/taxi-m9-qapp1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-mar-qapp1.xml:
      template: 'taxi_freeswitch/gateways/taxi-mar-qapp1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-myt-qapp1.xml:
      template: 'taxi_freeswitch/gateways/taxi-myt-qapp1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-std-sbc-mon.xml:
      template: 'taxi_freeswitch/gateways/taxi-std-sbc-mon.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-std-sbc1.xml:
      template: 'taxi_freeswitch/gateways/taxi-std-sbc1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/ya-in-01.xml:
      template: 'taxi_freeswitch/gateways/ya-in-01.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/ya-in-02.xml:
      template: 'taxi_freeswitch/gateways/ya-in-02.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/cipt-std-fs-sbc1.xml:
      template: 'taxi_freeswitch/gateways/cipt-std-fs-sbc1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/octonode-gw-m9b.xml:
      template: 'taxi_freeswitch/gateways/octonode-gw-m9b.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-std-monsbc.xml:
      template: 'taxi_freeswitch/gateways/taxi-std-monsbc.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/cipt-m9-monsbc.xml:
      template: 'taxi_freeswitch/gateways/cipt-m9-monsbc.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-kzata-sbc1.xml:
      template: 'taxi_freeswitch/gateways/taxi-kzata-sbc1.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-kzata-sbc2.xml:
      template: 'taxi_freeswitch/gateways/taxi-kzata-sbc2.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-m9-provreg3.xml:
      template: 'taxi_freeswitch/gateways/taxi-m9-provreg3.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-std-provreg3.xml:
      template: 'taxi_freeswitch/gateways/taxi-std-provreg3.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
    /etc/freeswitch/sip_profiles/internal-ipv6/taxi-phonecall.xml:
      template: 'taxi_freeswitch/gateways/taxi-phonecall-test.tpl'
      owner: 'freeswitch:root'
      mode: '400'
      secrets: 'sec-01ds0g4r1jtmr09gqxm9j5ykps->DUMMY_SECRET'
