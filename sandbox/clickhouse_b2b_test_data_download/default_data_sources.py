# coding=utf-8
DATA_SOURCES = {
    'sources': [
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'hits_all',
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'hits_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'visits_all',
            'date-column': 'StartDate',
            'override-merge': '^visits$'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'visits_layer',
            'metadata-only': True,
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'click_storage',
            'date-column': 'Date'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'user_param2_all',
            'date-column': 'UpdateTime'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'user_param2_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'offline_calls_log',
            'date-column': 'EventDate',
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'orders_to_counters',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'mouse_clicks_all',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'mouse_clicks_layer',
            'override-cluster': "logs_all",
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'mouse_clicks_layer_10',
            'override-cluster': "logs_all",
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'mouse_clicks_layer_100',
            'override-cluster': "logs_all",
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtgiga',
            'database': 'default',
            'table': 'mouse_clicks_layer_1000',
            'override-cluster': "logs_all",
            'date-column': 'EventDate'
        },

        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'client_events_all',
            'date-column': 'StartDate',
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'client_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'generic_events_all',
            'date-column': 'StartDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'generic_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'events_all',
            'date-column': 'StartDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'tracking_events_all',
            'date-column': 'StartDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'tracking_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'clicks_all',
            'date-column': 'ClickDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'clicks_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'open_events_all',
            'date-column': 'StartDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'open_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'total_notification_events_all',
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'total_notification_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'postbacks_notifications_all',
            'date-column': 'ConversionDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'postbacks_notifications_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'profiles_attributes_all',
            'date-column': 'UpdateDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'profiles_attributes_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'total_push_token_events_all',
            'date-column': 'StartDate'  # ?FakeDate?
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'total_push_token_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'revenue_events_all',
            'date-column': 'EventDate'
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'revenue_events_layer',
            'metadata-only': True
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'devices_client_events_all',
            'date-column': None  # тут тоже FakeDate, но есть toDate(toDateTime(EventTimestamp)) as EventDate
        },
        {
            'cluster-mtapi': 'mtmobgiga',
            'database': 'mobile',
            'table': 'devices_client_events_layer',
            'metadata-only': True
        },
        {
            "cluster-mtapi": "mtchvip",
            "database": "feriat",
            "table": "alexkuk_hosts",
            "date-column": None
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "metadata-only": True,
            "table": "total_crash_events_layer",
            "database": "mobile"
        },
        {
            "date-column": "StartDate",
            "cluster-mtapi": "mtmobgiga",
            "table": "total_crash_events_all",
            "database": "mobile"
        },
        {
            "cluster-mtapi": "mtgiga",
            "database": "publishers",
            "table": "publishers2",
            "date-column": "HitEventDate",
            "renames": {
                "mtpublishers_all": {
                    "databases": {
                        "publishers": "publishers_remote"
                    }
                }
            }
        },
        {
            "cluster-mtapi": "mtgiga",
            "database": "publishers",
            "table": "publishers2_merge",
            "date-column": "HitEventDate",
            "renames": {
                "mtpublishers_all": {
                    "databases": {
                        "publishers": "publishers_remote"
                    }
                }
            }
        },
        {
            "cluster-mtapi": "mtgiga",
            "database": "default",
            "table": "expenses",
            "date-column": "Date"
        },
        {
            "date-column": "EventDate",
            "cluster-mtapi": "mtmobgiga",
            "table": "test_ecommerce_events_all",
            "database": "mobile",
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "metadata-only": True,
            "table": "test_ecommerce_events_layer",
            "database": "mobile",
        },
        {
            "date-column": "EventDate",
            "cluster-mtapi": "mtmobgiga",
            "table": "crash_events_all",
            "database": "mobile",
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "metadata-only": True,
            "table": "crash_events_layer",
            "database": "mobile",
        },
        {
            "date-column": "CreateTime",
            "cluster-mtapi": "mtgiga",
            "database": "default",
            "table": "cdp_clients",
            "override-subcluster": "mdbcgg3ua7bothld2oh0",
            "format-create": {
                "cluster": "mtcdp_all"
            }
        },
        {
            "date-column": "CreateTime",
            "cluster-mtapi": "mtgiga",
            "database": "default",
            "table": "cdp_orders",
            "override-subcluster": "mdbcgg3ua7bothld2oh0",
            "format-create": {
                "cluster": "mtcdp_all"
            }
        },
        {
            "cluster-mtapi": "mtgiga",
            "database": "default",
            "table": "market_click_storage",
            "date-column": "Date"
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "table": "funnel_events_layer",
            "database": "mobile",
            "date-column": "EventDate"
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "table": "installations_layer",
            "database": "mobile",
            "date-column": "EventDate"
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "table": "skad_postbacks_all",
            "database": "mobile",
            "date-column": "EventDate",
            "format-create": {
                "mdb761rv6ikrbvtgll9t": "mtskadnetwork_all"
            }
        },
        {
            "cluster-mtapi": "mtgiga",
            "table": ".inner.pub_rows_uniques",
            "database": "merge",
            "date-column": "StartDate",
            "metadata-only": True,
        },
        {
            "cluster-mtapi": "mtgiga",
            "table": "pub_rows_uniques_layer",
            "database": "default",
            "date-column": "StartDate",
            "metadata-only": True,
        },
        {
            "cluster-mtapi": "mtgiga",
            "table": "last_hit_layer",
            "database": "default",
            "date-column": "RealDate",
        },
        {
            "cluster-mtapi": "mtgiga",
            "table": ".inner.last_hit2",
            "database": "merge",
            "date-column": "RealDate",
            "metadata-only": True
        },
        {
            "cluster-mtapi": "mtmobgiga",
            "table": "funnel_events_v2_layer",
            "database": "mobile",
            "date-column": "EventDate",
        },
        {
            "cluster-mtapi": "mtchvip",
            "table": "private_relay_ip",
            "database": "metr",
            "date-column": "Date",
            "metadata-only": True,
        },
    ]
}
