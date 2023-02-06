INSERT INTO yt.commercial_hiring_summary_report(park_id,
                                        report_date,
                                        acquisition_type,
                                        acquisition_source,
                                        car_profile_id,
                                        car_profile_brand_name,
                                        car_profile_model_name,
                                        car_number,
                                        cnt_orders,
                                        driver_type,
                                        driver_profile_id,
                                        full_name,
                                        paid_date_from,
                                        paid_date_to,
                                        commercial_hiring_commission,
                                        park_commission,
                                        rent,
                                        park_profit)
VALUES
    /* Here insert in reverse order to ensure
       that PK doesn't used for sorting */
    ('7ad36bc7560449998acbe2c57a75c293', '2020-09-22 00:00:00+03:00', 'partner', 'Партнеры', '123', 'VW', 'Polo', 'A456BC76', 7, 'owner', '456', 'Четыре Пять Шеть', '2020-01-04'::DATE, '2021-01-04'::DATE, 1000.00, 1500.00, 1000.00, 500.00),
    ('7ad36bc7560449998acbe2c57a75c293', '2020-09-22 00:00:00+03:00', 'sites', 'Реклама', '123', 'VW', 'Polo', 'A123BC76', 5, 'rent', '123', 'Один Два Три', '2020-02-04'::DATE, '2020-11-04'::DATE, 2000.50, 1500.50, 1000.00, 1500.00),
    ('7ad36bc7560449998acbe2c57a75c293', '2020-09-22 00:00:00+03:00', 'partner', 'Партнеры', '123', 'VW', 'Polo', 'A789BC76', 17, 'owner', '123456', 'Вася', '2021-02-04'::DATE, '2021-12-04'::DATE, 3000.50, 1500.00, 1000.00, 2500.50)
;
