const MonitoringCenter = require('../../page/signalq/MonitoringCenter');
const Selenoid = require('../../../../utils/api/Selenoid');
const {csvUtf8ParseToArray} = require('../../../../utils/files');

describe('SignalQ. Центр мониторинга. Выгрузка отчёта событий по машине csv', () => {

    const DATA = {
        file: 'events_7ad36bc7560449998acbe2c57a75c293_2021-08-23T21_00_00+0000_2021-08-24T20_59_59.999+0000.csv',
        report: [
            ['Время события', 'Тип события', 'Скорость', 'Водитель', 'Серийный номер', 'Резолюция', 'Гос. номер', 'Позывной', 'Ссылка на событие'],
            ['2021-08-24T11:54:06.111091', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/41fdab3d-a929-4a24-b8ee-464324bc637b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T11:57:06.353993', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/8eb4cd36-3d5b-49fe-b8c0-43b4e4763d60?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T11:57:06.353993', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/7d67b568-7284-44d1-8f48-94ecca179af0?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T11:57:06.353993', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/2fb572ce-3368-455b-9b12-d88cd6f12560?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:00:07.491438', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/c7ba943c-4088-42ce-ab43-d1829e587008?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:03:10.846023', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/e68c6d30-42ba-44e2-9d65-b9940f4b6a01?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:06:06.73024', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/4158a038-4e1e-4fab-87b5-228e5d10a12c?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:09:04.552449', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/b00d7d1c-90f1-4c3e-9799-dc4cf53573de?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:12:08.484403', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/f38ad34f-7823-4084-9877-2aa9e7646f3b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:12:08.484403', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/c82e239f-de38-4410-a40c-e62fb0c1e5da?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:15:06.61282', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/f34bd0cc-9c9e-4f1f-a72f-4bbe187ab04b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:18:07.192495', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/a84e2486-50e8-4384-b050-1e1ac40b7e08?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:18:07.192495', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/31a7b7b6-c6ff-4aa5-864d-e49786e9e4bc?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:24:06.352286', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/3d3a0c9c-67b2-4cef-9988-7b7522a08efc?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T12:30:06.469925', 'sleep', '22.000000', '', '002359B94E28E85C', '', 'У004УУ78', 'У004УУ78', 'https://fleet.tst.yandex.ru/signalq/stream/all/f9654c76-8b76-46c7-98d5-b95de7a751f6?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T15:48:05.802152', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ee8ae5a0-80cb-45f8-8f42-c132851d08a7?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T15:54:06.875616', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6f600bb4-9a01-4acf-9521-f3cda5bb592e?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T15:57:11.080808', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a13f0607-b8b2-4afc-bc6d-3af3b39deea8?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:00:12.176345', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/15651f4d-be1a-4084-8836-b70b8c872311?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:03:09.626514', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/f8aaf296-495d-4184-b0ad-e94b88ce97e4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:03:09.626514', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/d8c43110-6dcf-45f3-8f23-096f2cde267a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:06:07.998783', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/7b0213d3-3cd6-4594-a228-f6afb223b0b4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:09:13.103179', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/f34dc085-739e-4b3a-9ee4-763cf9f5ce3b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:09:13.103179', 'sleep', '22.000000', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/10fe844e-d12c-43d0-870d-11feebd200b9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:12:15.354094', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b708718e-9bde-4bbe-b2e1-ebf600b37f47?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:12:15.354094', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e8a95e1b-70c2-46d1-813a-fc51798a3072?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:12:15.354094', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e73043ac-f9c7-46d6-8e3b-af9db62c80f9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:15:11.921443', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/fd2eeef0-8a1c-491c-aca1-edb031d06d7e?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:18:04.89158', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6e7182ef-e621-4715-8708-ae7864384c52?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:24:05.974568', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/1444003a-3800-4861-8fa4-1314148f4d5c?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:27:07.60801', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/eafad817-ea0d-448e-ba53-27917eae1679?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:30:07.100927', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a3674bed-f38c-457e-af22-470839cd9d23?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:33:08.266482', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/7e6d350c-f411-42cb-b9c2-d5c86ce56e2d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:33:08.266482', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/37a4a116-3dee-41e0-8fe8-f56f423a3d0a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:33:08.266482', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4c428a05-d931-4b0e-8261-a20eca577556?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:36:09.938629', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/9b0f7cec-2875-4086-8efc-820d1511df5b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:39:07.479844', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/9709d6c8-e8da-475a-b783-537d392cef3d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:39:07.479844', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/00cbcb6c-a0ec-4d62-8a7c-ec631dfd8fbf?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:42:09.511193', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/d313c21b-1b0d-40ab-8a11-8a5c72e85243?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:48:12.805075', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/1117538b-2f3f-4132-95ac-56d7be76c881?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:48:12.805075', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5e808f3d-778b-4ce7-bae9-9b8afe6bf2f9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:51:04.025226', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/982bff46-319f-4ed9-a7bc-520558fdaa0b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T16:57:09.98488', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a0d6fa1b-b3d7-4e3f-a185-88320d87dba2?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:03:04.9418', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/bef5f602-cf68-4372-91a4-81dcd3dd836e?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:06:06.059675', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/654f3890-86f3-49e8-b7f3-35470a3e88b8?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:09:06.714572', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/524b634a-9aa2-43f1-b7e8-9f3c28685c65?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:12:04.062308', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2b6bf325-d815-4e66-af9f-2cd6a12aa889?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:15:05.462757', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/56ab71cc-0658-44d4-94cb-fd0700367fbb?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:15:05.462757', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/99665b47-aa43-4385-9ca0-2e4d792a30b1?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:18:06.418574', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6b7a0ce8-415f-495b-a53a-56e44ee624e2?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:18:06.418574', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/be237a7d-9f4a-4a77-af74-00487b5a8ea0?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:18:06.418574', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/f25210ce-01f3-499d-8564-9912de862534?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:21:08.151906', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2c151395-1d67-4fb2-b012-19a68e78f7cc?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:24:05.511732', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/094fd7ab-5db6-42ff-98de-da10c7f473b1?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:24:05.511732', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a4308781-c2b6-475d-9ca1-7c8a9a1c1158?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:33:12.947861', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/3eccbd0f-5dae-4696-806f-3a0db1e6687f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:33:12.947861', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ab08a92b-7f6b-4f62-8ea0-a85ab108f831?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:36:06.867681', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4e3a28e5-2da5-4f12-89f5-fde5870323ea?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:39:12.797651', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b1ee547f-3999-438f-8bff-d242960961f8?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:39:12.797651', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/77611352-ddd6-4052-ac18-b4cc0fd367cf?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:42:08.686393', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2dd0726e-a6de-46c9-80d7-f8427c87fc1d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:45:14.714102', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/c43b7496-24d0-4d89-8347-a636b31fcbec?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:48:12.355195', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/001db87d-e0b1-4361-9f4c-4bfc598fe6cb?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:48:12.355195', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/8678131c-996e-4326-b397-dde4854db1f6?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T17:54:13.344588', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/62d1d21b-c40f-4204-8993-0ae59f2bd77b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:00:08.164953', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5e7bc14e-149a-47bc-9c4a-2c29b2886921?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:03:06.504294', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/d97fc9c1-cb55-45b9-a4e7-eca060174092?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:03:06.504294', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5435f40e-efeb-45c7-92d9-fa5ee9857e51?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:12:09.282215', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6bf0bd49-935b-40f7-b5e6-fc6d95378ca9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:18:10.651863', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5d365229-4513-46ea-aeee-46a301225fbf?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:27:08.322644', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/8c218b1d-8dd5-4c9c-ad94-fe2c47989f19?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:30:04.992044', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/90f4cac3-3f7a-4c4b-8a79-0211e257302f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:36:06.230516', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/02488e7b-104a-4b77-abec-5b5d3be824d1?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:36:06.230516', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6a0cb85c-fbab-4e62-90f5-acec30ac9512?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:36:06.230516', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/fff35413-398b-47ce-a2df-28f6cecc1633?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:42:14.163157', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/67a8bb4b-ab45-4ab5-9a09-66e551478e3c?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:45:09.3599', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5ac5ed66-cb91-47d1-afb7-ea921d0e09df?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:51:05.665312', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/8267297c-4a07-4534-a2e1-6ffc10a3e7b4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:51:05.665312', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/12385620-dd9b-4111-9713-a5fa74482a38?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:54:05.452148', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4b058c3b-368e-4483-bc7c-a18b1fd09777?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:57:13.679815', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/361046ac-e503-4466-970a-c16c17fd668e?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T18:57:13.679815', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/24b55b63-f4cd-4adb-9cee-c15577844276?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:00:12.322436', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/dab98b70-27d8-4766-8012-cea58e621dd6?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:06:12.314205', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/3be36d8d-db6b-45d5-9236-c0cb1cb4e432?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:12:11.522315', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/38885e17-3c62-410c-a970-d871ab1c4548?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:12:11.522315', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/f9a4f86f-4d5f-4e39-aa31-c119d20d416d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:18:05.109923', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ee0ec847-4876-4501-bc8e-addc628f3db4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:18:05.109923', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/dd31a599-0f98-47a3-a3c3-400d6a5d0dfa?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:21:05.880728', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/d248c4bd-07ca-492e-a95a-2a795af96fe8?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:21:05.880728', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/96ddd8b1-1660-435d-ad91-52acf2c0e7eb?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:24:09.057447', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/acf9c351-512a-4fe7-99d5-75c322456775?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:24:09.057447', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/8ba4030e-3114-48e6-976f-54dafe5a3a56?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:27:08.698582', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ef94ec13-4d6c-4737-8f03-a012edb94c10?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:30:05.207471', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/59c13a0f-08d0-4426-867a-01d54ba40418?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:33:09.597092', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/05eb1906-a0e7-4c7c-b75c-451e0aa5a8b7?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:36:06.630939', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/58dccb4e-5b82-4593-b39d-7d23106c207f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:42:08.890487', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/59b007f3-27f9-48e2-84c3-fdce0f352088?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:42:08.890487', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/0b583356-dd19-45a5-a9f5-33a844d14281?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:45:07.360441', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/deca3a6b-b99e-416e-a888-869375849272?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:45:07.360441', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/29e4d516-9be3-4b6e-b773-d8b92c9e14fc?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:48:11.981879', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/58c5a5f3-a0db-4845-a51b-4b2c33bd71b4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:48:11.981879', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ec2ee46b-4c38-490e-a920-7388e76e620f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:48:11.981879', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/1a97cc51-6b11-4e8e-96e6-666f584a5f5f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:51:04.551837', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4ba8adb9-1753-4873-ab90-607954f764f9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T19:57:13.006517', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2667b53c-0bea-4b10-9b14-146b15609a1a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:00:07.396115', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/406873dc-817c-4b6f-a4fc-3e677d0b7c41?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:12:09.102472', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/7bfa8a42-80db-4d49-bbc4-3bb459a53ba0?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:15:05.97879', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/0f751173-727e-4e3f-acf6-222c4b236881?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:18:04.974397', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4eea98df-df41-4263-9d6c-bfeffc2e3c73?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:21:09.856584', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/03012828-dcf7-4b54-91fd-7e81e3791462?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:24:08.187899', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/550e1e74-a1f9-4624-96b9-ca2f4249007a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:27:08.407729', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/dcb2ad4c-c496-4720-b76d-5d57485efda5?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:45:11.635571', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a31554fd-95b3-4c12-8818-c410853308c3?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:45:11.635571', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/84ab3fd4-7347-4f1a-97bf-72af84360823?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:45:11.635571', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/1c7cc199-6aa3-4126-9715-75d5e845bda9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:48:09.606885', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/f63f78c2-e062-4e02-ab28-e21319eb673d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:51:05.115397', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/5188a714-e492-4f51-98e6-339d0c561e5f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T20:57:04.950601', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/014d10d6-4c63-4da5-aa45-5c993147a0e6?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:06:10.982909', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/58e7b326-e5b7-48bc-b678-cd692fd4daa9?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:12:05.517959', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6b092a75-6922-4760-ab8a-4eaea5eda095?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:18:09.448698', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4d8dd15e-66c9-4313-8857-57d5c8a91976?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:18:09.448698', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2b16ea95-115c-4ab2-802c-6c27a3380e68?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:18:09.448698', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/92f3b2ad-50e9-45ba-ac90-8d4ef3a49f84?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:24:10.666948', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e8b68435-2e5f-4cdc-9e02-7ff1f6619db2?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:30:13.913727', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6c92bb51-0af7-4076-a271-1f0895312f2a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:30:13.913727', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/2cf4f35e-aed0-432b-af5a-e2ae640a5498?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:33:11.858926', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a9178ee8-4a75-4164-8dce-420fa6452d21?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:36:06.387353', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/3b07c841-6cd0-4f85-963a-5a76c733fa70?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:42:07.939911', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e43fb116-e5bd-4e1b-a8ab-cedd92eaca81?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:42:07.939911', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e22b8589-5085-4ceb-8868-02f2d7f49ae6?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:45:06.051226', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6010a6e9-a7c7-45a9-98dc-9a6d92082df4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:45:06.051226', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/10f93896-4a49-4dd1-a8d6-37d962d9ab54?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:48:07.684907', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/c3addbe7-256c-4447-858b-baf94cb9db31?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:51:08.801829', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/e4738176-fdf6-4e8f-8e7f-7e5e21fd77a7?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:51:08.801829', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/526a1b8f-58e4-41d2-9be8-932fed4bec7d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:54:12.665416', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/565b34a9-1ba9-48ac-ba3d-f0caf2efd9f0?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:57:10.980663', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/cb3ad09f-dfc1-4fc4-8678-97a6a5379fa2?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T21:57:10.980663', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/27c4c225-abbe-4501-a0cc-95d7593784d3?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:00:08.090368', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/80dcc86c-0bfd-405f-b766-cec69e341d1b?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:00:08.090368', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b7435f19-fddf-4cec-bc25-8ee6655f997c?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:03:07.944911', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a3198733-465c-4e4c-bbcb-d1f8051bd879?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:03:07.944911', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/202beb5c-4743-4cf9-ad26-54c7b02ed748?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:06:08.520027', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a842aeab-5204-496d-8b10-34b8315147ef?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:09:05.249414', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/050aa08e-5b15-4132-bd1a-5dbadbeefaa5?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:12:10.017643', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/ff68e38c-b10e-4f19-99a8-8817a1842b1d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:12:10.017643', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/0eb6bd46-b6ee-4855-9c74-760cc136e413?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:15:10.880959', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/58c88953-17c1-4db7-92cf-c5167a85a094?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:18:15.271821', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a8ad56d3-1f5f-46ab-a78f-8a5db8b603ec?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:21:08.39527', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/dd27975a-73ba-4b6b-99d2-fe243e9ddfcd?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:24:06.884348', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/892d8cc7-e094-435d-9a41-854eee76e99f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:27:06.295834', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/c1588c77-1386-48e5-a417-e028473750d1?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:33:04.811204', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/36e6f8f2-bf1c-4c7f-a1b5-7797d26b68da?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:36:06.136394', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b625a786-49c0-4413-91f3-bf3c934241a8?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:36:06.136394', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/1a1272f5-b03f-4309-a7ee-5dc8c5cdc44a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:39:07.101717', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/16f68ffe-b7be-4bf3-8d8d-8fcb1e8fdc9f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:45:07.378976', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a286f73c-efb6-4144-a8ba-03fdc990fd49?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:48:09.22354', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/8dda2e93-6f38-47cc-8c27-be0e2bdc342d?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:48:09.22354', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b7deb748-7e6e-491d-9aa1-f3d52d964128?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:48:09.22354', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/4ee15629-bbee-4ccd-856f-201fe4427308?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:54:13.580266', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/31b935ae-c696-45cb-ba9b-57755bb2b31f?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T22:57:05.551124', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/12f67525-a26a-4aa3-bbd1-2a40a5aa7b49?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:00:08.068296', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/07dc4cde-ed70-4462-89a7-ff373e5f3dfc?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:06:09.185958', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/390450e2-6d79-42b8-8198-786697e90915?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:12:08.296081', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/611faacf-c2f4-47ab-b572-c778dab78889?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:18:07.427199', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/47e70e9b-7d3a-4a99-b652-95f7467436ac?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:21:11.471075', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/6f95d379-8031-402f-b182-1a083261780a?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:33:10.634889', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/cb9698f7-3c05-42f1-a9da-e25ec541b8b3?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:36:07.997653', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/db1c324f-7432-43ad-b05e-b1861be38f44?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:36:07.997653', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/55a8634d-8f7e-4ce0-8243-2a137eb66606?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:42:05.463895', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/bd6c3d70-2c0b-44a9-8c93-710881cb81ba?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:48:08.877789', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/d3cbf4b4-11c6-4dbf-8932-8c7899cb88a4?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:51:04.881499', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/a060c7dc-fc48-4507-8fac-b0528d846bac?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
            ['2021-08-24T23:54:10.132808', 'sleep', '', '', '000745C4F789A500', '', '', '', 'https://fleet.tst.yandex.ru/signalq/stream/all/b14cc170-d52e-4de9-bfbf-10477bc85212?grouping=vehicles&park_id=7ad36bc7560449998acbe2c57a75c293'],
        ],
    };

    let data;

    it('Открыт раздел "Центр мониторинга"', () => {
        MonitoringCenter.goTo();
    });

    it('Нажать на кнопку "Отчёт по всему транспорту"', () => {
        MonitoringCenter.allVehicleReportButton.click();
    });

    it('Выбрать дату за которую были события', () => {
        MonitoringCenter.getReport().dateInputFrom.click();
        MonitoringCenter.getReport().dateInputFrom.addValue(24_082_021);

        MonitoringCenter.getReport().dateInputTo.click();
        MonitoringCenter.getReport().dateInputTo.addValue(24_082_021);
    });

    it('Выбрать формат CSV', () => {
        MonitoringCenter.getReport().csv.click();
    });

    it('Нажать кнопку "загрузить"', () => {
        MonitoringCenter.getReport().downloadButton.click();
    });

    it('Отчёт сохранился', () => {
        data = Selenoid.getDownloadedFile(DATA.file);
    });

    it('Распарсить отчёт', () => {
        data = csvUtf8ParseToArray(data);
    });

    it('В сохраненном отчёте отображаются корректные данные', () => {
        expect(data).toEqual(DATA.report);
    });

});
