import {Mock} from "../../../lib";

export const androidCrashGroupsGridResponse =
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
                        "filters": "ym:cr2:operatingSystemInfo=='android'",
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
                                    "comment": "Версия AppMetrica SDK меньше 3.6.0",
                                    "first_occurrence": null,
                                    "last_occurrence": null,
                                    "binary_name": null,
                                    "file_name": null,
                                    "method_name": null,
                                    "source_line": "0"
                                }
                            ],
                            "metrics": [
                                68021,
                                64.12236048,
                                22032,
                                56.00691443,
                                0.38108911,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "3749432279756674295",
                                    "name": "android.database.sqlite.SQLiteFullException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.2 #3201 (3201)",
                                    "last_occurrence": "2022.03.3 #4674 (24022162)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativeExecuteForChangedRowCount",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                8059,
                                7.59709653,
                                2455,
                                6.24078499,
                                0.04246431,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "12454995534919700191",
                                    "name": "java.lang.IllegalStateException at SourceFile:72",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 BETA.3 #3248 (3248)",
                                    "last_occurrence": "2019.10.1 2947 #12874-review (12874)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.recyclerview.widget.LoggingRecyclerView.addView",
                                    "source_line": "72"
                                }
                            ],
                            "metrics": [
                                2733,
                                2.57635747,
                                2655,
                                6.74919925,
                                0.04592373,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "18105866812809628971",
                                    "name": "android.database.sqlite.SQLiteFullException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.1 #3177 (3177)",
                                    "last_occurrence": "2022.03.3 #4674 (24022162)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativeExecuteForLastInsertedRowId",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                2568,
                                2.42081448,
                                1367,
                                3.47501144,
                                0.0236451,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "5785868980532715233",
                                    "name": "android.database.sqlite.SQLiteException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.1 #3177 (3177)",
                                    "last_occurrence": "2022.03.3 #4674 (24022162)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativeExecute",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                2223,
                                2.09558824,
                                1292,
                                3.28435609,
                                0.02234782,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "10427529621369709895",
                                    "name": "android.database.sqlite.SQLiteException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 #3233 (3233)",
                                    "last_occurrence": "2022.03.3 #4674 (24022162)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativePrepareStatement",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                1335,
                                1.25848416,
                                47,
                                0.11947735,
                                0.00081296,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "4134954119304559650",
                                    "name": "android.database.sqlite.SQLiteException at SourceFile:426",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.2 #3269 (3269)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.setLocaleFromConfiguration",
                                    "source_line": "426"
                                }
                            ],
                            "metrics": [
                                1153,
                                1.08691554,
                                102,
                                0.25929127,
                                0.0017643,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "1349492918128318962",
                                    "name": "java.lang.IllegalStateException at SourceFile:8121",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 BETA.1 #3232 (3232)",
                                    "last_occurrence": "2019.06.2 #3208 (3208)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "com.yandex.passport.internal.ag.b",
                                    "source_line": "8121"
                                }
                            ],
                            "metrics": [
                                745,
                                0.70230015,
                                192,
                                0.48807769,
                                0.00332104,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "6226919780114714676",
                                    "name": "android.os.DeadSystemException at (Unknown Source)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "24021155 (24021155)",
                                    "binary_name": null,
                                    "file_name": null,
                                    "method_name": "com.google.android.gms.common.d.do",
                                    "source_line": "64"
                                }
                            ],
                            "metrics": [
                                729,
                                0.68721719,
                                636,
                                1.61675733,
                                0.01100094,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "10968604898541102144",
                                    "name": "java.lang.IllegalStateException at SourceFile:851",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.1.3207 (3207)",
                                    "last_occurrence": "2019.06.2 BETA.2 #3202 (3202)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.recyclerview.widget.RecyclerView$5.addView",
                                    "source_line": "851"
                                }
                            ],
                            "metrics": [
                                580,
                                0.54675716,
                                562,
                                1.42864406,
                                0.00972095,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "14314865551578678258",
                                    "name": "java.lang.NullPointerException at SourceFile:51",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.2 #3201 (3201)",
                                    "last_occurrence": "2020.03.1 #3395 (3395)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "okhttp3.r.do",
                                    "source_line": "51"
                                }
                            ],
                            "metrics": [
                                503,
                                0.47417044,
                                26,
                                0.06609385,
                                0.00044972,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7132796517861447921",
                                    "name": "android.os.DeadSystemException at SourceFile:20",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "0.0",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "cdj.bS",
                                    "source_line": "20"
                                }
                            ],
                            "metrics": [
                                489,
                                0.46097285,
                                316,
                                0.80329452,
                                0.00546588,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7337392191131051460",
                                    "name": "java.lang.ClassNotFoundException at SourceFile",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.08.2 #3233 (3233)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "ru.yandex.music.utils.f$1.handleMessage",
                                    "source_line": "-1"
                                }
                            ],
                            "metrics": [
                                411,
                                0.38744344,
                                1,
                                0.00254207,
                                0.0000173,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "3227164132574439880",
                                    "name": "android.os.TransactionTooLargeException at PendingTransactionActions.java:160",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.06.1.3207 (3207)",
                                    "binary_name": null,
                                    "file_name": "PendingTransactionActions.java",
                                    "method_name": "android.app.servertransaction.PendingTransactionActions$StopInfo.run",
                                    "source_line": "160"
                                }
                            ],
                            "metrics": [
                                373,
                                0.35162142,
                                219,
                                0.55671361,
                                0.00378806,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7117268639141053778",
                                    "name": "java.lang.UnsatisfiedLinkError at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.07.1 #3218 (3218)",
                                    "last_occurrence": "2020.08.1 #3525 (23020402)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "ru.yandex.speechkit.BaseSpeechKit.native_getContext",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                320,
                                0.30165913,
                                292,
                                0.74228481,
                                0.00505075,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "15256811207195161215",
                                    "name": "android.database.sqlite.SQLiteException at SourceFile:378",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.1 #3224 (3224)",
                                    "last_occurrence": "2022.03.4-SNAPSHOT #0 (24022170)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteOpenHelper.onDowngrade",
                                    "source_line": "378"
                                }
                            ],
                            "metrics": [
                                278,
                                0.26206637,
                                26,
                                0.06609385,
                                0.00044972,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "16091661245656610237",
                                    "name": "android.database.sqlite.SQLiteDiskIOException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.07.1 #3218 (3218)",
                                    "last_occurrence": "2022.03.3 #4674 (24022162)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativeExecute",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                270,
                                0.25452489,
                                203,
                                0.51604047,
                                0.00351131,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7846353672167316612",
                                    "name": "java.lang.NullPointerException at SourceFile:769",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.05.2 BETA.2 #3147 (3147)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "com.facebook.internal.ad.do",
                                    "source_line": "769"
                                }
                            ],
                            "metrics": [
                                257,
                                0.24226998,
                                257,
                                0.65331232,
                                0.00444535,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "10874962601629735121",
                                    "name": "com.facebook.p at SourceFile:144",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.1 #3249 (21019455)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "com.facebook.internal.ae.HO",
                                    "source_line": "144"
                                }
                            ],
                            "metrics": [
                                230,
                                0.2168175,
                                228,
                                0.57959225,
                                0.00394373,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "14246962484232748584",
                                    "name": "java.lang.AssertionError at SourceFile:18",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.1 BETA.4 #3250 (3250)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "bkp.for",
                                    "source_line": "18"
                                }
                            ],
                            "metrics": [
                                223,
                                0.2102187,
                                221,
                                0.56179775,
                                0.00382265,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "9180328120649562380",
                                    "name": "java.lang.OutOfMemoryError at SourceFile:114",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.1 #3249 (3249)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "ru.yandex.music.common.service.player.p.bxt",
                                    "source_line": "114"
                                }
                            ],
                            "metrics": [
                                208,
                                0.19607843,
                                130,
                                0.33046927,
                                0.00224862,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "10429823020601280834",
                                    "name": "java.lang.IllegalArgumentException at SourceFile:44",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.1 #3249 (3249)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.core.app.p$a.hP",
                                    "source_line": "44"
                                }
                            ],
                            "metrics": [
                                203,
                                0.19136501,
                                160,
                                0.4067314,
                                0.00276753,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "7794102704581947677",
                                    "name": "android.system.ErrnoException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 #3233 (3233)",
                                    "last_occurrence": "2021.07.3 #4004 (24021362)",
                                    "binary_name": null,
                                    "file_name": "Posix.java",
                                    "method_name": "libcore.io.Posix.android_getaddrinfo",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                192,
                                0.18099548,
                                13,
                                0.03304693,
                                0.00022486,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "15778048293593109084",
                                    "name": "android.database.sqlite.SQLiteFullException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.2 #3201 (3201)",
                                    "last_occurrence": "2022.03.1 #4615 (24022152)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativeExecute",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                168,
                                0.15837104,
                                146,
                                0.37114241,
                                0.00252537,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "13735952367628980377",
                                    "name": "java.lang.SecurityException at SourceFile:192",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 #3233 (3233)",
                                    "last_occurrence": "2019.09.1 #3249 (3249)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.core.app.JobIntentService$c.if",
                                    "source_line": "192"
                                }
                            ],
                            "metrics": [
                                161,
                                0.15177225,
                                1,
                                0.00254207,
                                0.0000173,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "11618892406029957186",
                                    "name": "java.lang.IllegalStateException at SourceFile:965",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.06.2 #3201 (3201)",
                                    "last_occurrence": "2021.12.2 6460 #18171 (24021610)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnectionPool.throwIfClosedLocked",
                                    "source_line": "965"
                                }
                            ],
                            "metrics": [
                                155,
                                0.14611614,
                                151,
                                0.38385276,
                                0.00261186,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "1536281939572358247",
                                    "name": "java.lang.SecurityException at SourceFile:216",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.1 #3249 (3249)",
                                    "last_occurrence": "2019.09.1 #3249 (3249)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.core.app.JobIntentService$c.hT",
                                    "source_line": "216"
                                }
                            ],
                            "metrics": [
                                153,
                                0.14423077,
                                1,
                                0.00254207,
                                0.0000173,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "6558440617702936992",
                                    "name": "android.view.WindowManager$BadTokenException at SourceFile:1007",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 #3233 (3233)",
                                    "last_occurrence": "2019.09.2 BETA.1 #3257 (3257)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "androidx.appcompat.app.a$a.ae",
                                    "source_line": "1007"
                                }
                            ],
                            "metrics": [
                                141,
                                0.13291855,
                                140,
                                0.35588998,
                                0.00242159,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "16713851609740653738",
                                    "name": "android.database.sqlite.SQLiteDatabaseLockedException at (Native Method)",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.08.2 #3233 (3233)",
                                    "last_occurrence": "2022.03.2 #4640 (24022157)",
                                    "binary_name": null,
                                    "file_name": "SourceFile",
                                    "method_name": "io.requery.android.database.sqlite.SQLiteConnection.nativePrepareStatement",
                                    "source_line": "-2"
                                }
                            ],
                            "metrics": [
                                131,
                                0.1234917,
                                99,
                                0.25166506,
                                0.00171241,
                                0
                            ]
                        },
                        {
                            "dimensions": [
                                {
                                    "id": "5119767380137259633",
                                    "name": "java.lang.IllegalStateException at ViewGroup.java:5099",
                                    "status": "OPEN",
                                    "comment": "",
                                    "first_occurrence": "2019.09.2 #3263 (3263)",
                                    "last_occurrence": "2020.09.1 #3542 (23020451)",
                                    "binary_name": null,
                                    "file_name": "ViewGroup.java",
                                    "method_name": "android.view.ViewGroup.addViewInner",
                                    "source_line": "5099"
                                }
                            ],
                            "metrics": [
                                122,
                                0.11500754,
                                121,
                                0.30759062,
                                0.00209295,
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
                    "total_rows": 1799,
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
                        106080,
                        100,
                        39338,
                        100,
                        0.68043225,
                        0
                    ],
                    "min": [
                        122,
                        0.11500754,
                        1,
                        0.00254207,
                        0.0000173,
                        0
                    ],
                    "max": [
                        68021,
                        64.12236048,
                        22032,
                        56.00691443,
                        0.38108911,
                        0
                    ],
                    "_profile": {
                        "queries": [
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                "time": 1,
                                "rows": 0,
                                "request_id": "1648824712578676-216757691198954165",
                                "event_date_time": "2022-04-01 17:51:52",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1648824712584,
                                "query_hash": 975835054
                            },
                            {
                                "host": "mtmobgiga049-1.metrika.yandex.net:8123",
                                "query": "WITH 1.0 AS W SELECT `ym:cr:crashGroupObj` AS `ym:cr2:crashGroupObj`, `ym:cr:crashGroupName` AS `ym:cr2:crashGroupName`, `ym:cr:crashGroupStatus` AS `ym:cr2:crashGroupStatus`, `ym:cr:crashGroupComment` AS `ym:cr2:crashGroupComment`, `ym:cr:crashGroupFirstOccurrence` AS `ym:cr2:crashGroupFirstOccurrence`, `ym:cr:crashGroupLastOccurrence` AS `ym:cr2:crashGroupLastOccurrence`, `ym:cr:crashBinaryName` AS `ym:cr2:crashBinaryName`, `ym:cr:crashFileName` AS `ym:cr2:crashFileName`, `ym:cr:crashMethodName` AS `ym:cr2:crashMethodName`, `ym:cr:crashSourceLine` AS `ym:cr2:crashSourceLine`, `ym:cr2:crashes` AS `ym:cr2:crashes`, `norm(ym:cr2:crashes)` AS `norm(ym:cr2:crashes)`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `norm(ym:cr2:crashDevices)`, `ym:cr2:crashDevices` / `ym:ge:uniqDeviceIDHash` AS `ym:cr2:crashesDevicesPercentage`, `ym:cr2:crashesUndecoded` AS `ym:cr2:crashesUndecoded` FROM (WITH 1.0 AS W SELECT DecodeGroupID AS `ym:cr:crashGroupObj`, toInt64(1) AS `ym:cr2:joiner`, max(`ym:cr:crashGroupObj` = toUInt64(0) ? 'Крэши без группы' : (OperatingSystem = 'android' ? (notEmpty(CrashReason) ? CrashReason || ' at ' || (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)'))) : (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)')))) : (notEmpty(CrashReason) ? CrashReason || ' at ' || (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)')) : (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)'))))) AS `ym:cr:crashGroupName`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupStatus`, max((APIKey,`ym:cr:crashGroupObj`,toString(OperatingSystem))) AS `ym:cr:crashGroupComment`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupFirstOccurrence`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupLastOccurrence`, max(CrashBinaryName) AS `ym:cr:crashBinaryName`, max(CrashFileName) AS `ym:cr:crashFileName`, max(CrashMethodName) AS `ym:cr:crashMethodName`, max(toInt64(CrashSourceLine)) AS `ym:cr:crashSourceLine`, sum(Sign) AS `ym:cr2:crashes`, sum(Sign) AS `norm(ym:cr2:crashes)`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes`, sumIf(Sign,DecodeStatus = 'parse_success') AS `ym:cr2:crashesUndecoded` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'android' GROUP BY `ym:cr:crashGroupObj`, toInt64(1) WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) global any left join (WITH 1.0 AS W SELECT toInt64(1) AS `ym:cr2:joiner`, uniq(DeviceIDHash) AS `ym:ge:uniqDeviceIDHash` FROM mobile.generic_events_layer as `mobile.generic_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and toString(OperatingSystem) = 'android' GROUP BY toInt64(1) WITH TOTALS ) using `ym:cr2:joiner` ORDER BY `ym:cr2:crashes` DESC, `ym:cr2:crashGroupObj` ASC limit 0,30",
                                "params": {
                                    "compress": "1",
                                    "extremes": "1",
                                    "distributed_aggregation_memory_efficient": "1"
                                },
                                "time": 1824,
                                "rows": 30,
                                "request_id": "1648824712578676-216757691198954165",
                                "event_date_time": "2022-04-01 17:51:52",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "clickhouse",
                                "base_time": 1648824712594,
                                "query_hash": 773951988
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.status AS status FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                "time": 57,
                                "rows": 29,
                                "request_id": "1648824712578676-216757691198954165",
                                "event_date_time": "2022-04-01 17:51:54",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648824714418,
                                "query_hash": 1236279510
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.comment AS comment FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                "time": 41,
                                "rows": 29,
                                "request_id": "1648824712578676-216757691198954165",
                                "event_date_time": "2022-04-01 17:51:54",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648824714475,
                                "query_hash": 685406326
                            },
                            {
                                "host": "ydb-ru.yandex.net:2135",
                                "database": "/ru/metricmob/production/crashes",
                                "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    MIN((t.create_time, t.app_build_number, t.app_version_name)) AS first_occurrence,    MAX((t.create_time, t.app_build_number, t.app_version_name)) AS last_occurrence FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/app_versions` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id GROUP BY k.app_id, k.event_type, k.crash_group_id",
                                "time": 29,
                                "rows": 29,
                                "request_id": "1648824712578676-216757691198954165",
                                "event_date_time": "2022-04-01 17:51:54",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "ydb",
                                "base_time": 1648824714516,
                                "query_hash": 731624932
                            }
                        ],
                        "additional": {
                            "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                            "layer": "0"
                        },
                        "base_time": 1648824712583,
                        "request_id": "1648824712578676-216757691198954165",
                        "request_uid": 1406498655,
                        "total_time": 1964,
                        "java_time": 12
                    },
                    "apiRequestUrl": "http://mobmetd-production.metrika.yandex.net/stat/v1/data?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D'android'&id=25378&date1=2019-09-01&date2=2019-09-30&metrics=ym%3Acr2%3Acrashes%2Cnorm(ym%3Acr2%3Acrashes)%2Cym%3Acr2%3AcrashDevices%2Cnorm(ym%3Acr2%3AcrashDevices)%2Cym%3Acr2%3AcrashesDevicesPercentage%2Cym%3Acr2%3AcrashesUndecoded&dimensions=ym%3Acr2%3AcrashGroupObj&sort=-ym%3Acr2%3Acrashes&offset=1&limit=30&include_undefined=true&debug=json&accuracy=1&proposedAccuracy=true&uid=1406498655"
                },
                "_profile": [
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648824712355,
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
                            "baseTime": 1648824712355,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=sessionid&host=appmetrica.yandex.ru&userip=2a02%3A6b8%3A81%3A0%3A5de7%3Ae1a0%3A9394%3A6cad&regname=yes&format=json&emails=getdefault&dbfields=subscription.login.669&get_user_ticket=1",
                            "method": "get",
                            "time": 9,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648824712366,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=checkip&ip=2a02%3A6b8%3A81%3A0%3A5de7%3Ae1a0%3A9394%3A6cad&nets=yandexusers&format=json",
                            "method": "get",
                            "time": 3,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648824712370,
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
                            "baseTime": 1648824712379,
                            "success": true,
                            "url": "http://mobmetd-production.metrika.yandex.net/management/v1/application/25378?interface=1&lang=ru&request_domain=ru&uid=1406498655",
                            "method": "get",
                            "time": 198,
                            "headers": null,
                            "data": "{\n  \"application\": {\n    \"name\": \"Яндекс.Музыка\",\n    \"time_zone_name\": \"Europe/Moscow\",\n    \"hide_address\": false,\n    \"gdpr_agreement_accepted\": false,\n    \"category\": 118,\n    \"bundle_id\": \"ru.yandex.mobile.music\",\n    \"team_id\": \"PGB36VEQ8D\",\n    \"use_universal_links\": true,\n    \"universal_link\": \"applinks:25378.redirect.appmetrica.yandex.com\",\n    \"metrika_counters\": [],\n    \"id\": 25378,\n    \"uid\": 178121744,\n    \"owner_login\": \"yastorepublisher\",\n    \"api_key128\": \"d7fc6f68-96e6-4764-a506-50908c78d2ef\",\n    \"import_token\": \"1d14c193-8602-4fec-b0d7-44094f68d0d8\",\n    \"permission\": \"edit\",\n    \"features\": [\n      \"ios\"\n    ],\n    \"time_zone_offset\": 10800,\n    \"create_date\": \"2015-05-01\"\n  }\n}",
                            "error": false,
                            "_profile": {
                                "queries": [
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712386,
                                        "query_hash": 975835054
                                    },
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "  SELECT a.*, b.label label, b.id label_id,    convert(pi.package_id using utf8) package_id,    convert(ti.apple_team_id using utf8) team_id,    u.use_universal_links use_universal_links ,    e.email notification_email   FROM applications a   LEFT JOIN user_labels g on (g.uid = ? and g.apikey = a.id)   LEFT JOIN labels b on (b.id = g.label_id and b.status = 'active')   LEFT JOIN apple_team_ids ti on (ti.application_id = a.id)   LEFT JOIN packages_ids pi on (pi.application_id = a.id)   LEFT JOIN use_universal_links u on (u.application_id = a.id)   LEFT JOIN notification_emails e on (e.application_id = a.id) WHERE a.id IN (25378) AND a.status = ?",
                                        "params": "[1406498655, active]",
                                        "time": 2,
                                        "rows": 1,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712387,
                                        "query_hash": 1685266620
                                    },
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT application_id, feature_name FROM application_features WHERE application_id IN (25378)",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712389,
                                        "query_hash": 1871037701
                                    },
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT DISTINCT application_id, metrika_counter_id FROM ecommerce_convert_rules WHERE application_id IN (25378) AND event_type = ? AND origin = 'interface'",
                                        "params": "[35]",
                                        "time": 0,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712390,
                                        "query_hash": 2012856126
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT o.obj_id, o.obj_type, o.created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid IN (1406498655) AND o.obj_type IN (?, ?) AND u.role_id = ? AND o.obj_id IN (25378)",
                                        "params": "[13, 14, 1]",
                                        "time": 21,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712390,
                                        "query_hash": 1359317459
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT o.obj_id, o.obj_type, o.created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid IN (1406498655) AND o.obj_type IN (?, ?) AND u.role_id = ? AND o.obj_id IN (25378)",
                                        "params": "[29, 28, 1]",
                                        "time": 20,
                                        "rows": 1,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712411,
                                        "query_hash": 1359317459
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 20, 1]",
                                        "time": 21,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712431,
                                        "query_hash": 1809974776
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 21, 1]",
                                        "time": 20,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712452,
                                        "query_hash": 1809974776
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 22, 1]",
                                        "time": 20,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712472,
                                        "query_hash": 1809974776
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id FROM uid_role_class u JOIN role_perm rp ON rp.role_id = u.role_id JOIN objects o USE INDEX (reverse_primary) ON ((o.class = u.class )  OR u.class = 1) AND rp.obj_type = o.obj_type WHERE (u.uid IN (1406498655) OR u.uid = 0) AND rp.perm_id IN (32) AND o.obj_id IN (25378)",
                                        "time": 22,
                                        "rows": 1,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712492,
                                        "query_hash": 37018707
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 20, 1]",
                                        "time": 20,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712514,
                                        "query_hash": 1809974776
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 21, 1]",
                                        "time": 19,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712534,
                                        "query_hash": 1809974776
                                    },
                                    {
                                        "host": "mdba9rfv14fq4q6vfvsh.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "rbac",
                                        "query": "SELECT DISTINCT o.obj_id AS obj_id,    o.created_at AS created_at FROM uid_role_class u JOIN objects o ON o.class = u.class WHERE uid = ? AND o.obj_type = ? AND u.role_id = ?",
                                        "params": "[1406498655, 22, 1]",
                                        "time": 18,
                                        "rows": 0,
                                        "request_id": "1648824712380731-4232978586997814829",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712553,
                                        "query_hash": 1809974776
                                    }
                                ],
                                "additional": {
                                    "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080"
                                },
                                "base_time": 1648824712385,
                                "request_id": "1648824712380731-4232978586997814829",
                                "request_uid": 1406498655,
                                "total_time": 187,
                                "java_time": 2
                            }
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1648824712578,
                            "success": true,
                            "url": "http://mobmetd-production.metrika.yandex.net/stat/v1/data?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D%27android%27&id=25378&date1=2019-09-01&date2=2019-09-30&metrics=ym%3Acr2%3Acrashes%2Cnorm%28ym%3Acr2%3Acrashes%29%2Cym%3Acr2%3AcrashDevices%2Cnorm%28ym%3Acr2%3AcrashDevices%29%2Cym%3Acr2%3AcrashesDevicesPercentage%2Cym%3Acr2%3AcrashesUndecoded&dimensions=ym%3Acr2%3AcrashGroupObj&sort=-ym%3Acr2%3Acrashes&offset=1&limit=30&include_undefined=true&debug=json&accuracy=1&proposedAccuracy=true&uid=1406498655",
                            "method": "get",
                            "time": 1975,
                            "headers": null,
                            "data": "{\n  \"query\": {\n    \"ids\": [\n      25378\n    ],\n    \"dimensions\": [\n      \"ym:cr2:crashGroupObj\"\n    ],\n    \"metrics\": [\n      \"ym:cr2:crashes\",\n      \"norm(ym:cr2:crashes)\",\n      \"ym:cr2:crashDevices\",\n      \"norm(ym:cr2:crashDevices)\",\n      \"ym:cr2:crashesDevicesPercentage\",\n      \"ym:cr2:crashesUndecoded\"\n    ],\n    \"sort\": [\n      \"-ym:cr2:crashes\"\n    ],\n    \"humanized_filter\": \"\",\n    \"date1\": \"2019-09-01\",\n    \"date2\": \"2019-09-30\",\n    \"filters\": \"ym:cr2:operatingSystemInfo=='android'\",\n    \"limit\": 30,\n    \"offset\": 1,\n    \"group\": \"Week\",\n    \"pca_integer_intervals\": \"false\",\n    \"auto_group_size\": \"1\",\n    \"pca_intervals_length\": \"0\",\n    \"quantile\": \"50\",\n    \"from\": \"0\",\n    \"currency\": \"XXX\",\n    \"funnel_window\": \"\",\n    \"to\": \"0\",\n    \"funnel_pattern\": \"\",\n    \"funnel_restriction\": \"\",\n    \"profile_attribute_id\": \"0\"\n  },\n  \"data\": [\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"0\",\n          \"name\": \"Крэши без группы\",\n          \"status\": \"OPEN\",\n          \"comment\": \"Версия AppMetrica SDK меньше 3.6.0\",\n          \"first_occurrence\": null,\n          \"last_occurrence\": null,\n          \"binary_name\": null,\n          \"file_name\": null,\n          \"method_name\": null,\n          \"source_line\": \"0\"\n        }\n      ],\n      \"metrics\": [\n        68021,\n        64.12236048,\n        22032,\n        56.00691443,\n        0.38108911,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"3749432279756674295\",\n          \"name\": \"android.database.sqlite.SQLiteFullException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.2 #3201 (3201)\",\n          \"last_occurrence\": \"2022.03.3 #4674 (24022162)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativeExecuteForChangedRowCount\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        8059,\n        7.59709653,\n        2455,\n        6.24078499,\n        0.04246431,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"12454995534919700191\",\n          \"name\": \"java.lang.IllegalStateException at SourceFile:72\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 BETA.3 #3248 (3248)\",\n          \"last_occurrence\": \"2019.10.1 2947 #12874-review (12874)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.recyclerview.widget.LoggingRecyclerView.addView\",\n          \"source_line\": \"72\"\n        }\n      ],\n      \"metrics\": [\n        2733,\n        2.57635747,\n        2655,\n        6.74919925,\n        0.04592373,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"18105866812809628971\",\n          \"name\": \"android.database.sqlite.SQLiteFullException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.1 #3177 (3177)\",\n          \"last_occurrence\": \"2022.03.3 #4674 (24022162)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativeExecuteForLastInsertedRowId\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        2568,\n        2.42081448,\n        1367,\n        3.47501144,\n        0.0236451,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"5785868980532715233\",\n          \"name\": \"android.database.sqlite.SQLiteException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.1 #3177 (3177)\",\n          \"last_occurrence\": \"2022.03.3 #4674 (24022162)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativeExecute\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        2223,\n        2.09558824,\n        1292,\n        3.28435609,\n        0.02234782,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"10427529621369709895\",\n          \"name\": \"android.database.sqlite.SQLiteException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"last_occurrence\": \"2022.03.3 #4674 (24022162)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativePrepareStatement\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        1335,\n        1.25848416,\n        47,\n        0.11947735,\n        0.00081296,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"4134954119304559650\",\n          \"name\": \"android.database.sqlite.SQLiteException at SourceFile:426\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.2 #3269 (3269)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.setLocaleFromConfiguration\",\n          \"source_line\": \"426\"\n        }\n      ],\n      \"metrics\": [\n        1153,\n        1.08691554,\n        102,\n        0.25929127,\n        0.0017643,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"1349492918128318962\",\n          \"name\": \"java.lang.IllegalStateException at SourceFile:8121\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 BETA.1 #3232 (3232)\",\n          \"last_occurrence\": \"2019.06.2 #3208 (3208)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"com.yandex.passport.internal.ag.b\",\n          \"source_line\": \"8121\"\n        }\n      ],\n      \"metrics\": [\n        745,\n        0.70230015,\n        192,\n        0.48807769,\n        0.00332104,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"6226919780114714676\",\n          \"name\": \"android.os.DeadSystemException at (Unknown Source)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"24021155 (24021155)\",\n          \"binary_name\": null,\n          \"file_name\": null,\n          \"method_name\": \"com.google.android.gms.common.d.do\",\n          \"source_line\": \"64\"\n        }\n      ],\n      \"metrics\": [\n        729,\n        0.68721719,\n        636,\n        1.61675733,\n        0.01100094,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"10968604898541102144\",\n          \"name\": \"java.lang.IllegalStateException at SourceFile:851\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.1.3207 (3207)\",\n          \"last_occurrence\": \"2019.06.2 BETA.2 #3202 (3202)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.recyclerview.widget.RecyclerView$5.addView\",\n          \"source_line\": \"851\"\n        }\n      ],\n      \"metrics\": [\n        580,\n        0.54675716,\n        562,\n        1.42864406,\n        0.00972095,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"14314865551578678258\",\n          \"name\": \"java.lang.NullPointerException at SourceFile:51\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.2 #3201 (3201)\",\n          \"last_occurrence\": \"2020.03.1 #3395 (3395)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"okhttp3.r.do\",\n          \"source_line\": \"51\"\n        }\n      ],\n      \"metrics\": [\n        503,\n        0.47417044,\n        26,\n        0.06609385,\n        0.00044972,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7132796517861447921\",\n          \"name\": \"android.os.DeadSystemException at SourceFile:20\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"0.0\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"cdj.bS\",\n          \"source_line\": \"20\"\n        }\n      ],\n      \"metrics\": [\n        489,\n        0.46097285,\n        316,\n        0.80329452,\n        0.00546588,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7337392191131051460\",\n          \"name\": \"java.lang.ClassNotFoundException at SourceFile\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"ru.yandex.music.utils.f$1.handleMessage\",\n          \"source_line\": \"-1\"\n        }\n      ],\n      \"metrics\": [\n        411,\n        0.38744344,\n        1,\n        0.00254207,\n        0.0000173,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"3227164132574439880\",\n          \"name\": \"android.os.TransactionTooLargeException at PendingTransactionActions.java:160\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.06.1.3207 (3207)\",\n          \"binary_name\": null,\n          \"file_name\": \"PendingTransactionActions.java\",\n          \"method_name\": \"android.app.servertransaction.PendingTransactionActions$StopInfo.run\",\n          \"source_line\": \"160\"\n        }\n      ],\n      \"metrics\": [\n        373,\n        0.35162142,\n        219,\n        0.55671361,\n        0.00378806,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7117268639141053778\",\n          \"name\": \"java.lang.UnsatisfiedLinkError at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.07.1 #3218 (3218)\",\n          \"last_occurrence\": \"2020.08.1 #3525 (23020402)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"ru.yandex.speechkit.BaseSpeechKit.native_getContext\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        320,\n        0.30165913,\n        292,\n        0.74228481,\n        0.00505075,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"15256811207195161215\",\n          \"name\": \"android.database.sqlite.SQLiteException at SourceFile:378\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.1 #3224 (3224)\",\n          \"last_occurrence\": \"2022.03.4-SNAPSHOT #0 (24022170)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteOpenHelper.onDowngrade\",\n          \"source_line\": \"378\"\n        }\n      ],\n      \"metrics\": [\n        278,\n        0.26206637,\n        26,\n        0.06609385,\n        0.00044972,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"16091661245656610237\",\n          \"name\": \"android.database.sqlite.SQLiteDiskIOException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.07.1 #3218 (3218)\",\n          \"last_occurrence\": \"2022.03.3 #4674 (24022162)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativeExecute\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        270,\n        0.25452489,\n        203,\n        0.51604047,\n        0.00351131,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7846353672167316612\",\n          \"name\": \"java.lang.NullPointerException at SourceFile:769\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.05.2 BETA.2 #3147 (3147)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"com.facebook.internal.ad.do\",\n          \"source_line\": \"769\"\n        }\n      ],\n      \"metrics\": [\n        257,\n        0.24226998,\n        257,\n        0.65331232,\n        0.00444535,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"10874962601629735121\",\n          \"name\": \"com.facebook.p at SourceFile:144\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.1 #3249 (21019455)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"com.facebook.internal.ae.HO\",\n          \"source_line\": \"144\"\n        }\n      ],\n      \"metrics\": [\n        230,\n        0.2168175,\n        228,\n        0.57959225,\n        0.00394373,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"14246962484232748584\",\n          \"name\": \"java.lang.AssertionError at SourceFile:18\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.1 BETA.4 #3250 (3250)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"bkp.for\",\n          \"source_line\": \"18\"\n        }\n      ],\n      \"metrics\": [\n        223,\n        0.2102187,\n        221,\n        0.56179775,\n        0.00382265,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"9180328120649562380\",\n          \"name\": \"java.lang.OutOfMemoryError at SourceFile:114\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"ru.yandex.music.common.service.player.p.bxt\",\n          \"source_line\": \"114\"\n        }\n      ],\n      \"metrics\": [\n        208,\n        0.19607843,\n        130,\n        0.33046927,\n        0.00224862,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"10429823020601280834\",\n          \"name\": \"java.lang.IllegalArgumentException at SourceFile:44\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.core.app.p$a.hP\",\n          \"source_line\": \"44\"\n        }\n      ],\n      \"metrics\": [\n        203,\n        0.19136501,\n        160,\n        0.4067314,\n        0.00276753,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"7794102704581947677\",\n          \"name\": \"android.system.ErrnoException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"last_occurrence\": \"2021.07.3 #4004 (24021362)\",\n          \"binary_name\": null,\n          \"file_name\": \"Posix.java\",\n          \"method_name\": \"libcore.io.Posix.android_getaddrinfo\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        192,\n        0.18099548,\n        13,\n        0.03304693,\n        0.00022486,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"15778048293593109084\",\n          \"name\": \"android.database.sqlite.SQLiteFullException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.2 #3201 (3201)\",\n          \"last_occurrence\": \"2022.03.1 #4615 (24022152)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativeExecute\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        168,\n        0.15837104,\n        146,\n        0.37114241,\n        0.00252537,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"13735952367628980377\",\n          \"name\": \"java.lang.SecurityException at SourceFile:192\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"last_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.core.app.JobIntentService$c.if\",\n          \"source_line\": \"192\"\n        }\n      ],\n      \"metrics\": [\n        161,\n        0.15177225,\n        1,\n        0.00254207,\n        0.0000173,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"11618892406029957186\",\n          \"name\": \"java.lang.IllegalStateException at SourceFile:965\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.06.2 #3201 (3201)\",\n          \"last_occurrence\": \"2021.12.2 6460 #18171 (24021610)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnectionPool.throwIfClosedLocked\",\n          \"source_line\": \"965\"\n        }\n      ],\n      \"metrics\": [\n        155,\n        0.14611614,\n        151,\n        0.38385276,\n        0.00261186,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"1536281939572358247\",\n          \"name\": \"java.lang.SecurityException at SourceFile:216\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"last_occurrence\": \"2019.09.1 #3249 (3249)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.core.app.JobIntentService$c.hT\",\n          \"source_line\": \"216\"\n        }\n      ],\n      \"metrics\": [\n        153,\n        0.14423077,\n        1,\n        0.00254207,\n        0.0000173,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"6558440617702936992\",\n          \"name\": \"android.view.WindowManager$BadTokenException at SourceFile:1007\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"last_occurrence\": \"2019.09.2 BETA.1 #3257 (3257)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"androidx.appcompat.app.a$a.ae\",\n          \"source_line\": \"1007\"\n        }\n      ],\n      \"metrics\": [\n        141,\n        0.13291855,\n        140,\n        0.35588998,\n        0.00242159,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"16713851609740653738\",\n          \"name\": \"android.database.sqlite.SQLiteDatabaseLockedException at (Native Method)\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.08.2 #3233 (3233)\",\n          \"last_occurrence\": \"2022.03.2 #4640 (24022157)\",\n          \"binary_name\": null,\n          \"file_name\": \"SourceFile\",\n          \"method_name\": \"io.requery.android.database.sqlite.SQLiteConnection.nativePrepareStatement\",\n          \"source_line\": \"-2\"\n        }\n      ],\n      \"metrics\": [\n        131,\n        0.1234917,\n        99,\n        0.25166506,\n        0.00171241,\n        0\n      ]\n    },\n    {\n      \"dimensions\": [\n        {\n          \"id\": \"5119767380137259633\",\n          \"name\": \"java.lang.IllegalStateException at ViewGroup.java:5099\",\n          \"status\": \"OPEN\",\n          \"comment\": \"\",\n          \"first_occurrence\": \"2019.09.2 #3263 (3263)\",\n          \"last_occurrence\": \"2020.09.1 #3542 (23020451)\",\n          \"binary_name\": null,\n          \"file_name\": \"ViewGroup.java\",\n          \"method_name\": \"android.view.ViewGroup.addViewInner\",\n          \"source_line\": \"5099\"\n        }\n      ],\n      \"metrics\": [\n        122,\n        0.11500754,\n        121,\n        0.30759062,\n        0.00209295,\n        0\n      ]\n    }\n  ],\n  \"meta\": {\n    \"dimensions\": [\n      {\n        \"id\": \"CrashGroupObj\",\n        \"dim\": \"ym:cr2:crashGroupObj\",\n        \"name\": \"Описание группы крэша\",\n        \"short_name\": \"Описание группы крэша\",\n        \"internal_type\": \"UInt64\",\n        \"allow_filters\": false,\n        \"fields\": {\n          \"last_occurrence\": {\n            \"id\": \"CrashGroupLastOccurrence\",\n            \"dim\": \"ym:cr2:crashGroupLastOccurrence\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"first_occurrence\": {\n            \"id\": \"CrashGroupFirstOccurrence\",\n            \"dim\": \"ym:cr2:crashGroupFirstOccurrence\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"method_name\": {\n            \"id\": \"CrashMethodName\",\n            \"dim\": \"ym:cr2:crashMethodName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"file_name\": {\n            \"id\": \"CrashFileName\",\n            \"dim\": \"ym:cr2:crashFileName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"source_line\": {\n            \"id\": \"CrashSourceLine\",\n            \"dim\": \"ym:cr2:crashSourceLine\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Int64\",\n            \"allow_filters\": false,\n            \"allow_sort\": true,\n            \"default_sort\": \"desc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"name\": {\n            \"id\": \"CrashGroupName\",\n            \"dim\": \"ym:cr2:crashGroupName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"comment\": {\n            \"id\": \"CrashGroupComment\",\n            \"dim\": \"ym:cr2:crashGroupComment\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64,String)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"id\": {\n            \"id\": \"CrashGroupObj\",\n            \"dim\": \"ym:cr2:crashGroupObj\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"UInt64\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"binary_name\": {\n            \"id\": \"CrashBinaryName\",\n            \"dim\": \"ym:cr2:crashBinaryName\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"String\",\n            \"allow_filters\": true,\n            \"allow_sort\": true,\n            \"default_sort\": \"asc\",\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          },\n          \"status\": {\n            \"id\": \"CrashGroupStatus\",\n            \"dim\": \"ym:cr2:crashGroupStatus\",\n            \"name\": \"Описание группы крэша\",\n            \"short_name\": \"Описание группы крэша\",\n            \"internal_type\": \"Tuple(UInt32,UInt64)\",\n            \"allow_filters\": false,\n            \"allow_sort\": false,\n            \"allow_null\": false,\n            \"permission_scope\": \"common\",\n            \"required_keys\": [\n              \"app\"\n            ],\n            \"secret\": false,\n            \"exposes_secret_data\": false,\n            \"disjoint\": true\n          }\n        },\n        \"allow_sort\": false,\n        \"allow_null\": false,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"disjoint\": true\n      }\n    ],\n    \"metrics\": [\n      {\n        \"dim\": \"ym:cr2:crashes\",\n        \"name\": \"Количество крэшей\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"norm(ym:cr2:crashes)\",\n        \"metric_string\": \"norm(ym:cr2:crashes)\",\n        \"name\": \"Количество крэшей\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashDevices\",\n        \"metric_string\": \"ym:cr2:crashDevices\",\n        \"name\": \"Количество устройств, на которых возникли аварийные остановки приложения\",\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"norm(ym:cr2:crashDevices)\",\n        \"metric_string\": \"norm(ym:cr2:crashDevices)\",\n        \"name\": \"Количество устройств, на которых возникли аварийные остановки приложения\",\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashesDevicesPercentage\",\n        \"metric_string\": \"ym:cr2:crashesDevicesPercentage\",\n        \"name\": \"Процент устройств с крэшами\",\n        \"allow_filters\": true,\n        \"type\": \"percents\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashesUndecoded\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      }\n    ]\n  },\n  \"total_rows\": 1799,\n  \"total_rows_rounded\": false,\n  \"sampled\": false,\n  \"sampleable\": true,\n  \"contains_sensitive_data\": false,\n  \"sample_share\": 1,\n  \"max_sample_share\": 0.0001,\n  \"sample_size\": 61255475760,\n  \"sample_space\": 61255475760,\n  \"data_lag\": 0,\n  \"totals\": [\n    106080,\n    100,\n    39338,\n    100,\n    0.68043225,\n    0\n  ],\n  \"min\": [\n    122,\n    0.11500754,\n    1,\n    0.00254207,\n    0.0000173,\n    0\n  ],\n  \"max\": [\n    68021,\n    64.12236048,\n    22032,\n    56.00691443,\n    0.38108911,\n    0\n  ]\n}",
                            "error": false,
                            "_profile": {
                                "queries": [
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1648824712578676-216757691198954165",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1648824712584,
                                        "query_hash": 975835054
                                    },
                                    {
                                        "host": "mtmobgiga049-1.metrika.yandex.net:8123",
                                        "query": "WITH 1.0 AS W SELECT `ym:cr:crashGroupObj` AS `ym:cr2:crashGroupObj`, `ym:cr:crashGroupName` AS `ym:cr2:crashGroupName`, `ym:cr:crashGroupStatus` AS `ym:cr2:crashGroupStatus`, `ym:cr:crashGroupComment` AS `ym:cr2:crashGroupComment`, `ym:cr:crashGroupFirstOccurrence` AS `ym:cr2:crashGroupFirstOccurrence`, `ym:cr:crashGroupLastOccurrence` AS `ym:cr2:crashGroupLastOccurrence`, `ym:cr:crashBinaryName` AS `ym:cr2:crashBinaryName`, `ym:cr:crashFileName` AS `ym:cr2:crashFileName`, `ym:cr:crashMethodName` AS `ym:cr2:crashMethodName`, `ym:cr:crashSourceLine` AS `ym:cr2:crashSourceLine`, `ym:cr2:crashes` AS `ym:cr2:crashes`, `norm(ym:cr2:crashes)` AS `norm(ym:cr2:crashes)`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `norm(ym:cr2:crashDevices)`, `ym:cr2:crashDevices` / `ym:ge:uniqDeviceIDHash` AS `ym:cr2:crashesDevicesPercentage`, `ym:cr2:crashesUndecoded` AS `ym:cr2:crashesUndecoded` FROM (WITH 1.0 AS W SELECT DecodeGroupID AS `ym:cr:crashGroupObj`, toInt64(1) AS `ym:cr2:joiner`, max(`ym:cr:crashGroupObj` = toUInt64(0) ? 'Крэши без группы' : (OperatingSystem = 'android' ? (notEmpty(CrashReason) ? CrashReason || ' at ' || (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)'))) : (CrashSourceLine = 18446744073709551614 ? '(Native Method)' : (notEmpty(CrashFileName) AND toInt64(CrashSourceLine) > toInt64(0) ? CrashFileName || ':' || toString(CrashSourceLine) : (notEmpty(CrashFileName) ? CrashFileName : '(Unknown Source)')))) : (notEmpty(CrashReason) ? CrashReason || ' at ' || (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)')) : (notEmpty(CrashFileName) ? CrashFileName || (CrashSourceLine != toUInt64(0) ? ':' || toString(toInt64(CrashSourceLine)) : '') : (notEmpty(CrashBinaryName) ? CrashBinaryName : '(Missing)'))))) AS `ym:cr:crashGroupName`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupStatus`, max((APIKey,`ym:cr:crashGroupObj`,toString(OperatingSystem))) AS `ym:cr:crashGroupComment`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupFirstOccurrence`, max((APIKey,`ym:cr:crashGroupObj`)) AS `ym:cr:crashGroupLastOccurrence`, max(CrashBinaryName) AS `ym:cr:crashBinaryName`, max(CrashFileName) AS `ym:cr:crashFileName`, max(CrashMethodName) AS `ym:cr:crashMethodName`, max(toInt64(CrashSourceLine)) AS `ym:cr:crashSourceLine`, sum(Sign) AS `ym:cr2:crashes`, sum(Sign) AS `norm(ym:cr2:crashes)`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes`, sumIf(Sign,DecodeStatus = 'parse_success') AS `ym:cr2:crashesUndecoded` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'android' GROUP BY `ym:cr:crashGroupObj`, toInt64(1) WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) global any left join (WITH 1.0 AS W SELECT toInt64(1) AS `ym:cr2:joiner`, uniq(DeviceIDHash) AS `ym:ge:uniqDeviceIDHash` FROM mobile.generic_events_layer as `mobile.generic_events_layer` WHERE EventDate >= toDate('2019-09-01') and EventDate <= toDate('2019-09-30') and APIKey = toUInt32(25378) and toString(OperatingSystem) = 'android' GROUP BY toInt64(1) WITH TOTALS ) using `ym:cr2:joiner` ORDER BY `ym:cr2:crashes` DESC, `ym:cr2:crashGroupObj` ASC limit 0,30",
                                        "params": {
                                            "compress": "1",
                                            "extremes": "1",
                                            "distributed_aggregation_memory_efficient": "1"
                                        },
                                        "time": 1824,
                                        "rows": 30,
                                        "request_id": "1648824712578676-216757691198954165",
                                        "event_date_time": "2022-04-01 17:51:52",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "clickhouse",
                                        "base_time": 1648824712594,
                                        "query_hash": 773951988
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.status AS status FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                        "time": 57,
                                        "rows": 29,
                                        "request_id": "1648824712578676-216757691198954165",
                                        "event_date_time": "2022-04-01 17:51:54",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648824714418,
                                        "query_hash": 1236279510
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    t.comment AS comment FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/management` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id",
                                        "time": 41,
                                        "rows": 29,
                                        "request_id": "1648824712578676-216757691198954165",
                                        "event_date_time": "2022-04-01 17:51:54",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648824714475,
                                        "query_hash": 685406326
                                    },
                                    {
                                        "host": "ydb-ru.yandex.net:2135",
                                        "database": "/ru/metricmob/production/crashes",
                                        "query": "DECLARE $keys AS List<Struct<'app_id': Uint32, 'app_id_hash': Uint64, 'crash_group_id': Uint64, 'event_type': Uint8>>; SELECT    k.app_id AS app_id,    k.event_type AS event_type,    k.crash_group_id AS crash_group_id,    MIN((t.create_time, t.app_build_number, t.app_version_name)) AS first_occurrence,    MAX((t.create_time, t.app_build_number, t.app_version_name)) AS last_occurrence FROM AS_TABLE($keys) AS k INNER JOIN `crash_groups/app_versions` AS t ON t.app_id_hash = k.app_id_hash AND t.app_id = k.app_id AND t.event_type = k.event_type AND t.crash_group_id = k.crash_group_id GROUP BY k.app_id, k.event_type, k.crash_group_id",
                                        "time": 29,
                                        "rows": 29,
                                        "request_id": "1648824712578676-216757691198954165",
                                        "event_date_time": "2022-04-01 17:51:54",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "ydb",
                                        "base_time": 1648824714516,
                                        "query_hash": 731624932
                                    }
                                ],
                                "additional": {
                                    "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                                    "layer": "0"
                                },
                                "base_time": 1648824712583,
                                "request_id": "1648824712578676-216757691198954165",
                                "request_uid": 1406498655,
                                "total_time": 1964,
                                "java_time": 12
                            }
                        },
                        "isBlackbox": false
                    }
                ],
                "_version": "2.1243321415.2"
            }
        ]
    };


export const androidCrashGroupsGridMock = new Mock(
    /.*\/transport\/i-stat\/getData*/,
    androidCrashGroupsGridResponse
);

export const androidCrashGroupsChartResponse =
    {
        "response": [
            {
                "status": 200,
                "data": {
                    "query": {
                        "ids": [
                            25378
                        ],
                        "dimensions": [],
                        "metrics": [
                            "ym:cr2:crashes",
                            "ym:cr2:crashDevices"
                        ],
                        "sort": [
                            "-ym:cr2:crashes"
                        ],
                        "humanized_filter": "",
                        "date1": "2019-09-01",
                        "date2": "2019-09-30",
                        "filters": "ym:cr2:operatingSystemInfo=='android'",
                        "group": "day",
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
                        "profile_attribute_id": "0",
                        "auto_group_type": "day"
                    },
                    "data": [
                        {
                            "dimensions": [],
                            "metrics": [
                                [
                                    5000,
                                    6000,
                                    8000,
                                    1000,
                                    3609,
                                    3704,
                                    3693,
                                    3692,
                                    3586,
                                    3701,
                                    3729,
                                    3541,
                                    3504,
                                    3711,
                                    3460,
                                    3205,
                                    3434,
                                    3329,
                                    3376,
                                    3365,
                                    3408,
                                    3466,
                                    3428,
                                    3393,
                                    3475,
                                    3361,
                                    3346,
                                    3994,
                                    3603,
                                    3400
                                ],
                                [
                                    1861,
                                    1873,
                                    1952,
                                    1965,
                                    1916,
                                    2010,
                                    1980,
                                    1905,
                                    1845,
                                    1889,
                                    1935,
                                    1869,
                                    1942,
                                    1939,
                                    1790,
                                    1758,
                                    1770,
                                    1739,
                                    1754,
                                    1835,
                                    1866,
                                    1781,
                                    1812,
                                    1821,
                                    1834,
                                    1773,
                                    1871,
                                    1891,
                                    1877,
                                    1785
                                ]
                            ]
                        }
                    ],
                    "meta": {
                        "dimensions": [],
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
                            }
                        ]
                    },
                    "total_rows": 30,
                    "total_rows_rounded": false,
                    "sampled": false,
                    "sampleable": true,
                    "contains_sensitive_data": false,
                    "sample_share": 1,
                    "max_sample_share": 0.0001,
                    "sample_size": 63497086050,
                    "sample_space": 63497086050,
                    "data_lag": 0,
                    "totals": [
                        [
                            106080,
                            39338
                        ]
                    ],
                    "time_intervals": [
                        [
                            "2019-09-01",
                            "2019-09-01"
                        ],
                        [
                            "2019-09-02",
                            "2019-09-02"
                        ],
                        [
                            "2019-09-03",
                            "2019-09-03"
                        ],
                        [
                            "2019-09-04",
                            "2019-09-04"
                        ],
                        [
                            "2019-09-05",
                            "2019-09-05"
                        ],
                        [
                            "2019-09-06",
                            "2019-09-06"
                        ],
                        [
                            "2019-09-07",
                            "2019-09-07"
                        ],
                        [
                            "2019-09-08",
                            "2019-09-08"
                        ],
                        [
                            "2019-09-09",
                            "2019-09-09"
                        ],
                        [
                            "2019-09-10",
                            "2019-09-10"
                        ],
                        [
                            "2019-09-11",
                            "2019-09-11"
                        ],
                        [
                            "2019-09-12",
                            "2019-09-12"
                        ],
                        [
                            "2019-09-13",
                            "2019-09-13"
                        ],
                        [
                            "2019-09-14",
                            "2019-09-14"
                        ],
                        [
                            "2019-09-15",
                            "2019-09-15"
                        ],
                        [
                            "2019-09-16",
                            "2019-09-16"
                        ],
                        [
                            "2019-09-17",
                            "2019-09-17"
                        ],
                        [
                            "2019-09-18",
                            "2019-09-18"
                        ],
                        [
                            "2019-09-19",
                            "2019-09-19"
                        ],
                        [
                            "2019-09-20",
                            "2019-09-20"
                        ],
                        [
                            "2019-09-21",
                            "2019-09-21"
                        ],
                        [
                            "2019-09-22",
                            "2019-09-22"
                        ],
                        [
                            "2019-09-23",
                            "2019-09-23"
                        ],
                        [
                            "2019-09-24",
                            "2019-09-24"
                        ],
                        [
                            "2019-09-25",
                            "2019-09-25"
                        ],
                        [
                            "2019-09-26",
                            "2019-09-26"
                        ],
                        [
                            "2019-09-27",
                            "2019-09-27"
                        ],
                        [
                            "2019-09-28",
                            "2019-09-28"
                        ],
                        [
                            "2019-09-29",
                            "2019-09-29"
                        ],
                        [
                            "2019-09-30",
                            "2019-09-30"
                        ]
                    ],
                    "_profile": {
                        "queries": [
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                "time": 1,
                                "rows": 0,
                                "request_id": "1649060863588107-14312884652228168942",
                                "event_date_time": "2022-04-04 11:27:43",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1649060863594,
                                "query_hash": 975835054
                            },
                            {
                                "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                "database": "mobile",
                                "query": "select sum(rows_count) from applications where id in (25378)",
                                "time": 1,
                                "rows": 0,
                                "request_id": "1649060863588107-14312884652228168942",
                                "event_date_time": "2022-04-04 11:27:43",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "mysql",
                                "base_time": 1649060863596,
                                "query_hash": 1759072458
                            },
                            {
                                "host": "mtmobgiga153-3.metrika.yandex.net:8123",
                                "query": "WITH 1.0 AS W SELECT `ym:cr2:date` AS `ym:cr2:date`, `ym:cr2:crashes` AS `ym:cr2:crashes`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices` FROM (WITH 1.0 AS W SELECT EventDate AS `ym:cr2:date`, sum(Sign) AS `ym:cr2:crashes`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE `ym:cr2:date` >= toDate('2019-09-01') and `ym:cr2:date` <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'android' GROUP BY `ym:cr2:date` WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) ORDER BY `ym:cr2:date` ASC limit 0,30",
                                "params": {
                                    "compress": "1",
                                    "extremes": "1",
                                    "distributed_aggregation_memory_efficient": "1"
                                },
                                "time": 657,
                                "rows": 30,
                                "request_id": "1649060863588107-14312884652228168942",
                                "event_date_time": "2022-04-04 11:27:43",
                                "daemon_name": "yandex-metrika-mobmetd",
                                "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                "db_type": "clickhouse",
                                "base_time": 1649060863601,
                                "query_hash": 1632527817
                            }
                        ],
                        "additional": {
                            "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                            "layer": "0"
                        },
                        "base_time": 1649060863594,
                        "request_id": "1649060863588107-14312884652228168942",
                        "request_uid": 1406498655,
                        "total_time": 665,
                        "java_time": 6
                    },
                    "apiRequestUrl": "http://mobmetd-production.metrika.yandex.net/stat/v1/data/bytime?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D'android'&id=25378&date1=2019-09-01&date2=2019-09-30&group=day&metrics=ym%3Acr2%3Acrashes%2Cym%3Acr2%3AcrashDevices&dimensions=&include_undefined=true&debug=json&require_metric_values=true&accuracy=1&proposedAccuracy=true&uid=1406498655"
                },
                "_profile": [
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649060863561,
                            "success": true,
                            "url": "http://localhost:4/tvm/tickets?dsts=2000337%2C222%2C2000268",
                            "method": "get",
                            "time": 7,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": false
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649060863560,
                            "success": true,
                            "url": "http://blackbox.yandex.net/blackbox?method=sessionid&host=appmetrica.yandex.ru&userip=2a02%3A6b8%3A81%3A0%3A102c%3A5203%3A5f0a%3Ae24f&regname=yes&format=json&emails=getdefault&dbfields=subscription.login.669&get_user_ticket=1",
                            "method": "get",
                            "time": 13,
                            "headers": null,
                            "data": "null",
                            "error": false
                        },
                        "isBlackbox": true
                    },
                    {
                        "type": "api-request",
                        "data": {
                            "baseTime": 1649060863577,
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
                            "baseTime": 1649060863586,
                            "success": true,
                            "url": "http://mobmetd-production.metrika.yandex.net/stat/v1/data/bytime?interface=1&lang=ru&request_domain=ru&filters=ym%3Acr2%3AoperatingSystemInfo%3D%3D%27android%27&id=25378&date1=2019-09-01&date2=2019-09-30&group=day&metrics=ym%3Acr2%3Acrashes%2Cym%3Acr2%3AcrashDevices&dimensions=&include_undefined=true&debug=json&require_metric_values=true&accuracy=1&proposedAccuracy=true&uid=1406498655",
                            "method": "get",
                            "time": 677,
                            "headers": null,
                            "data": "{\n  \"query\": {\n    \"ids\": [\n      25378\n    ],\n    \"dimensions\": [],\n    \"metrics\": [\n      \"ym:cr2:crashes\",\n      \"ym:cr2:crashDevices\"\n    ],\n    \"sort\": [\n      \"-ym:cr2:crashes\"\n    ],\n    \"humanized_filter\": \"\",\n    \"date1\": \"2019-09-01\",\n    \"date2\": \"2019-09-30\",\n    \"filters\": \"ym:cr2:operatingSystemInfo=='android'\",\n    \"group\": \"day\",\n    \"pca_integer_intervals\": \"false\",\n    \"auto_group_size\": \"1\",\n    \"pca_intervals_length\": \"0\",\n    \"quantile\": \"50\",\n    \"from\": \"0\",\n    \"currency\": \"XXX\",\n    \"funnel_window\": \"\",\n    \"to\": \"0\",\n    \"funnel_pattern\": \"\",\n    \"funnel_restriction\": \"\",\n    \"profile_attribute_id\": \"0\",\n    \"auto_group_type\": \"day\"\n  },\n  \"data\": [\n    {\n      \"dimensions\": [],\n      \"metrics\": [\n        [\n          3539,\n          3812,\n          3589,\n          3627,\n          3609,\n          3704,\n          3693,\n          3692,\n          3586,\n          3701,\n          3729,\n          3541,\n          3504,\n          3711,\n          3460,\n          3205,\n          3434,\n          3329,\n          3376,\n          3365,\n          3408,\n          3466,\n          3428,\n          3393,\n          3475,\n          3361,\n          3346,\n          3994,\n          3603,\n          3400\n        ],\n        [\n          1861,\n          1873,\n          1952,\n          1965,\n          1916,\n          2010,\n          1980,\n          1905,\n          1845,\n          1889,\n          1935,\n          1869,\n          1942,\n          1939,\n          1790,\n          1758,\n          1770,\n          1739,\n          1754,\n          1835,\n          1866,\n          1781,\n          1812,\n          1821,\n          1834,\n          1773,\n          1871,\n          1891,\n          1877,\n          1785\n        ]\n      ]\n    }\n  ],\n  \"meta\": {\n    \"dimensions\": [],\n    \"metrics\": [\n      {\n        \"dim\": \"ym:cr2:crashes\",\n        \"name\": \"Количество крэшей\",\n        \"allow_normalisation\": true,\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"support_confidence\": true,\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      },\n      {\n        \"dim\": \"ym:cr2:crashDevices\",\n        \"metric_string\": \"ym:cr2:crashDevices\",\n        \"name\": \"Количество устройств, на которых возникли аварийные остановки приложения\",\n        \"allow_filters\": true,\n        \"type\": \"int\",\n        \"allow_sort\": true,\n        \"default_sort\": \"desc\",\n        \"negative\": true,\n        \"permission_scope\": \"common\",\n        \"required_keys\": [\n          \"app\"\n        ],\n        \"secret\": false,\n        \"exposes_secret_data\": false,\n        \"additive\": true\n      }\n    ]\n  },\n  \"total_rows\": 30,\n  \"total_rows_rounded\": false,\n  \"sampled\": false,\n  \"sampleable\": true,\n  \"contains_sensitive_data\": false,\n  \"sample_share\": 1,\n  \"max_sample_share\": 0.0001,\n  \"sample_size\": 63497086050,\n  \"sample_space\": 63497086050,\n  \"data_lag\": 0,\n  \"totals\": [\n    [\n      106080,\n      39338\n    ]\n  ],\n  \"time_intervals\": [\n    [\n      \"2019-09-01\",\n      \"2019-09-01\"\n    ],\n    [\n      \"2019-09-02\",\n      \"2019-09-02\"\n    ],\n    [\n      \"2019-09-03\",\n      \"2019-09-03\"\n    ],\n    [\n      \"2019-09-04\",\n      \"2019-09-04\"\n    ],\n    [\n      \"2019-09-05\",\n      \"2019-09-05\"\n    ],\n    [\n      \"2019-09-06\",\n      \"2019-09-06\"\n    ],\n    [\n      \"2019-09-07\",\n      \"2019-09-07\"\n    ],\n    [\n      \"2019-09-08\",\n      \"2019-09-08\"\n    ],\n    [\n      \"2019-09-09\",\n      \"2019-09-09\"\n    ],\n    [\n      \"2019-09-10\",\n      \"2019-09-10\"\n    ],\n    [\n      \"2019-09-11\",\n      \"2019-09-11\"\n    ],\n    [\n      \"2019-09-12\",\n      \"2019-09-12\"\n    ],\n    [\n      \"2019-09-13\",\n      \"2019-09-13\"\n    ],\n    [\n      \"2019-09-14\",\n      \"2019-09-14\"\n    ],\n    [\n      \"2019-09-15\",\n      \"2019-09-15\"\n    ],\n    [\n      \"2019-09-16\",\n      \"2019-09-16\"\n    ],\n    [\n      \"2019-09-17\",\n      \"2019-09-17\"\n    ],\n    [\n      \"2019-09-18\",\n      \"2019-09-18\"\n    ],\n    [\n      \"2019-09-19\",\n      \"2019-09-19\"\n    ],\n    [\n      \"2019-09-20\",\n      \"2019-09-20\"\n    ],\n    [\n      \"2019-09-21\",\n      \"2019-09-21\"\n    ],\n    [\n      \"2019-09-22\",\n      \"2019-09-22\"\n    ],\n    [\n      \"2019-09-23\",\n      \"2019-09-23\"\n    ],\n    [\n      \"2019-09-24\",\n      \"2019-09-24\"\n    ],\n    [\n      \"2019-09-25\",\n      \"2019-09-25\"\n    ],\n    [\n      \"2019-09-26\",\n      \"2019-09-26\"\n    ],\n    [\n      \"2019-09-27\",\n      \"2019-09-27\"\n    ],\n    [\n      \"2019-09-28\",\n      \"2019-09-28\"\n    ],\n    [\n      \"2019-09-29\",\n      \"2019-09-29\"\n    ],\n    [\n      \"2019-09-30\",\n      \"2019-09-30\"\n    ]\n  ]\n}",
                            "error": false,
                            "_profile": {
                                "queries": [
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "SELECT COUNT(*) FROM applications WHERE id IN (25378) AND `status` <> 'deleted'",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1649060863588107-14312884652228168942",
                                        "event_date_time": "2022-04-04 11:27:43",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1649060863594,
                                        "query_hash": 975835054
                                    },
                                    {
                                        "host": "mdbliv24jkovhf87tjs0.haproxy-prod.metrika.yandex.net:3306",
                                        "database": "mobile",
                                        "query": "select sum(rows_count) from applications where id in (25378)",
                                        "time": 1,
                                        "rows": 0,
                                        "request_id": "1649060863588107-14312884652228168942",
                                        "event_date_time": "2022-04-04 11:27:43",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "mysql",
                                        "base_time": 1649060863596,
                                        "query_hash": 1759072458
                                    },
                                    {
                                        "host": "mtmobgiga153-3.metrika.yandex.net:8123",
                                        "query": "WITH 1.0 AS W SELECT `ym:cr2:date` AS `ym:cr2:date`, `ym:cr2:crashes` AS `ym:cr2:crashes`, least(`ym:cr:uniqCrashDevice`,`ym:cr:sumCrashEventTypes`) AS `ym:cr2:crashDevices` FROM (WITH 1.0 AS W SELECT EventDate AS `ym:cr2:date`, sum(Sign) AS `ym:cr2:crashes`, uniq(DeviceIDHash) AS `ym:cr:uniqCrashDevice`, sum(Sign) AS `ym:cr:sumCrashEventTypes` FROM mobile.total_crash_events_layer as `mobile.total_crash_events_layer` WHERE `ym:cr2:date` >= toDate('2019-09-01') and `ym:cr2:date` <= toDate('2019-09-30') and APIKey = toUInt32(25378) and EventType IN (3,26) and toString(OperatingSystem) = 'android' GROUP BY `ym:cr2:date` WITH TOTALS  HAVING `ym:cr2:crashes` > toInt8(0)) ORDER BY `ym:cr2:date` ASC limit 0,30",
                                        "params": {
                                            "compress": "1",
                                            "extremes": "1",
                                            "distributed_aggregation_memory_efficient": "1"
                                        },
                                        "time": 657,
                                        "rows": 30,
                                        "request_id": "1649060863588107-14312884652228168942",
                                        "event_date_time": "2022-04-04 11:27:43",
                                        "daemon_name": "yandex-metrika-mobmetd",
                                        "client_host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net",
                                        "db_type": "clickhouse",
                                        "base_time": 1649060863601,
                                        "query_hash": 1632527817
                                    }
                                ],
                                "additional": {
                                    "frontend-host": "vz4p63ajxbdinoyh.vla.yp-c.yandex.net:8080",
                                    "layer": "0"
                                },
                                "base_time": 1649060863594,
                                "request_id": "1649060863588107-14312884652228168942",
                                "request_uid": 1406498655,
                                "total_time": 665,
                                "java_time": 6
                            }
                        },
                        "isBlackbox": false
                    }
                ],
                "_version": "2.1243321415.2"
            }
        ]
    };

export const androidCrashGroupsChartMock = new Mock(
    /.*\/transport\/i-stat\/getDataBytime*/,
    androidCrashGroupsChartResponse
);
