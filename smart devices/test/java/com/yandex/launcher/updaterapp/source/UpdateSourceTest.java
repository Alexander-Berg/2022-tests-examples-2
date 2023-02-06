package com.yandex.launcher.updaterapp.source;

import com.yandex.launcher.updaterapp.common.utils.CheckException;
import com.yandex.launcher.updaterapp.contract.models.Update;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Before;
import org.junit.Test;
import org.robolectric.RuntimeEnvironment;

import java.io.IOException;

import androidx.annotation.NonNull;
import okhttp3.HttpUrl;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.RecordedRequest;

import static java.net.HttpURLConnection.HTTP_OK;
import static junit.framework.Assert.assertEquals;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.mockito.Mockito.when;

public class UpdateSourceTest extends BaseUpdateSourceTest {

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        setupSystemInfo();
    }

    @Test
    public void checkForUpdates() throws IOException, CheckException, InterruptedException, JSONException {
        final String response = getResponseText("update_source_response.json");
        getWebServer().enqueue(new MockResponse().setResponseCode(HTTP_OK).setBody(response));
        getWebServer().start();

        final UpdateSource updateSource = createUpdateSource();
        final UpdatesResponseImpl updates = updateSource.getAppUpdates();

        assertEquals(2, updates.size());
        assertEquals(
                new Update(
                        "launcher",
                        "com.yandex.launcher",
                        "https://beta.m.soft.yandex.ru/download/launcher/dev/launcher-android.apk?time=1463656030&signature=d3496a7802064495441aff97b164b56b2c2a8bc5cc30810a6439033f0efa4286",
                        "1.2.3",
                        123),
                updates.updates.get(0));
        assertEquals(
                new Update(
                        "launcher_updater",
                        "com.yandex.launcher.updaterapp",
                        "https://beta.m.soft.yandex.ru/download/launcher_updater/beta/launcher_updater-android.apk?time=1463656030&signature=66ff4b9425e97445cd832ce3bfeaef2e52b167c30fc36c80006b4e103b735edf",
                        "5.6.7-xxx",
                        123456),
                updates.updates.get(1));

        final RecordedRequest request = getWebServer().takeRequest();
        JSONObject jsonRequestBody = new JSONObject(request.getBody().readUtf8());
        JSONArray requestInstalledApps = jsonRequestBody.getJSONArray("installed_apps");

        assertThat(jsonRequestBody.get("device_id"), is(DEVICE_ID));
        assertThat(requestInstalledApps.length(), is(1));
        assertThat(requestInstalledApps.getJSONObject(0).get("package_name"), is("com.yandex.launcher.updaterapp"));
        assertThat(requestInstalledApps.getJSONObject(0).get("version_name"), is(not(nullValue())));
        assertThat(requestInstalledApps.getJSONObject(0).get("version_code"), is(not(nullValue())));
        assertEquals(request.getHeader("User-Agent"), USER_AGENT);
        assertEquals(request.getHeader("X-YaUuid"), YA_UUID);
        assertThat(request.getHeader("Serial"), is(SERIAL));
        assertThat(request.getHeader("YPhone-Id"), is(""));
    }

    @Test
    public void checkForUpdatesWithTwo500() throws IOException, CheckException, InterruptedException, JSONException {
        final String response = getResponseText("update_source_response.json");
        getWebServer().enqueue(new MockResponse().setResponseCode(500));
        getWebServer().enqueue(new MockResponse().setResponseCode(503));
        getWebServer().enqueue(new MockResponse().setResponseCode(HTTP_OK).setBody(response));
        getWebServer().start();

        final UpdateSource updateSource = createUpdateSource();
        final UpdatesResponseImpl updates = updateSource.getAppUpdates();

        assertEquals(2, updates.size());
        assertEquals(
                new Update(
                        "launcher",
                        "com.yandex.launcher",
                        "https://beta.m.soft.yandex.ru/download/launcher/dev/launcher-android.apk?time=1463656030&signature=d3496a7802064495441aff97b164b56b2c2a8bc5cc30810a6439033f0efa4286",
                        "1.2.3",
                        123),
                updates.updates.get(0));
        assertEquals(
                new Update(
                        "launcher_updater",
                        "com.yandex.launcher.updaterapp",
                        "https://beta.m.soft.yandex.ru/download/launcher_updater/beta/launcher_updater-android.apk?time=1463656030&signature=66ff4b9425e97445cd832ce3bfeaef2e52b167c30fc36c80006b4e103b735edf",
                        "5.6.7-xxx",
                        123456),
                updates.updates.get(1));

        final RecordedRequest request = getWebServer().takeRequest();

        JSONObject jsonRequestBody = new JSONObject(request.getBody().readUtf8());
        JSONArray requestInstalledApps = jsonRequestBody.getJSONArray("installed_apps");

        assertThat(jsonRequestBody.get("device_id"), is(DEVICE_ID));
        assertThat(requestInstalledApps.length(), is(1));
        assertThat(requestInstalledApps.getJSONObject(0).get("package_name"), is("com.yandex.launcher.updaterapp"));
        assertThat(requestInstalledApps.getJSONObject(0).get("version_name"), is(not(nullValue())));
        assertThat(requestInstalledApps.getJSONObject(0).get("version_code"), is(not(nullValue())));
        assertEquals(request.getHeader("User-Agent"), USER_AGENT);
        assertEquals(request.getHeader("X-YaUuid"), YA_UUID);
        assertThat(request.getHeader("Serial"), is(SERIAL));
        assertThat(request.getHeader("YPhone-Id"), is(""));
    }

    @Test
    public void responseRejected() throws IOException, CheckException {
        getWebServer().enqueue(new MockResponse().setResponseCode(404).setBody(""));
        getWebServer().start();

        final UpdateSource updateSource = createUpdateSource();

        thrownException.expect(CheckException.class);

        updateSource.getAppUpdates();
    }

    @Test
    public void noResponseThree500() throws IOException, CheckException {
        getWebServer().enqueue(new MockResponse().setResponseCode(500).setBody(""));
        getWebServer().enqueue(new MockResponse().setResponseCode(501).setBody(""));
        getWebServer().enqueue(new MockResponse().setResponseCode(502).setBody(""));
        getWebServer().start();

        final UpdateSource updateSource = createUpdateSource();

        thrownException.expect(CheckException.class);

        updateSource.getAppUpdates();
    }

    @Test
    public void invalidResponse() throws IOException, CheckException {
        getWebServer().enqueue(new MockResponse().setResponseCode(HTTP_OK).setBody("AAA"));
        getWebServer().start();


        final UpdateSource updateSource = createUpdateSource();

        thrownException.expect(CheckException.class);

        updateSource.getAppUpdates();
    }

    @Test
    public void noPackageName() throws IOException, CheckException {
        getWebServer().enqueue(new MockResponse()
                .setResponseCode(HTTP_OK)
                .setBody(getResponseText("update_source_response_no_package_name.json")));
        getWebServer().start();

        final UpdateSource updateSource = createUpdateSource();

        thrownException.expect(CheckException.class);

        updateSource.getAppUpdates();
    }

    @NonNull
    private UpdateSource createUpdateSource() {
        final HttpUrl url = getWebServer().url("");
        when(getSettings().getServerPath()).thenReturn("/api/v1/updates");
        when(getSettings().getServerHost()).thenReturn(url.host());
        when(getSettings().getServerPort()).thenReturn(url.port());
        return new UpdateSource(RuntimeEnvironment.application, getSystemInfoProvider(),
                getSettings(), getUpdateContext());
    }
}
