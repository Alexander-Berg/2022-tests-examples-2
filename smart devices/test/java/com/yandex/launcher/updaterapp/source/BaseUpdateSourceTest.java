package com.yandex.launcher.updaterapp.source;

import com.yandex.launcher.updaterapp.BaseRobolectricTest;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.rules.ExpectedException;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;

import okhttp3.mockwebserver.MockWebServer;
import okio.BufferedSource;
import okio.Okio;

public abstract class BaseUpdateSourceTest extends BaseRobolectricTest {

    private MockWebServer mockWebServer;

    @Rule
    public final ExpectedException thrownException = ExpectedException.none();

    @Override
    @Before
    public void setUp() throws Exception {
        super.setUp();
        mockWebServer = new MockWebServer();
    }

    @After
    public void tearDown() throws Exception {
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
}
