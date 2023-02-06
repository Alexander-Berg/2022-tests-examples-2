insert into services (id, name, cluster_type) values
(139, 'hejmdal', 'nanny');

insert into branches (id, service_id, env, direct_link, branch_name) values
(1, 139, 'stable', 'hejmdal_dirlink', 'hejmdal_branch_stable');

insert into branch_domains (branch_id, solomon_object, name) values
(1, 'hejmdal_yandex_net', 'hejmdal.yandex.net'),
(1, 'hejmdal_taxi_yandex_net', 'hejmdal.taxi.yandex.net'),
(1, 'hejmdal_yandex_net_view_POST', 'hejmdal.yandex.net/view_POST'),
(1, 'hejmdal_yandex_net_view2_GET', 'hejmdal_yandex_net_view2_GET'),
(1, 'TOTAL', 'TOTAL');
