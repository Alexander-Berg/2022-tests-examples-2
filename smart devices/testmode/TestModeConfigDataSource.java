package ru.yandex.quasar.testmode;

import androidx.annotation.NonNull;

import java.io.IOException;

import javax.annotation.Nullable;

import ru.yandex.quasar.data.DataSource;

/**
 * @author Tim Malygin.
 */
final class TestModeConfigDataSource implements DataSource<String> {

    private final String config = "{\n" +
            "\"testMode\" : {\n" +
            "          \"enabled\" : true,\n" +
            "          \"players\": [\n" +
            "                \"default\"\n" +
            "                ,\"yadoma\"\n" +
            "                ,\"24video\"\n" +
            "                ,\"vk\"\n" +
            "                 ,\"ok\"\n" +
            "               ,\"rutube\"\n" +
            "          ],\n" +
            "          \"type\": \"NEW\" // [RESTART | NEW]\n" +
            "    },\n" +
            "    // \"testModeType\": \"\", //[yadoma | 24video | vk | ok | rutube | default]\n" +
            "    \"audiod\": {\n" +
            "        \"port\": 9876,\n" +
            "        \"periodSize\" : 1024,\n" +
            "        \"micChannels\": 7,\n" +
            "        \"spkChannels\": 3,\n" +
            "        \"VQEtype\": \"fraunhofer\", //[yandex | fraunhofer]\n" +
            "        \"inRate\": 16000,\n" +
            "        \"cardNumber\": 2,\n" +
            "        \"deviceNumber\": 0,\n" +
            "        \"bfWeightsPath\": \"/system/vendor/quasar/weights\",\n" +
            "        \"dumpBySignal\": true,\n" +
            "        \"inputMicFileName\": \"/mnt/mic.raw\",\n" +
            "        \"inputSpkFileName\": \"/mnt/spk.raw\",\n" +
            "        \"outputFileName\": \"/mnt/out.raw\",\n" +
            "        \"volumeMixerControl\": 15,\n" +
            "        \"omniMode\": true,\n" +
            "    //    \"affinityMask\": 8,\n" +
            "\n" +
            "        \"Logging\": {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/audiod.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        }\n" +
            "    },\n" +
            "    \"speechkit\": {\n" +
            "        \"port\": 9875,\n" +
            "        \"Logging\": {\n" +
            "            \"level\": \"debug\"\n" +
            "        },\n" +
            "        \"language\" : \"russian\",\n" +
            "        \"apiKey\" : \"51ae06cc-5c8f-48dc-93ae-7214517679e6\",\n" +
            "        \"uniProxyUrl\" : \"wss://uniproxy.alice.yandex.net/uni.ws\",\n" +
            "        \"spotterModelsPath\": \"/system/vendor/quasar/spotter_models\",\n" +
            "        \"shortRecognizerModel\" : \"quasar-general\",\n" +
            "        \"longRecognizerModel\" : \"quasar-video\",\n" +
            "        \"longDialogTimeoutSec\" : 600,\n" +
            "        \"vinsUrl\": \"http://vins-int.voicetech.yandex.net/speechkit/app/quasar/\",\n" +
            "        // \"bassUrl\": \"http://bass-testing.n.yandex-team.ru/\",\n" +
            "        \"longListeningEnabled\" : true,\n" +
            "        \"longTimeout\" : 20,\n" +
            "        \"shortTimeout\" : 5,\n" +
            "        \"skillTimeoutSec\" : 30,\n" +
            "        \"experiments\" : [\"video_youtube_omit_restriction\", \"music\", \"general_conversation\", \"quasar\", \"enable_reminders_todos\", \"enable_partials\"],\n" +
            "        \"jingle\" : false\n" +
            "    },\n" +
            "    \"wifid\": {\n" +
            "        \"port\" : 9877,\n" +
            "        \"accessPointStartTimeoutSec\" : 0\n" +
            "    },\n" +
            "    \"firstrund\" : {\n" +
            "        \"httpPort\" : 8080,\n" +
            "        \"port\" : 9884,\n" +
            "        \"Logging\": {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/firstrund.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        },\n" +
            "        \"accessPointName\" : \"Yandex-Station\"\n" +
            "    },\n" +
            "    \"authd\" : {\n" +
            "        \"port\" : 9878,\n" +
            "        \"accountStorageFile\" : \"account_storage.dat\",\n" +
            "        \"oauthUrl\" : \"https://oauth.yandex.ru/token\",\n" +
            "        \"xTokenClientId\": \"ee06d0aa5b0b4fbe8ae476bb33d13721\",\n" +
            "        \"xTokenClientSecret\": \"8308d2ea7299475a84be851fe32a57d3\",\n" +
            "        \"authTokenClientId\": \"0f7488e7bfdf49be85c64158f2b67c6c\",\n" +
            "        \"authTokenClientSecret\": \"8e9800ee9c9f4a5db6933b8fb88fef6a\",\n" +
            "\n" +
            "        \"deviceName\" : \"Яндекс.Станция (dev)\",\n" +
            "        \n" +
            "        \"Logging\" : {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/authd.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        },        \n" +
            "        \"oauthMinRequestTimeMs\": 15000\n" +
            "    },    \n" +
            "    \"music\" : {\n" +
            "        \"port\" : 9880,\n" +
            "        \"quasarUrl\" : \"https://quasar.yandex.net/dev/static/music_v2.html\",\n" +
            "        \"musicBackendUrl\" : \"wss://ws-api.music.yandex.net/quasar/websocket\"\n" +
            "    },\n" +
            "    \"pushd\" : {\n" +
            "    \t\"port\" : 9881,\n" +
            "    \t\"xivaSubscribeUrl\" : \"wss://push.yandex.ru/v2/subscribe/websocket?service=quasar-realtime&client=q&session=first\"\n" +
            "    },\n" +
            "    \"external\" : {\n" +
            "        \"port\" : 9880,\n" +
            "        \"serviceName\" : \"Alice\",\n" +
            "        \"serviceType\" : \"_quasar._tcp.\",\n" +
            "        \"registrationRetries\" : 3\n" +
            "    },\n" +
            "    \"audioinit\": {\n" +
            "        \"port\" : 9883\n" +
            "    },\n" +
            "    \"alarm\": {\n" +
            "        \"port\": 9886,\n" +
            "        \"dbFileName\": \"/data/quasar/alarms.dat\",\n" +
            "        \"alarmSound\": \"/system/vendor/quasar/sounds/alarm.wav\"\n" +
            "    },\n" +
            "    \"metrica\": {\n" +
            "        \"port\": 9887,\n" +
            "        \"apiKey\": \"46b160aa-bba7-421a-9e3d-f366e76386ef\"\n" +
            "    },\n" +
            "    \"volume\": {\n" +
            "        \"port\": 9888,\n" +
            "        \"cutOffRate\": 0.85\n" +
            "    },\n" +
            "    \"updatesd\": {\n" +
            "        \"port\": 9889,\n" +
            "        \"Logging\" : {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/updatesd.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        },\n" +
            "        \"minUpdateHour\" : 4,\n" +
            "        \"maxUpdateHour\" : 5,\n" +
            "        \"updatesDir\" : \"/cache\"\n" +
            "    },\n" +
            "    \"soundd\": {\n" +
            "        \"port\": 9890\n" +
            "    },\n" +
            "    \"bluetooth\": {\n" +
            "        \"port\": 9892\n" +
            "    },\n" +
            "    \"videod\" : {\n" +
            "        \"port\": 9893,\n" +
            "        \"stateSaveIntervalMs\" : 1000\n" +
            "    },\n" +
            "    \"weatherd\" : {\n" +
            "        \"port\" : 9894\n" +
            "    },\n" +
            "    \"monitord\" : {\n" +
            "        \"port\" : 9895,\n" +
            "        \"Logging\" : {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/monitord.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        },\n" +
            "        \"bugReportLogs\" : [\n" +
            "            {\n" +
            "                \"fileName\": \"/data/quasar/daemons_logs/firstrund.log\",\n" +
            "                \"size\": 200000\n" +
            "            },\n" +
            "            {\n" +
            "                \"fileName\": \"/data/quasar/daemons_logs/authd.log\",\n" +
            "                \"size\": 200000            \n" +
            "            },\n" +
            "            {\n" +
            "                \"fileName\": \"/data/quasar/daemons_logs/updatesd.log\",\n" +
            "                \"size\": 200000            \n" +
            "            },\n" +
            "            {\n" +
            "                \"fileName\": \"/data/quasar/daemons_logs/logcat.log\",\n" +
            "                \"size\": 200000            \n" +
            "            }\n" +
            "        ]\n" +
            "    },\n" +
            "    \"locationd\" : {\n" +
            "        \"port\" : 9896\n" +
            "    },\n" +
            "    \"syncd\": {\n" +
            "        \"port\": 9897,\n" +
            "        \"configPath\": \"/data/quasar/data/config.dat\",\n" +
            "        \"Logging\" : {\n" +
            "            \"level\": \"debug\",\n" +
            "            \"fileName\": \"daemons_logs/syncd.log\",\n" +
            "            \"maxBackupIndex\": 1,\n" +
            "            \"maxFileSize\": \"10MB\"\n" +
            "        }        \n" +
            "    },\n" +
            "    \"smarthome\": {\n" +
            "        \"philipsHueUrl\": \"http://192.168.1.14/api/i4cjwJOObKykMOVsSBUrU71Ed3bVPzwbAviSXUOY/lights/3/state\"\n" +
            "    },\n" +
            "    \"common\" : {\n" +
            "        \"accessPointName\" : \"Yandex-Station\",\n" +
            "        \"caCertsFile\" : \"/system/vendor/quasar/ca-certificates.crt\",\n" +
            "        \"curlVerbose\" : true,\n" +
            "        \"backendUrl\" : \"https://quasar.yandex.net/dev\",\n" +
            "        \"softwareVersion\" : \"__QUASAR_VERSION_PLACEHOLDER__\",\n" +
            "        \"isModule\" : false,\n" +
            "        \"isNewMain\" : true,\n" +
            "        \"isDev\" : true,\n" +
            "        \"durationUpdateMainSuggestMS\":6000,\n" +
            "        \"waitForScreensaverMS\":300000,\n" +
            "        \"screensaverPhotosUrl\" : \"https://quasar.yandex.net/dev/get_screensaver_config\",\n" +
            "        \"screensaverVideoUrl\" : \"https://quasar.s3.yandex.net/temporary/screenSaverConfigTestVideoHD.json\",\n" +
            "        \"defaultVolume\" : 5,\n" +
            "        \"ntpClientCommand\" : \"/system/vendor/quasar/ntpclient_aarch64 -c 1 -s -h\",\n" +
            "        \"ntpServerList\" : [\n" +
            "            \"0.ru.pool.ntp.org\", \n" +
            "            \"1.ru.pool.ntp.org\",\n" +
            "            \"2.ru.pool.ntp.org\",\n" +
            "            \"3.ru.pool.ntp.org\"\n" +
            "        ],\n" +
            "        \"cryptography\" : {\n" +
            "            \"publicKeyPath\" : \"/data/quasar/public.pem\",\n" +
            "            \"privateKeyPath\" : \"/data/quasar/private.pem\",\n" +
            "            \"devicePublicKeyPath\": \"/secret/device_key.public.pem\",\n" +
            "            \"devicePrivateKeyPath\": \"/secret/device_key.pem\"\n" +
            "        }\n" +
            "    }\n" +
            "}\n";

    @Override
    public boolean store(@NonNull String data) throws IOException {
        throw new UnsupportedOperationException("Can't write to config");
    }

    @Nullable
    @Override
    public String loadData() throws IOException {
        return config;
    }
}
