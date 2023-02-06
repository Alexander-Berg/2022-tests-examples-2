INSERT INTO cache.user_offers (offer_id, user_id, table_name, offer_data)
VALUES (
           'offer1', 'user3', '2021-09-22',
           JSON('{
                  "categories": {
                    "econom": {
                      "fixed_price": true,
                      "payment_type": "cash",
                      "surge_value": 1.1,
                      "user_price": 229.0
                    }
                  },
                  "created": "2021-09-22T09:00:00+00:00",
                  "due": "2021-09-22T09:00:00+00:00",
                  "is_corp_decoupling": false,
                  "tariff_name": "moscow",
                  "waypoints": [
                    [
                      37.67347722471099,
                      55.70793157976327
                    ],
                    [
                      37.667271047,
                      55.706056341
                    ]
                  ]
                }')
       ),
       ('offer3', 'user3', '2021-09-22',
        JSON('{
                  "categories": {
                    "econom": {
                      "fixed_price": true,
                      "payment_type": "cash",
                      "surge_value": 1.1,
                      "user_price": 229.0
                    }
                  },
                  "created": "2021-09-22T10:00:00+00:00",
                  "due": "2021-09-22T10:00:00+00:00",
                  "is_corp_decoupling": false,
                  "tariff_name": "moscow",
                  "waypoints": [
                    [
                      37.67347722471099,
                      55.70793157976327
                    ],
                    [
                      37.667271047,
                      55.706056341
                    ]
                  ]
                }')
       ),
       ('offer4', 'user3', '2021-09-22',
        JSON('{"_id": "offer4", "created": "2021-09-22T10:00:00+00:00", ' ||
             '"distance": 7500, "time": 1200, "due": "2021-09-20T12:00:00+00:00", "routestats_type": "RT", ' ||
             '"routestats_link": "key_link2", "if_fixed_price": true, "payment_type": "money", "authorized": true, ' ||
             '"prices": [{"cls": "econom", "pricing_data": {"links": {"prepare": "prepare_link2"}, ' ||
             '"driver": {"category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8"}, ' ||
             '"user": {"category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8"} }}]}')
       ),
       ('offer5', 'user3', '2021-09-22',
        JSON('{"_id": "offer5", "created": "2021-09-22T10:00:00+00:00", ' ||
             '"distance": 7500, "time": 1200, "due": "2021-09-20T12:00:00+00:00", "routestats_type": "RT", ' ||
             '"routestats_link": "key_link2", "if_fixed_price": true, "payment_type": "money", "authorized": true, ' ||
             '"prices": [{"cls": "econom", "pricing_data": {"links": {"prepare": "prepare_link2"}, ' ||
             '"driver": {"category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8"}, ' ||
             '"user": {"category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8"} }}]}')
       );

INSERT INTO cache.offers_details (
                                  offer_id,
                                  category,
                                  dynamic_checked,
                                  yql_link,
                                  yql_share_link,
                                  prepare_link,
                                  common_data,
                                  category_user_data,
                                  category_driver_data,
                                  route_user_data,
                                  backend_variables_user,
                                  yql_error,
                                  paid_supply_user_data,
                                  paid_supply_driver_data
                                )
VALUES
       (
           'offer1', 'econom', true, 'link1', 'sharelink1', 'prepare1', null, null, null, null, null, null, null, null
       ),
    (
        'offer4', 'econom', true, null, 'sharelink4', 'prepare4', null, null, null, null, null, 'yql erorr happened', null, null
    ),
    (
        'offer5', 'econom', false, null, null, 'prepare5', null, null, null, null, null, null, null, null
    ),
       (
        'offer3',
        'econom',
        true,
        null,
        'sharelink3',
        'prepare3',
        JSON('{'
      '"_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-prepare-common-json-log/1800-1800/1621694400/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-common-json-log:0@@25995078@@4wcCp2jkybfxIgNPe1Bz_Q@@1621692610309@@1621692610@@taxi-pricing-data-preparer-yandex-taxi-v2-prepare-common-json-log@@131469614@@1621692610327",
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "delayed_flag": null,
      "disable_fixed_price": false,
      "disable_paid_supply": null,
      "disable_surge": false,
      "due": "2021-05-22T17:10:09.22370962+03:00",
      "extra": {
        "surge_calculation_id": "cbab94e3da4c44d78d7d9ddaf9b4142a",
        "uuids": {
          "driver_category": {
            "business": "5fe09cc6deed488e9a15a2745852e940",
            "cargo": "3e2322c4cf2a4420b54f51a27855c980",
            "cargocorp": "68c05acf0e5b4731baaf3fad340daf16",
            "child_tariff": "43c7261817274f139c71697fa63fff29",
            "comfortplus": "5c45f34403c54cb2b15fc286effe98bb",
            "courier": "d703c37fc001423c85ddc0a91cbce541",
            "econom": "41d44dfc471b4913aee63d4d1fe416d3",
            "eda": "091351e1c644424fb47ff25932dcae9f",
            "express": "4da72aa1d5184947ab88342a387d5b44",
            "lavka": "2efdad7d62334fed9415cd524f2c007c",
            "premium_suv": "5db808ad689e428eab402e50e8a7e782",
            "suv": "b088f58b7362466a8d5a26d89e06c91a",
            "vip": "bede9e465dc241c4ba21fa167a399e49"
          },
          "driver_routes": null,
          "route_jams": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
          "user_category": {
            "business": "feb97312c992483aabd1e134cf64b3a6",
            "cargo": "7bca8e4bc9d74a56858d90afc7254e6a",
            "cargocorp": "26e93c1da0044acfae662cb0e4eaa132",
            "child_tariff": "a1c4ac6d005146eb834b96f7737aca89",
            "comfortplus": "830a7415cedc4a65baad58f6fbeb293b",
            "courier": "dcc3a58197c14d1eb3cd43a5b17c458f",
            "econom": "4c02091952da40f19416f72cbc5cf7a0",
            "eda": "a44b9f96a2eb41bdb1c6731ff3d9e2e6",
            "express": "5d3448011bd34bc99d588653291263a9",
            "lavka": "04f81a3c4fea4e1c8dbaddf70d23471a",
            "premium_suv": "23ab118016fe435689a95d06ccb5beb8",
            "suv": "a2641806fc2942f7aac36a0881a2c3b5",
            "vip": "491a293072d842ae84c58641e90a54c8"
          },
          "user_routes": {
            "business": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "cargo": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "cargocorp": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "child_tariff": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "comfortplus": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "courier": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "econom": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "eda": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "express": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "lavka": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "premium_suv": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "suv": "7cb72106-478a-4bb2-826d-c052d7fe7fec",
            "vip": "7cb72106-478a-4bb2-826d-c052d7fe7fec"
          }
        }
      },
      "is_corp_decoupling": false,
      "is_decoupling": false,
      "iso_eventtime": "2021-05-22 17:10:09",
      "link": "35bfbfd52a5b40d7b40923b45d81d5d2",
      "source_uri": "prt://taxi@aoqf24wxbrcheue2.sas.yp-c.yandex.net/var/log/yandex/taxi-pricing-data-preparer/yt/v2_prepare_common.log",
      "stat": {
        "corp_tariffs": "not_used",
        "coupons": "not_used",
        "discounts": "success",
        "phone": "success",
        "route_with_jams": "success",
        "route_without_jams": "not_used",
        "surge": "success",
        "tags": "success",
        "user": "success"
      },
      "tariff_name": "krasnodar",
      "timestamp": "2021-05-22T17:10:09.389759484+03:00",
      "uuid": "c291947d05aa452aaaaee09e85705101",
      "waypoints": [
        [
          39.06284993647108,
          44.9802644966958
        ],
        [
          39.067874282,
          45.005848326
        ]
      ]
    }'),
        JSON(' {
      "_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log/1800-1800/1621696500/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log:0@@96809265@@anF4AG8IV69LGdidOkVq7g@@1621692609657@@1621692609@@taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log@@2645337424@@1621692609681",
      "alternative_prices_delta_list": {"altprice": [{
          "components": [
            10.0,
            300.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 682
        },
        {
          "components": [
            20.0,
            400.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 683
        }]},
      "alternative_prices_meta": {"altprice": {"increase_to_minimum_price_delta": 20.0,
        "increase_to_minimum_price_delta_raw": 20.0,
        "min_price": 20.0}},
      "base_price": [
        99.0,
        15.924543083429336,
        26.5,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "category_name": "business",
      "category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8",
      "extra": null,
      "fixed_price_discard_reason": null,
      "geoarea_ids": [
        "g/f9db3cffb7534f4eab0435d4ba1b69a9"
      ],
      "is_transfer": false,
      "is_user": true,
      "iso_eventtime": "2021-05-22 17:10:09",
      "price_delta_list": [
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 682
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 683
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 808
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 851
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 864
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 861
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 686
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 687
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 714
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 688
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 664
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 839
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 877
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 690
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 850
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 786
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 844
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 847
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 705
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 813
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 766
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 765
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 815
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 821
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 816
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 798
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 698
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 799
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 730
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 785
        }
      ],
      "price_meta": {
        "gepard_base_price_raw": 141.42454308342937,
        "gepard_free_waiting_minutes": 3.0,
        "gepard_min_price_raw": 99.0,
        "gepard_paid_waiting_minutes": 0.0,
        "gepard_waiting_in_destination_price_raw": 0.0,
        "gepard_waiting_in_transit_price_raw": 0.0,
        "gepard_waiting_price_raw": 0.0,
        "min_price": 99.0,
        "paid_cancel_in_waiting_paid_time": 0.0,
        "paid_cancel_in_waiting_price": 99.0,
        "paid_cancel_price": 99.0,
        "price_after_surge": 141.42454308342937,
        "surge_delta": 0.0,
        "surge_delta_raw": 0.0,
        "use_cost_includes_coupon": 1.0,
        "waiting_in_destination_price": 0.0,
        "waiting_in_transit_price": 0.0,
        "waiting_price": 0.0
      },
      "routepart_list": [
        [
          "krasnodar",
          3224.9648525714874,
          618.0,
          15.924543083429336,
          26.5,
          0
        ]
      ],
      "source_uri": "prt://taxi@aoqf24wxbrcheue2.sas.yp-c.yandex.net/var/log/yandex/taxi-pricing-data-preparer/yt/v2_prepare_category_info.log",
      "timestamp": "2021-05-22T17:10:09.388995928+03:00",
      "use_fixed_price": true,
      "use_jams": true,
      "uuid": "feb97312c992483aabd1e134cf64b3a6"
    }'),
        JSON('{
      "_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log/1800-1800/1621696500/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log:0@@96809265@@anF4AG8IV69LGdidOkVq7g@@1621692609657@@1621692609@@taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log@@2645337424@@1621692609681",
      "alternative_prices_delta_list": {"altprice": [{
          "components": [
            10.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 682
        },
        {
          "components": [
            20.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 683
        }]},
      "alternative_prices_meta": {"altprice": {"increase_to_minimum_price_delta": 200.0,
        "increase_to_minimum_price_delta_raw": 200.0,
        "min_price": 200.0}},
      "base_price": [
        99.0,
        15.924543083429336,
        26.5,
        0.0,
        0.0,
        0.0,
        0.0
      ],
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "category_name": "business",
      "category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8",
      "extra": null,
      "fixed_price_discard_reason": null,
      "geoarea_ids": [
        "g/f9db3cffb7534f4eab0435d4ba1b69a9"
      ],
      "is_transfer": false,
      "is_user": false,
      "iso_eventtime": "2021-05-22 17:10:09",
      "price_delta_list": [
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 682
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 683
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 808
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 851
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 864
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 861
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 686
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 687
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 714
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 688
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 664
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 876
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 690
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 850
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 786
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 841
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 705
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 813
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 798
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 697
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 853
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 765
        },
        {
          "components": [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 785
        }
      ],
      "price_meta": {
        "increase_to_minimum_price_delta": 0.0,
        "increase_to_minimum_price_delta_raw": 0.0,
        "min_price": 99.0,
        "paid_cancel_in_waiting_paid_time": 0.0,
        "paid_cancel_in_waiting_price": 99.0,
        "paid_cancel_price": 99.0,
        "price_after_surge": 141.42454308342937,
        "surge_delta": 0.0,
        "surge_delta_raw": 0.0,
        "waiting_in_destination_price": 0.0,
        "waiting_in_transit_price": 0.0,
        "waiting_price": 0.0
      },
      "routepart_list": [
        [
          "krasnodar",
          3224.9648525714874,
          618.0,
          15.924543083429336,
          26.5,
          0
        ]
      ],
      "source_uri": "prt://taxi@aoqf24wxbrcheue2.sas.yp-c.yandex.net/var/log/yandex/taxi-pricing-data-preparer/yt/v2_prepare_category_info.log",
      "timestamp": "2021-05-22T17:10:09.388922608+03:00",
      "use_fixed_price": true,
      "use_jams": true,
      "uuid": "5fe09cc6deed488e9a15a2745852e940"
    }'),
        JSON('{
      "_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-prepare-route-json-log/1800-1800/1621695600/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-route-json-log:0@@31907576@@f1jyUWfjo9hxFyfv6sAjvQ@@1621692609742@@1621692614@@taxi-pricing-data-preparer-yandex-taxi-v2-prepare-route-json-log@@953514495@@1621692609830",
      "blocked": false,
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "distance": 3224.9648525714874,
      "iso_eventtime": "2021-05-22 17:10:09",
      "jams": true,
      "points": [
        [
          39.062849,
          44.980264,
          0.0,
          0.0
        ],
        [
          39.063001,
          44.980717,
          52.0,
          10.0
        ],
        [
          39.063323,
          44.981633,
          157.0,
          30.0
        ],
        [
          39.063644,
          44.982551,
          262.0,
          50.0
        ],
        [
          39.063859,
          44.983154,
          331.0,
          63.0
        ],
        [
          39.064403,
          44.984651,
          503.0,
          96.0
        ],
        [
          39.064947,
          44.986148,
          675.0,
          129.0
        ],
        [
          39.065414,
          44.98752,
          832.0,
          160.0
        ],
        [
          39.065882,
          44.98889,
          988.0,
          189.0
        ],
        [
          39.066348,
          44.990262,
          1145.0,
          220.0
        ],
        [
          39.066306,
          44.990346,
          1155.0,
          221.0
        ],
        [
          39.066193,
          44.990407,
          1166.0,
          223.0
        ],
        [
          39.065673,
          44.99046,
          1208.0,
          232.0
        ],
        [
          39.065097,
          44.990437,
          1253.0,
          240.0
        ],
        [
          39.065145,
          44.990531,
          1264.0,
          243.0
        ],
        [
          39.065174,
          44.990587,
          1271.0,
          244.0
        ],
        [
          39.066474,
          44.990742,
          1374.0,
          264.0
        ],
        [
          39.066533,
          44.990823,
          1385.0,
          266.0
        ],
        [
          39.066807,
          44.991152,
          1427.0,
          273.0
        ],
        [
          39.066923,
          44.991271,
          1443.0,
          277.0
        ],
        [
          39.067413,
          44.991776,
          1511.0,
          290.0
        ],
        [
          39.067469,
          44.991847,
          1520.0,
          291.0
        ],
        [
          39.067505,
          44.991912,
          1528.0,
          292.0
        ],
        [
          39.067515,
          44.991954,
          1533.0,
          293.0
        ],
        [
          39.067539,
          44.992082,
          1547.0,
          296.0
        ],
        [
          39.067543,
          44.992103,
          1549.0,
          297.0
        ],
        [
          39.067608,
          44.992404,
          1583.0,
          303.0
        ],
        [
          39.067663,
          44.992482,
          1593.0,
          305.0
        ],
        [
          39.068018,
          44.992826,
          1640.0,
          314.0
        ],
        [
          39.068317,
          44.993116,
          1680.0,
          322.0
        ],
        [
          39.068374,
          44.993168,
          1687.0,
          324.0
        ],
        [
          39.068478,
          44.993267,
          1701.0,
          326.0
        ],
        [
          39.070004,
          44.994692,
          1900.0,
          364.0
        ],
        [
          39.070131,
          44.994827,
          1918.0,
          368.0
        ],
        [
          39.070232,
          44.994943,
          1933.0,
          371.0
        ],
        [
          39.070264,
          44.994994,
          1939.0,
          371.0
        ],
        [
          39.070287,
          44.995051,
          1946.0,
          372.0
        ],
        [
          39.070316,
          44.995159,
          1958.0,
          375.0
        ],
        [
          39.070323,
          44.995235,
          1967.0,
          377.0
        ],
        [
          39.070312,
          44.995911,
          2042.0,
          391.0
        ],
        [
          39.070307,
          44.996371,
          2093.0,
          401.0
        ],
        [
          39.070305,
          44.996502,
          2107.0,
          404.0
        ],
        [
          39.070285,
          44.997721,
          2243.0,
          429.0
        ],
        [
          39.070273,
          44.99803,
          2277.0,
          436.0
        ],
        [
          39.070237,
          44.999153,
          2402.0,
          460.0
        ],
        [
          39.070201,
          45.000277,
          2527.0,
          484.0
        ],
        [
          39.070198,
          45.001105,
          2619.0,
          502.0
        ],
        [
          39.070194,
          45.001406,
          2653.0,
          509.0
        ],
        [
          39.070187,
          45.001605,
          2675.0,
          512.0
        ],
        [
          39.070178,
          45.001835,
          2701.0,
          517.0
        ],
        [
          39.070155,
          45.002144,
          2735.0,
          524.0
        ],
        [
          39.070134,
          45.002273,
          2749.0,
          527.0
        ],
        [
          39.070026,
          45.00248,
          2774.0,
          532.0
        ],
        [
          39.069864,
          45.002703,
          2802.0,
          537.0
        ],
        [
          39.069831,
          45.002739,
          2807.0,
          538.0
        ],
        [
          39.069654,
          45.002895,
          2829.0,
          542.0
        ],
        [
          39.069543,
          45.003004,
          2844.0,
          545.0
        ],
        [
          39.069451,
          45.003101,
          2857.0,
          547.0
        ],
        [
          39.069375,
          45.003188,
          2868.0,
          549.0
        ],
        [
          39.069298,
          45.003276,
          2880.0,
          552.0
        ],
        [
          39.069115,
          45.003487,
          2907.0,
          557.0
        ],
        [
          39.069009,
          45.003611,
          2923.0,
          560.0
        ],
        [
          39.06856,
          45.004141,
          2992.0,
          573.0
        ],
        [
          39.068305,
          45.004442,
          3031.0,
          580.0
        ],
        [
          39.06806,
          45.00473,
          3068.0,
          588.0
        ],
        [
          39.067995,
          45.004806,
          3078.0,
          590.0
        ],
        [
          39.067663,
          45.00519,
          3128.0,
          599.0
        ],
        [
          39.067489,
          45.00539,
          3154.0,
          604.0
        ],
        [
          39.067408,
          45.005489,
          3167.0,
          607.0
        ],
        [
          39.067321,
          45.005595,
          3181.0,
          609.0
        ],
        [
          39.067407,
          45.005606,
          3188.0,
          611.0
        ],
        [
          39.067514,
          45.005616,
          3196.0,
          613.0
        ],
        [
          39.067882,
          45.005622,
          3225.0,
          618.0
        ]
      ],
      "router_settings": {
        "intent": "ROUTESTATS",
        "jams": true,
        "mode": "approx",
        "request_id": "3f3779b5d3e840d1ba70453c958962d1",
        "tolls": false,
        "user_id": "b77c536b99763cf7cdd39a3a4e19397c"
      },
      "source_uri": "prt://taxi@aoqf24wxbrcheue2.sas.yp-c.yandex.net/var/log/yandex/taxi-pricing-data-preparer/yt/v2_prepare_route.log",
      "time": 618.0,
      "timestamp": "2021-05-22T17:10:09.389611023+03:00",
      "tolls": false,
      "uuid": "7cb72106-478a-4bb2-826d-c052d7fe7fec"
    }'),
    JSON('{"caller_link": "caller_link_1",
    "category_name": "econom",
    "data": {"variable6": "value"},
    "prepare_link": "offer1",
    "source": "v2/prepare",
    "subject": "user",
    "timestamp": "2020-09-23T12:00:00+03:00",
    "user_id": "user1",
    "uuid": "category_info_user",
    "version": 1}'),
    null,
        JSON('{
      "_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-calc-paid-supply-json-log/1800-1800/1621696500/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log:0@@96809265@@anF4AG8IV69LGdidOkVq7g@@1621692609657@@1621692609@@taxi-pricing-data-preparer-yandex-taxi-v2-calc-paid-supply-json-log@@2645337424@@1621692609681",
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "category_name": "business",
      "category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8",
      "extra": null,
      "is_user": false,
      "price_delta_list": [
        {
          "components": [
            354.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 785
        }
      ],
      "price_meta": {
        "paid_supply_meta": 100
      },
      "timestamp": "2021-05-22T17:10:09.388922608+03:00",
      "uuid": "5fe09cc6deed488e9a15a2745852e940"
    }'),
        JSON('{
      "_logfeller_index_bucket": "//home/logfeller/index/taxi/taxi-pricing-data-preparer-yandex-taxi-v2-calc-paid-supply-json-log/1800-1800/1621696500/1621692000",
      "_logfeller_timestamp": "1621692609",
      "_stbx": "rt3.sas--taxi--taxi-pricing-data-preparer-yandex-taxi-v2-prepare-category-info-json-log:0@@96809265@@anF4AG8IV69LGdidOkVq7g@@1621692609657@@1621692609@@taxi-pricing-data-preparer-yandex-taxi-v2-calc-paid-supply-json-log@@2645337424@@1621692609681",
      "caller_link": "f614c7e74f5104fbeffc26823928741b",
      "category_name": "business",
      "category_prices_id": "c/294cdf0584c344428e3ed64fb70883a8",
      "extra": null,
      "is_user": true,
      "price_delta_list": [
        {
          "components": [
            453.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
          ],
          "id": 785
        }
      ],
      "price_meta": {
        "paid_supply_meta": 200
      },
      "timestamp": "2021-05-22T17:10:09.388922608+03:00",
      "uuid": "5fe09cc6deed488e9a15a2745852e940"
    }')
       );
