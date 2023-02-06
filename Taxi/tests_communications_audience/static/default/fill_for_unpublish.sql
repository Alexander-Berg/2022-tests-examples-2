-- noinspection SqlNoDataSourceInspectionForFile

$test_uid_1 = "test_uid_1";
$test_uid_2 = "test_uid_2";
$test_uid_3 = "test_uid_3";
$test_uid_4 = "test_uid_4";

$test_phone_id_1 = "test_phone_id_1";
$test_phone_id_2 = "test_phone_id_2";
$test_phone_id_3 = "test_phone_id_3";
$test_phone_id_4 = "test_phone_id_4";


$test_personal_phone_id = "test_personal_phone_id";
$test_personal_phone_id_1 = "test_personal_phone_id_1";
$test_personal_phone_id_2 = "test_personal_phone_id_2";
$test_personal_phone_id_3 = "test_personal_phone_id_3";
$test_personal_phone_id_4 = "test_personal_phone_id_4";

$test_device_id_1 = "test_device_id_1";
$test_device_id_2 = "test_device_id_2";
$test_device_id_3 = "test_device_id_3";
$test_device_id_4 = "test_device_id_4";

$test_campaign = "test_campaign";
$test_campaign_1 = "test_campaign_1";
$test_campaign_2 = "test_campaign_2";
$test_campaign_3 = "test_campaign_3";
$test_campaign_4 = "test_campaign_4";


REPLACE INTO audience_by_yandex_uid 
(yandex_uid, campaign_id) 
VALUES
($test_uid_1, $test_campaign),
($test_uid_3, $test_campaign_4);

REPLACE INTO audience_by_phone_id 
(phone_id, campaign_id) 
VALUES
($test_phone_id_1, $test_campaign),
($test_phone_id_1, $test_campaign_1),
($test_phone_id_2, $test_campaign_2);

REPLACE INTO audience_by_personal_phone_id 
(personal_phone_id, campaign_id) 
VALUES
($test_personal_phone_id_1, $test_campaign),
($test_personal_phone_id_2, $test_campaign),
($test_personal_phone_id, $test_campaign_1);

REPLACE INTO audience_by_device_id 
(device_id, campaign_id) 
VALUES
($test_device_id_1, $test_campaign_1),
($test_device_id_2, $test_campaign);
