import {Mock} from "../../../lib";

export const iosCrashGroupsGridResponse =
    {
        "response": [
            {
                "status": 200,
                "data": {
                    "query": {
                        "ids": [
                            25378
                        ],
                        "dimensions": [
                            "ym:cr2:crashGroupObj"
                        ],
                        "metrics": [
                            "ym:cr2:crashes",
                            "norm(ym:cr2:crashes)",
                            "ym:cr2:crashDevices",
                            "norm(ym:cr2:crashDevices)",
                            "ym:cr2:crashesDevicesPercentage",
                            "ym:cr2:crashesUndecoded"
                        ],
                        "sort": [
                            "-ym:cr2:crashes"
                        ],
                        "humanized_filter": "",
                        "date1": "2019-09-01",
                        "date2": "2019-09-30",
                        "filters": "ym:cr2:operatingSystemInfo=='ios'",
                        "limit": 30,
                        "offset": 1,
                        "group": "Week",
                        "pca_integer_intervals": "false",
                        "auto_group_size": "1",
                        "pca_intervals_length": "0",
                        "quantile": "50",
                        "from": "0",
                        "currency": "XXX",
                        "funnel_window": "",
                        "to": "0",
                        "funnel_pattern": "",
                        "funnel_restriction": "",
                        "profile_attribute_id": "0"
                    },
                    "data": [
                        {
                            "dimensions": [
                                {
                                    "id": "0",
                                    "name": "Крэши без группы",
                                    "status": "OPEN",
                                    "comment": "Версия AppMetrica SDK меньше 3.7.1",
                                    "first_occurrence": null,
                                    "last_occurrence": null,
                                    "binary_name": null,
                                    "file_name": null,
                                    "method_name": null,
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                2221,
                                54.27663734,
                                1322,
                                47.69119769,
                                0.09296164,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "570462385381130762",
                                    "name": "UIViewControllerHierarchyInconsistency at Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "456 (26699)",
                                    "last_occurrence": "466 (32153)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": null,
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                769,
                                18.79276637,
                                563,
                                20.31024531,
                                0.03958956,
                                769
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "2629259209093869222",
                                    "name": "main.swift",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "460 (27882)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "Maple",
                                    "file_name": "main.swift",
                                    "method_name": "main",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                197,
                                4.81427175,
                                186,
                                6.70995671,
                                0.01307932,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "15042766137449359880",
                                    "name": "CFNetwork",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "460 (27882)",
                                    "binary_name": "CFNetwork",
                                    "file_name": null,
                                    "method_name": "<redacted>",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                105,
                                2.5659824,
                                84,
                                3.03030303,
                                0.00590679,
                                105
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "16215218784457656928",
                                    "name": "UIImage+YP.swift:29",
                                    "status": "CLOSED",
                                    "comment": "https://st.yandex-team.ru/MUSICIOS-9952",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "UIImage+YP.swift",
                                    "method_name": "specialized UIImage.fitImageIfDoesNotFit(in:scale:)",
                                    "source_line": "29"
                                }
                            ],
                            "metrics": [
                                78,
                                1.90615836,
                                58,
                                2.09235209,
                                0.0040785,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "153795416633377827",
                                    "name": "libobjc.A.dylib",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "libobjc.A.dylib",
                                    "file_name": null,
                                    "method_name": "objc_release",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                67,
                                1.63734115,
                                64,
                                2.30880231,
                                0.00450041,
                                48
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "8350703866420833068",
                                    "name": "AGXGLDriver",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "468 (32347)",
                                    "binary_name": "AGXGLDriver",
                                    "file_name": null,
                                    "method_name": "gldUpdateDispatch",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                58,
                                1.4173998,
                                54,
                                1.94805195,
                                0.00379722,
                                50
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "942942103237849762",
                                    "name": "<compiler-generated>",
                                    "status": "OPEN",
                                    "comment": "https://st.yandex-team.ru/MUSICIOS-9763",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "Maple",
                                    "file_name": "<compiler-generated>",
                                    "method_name": null,
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                52,
                                1.27077224,
                                50,
                                1.8037518,
                                0.00351595,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "2275483802061141669",
                                    "name": "Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": "SpeechKit::WorkingThread<SpeechKit::RecognizerProtocolEmbedded, SpeechKit::RecognizerProtocolEmbedded::State>::workingThreadFunc(void*)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                45,
                                1.09970674,
                                45,
                                1.62337662,
                                0.00316435,
                                45
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "167753772377683592",
                                    "name": "com.apple.coreaudio.avfaudio at CoreFoundation",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "458 (27178)",
                                    "last_occurrence": "468 (32347)",
                                    "binary_name": "CoreFoundation",
                                    "file_name": null,
                                    "method_name": "<redacted>",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                43,
                                1.05083089,
                                21,
                                0.75757576,
                                0.0014767,
                                41
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "15289707161470248615",
                                    "name": "AudioToolbox",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "AudioToolbox",
                                    "file_name": null,
                                    "method_name": "<redacted>",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                32,
                                0.78201369,
                                27,
                                0.97402597,
                                0.00189861,
                                32
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "14968647856837752700",
                                    "name": "CoreMedia",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "CoreMedia",
                                    "file_name": null,
                                    "method_name": "FigXPCRemoteClientSendSyncMessageCreatingReply",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                26,
                                0.63538612,
                                26,
                                0.93795094,
                                0.00182829,
                                23
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "4454298658456032919",
                                    "name": "CoreFoundation",
                                    "status": "OPEN",
                                    "comment": "https://st.yandex-team.ru/MUSICIOS-10109",
                                    "first_occurrence": "460 (27882)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "CoreFoundation",
                                    "file_name": null,
                                    "method_name": "-[__NSDictionaryM objectForKey:]",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                20,
                                0.48875855,
                                20,
                                0.72150072,
                                0.00140638,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "16465690619741776554",
                                    "name": "memory:3875",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "memory",
                                    "method_name": "get",
                                    "source_line": "3875"
                                }
                            ],
                            "metrics": [
                                16,
                                0.39100684,
                                16,
                                0.57720058,
                                0.0011251,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "2941642789001495926",
                                    "name": "AGXGLDriver",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "460 (27882)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "AGXGLDriver",
                                    "file_name": null,
                                    "method_name": null,
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                14,
                                0.34213099,
                                14,
                                0.50505051,
                                0.00098447,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "11207687737974538324",
                                    "name": "Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "468 (32347)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": "radr://5614542",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                12,
                                0.29325513,
                                2,
                                0.07215007,
                                0.00014064,
                                12
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "8348433614417085650",
                                    "name": "CFNetwork",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "CFNetwork",
                                    "file_name": null,
                                    "method_name": "HTTP2Stream::cleanUpInUserDataResetCallback(nghttp2_session*, int, unsigned int, HTTP2Connection*)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                11,
                                0.2688172,
                                11,
                                0.3968254,
                                0.00077351,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "13685130149951862520",
                                    "name": "CFNetwork",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "CFNetwork",
                                    "file_name": null,
                                    "method_name": "resolveTubeTypeForKey(HTTPConnectionCacheKey*, CoreLoggable*, TubeType*, __CFArray const**)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                11,
                                0.2688172,
                                11,
                                0.3968254,
                                0.00077351,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "2925713541098793142",
                                    "name": "Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "462 (28518)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": "SpeechKit::WorkingThread<SpeechKit::UniProxyClientProcess, SpeechKit::UniProxyClientState>::workingThreadFunc(void*)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                10,
                                0.24437928,
                                1,
                                0.03607504,
                                0.00007032,
                                10
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7686303906867705730",
                                    "name": "NSRangeException at Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "460 (27882)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": "void* std::__1::__thread_proxy<std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(void*), void*> >(void*)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                10,
                                0.24437928,
                                10,
                                0.36075036,
                                0.00070319,
                                9
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "1369425525815923039",
                                    "name": "com.apple.coreaudio.avfaudio at CoreFoundation",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "CoreFoundation",
                                    "file_name": null,
                                    "method_name": "__exceptionPreprocess",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                9,
                                0.21994135,
                                7,
                                0.25252525,
                                0.00049223,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "5909403158537152133",
                                    "name": "Maple",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "460 (27882)",
                                    "binary_name": "Maple",
                                    "file_name": null,
                                    "method_name": "SpeechKit::WorkingThread<SpeechKit::VocalizerProcess, SpeechKit::VocalizerState>::workingThreadFunc(void*)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                9,
                                0.21994135,
                                9,
                                0.32467532,
                                0.00063287,
                                9
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7131095477639358494",
                                    "name": "WebKitLegacy",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "462 (28518)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "WebKitLegacy",
                                    "file_name": null,
                                    "method_name": "<redacted>",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                8,
                                0.19550342,
                                8,
                                0.28860029,
                                0.00056255,
                                8
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "10044022238349485681",
                                    "name": "StreamLogger.cpp:55",
                                    "status": "OPEN",
                                    "comment": "https://st.yandex-team.ru/OBJCLIBS-374",
                                    "first_occurrence": "460 (27882)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "Maple",
                                    "file_name": "StreamLogger.cpp",
                                    "method_name": "SpeechKit::StreamLogger::initLoggerInstance()",
                                    "source_line": "55"
                                }
                            ],
                            "metrics": [
                                8,
                                0.19550342,
                                8,
                                0.28860029,
                                0.00056255,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "11503224317221284282",
                                    "name": "NSRangeException at <compiler-generated>",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "Maple",
                                    "file_name": "<compiler-generated>",
                                    "method_name": "@objc Application.sendEvent(_:)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                7,
                                0.17106549,
                                7,
                                0.25252525,
                                0.00049223,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "12726225025829132154",
                                    "name": "CBLParseDate.c:295",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "CBLParseDate.c",
                                    "method_name": "CBLParseISO8601Date",
                                    "source_line": "295"
                                }
                            ],
                            "metrics": [
                                7,
                                0.17106549,
                                1,
                                0.03607504,
                                0.00007032,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "17880485562058045939",
                                    "name": "<compiler-generated>",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "<compiler-generated>",
                                    "method_name": "protocol witness for YPAnalyticsStorage.allLogRecords() in conformance YPSearchFeedbackAnalytiscStorage",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                7,
                                0.17106549,
                                1,
                                0.03607504,
                                0.00007032,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "6889427870954260090",
                                    "name": "NSInternalInconsistencyException at YPAlbumMoreTracksController.m",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "470 (33734)",
                                    "binary_name": "Maple",
                                    "file_name": "YPAlbumMoreTracksController.m",
                                    "method_name": "-[YPAlbumMoreTracksController setHasMoreTracks:animated:]",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                6,
                                0.14662757,
                                3,
                                0.10822511,
                                0.00021096,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7534492779013280077",
                                    "name": "<compiler-generated>",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "<compiler-generated>",
                                    "method_name": "@objc YPArrayTrackListSource.init(tracks:)",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                6,
                                0.14662757,
                                1,
                                0.03607504,
                                0.00007032,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "11180933467566909405",
                                    "name": "<compiler-generated>",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "464 (30888)",
                                    "last_occurrence": "464 (30888)",
                                    "binary_name": "Maple",
                                    "file_name": "<compiler-generated>",
                                    "method_name": "type metadata accessor for AsyncOperation<(), [YPCustomizedPurchaseAlertInfo<YPCustomizedPurchaseOptionStore>]>",
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                6,
                                0.14662757,
                                1,
                                0.03607504,
                                0.00007032,
                                0
                            ]
                        }
                    ],
                    "meta": {
                        "dimensions": [
                            {
                                "id": "CrashGroupObj",
                                "dim": "ym:cr2:crashGroupObj",
                                "name": "Описание группы крэша",
                                "short_name": "Описание группы крэша",
                                "internal_type": "UInt64",
                                "allow_filters": false,
                                "fields": {
                                    "last_occurrence": {
                                        "id": "CrashGroupLastOccurrence",
                                        "dim": "ym:cr2:crashGroupLastOccurrence",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "Tuple(UInt32,UInt64)",
                                        "allow_filters": false,
                                        "allow_sort": false,
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "first_occurrence": {
                                        "id": "CrashGroupFirstOccurrence",
                                        "dim": "ym:cr2:crashGroupFirstOccurrence",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "Tuple(UInt32,UInt64)",
                                        "allow_filters": false,
                                        "allow_sort": false,
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "method_name": {
                                        "id": "CrashMethodName",
                                        "dim": "ym:cr2:crashMethodName",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "String",
                                        "allow_filters": true,
                                        "allow_sort": true,
                                        "default_sort": "asc",
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "file_name": {
                                        "id": "CrashFileName",
                                        "dim": "ym:cr2:crashFileName",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "String",
                                        "allow_filters": true,
                                        "allow_sort": true,
                                        "default_sort": "asc",
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "source_line": {
                                        "id": "CrashSourceLine",
                                        "dim": "ym:cr2:crashSourceLine",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "Int64",
                                        "allow_filters": false,
                                        "allow_sort": true,
                                        "default_sort": "desc",
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "name": {
                                        "id": "CrashGroupName",
                                        "dim": "ym:cr2:crashGroupName",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "String",
                                        "allow_filters": true,
                                        "allow_sort": true,
                                        "default_sort": "asc",
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "comment": {
                                        "id": "CrashGroupComment",
                                        "dim": "ym:cr2:crashGroupComment",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "Tuple(UInt32,UInt64,String)",
                                        "allow_filters": false,
                                        "allow_sort": false,
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "id": {
                                        "id": "CrashGroupObj",
                                        "dim": "ym:cr2:crashGroupObj",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "UInt64",
                                        "allow_filters": false,
                                        "allow_sort": false,
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "binary_name": {
                                        "id": "CrashBinaryName",
                                        "dim": "ym:cr2:crashBinaryName",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "String",
                                        "allow_filters": true,
                                        "allow_sort": true,
                                        "default_sort": "asc",
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    },
                                    "status": {
                                        "id": "CrashGroupStatus",
                                        "dim": "ym:cr2:crashGroupStatus",
                                        "name": "Описание группы крэша",
                                        "short_name": "Описание группы крэша",
                                        "internal_type": "Tuple(UInt32,UInt64)",
                                        "allow_filters": false,
                                        "allow_sort": false,
                                        "allow_null": false,
                                        "permission_scope": "common",
                                        "required_keys": [
                                            "app"
                                        ],
                                        "secret": false,
                                        "exposes_secret_data": false,
                                        "disjoint": true
                                    }
                                },
                                "allow_sort": false,
                                "allow_null": false,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "disjoint": true
                            }
                        ],
                        "metrics": [
                            {
                                "dim": "ym:cr2:crashes",
                                "name": "Количество крэшей",
                                "allow_normalisation": true,
                                "allow_filters": true,
                                "type": "int",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "support_confidence": true,
                                "negative": true,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            },
                            {
                                "dim": "norm(ym:cr2:crashes)",
                                "metric_string": "norm(ym:cr2:crashes)",
                                "name": "Количество крэшей",
                                "allow_normalisation": true,
                                "allow_filters": true,
                                "type": "percents",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "support_confidence": true,
                                "negative": true,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            },
                            {
                                "dim": "ym:cr2:crashDevices",
                                "metric_string": "ym:cr2:crashDevices",
                                "name": "Количество устройств, на которых возникли аварийные остановки приложения",
                                "allow_filters": true,
                                "type": "int",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "negative": true,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            },
                            {
                                "dim": "norm(ym:cr2:crashDevices)",
                                "metric_string": "norm(ym:cr2:crashDevices)",
                                "name": "Количество устройств, на которых возникли аварийные остановки приложения",
                                "allow_filters": true,
                                "type": "percents",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "negative": true,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            },
                            {
                                "dim": "ym:cr2:crashesDevicesPercentage",
                                "metric_string": "ym:cr2:crashesDevicesPercentage",
                                "name": "Процент устройств с крэшами",
                                "allow_filters": true,
                                "type": "percents",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            },
                            {
                                "dim": "ym:cr2:crashesUndecoded",
                                "allow_normalisation": true,
                                "allow_filters": true,
                                "type": "int",
                                "allow_sort": true,
                                "default_sort": "desc",
                                "support_confidence": true,
                                "negative": true,
                                "permission_scope": "common",
                                "required_keys": [
                                    "app"
                                ],
                                "secret": false,
                                "exposes_secret_data": false,
                                "additive": true
                            }
                        ]
                    },
                    "total_rows": 168,
                    "total_rows_rounded": false,
                    "sampled": false,
                    "sampleable": true,
                    "contains_sensitive_data": false,
                    "sample_share": 1,
                    "max_sample_share": 0.0001,
                    "sample_size": 61255475760,
                    "sample_space": 61255475760,
                    "data_lag": 0,
                    "totals": [
                        4092,
                        100,
                        2772,
                        100,
                        0.1949241,
                        1199
                    ],
                    "min": [
                        6,
                        0.14662757,
                        1,
                        0.03607504,
                        0.00007032,
                        0
                    ],
                    "max": [
                        2221,
                        54.27663734,
                        1322,
                        47.69119769,
                        0.09296164,
                        769
                    ],
                    "_profile": {
                        "queries": [
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                "time": 0,
                                "rows": 0,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:37",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1648825057527,
                                "query_hash": 975835054
                            },
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "SELECT time_zone_id FROM applications WHERE id = ?",
                                "params": "[25378]",
                                "time": 0,
                                "rows": 0,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:37",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1648825057528,
                                "query_hash": 1779967304
                            },
                            {
                                "host": "mtmobgiga094-1.metrika.yandex.net:8123",
                                "query": "WITH 1.0 AS W SELECT `ym:cr:crashGroupObj` AS `ym:cr2:crashGroupObj`, `ym:cr:crashGroupName` AS `ym:cr2:crashGroupName`, `ym:cr:crashGroupStatus` AS `ym:cr2:crashGroupStatus`, `ym:cr:crashGroupComment` AS `ym:cr2:crashGroupComment`, `ym:cr:crashGroupFirstOccurrence` AS `ym:cr2:crashGroupFirstOccurrence`, `ym:cr:crashGroupLastOccurrence` AS `ym:cr2:crashGroupLastOccurrence`, `ym:cr:crashBinaryName` AS `ym:cr2:crashBinaryName`, `ym:cr:crashFileName` AS `ym:cr2:crashFileName`, `ym:cr:crashMethodName` AS `ym:cr2:crashMethodName`, `ym:cr:crashSourceLine` AS `ym:cr2:crashSourceLine`, `ym:cr2:crashes` AS `ym:cr2:crashes`, `norm(ym:cr2:crashes)` AS `norm(ym:cr2:crashes)`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `norm(ym:cr2:crashDevices)`, `ym:cr2:crashDevices` / `ym:ge:uniqDeviceIDHash` AS `ym:cr2:crashesDevicesPercentage`, `ym:cr2:crashesUndecoded` AS `ym:cr2:crashesUndecoded` FROM (WITH 1.0 AS W SELECT DecodeGroupID AS `ym:cr:crashGroupObj`, toInt64(1) AS `ym:cr2:joiner`, max(`ym:cr:crashGroupObj` = toUInt64(0) ? 'Крэши без группы' : (OperatingSystem = 'android' ? (notEmpty(CrashReason) ? CrashReason || ' at ' || (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)'))) : (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)')))) : (notEmpty(CrashReason) ? CrashReason || ' at ' || (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)')) : (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)'))))) AS `ym:cr:crashGroupName`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupStatus`, max((APIKey,`ym:cr:crashGroupObj`,toString(OperatingSystem))) AS `ym:cr:crashGroupComment`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupFirstOccurrence`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupLastOccurrence`, max(CrashBinaryName) AS `ym:cr:crashBinaryName`, max(CrashFileName) AS `ym:cr:crashFileName`, max(CrashMethodName) AS `ym:cr:crashMethodName`, max(toInt64(CrashSourceLine)) AS `ym:cr:crashSourceLine`, sum(Sign) AS `ym:cr2:crashes`, sum(Sign) AS `norm(ym:cr2:crashes)`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes`, sumIf(Sign,DecodeStatus = 'parse_success') AS `ym:cr2:crashesUndecoded` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'ios' GROUP BY `ym:cr:crashGroupObj`, toInt64(1) WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) global any left join (WITH 1.0 AS W SELECT toInt64(1) AS `ym:cr2:joiner`, uniq(DeviceIDHash) AS `ym:ge:uniqDeviceIDHash` FROM mobile.generic_events_layer as `mobile.generic_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and toString(OperatingSystem) = 'ios' GROUP BY toInt64(1) WITH TOTALS ) using `ym:cr2:joiner` ORDER BY `ym:cr2:crashes` DESC, `ym:cr2:crashGroupObj` ASC limit 0,30",
                                "params": {
                                    "compress": "1",
                                    "extremes": "1",
                                    "distributed_aggregation_memory_efficient": "1"
                                },
                                "time": 4029,
                                "rows": 30,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:37",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "clickhouse",
                                "base_time": 1648825057536,
                                "query_hash": 773951988
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.status AS status FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                "time": 17,
                                "rows": 29,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:41",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648825061566,
                                "query_hash": 1236279510
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.comment AS comment FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                "time": 14,
                                "rows": 29,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:41",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648825061583,
                                "query_hash": 685406326
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    MIN((t.create_time, t.app_build_number, t.app_version_name)) AS first_occurrence,    MAX((t.create_time, t.app_build_number, t.app_version_name)) AS last_occurrence FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/app_versions` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id GROUP BY k.app_id, k.event_type, k.crash_group_id",
                                "time": 20,
                                "rows": 29,
                                "request_id": "1648825057527074-16411907058920688614",
                                "event_date_time": "2022-04-01 17:57:41",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648825061598,
                                "query_hash": 731624932
                            }
                        ],
                        "additional": {
                            "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                            "layer": "0"
                        },
                        "base_time": 1648825057526,
                        "request_id": "1648825057527074-16411907058920688614",
                        "request_uid": 1406498655,
                        "total_time": 4094,
                        "java_time": 14
                    },
                    "apiRequestUrl": "http://mobmetd-production.metrika.yandex.net/stat/v1/data?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D'ios'&id=25378&date1=2019-09-01&date2=2019-09-30&metrics=ym%3Acr2%3Acrashes%2Cnorm(ym%3Acr2%3Acrashes)%2Cym%3Acr2%3AcrashDevices%2Cnorm(ym%3Acr2%3AcrashDevices)%2Cym%3Acr2%3AcrashesDevicesPercentage%2Cym%3Acr2%3AcrashesUndecoded&dimensions=ym%3Acr2%3AcrashGroupObj&sort=-ym%3Acr2%3Acrashes&offset=1&limit=30&include_undefined=true&debug=json&accuracy=1&proposedAccuracy=true&uid=1406498655"
                },
                "_profile": [
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648825057498,
                            "success": true,
                            "url": "http://localhost:4/tvm/tickets?dsts=2000337%2C222%2C2000268",
                            "method": "get",
                            "time": 4,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648825057497,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=sessionid&host=appmetrica.yandex.ru&userip=2a02%3A6b8%3A81%3A0%3A5de7%3Ae1a0%3A9394%3A6cad&regname=yes&format=json&emails=getdefault&dbfields=subscription.login.669&get_user_ticket=1",
                            "method": "get",
                            "time": 12,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648825057513,
                            "success": true,
                            "url": "http://uatraits.qloud.yandex.ru/v0/detect",
                            "method": "POST",
                            "time": 4,
                            "headers": null,
                            "post": "{\n  \"User-Agent\": \"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15\"\n}",
                            "data": "{\n  \"isTouch\": false,\n  \"isMobile\": false,\n  \"isBrowser\": true,\n  \"OSVersion\": \"10.15.7\",\n  \"OSName\": \"macOS Catalina\",\n  \"AntiITP\": true,\n  \"ITP\": true,\n  \"OSFamily\": \"MacOS\",\n  \"BrowserVersion\": \"15.2\",\n  \"BrowserEngineVersion\": \"605.1.15\",\n  \"BrowserName\": \"Safari\",\n  \"CSP1Support\": true,\n  \"CSP2Support\": true,\n  \"BrowserEngine\": \"WebKit\",\n  \"ITPFakeCookie\": true\n}",
                            "error": false
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648825057524,
                            "success": true,
                            "url": "http://mobmetd-production.metrika.yandex.net/stat/v1/data?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D%27ios%27&id=25378&date1=2019-09-01&date2=2019-09-30&metrics=ym%3Acr2%3Acrashes%2Cnorm%28ym%3Acr2%3Acrashes%29%2Cym%3Acr2%3AcrashDevices%2Cnorm%28ym%3Acr2%3AcrashDevices%29%2Cym%3Acr2%3AcrashesDevicesPercentage%2Cym%3Acr2%3AcrashesUndecoded&dimensions=ym%3Acr2%3AcrashGroupObj&sort=-ym%3Acr2%3Acrashes&offset=1&limit=30&include_undefined=true&debug=json&accuracy=1&proposedAccuracy=true&uid=1406498655",
                            "method": "get",
                            "time": 4099,
                            "headers": null,
                            "data": "{\n  \"query\": {\n    \"ids\": [\n      25378\n    ],\n    \"dimensions\": [\n      \"ym:cr2:crashGroupObj\"\n    ],\n    \"metrics\": [\n      \"ym:cr2:crashes\",\n      \"norm(ym:cr2:crashes)\",\n      \"ym:cr2:crashDevices\",\n      \"norm(ym:cr2:crashDevices)\",\n      \"ym:cr2:crashesDevicesPercentage\",\n      \"ym:cr2:crashesUndecoded\"\n    ],\n    \"sort\": [\n      \"-ym:cr2:crashes\"\n    ],\n    \"humanized_filter\": \"\",\n    \"date1\": \"2019-09-01\",\n    \"date2\": \"2019-09-30\",\n    \"filters\": \"ym:cr2:operatingSystemInfo=='ios'\",\n    \"limit\": 30,\n    \"offset\": 1,\n    \"group\": \"Week\",\n    \"pca_integer_intervals\": \"false\",\n    \"auto_group_size\": \"1\",\n    \"pca_intervals_length\": \"0\",\n    \"quantile\": \"50\",\n    \"from\": \"0\",\n    \"currency\": \"XXX\",\n    \"funnel_window\": \"\",\n    \"to\": \"0\",\n    \"funnel_pattern\": \"\",\n    \"funnel_restriction\": \"\",\n    \"profile_attribute_id\": \"0\"\n  },\n  \"data\": [\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"0\",\n          \"name\": \"Крэши без группы\",\n          \"status\": \"OPEN\",\n          \"comment\": \"Версия AppMetrica SDK меньше 3.7.1\",\n          \"first_occurrence\": null,\n          \"last_occurrence\": null,\n          \"binary_name\": null,\n          \"file_name\": null,\n          \"method_name\": null,\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        2221,\n        54.27663734,\n        1322,\n        47.69119769,\n        0.09296164,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"570462385381130762\",\n          \"name\": \"UIViewControllerHierarchyInconsistency at Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"456 (26699)\",\n          \"last_occurrence\": \"466 (32153)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": null,\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        769,\n        18.79276637,\n        563,\n        20.31024531,\n        0.03958956,\n        769\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"2629259209093869222\",\n          \"name\": \"main.swift\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"460 (27882)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"main.swift\",\n          \"method_name\": \"main\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        197,\n        4.81427175,\n        186,\n        6.70995671,\n        0.01307932,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"15042766137449359880\",\n          \"name\": \"CFNetwork\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"460 (27882)\",\n          \"binary_name\": \"CFNetwork\",\n          \"file_name\": null,\n          \"method_name\": \"<redacted>\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        105,\n        2.5659824,\n        84,\n        3.03030303,\n        0.00590679,\n        105\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"16215218784457656928\",\n          \"name\": \"UIImage+YP.swift:29\",\n          \"status\": \"CLOSED\",\n          \"comment\": \"https://st.yandex-team.ru/MUSICIOS-9952\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"UIImage+YP.swift\",\n          \"method_name\": \"specialized UIImage.fitImageIfDoesNotFit(in:scale:)\",\n          \"source_line\": \"29\"\n        }\n      ],\n      \"metrics\": [\n        78,\n        1.90615836,\n        58,\n        2.09235209,\n        0.0040785,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"153795416633377827\",\n          \"name\": \"libobjc.A.dylib\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"libobjc.A.dylib\",\n          \"file_name\": null,\n          \"method_name\": \"objc_release\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        67,\n        1.63734115,\n        64,\n        2.30880231,\n        0.00450041,\n        48\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"8350703866420833068\",\n          \"name\": \"AGXGLDriver\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"468 (32347)\",\n          \"binary_name\": \"AGXGLDriver\",\n          \"file_name\": null,\n          \"method_name\": \"gldUpdateDispatch\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        58,\n        1.4173998,\n        54,\n        1.94805195,\n        0.00379722,\n        50\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"942942103237849762\",\n          \"name\": \"<compiler-generated>\",\n          \"status\": \"OPEN\",\n          \"comment\": \"https://st.yandex-team.ru/MUSICIOS-9763\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"<compiler-generated>\",\n          \"method_name\": null,\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        52,\n        1.27077224,\n        50,\n        1.8037518,\n        0.00351595,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"2275483802061141669\",\n          \"name\": \"Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": \"SpeechKit::WorkingThread<SpeechKit::RecognizerProtocolEmbedded, SpeechKit::RecognizerProtocolEmbedded::State>::workingThreadFunc(void*)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        45,\n        1.09970674,\n        45,\n        1.62337662,\n        0.00316435,\n        45\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"167753772377683592\",\n          \"name\": \"com.apple.coreaudio.avfaudio at CoreFoundation\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"458 (27178)\",\n          \"last_occurrence\": \"468 (32347)\",\n          \"binary_name\": \"CoreFoundation\",\n          \"file_name\": null,\n          \"method_name\": \"<redacted>\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        43,\n        1.05083089,\n        21,\n        0.75757576,\n        0.0014767,\n        41\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"15289707161470248615\",\n          \"name\": \"AudioToolbox\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"AudioToolbox\",\n          \"file_name\": null,\n          \"method_name\": \"<redacted>\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        32,\n        0.78201369,\n        27,\n        0.97402597,\n        0.00189861,\n        32\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"14968647856837752700\",\n          \"name\": \"CoreMedia\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"CoreMedia\",\n          \"file_name\": null,\n          \"method_name\": \"FigXPCRemoteClientSendSyncMessageCreatingReply\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        26,\n        0.63538612,\n        26,\n        0.93795094,\n        0.00182829,\n        23\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"4454298658456032919\",\n          \"name\": \"CoreFoundation\",\n          \"status\": \"OPEN\",\n          \"comment\": \"https://st.yandex-team.ru/MUSICIOS-10109\",\n          \"first_occurrence\": \"460 (27882)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"CoreFoundation\",\n          \"file_name\": null,\n          \"method_name\": \"-[__NSDictionaryM objectForKey:]\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        20,\n        0.48875855,\n        20,\n        0.72150072,\n        0.00140638,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"16465690619741776554\",\n          \"name\": \"memory:3875\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"memory\",\n          \"method_name\": \"get\",\n          \"source_line\": \"3875\"\n        }\n      ],\n      \"metrics\": [\n        16,\n        0.39100684,\n        16,\n        0.57720058,\n        0.0011251,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"2941642789001495926\",\n          \"name\": \"AGXGLDriver\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"460 (27882)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"AGXGLDriver\",\n          \"file_name\": null,\n          \"method_name\": null,\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        14,\n        0.34213099,\n        14,\n        0.50505051,\n        0.00098447,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"11207687737974538324\",\n          \"name\": \"Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"468 (32347)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": \"radr://5614542\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        12,\n        0.29325513,\n        2,\n        0.07215007,\n        0.00014064,\n        12\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"8348433614417085650\",\n          \"name\": \"CFNetwork\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"CFNetwork\",\n          \"file_name\": null,\n          \"method_name\": \"HTTP2Stream::cleanUpInUserDataResetCallback(nghttp2_session*, int, unsigned int, HTTP2Connection*)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        11,\n        0.2688172,\n        11,\n        0.3968254,\n        0.00077351,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"13685130149951862520\",\n          \"name\": \"CFNetwork\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"CFNetwork\",\n          \"file_name\": null,\n          \"method_name\": \"resolveTubeTypeForKey(HTTPConnectionCacheKey*, CoreLoggable*, TubeType*, __CFArray const**)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        11,\n        0.2688172,\n        11,\n        0.3968254,\n        0.00077351,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"2925713541098793142\",\n          \"name\": \"Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"462 (28518)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": \"SpeechKit::WorkingThread<SpeechKit::UniProxyClientProcess, SpeechKit::UniProxyClientState>::workingThreadFunc(void*)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        10,\n        0.24437928,\n        1,\n        0.03607504,\n        0.00007032,\n        10\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7686303906867705730\",\n          \"name\": \"NSRangeException at Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"460 (27882)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": \"void* std::__1::__thread_proxy<std::__1::tuple<std::__1::unique_ptr<std::__1::__thread_struct, std::__1::default_delete<std::__1::__thread_struct> >, void (*)(void*), void*> >(void*)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        10,\n        0.24437928,\n        10,\n        0.36075036,\n        0.00070319,\n        9\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"1369425525815923039\",\n          \"name\": \"com.apple.coreaudio.avfaudio at CoreFoundation\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"CoreFoundation\",\n          \"file_name\": null,\n          \"method_name\": \"__exceptionPreprocess\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        9,\n        0.21994135,\n        7,\n        0.25252525,\n        0.00049223,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"5909403158537152133\",\n          \"name\": \"Maple\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"460 (27882)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": null,\n          \"method_name\": \"SpeechKit::WorkingThread<SpeechKit::VocalizerProcess, SpeechKit::VocalizerState>::workingThreadFunc(void*)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        9,\n        0.21994135,\n        9,\n        0.32467532,\n        0.00063287,\n        9\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7131095477639358494\",\n          \"name\": \"WebKitLegacy\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"462 (28518)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"WebKitLegacy\",\n          \"file_name\": null,\n          \"method_name\": \"<redacted>\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        8,\n        0.19550342,\n        8,\n        0.28860029,\n        0.00056255,\n        8\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"10044022238349485681\",\n          \"name\": \"StreamLogger.cpp:55\",\n          \"status\": \"OPEN\",\n          \"comment\": \"https://st.yandex-team.ru/OBJCLIBS-374\",\n          \"first_occurrence\": \"460 (27882)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"StreamLogger.cpp\",\n          \"method_name\": \"SpeechKit::StreamLogger::initLoggerInstance()\",\n          \"source_line\": \"55\"\n        }\n      ],\n      \"metrics\": [\n        8,\n        0.19550342,\n        8,\n        0.28860029,\n        0.00056255,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"11503224317221284282\",\n          \"name\": \"NSRangeException at <compiler-generated>\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"<compiler-generated>\",\n          \"method_name\": \"@objc Application.sendEvent(_:)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        7,\n        0.17106549,\n        7,\n        0.25252525,\n        0.00049223,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"12726225025829132154\",\n          \"name\": \"CBLParseDate.c:295\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"CBLParseDate.c\",\n          \"method_name\": \"CBLParseISO8601Date\",\n          \"source_line\": \"295\"\n        }\n      ],\n      \"metrics\": [\n        7,\n        0.17106549,\n        1,\n        0.03607504,\n        0.00007032,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"17880485562058045939\",\n          \"name\": \"<compiler-generated>\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"<compiler-generated>\",\n          \"method_name\": \"protocol witness for YPAnalyticsStorage.allLogRecords() in conformance YPSearchFeedbackAnalytiscStorage\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        7,\n        0.17106549,\n        1,\n        0.03607504,\n        0.00007032,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"6889427870954260090\",\n          \"name\": \"NSInternalInconsistencyException at YPAlbumMoreTracksController.m\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"470 (33734)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"YPAlbumMoreTracksController.m\",\n          \"method_name\": \"-[YPAlbumMoreTracksController setHasMoreTracks:animated:]\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        6,\n        0.14662757,\n        3,\n        0.10822511,\n        0.00021096,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7534492779013280077\",\n          \"name\": \"<compiler-generated>\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"<compiler-generated>\",\n          \"method_name\": \"@objc YPArrayTrackListSource.init(tracks:)\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        6,\n        0.14662757,\n        1,\n        0.03607504,\n        0.00007032,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"11180933467566909405\",\n          \"name\": \"<compiler-generated>\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"464 (30888)\",\n          \"last_occurrence\": \"464 (30888)\",\n          \"binary_name\": \"Maple\",\n          \"file_name\": \"<compiler-generated>\",\n          \"method_name\": \"type metadata accessor for AsyncOperation<(), [YPCustomizedPurchaseAlertInfo<YPCustomizedPurchaseOptionStore>]>\",\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        6,\n        0.14662757,\n        1,\n        0.03607504,\n        0.00007032,\n        0\n      ]\n    }\n  ],\n  \"meta\": {\n    \"dimensions\": [\n      {\n        \"id\": \"CrashGroupObj\",\n        \"dim\": \"ym:cr2:crashGroupObj\",\n        \"name\": \"Описание группы крэша\",\n        \"short_name\": \"Описание группы крэша\",\n        \"internal_type\": \"UInt64\",\n        \"allow_filters\": false,\n        \"fields\": {\n          \"last_occurrence\": {\n            \"id\": \"CrashGroupLastOccurrence\",\n            \"dim\": \"ym:cr2:crashGroupLastOccurrence\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"first_occurrence\": {\n            \"id\": \"CrashGroupFirstOccurrence\",\n            \"dim\": \"ym:cr2:crashGroupFirstOccurrence\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"method_name\": {\n            \"id\": \"CrashMethodName\",\n            \"dim\": \"ym:cr2:crashMethodName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"file_name\": {\n            \"id\": \"CrashFileName\",\n            \"dim\": \"ym:cr2:crashFileName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"source_line\": {\n            \"id\": \"CrashSourceLine\",\n            \"dim\": \"ym:cr2:crashSourceLine\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Int64\",\n            \"allow_filters\": false,\n            \"allow_sort\": true,\n            \"default_sort\": \"desc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"name\": {\n            \"id\": \"CrashGroupName\",\n            \"dim\": \"ym:cr2:crashGroupName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"comment\": {\n            \"id\": \"CrashGroupComment\",\n            \"dim\": \"ym:cr2:crashGroupComment\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64,String)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"id\": {\n            \"id\": \"CrashGroupObj\",\n            \"dim\": \"ym:cr2:crashGroupObj\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"UInt64\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"binary_name\": {\n            \"id\": \"CrashBinaryName\",\n            \"dim\": \"ym:cr2:crashBinaryName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"status\": {\n            \"id\": \"CrashGroupStatus\",\n            \"dim\": \"ym:cr2:crashGroupStatus\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          }\n        },\n        \"allow_sort\": false,\n        \"allow_null\": false,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"disjoint\": true\n      }\n    ],\n    \"metrics\": [\n      {\n        \"dim\": \"ym:cr2:crashes\",\n        \"name\": \"Количество крэшей\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"norm(ym:cr2:crashes)\",\n        \"metric_string\": \"norm(ym:cr2:crashes)\",\n        \"name\": \"Количество крэшей\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashDevices\",\n        \"metric_string\": \"ym:cr2:crashDevices\",\n        \"name\": \"Количество устройств, на которых возникли аварийные остановки приложения\",\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"norm(ym:cr2:crashDevices)\",\n        \"metric_string\": \"norm(ym:cr2:crashDevices)\",\n        \"name\": \"Количество устройств, на которых возникли аварийные остановки приложения\",\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashesDevicesPercentage\",\n        \"metric_string\": \"ym:cr2:crashesDevicesPercentage\",\n        \"name\": \"Процент устройств с крэшами\",\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashesUndecoded\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      }\n    ]\n  },\n  \"total_rows\": 168,\n  \"total_rows_rounded\": false,\n  \"sampled\": false,\n  \"sampleable\": true,\n  \"contains_sensitive_data\": false,\n  \"sample_share\": 1,\n  \"max_sample_share\": 0.0001,\n  \"sample_size\": 61255475760,\n  \"sample_space\": 61255475760,\n  \"data_lag\": 0,\n  \"totals\": [\n    4092,\n    100,\n    2772,\n    100,\n    0.1949241,\n    1199\n  ],\n  \"min\": [\n    6,\n    0.14662757,\n    1,\n    0.03607504,\n    0.00007032,\n    0\n  ],\n  \"max\": [\n    2221,\n    54.27663734,\n    1322,\n    47.69119769,\n    0.09296164,\n    769\n  ]\n}",
                            "error": false,
                            "_profile": {
                                "queries": [
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                        "time": 0,
                                        "rows": 0,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:37",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648825057527,
                                        "query_hash": 975835054
                                    },
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT time_zone_id FROM applications WHERE id = ?",
                                        "params": "[25378]",
                                        "time": 0,
                                        "rows": 0,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:37",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648825057528,
                                        "query_hash": 1779967304
                                    },
                                    {
                                        "host": "mtmobgiga094-1.metrika.yandex.net:8123",
                                        "query": "WITH 1.0 AS W SELECT `ym:cr:crashGroupObj` AS `ym:cr2:crashGroupObj`, `ym:cr:crashGroupName` AS `ym:cr2:crashGroupName`, `ym:cr:crashGroupStatus` AS `ym:cr2:crashGroupStatus`, `ym:cr:crashGroupComment` AS `ym:cr2:crashGroupComment`, `ym:cr:crashGroupFirstOccurrence` AS `ym:cr2:crashGroupFirstOccurrence`, `ym:cr:crashGroupLastOccurrence` AS `ym:cr2:crashGroupLastOccurrence`, `ym:cr:crashBinaryName` AS `ym:cr2:crashBinaryName`, `ym:cr:crashFileName` AS `ym:cr2:crashFileName`, `ym:cr:crashMethodName` AS `ym:cr2:crashMethodName`, `ym:cr:crashSourceLine` AS `ym:cr2:crashSourceLine`, `ym:cr2:crashes` AS `ym:cr2:crashes`, `norm(ym:cr2:crashes)` AS `norm(ym:cr2:crashes)`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `norm(ym:cr2:crashDevices)`, `ym:cr2:crashDevices` / `ym:ge:uniqDeviceIDHash` AS `ym:cr2:crashesDevicesPercentage`, `ym:cr2:crashesUndecoded` AS `ym:cr2:crashesUndecoded` FROM (WITH 1.0 AS W SELECT DecodeGroupID AS `ym:cr:crashGroupObj`, toInt64(1) AS `ym:cr2:joiner`, max(`ym:cr:crashGroupObj` = toUInt64(0) ? 'Крэши без группы' : (OperatingSystem = 'android' ? (notEmpty(CrashReason) ? CrashReason || ' at ' || (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)'))) : (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)')))) : (notEmpty(CrashReason) ? CrashReason || ' at ' || (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)')) : (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)'))))) AS `ym:cr:crashGroupName`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupStatus`, max((APIKey,`ym:cr:crashGroupObj`,toString(OperatingSystem))) AS `ym:cr:crashGroupComment`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupFirstOccurrence`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupLastOccurrence`, max(CrashBinaryName) AS `ym:cr:crashBinaryName`, max(CrashFileName) AS `ym:cr:crashFileName`, max(CrashMethodName) AS `ym:cr:crashMethodName`, max(toInt64(CrashSourceLine)) AS `ym:cr:crashSourceLine`, sum(Sign) AS `ym:cr2:crashes`, sum(Sign) AS `norm(ym:cr2:crashes)`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes`, sumIf(Sign,DecodeStatus = 'parse_success') AS `ym:cr2:crashesUndecoded` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'ios' GROUP BY `ym:cr:crashGroupObj`, toInt64(1) WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) global any left join (WITH 1.0 AS W SELECT toInt64(1) AS `ym:cr2:joiner`, uniq(DeviceIDHash) AS `ym:ge:uniqDeviceIDHash` FROM mobile.generic_events_layer as `mobile.generic_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and toString(OperatingSystem) = 'ios' GROUP BY toInt64(1) WITH TOTALS ) using `ym:cr2:joiner` ORDER BY `ym:cr2:crashes` DESC, `ym:cr2:crashGroupObj` ASC limit 0,30",
                                        "params": {
                                            "compress": "1",
                                            "extremes": "1",
                                            "distributed_aggregation_memory_efficient": "1"
                                        },
                                        "time": 4029,
                                        "rows": 30,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:37",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "clickhouse",
                                        "base_time": 1648825057536,
                                        "query_hash": 773951988
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.status AS status FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                        "time": 17,
                                        "rows": 29,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:41",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648825061566,
                                        "query_hash": 1236279510
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.comment AS comment FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                        "time": 14,
                                        "rows": 29,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:41",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648825061583,
                                        "query_hash": 685406326
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    MIN((t.create_time, t.app_build_number, t.app_version_name)) AS first_occurrence,    MAX((t.create_time, t.app_build_number, t.app_version_name)) AS last_occurrence FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/app_versions` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id GROUP BY k.app_id, k.event_type, k.crash_group_id",
                                        "time": 20,
                                        "rows": 29,
                                        "request_id": "1648825057527074-16411907058920688614",
                                        "event_date_time": "2022-04-01 17:57:41",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648825061598,
                                        "query_hash": 731624932
                                    }
                                ],
                                "additional": {
                                    "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                                    "layer": "0"
                                },
                                "base_time": 1648825057526,
                                "request_id": "1648825057527074-16411907058920688614",
                                "request_uid": 1406498655,
                                "total_time": 4094,
                                "java_time": 14
                            }
                        },
                        "isBlackbox": false
                    }
                ],
                "_version": "2.1243321415.2"
            }
        ]
    };

export const iosCrashGroupsGridMock = new Mock(
    /.*\/transport\/i-stat\/getData*/,
    iosCrashGroupsGridResponse
);

