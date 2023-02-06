package ru.yandex.quasar.app.configs;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.annotation.Config;

import androidx.annotation.NonNull;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import ru.yandex.quasar.fakes.FakeConfiguration;
import ru.yandex.quasar.TestUtils;
import ru.yandex.quasar.UtilHelper;
import ru.yandex.quasar.protobuf.ModelObjects;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

@RunWith(value = AndroidJUnit4.class)
@Config(sdk = 19)
public class StationConfigTest {
    @NonNull
    private ObjectMapper objectMapper = new ObjectMapper();

    @Test
    public void testEmptyGroupConfig() {
        FakeConfiguration configuration = new FakeConfiguration();
        configuration.initialize("{'aliced':{'experiments':[]}, 'metricad':{'port': 9887}}");
        UtilHelper.setDeviceID("X");

        ModelObjects.UserConfig userConfig = ModelObjects.UserConfig
                .newBuilder()
                .setConfig(TestUtils.INSTANCE.toJsonQuotes("{'account_config': {'contentAccess': 'foo', 'spotter': 'yandex'}, 'system_config': {}}"))
                .setGroupConfig("{}")
                .setPassportUid("123")
                .build();

        StationConfig stationConfig = StationConfig.fromUserConfigUpdate(userConfig, objectMapper, configuration);

        assertNotNull(stationConfig.getGroupConfig());
        assertFalse(stationConfig.getGroupConfig().weAreLeader(configuration));
        assertNull(stationConfig.getGroupConfig().getFollower());
    }

    @Test
    public void testWeAreLeader() {
        FakeConfiguration configuration = new FakeConfiguration();
        configuration.initialize(TestUtils.INSTANCE.toJsonQuotes("{'common': {'deviceType': 'yandexstation'}, 'aliced':{'experiments':[]}, 'metricad':{'port': 9887}}"));
        UtilHelper.setDeviceID("X");

        ModelObjects.UserConfig userConfig = ModelObjects.UserConfig
                .newBuilder()
                .setConfig(TestUtils.INSTANCE.toJsonQuotes("{'account_config': {'contentAccess': 'foo', 'spotter': 'yandex'}, 'system_config': {}}"))
                .setGroupConfig(TestUtils.INSTANCE.toJsonQuotes("{'id': '123', 'secret': '234', 'devices': [{'id': 'X', 'role': 'leader', 'platform': 'yandexstation'}, {'id': 'Y', 'role': 'follower', 'platform': 'yandexmodule'}]}"))
                .setPassportUid("123")
                .build();

        StationConfig stationConfig = StationConfig.fromUserConfigUpdate(userConfig, objectMapper, configuration);

        assertNotNull(stationConfig.getGroupConfig());
        assertTrue(stationConfig.getGroupConfig().weAreLeader(configuration));
        assertNotNull(stationConfig.getGroupConfig().getFollower());
    }
}
