package com.yandex.launcher.updaterapp.core.configure;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.mockito.Mockito.when;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;
import com.yandex.launcher.updaterapp.BuildConfig;
import com.yandex.launcher.updaterapp.common.ApplicationConfig;
import com.yandex.launcher.updaterapp.configure.ConfigurerImpl;
import com.yandex.launcher.updaterapp.utils.MockWebServerDispatcher;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;

import androidx.annotation.NonNull;
import okhttp3.HttpUrl;
import okhttp3.mockwebserver.MockWebServer;
import okhttp3.mockwebserver.RecordedRequest;
import okio.BufferedSource;
import okio.Okio;

public class ConfigurerTest extends BaseRobolectricTest {

    private MockWebServer mockWebServer;
    private MockWebServerDispatcher webServerDispatcher;

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        webServerDispatcher = new MockWebServerDispatcher();
        mockWebServer = new MockWebServer();
        mockWebServer.setDispatcher(webServerDispatcher);
        mockWebServer.start();
        setupSystemInfo();
    }

    @After
    public void tearDown() throws Exception {
        webServerDispatcher.clear();
        mockWebServer.shutdown();
    }

    MockWebServer getWebServer() {
        return mockWebServer;
    }

    String getResponseText(String fileName) throws IOException {
        try (InputStream responseStream = this.getClass().getClassLoader().getResourceAsStream(fileName)) {
            final BufferedSource responseSource = Okio.buffer(Okio.source(responseStream));
            return responseSource.readString(Charset.defaultCharset());
        }
    }

    @Test
    public void shouldStoreAndRestoreSameDefaultConfiguration() {
        final ConfigurerImpl configurer = new ConfigurerImpl(getUpdateContext().getContext(), getUpdateContext().getSettings(),
                getSystemInfoProvider());
        final Configuration config = new Configuration.Builder(ApplicationConfig.getInstance(getApp())).build();

        configurer.storeConfiguration(config);

        final Configuration restoredConfig = configurer.restoreConfiguration(getUpdateContext().getContext());

        assertThat(config, is(restoredConfig));
    }

    @Test
    public void shouldFetchConfigurationSuccessfullyWithProperHeadersWithInvalidResponse() throws IOException, InterruptedException {
        final String response = getResponseText("configuration_deprecated.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response, true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(6);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(2);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_ALL);

        assertThat(config, is(expectedConfigurationBuilder.build()));

        final RecordedRequest request = getWebServer().takeRequest();

        assertThat(request.getHeader("User-Agent"), is(USER_AGENT));
        assertThat(request.getHeader("X-YaUuid"), is(YA_UUID));
        assertThat(request.getHeader("Serial"), is(SERIAL));
        assertThat(request.getHeader("YPhone-Id"), is(""));
    }

    @Test
    public void shouldFetchConfigurationSuccessfully() throws IOException {
        final String response = getResponseText("configuration.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response, true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(4);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(3);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_NONE);
        expectedConfigurationBuilder.setAutoCheckEnabled(true);
        expectedConfigurationBuilder.setUpdateInterruptStrategy(Configuration.INTERRUPTION_EXCEPT_PLAY);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchConfigurationWithAdditionalFieldsSuccessfully() throws IOException {
        final String response = getResponseText("configuration_additional_fields.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response, true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();

        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(4);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(3);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_NONE);
        expectedConfigurationBuilder.setAutoCheckEnabled(true);
        expectedConfigurationBuilder.setUpdateInterruptStrategy(Configuration.INTERRUPTION_EXCEPT_PLAYER);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchEmptyJsonConfiguration() {
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, "{}", true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(6);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(2);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_ALL);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchJsonArrayConfiguration() {
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, "[\"item\"]", true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(6);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(2);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_ALL);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchInvalidJsonConfiguration() throws IOException {
        final String response = getResponseText("configuration_invalid_fields.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response, true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(6);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(3);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_NONE);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchEmptyStringConfiguration() {
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, "", true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(6);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(2);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_ALL);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchIncompleteConfiguration() throws IOException {
        final String response = getResponseText("configuration_incomplete.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response, true);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(4);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(2);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_ALL);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void shouldFetchConfigurationSuccessfullyAfterTwo500() throws IOException {
        final String response = getResponseText("configuration.json");

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 500, "");
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 504, "");
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 200, response);

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder expectedConfigurationBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        expectedConfigurationBuilder.setNightIntervalEndTimeHours(4);
        expectedConfigurationBuilder.setNightIntervalStartTimeHours(3);
        expectedConfigurationBuilder.setNotifications(Configuration.NOTIFICATION_NONE);
        expectedConfigurationBuilder.setAutoCheckEnabled(true);
        expectedConfigurationBuilder.setUpdateInterruptStrategy(Configuration.INTERRUPTION_EXCEPT_PLAY);

        assertThat(config, is(expectedConfigurationBuilder.build()));
    }

    @Test
    public void overriddenConfiguration() {
        final ConfigurerImpl configurer = new ConfigurerImpl(getUpdateContext().getContext(), getUpdateContext().getSettings(),
                getSystemInfoProvider());

        final Configuration.Builder configBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configBuilder.setNightIntervalStartTimeHours(19);

        final Configuration config = configBuilder.build();

        configurer.storeConfiguration(config);
        configurer.storeOverriddenConfiguration(Configuration.FieldName.NIGHT_INTERVAL_START_TIME_HOURS, null);

        final Configuration restoredConfig = configurer.restoreConfiguration(getUpdateContext().getContext());

        assertThat(restoredConfig.getNightIntervalStartTimeHours(), is(19));
    }

    @Test
    public void shouldFetchConfigurationErrorAfterThree500() throws IOException {
        final String response = getResponseText("configuration_deprecated.json");

        final ConfigurerImpl configurer = createConfigurer();

        final Configuration initialConfig = configurer.fetchConfiguration();

        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 500, response);
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 504, response);
        webServerDispatcher.enqueue(settings.getServerPathV3() + ConfigurerImpl.SETTINGS_PATH, 505, response);

        final Configuration config = configurer.fetchConfiguration();
        final Configuration.Builder configurationFromResponseBuilder = new Configuration.Builder(ApplicationConfig.getInstance(getApp()));

        configurationFromResponseBuilder.setNightIntervalEndTimeHours(6);
        configurationFromResponseBuilder.setNightIntervalStartTimeHours(2);
        configurationFromResponseBuilder.setNotifications(Configuration.NOTIFICATION_NONE);

        assertThat(config, not(configurationFromResponseBuilder.build()));
        assertThat(config, is(initialConfig));
    }

    @NonNull
    private ConfigurerImpl createConfigurer() {
        final HttpUrl url = getWebServer().url("/api/v3/settings");

        when(getSettings().getServerHost()).thenReturn(url.host());
        when(getSettings().getServerPath()).thenReturn("api");
        when(getSettings().getServerPort()).thenReturn(url.port());
        return new ConfigurerImpl(getUpdateContext().getContext(), getUpdateContext().getSettings(), getSystemInfoProvider());
    }
}
