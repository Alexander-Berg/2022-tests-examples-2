package ru.yandex.quasar.glagol.impl;

import com.google.gson.Gson;
import java.io.IOException;
import java.net.InetAddress;
import java.util.ArrayList;
import java.util.List;

import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.Test;

import ru.yandex.quasar.glagol.Config;
import ru.yandex.quasar.glagol.Connector;
import ru.yandex.quasar.glagol.Conversation;
import ru.yandex.quasar.glagol.DiscoveryResultItem;
import ru.yandex.quasar.glagol.DiscoveryResultItemDummy;
import ru.yandex.quasar.glagol.GlagolException;
import ru.yandex.quasar.glagol.Payload;
import ru.yandex.quasar.glagol.backend.model.Device;
import ru.yandex.quasar.glagol.backend.model.Devices;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class ConnectorImplTest {
    private final Gson gson = new Gson();

    private final static String testCertificate = "-----BEGIN CERTIFICATE-----\n" +
            "MIIDBjCCAe4CCQCifnwdKnB7CDANBgkqhkiG9w0BAQsFADBFMQswCQYDVQQGEwJB\n" +
            "VTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50ZXJuZXQgV2lkZ2l0\n" +
            "cyBQdHkgTHRkMB4XDTE5MDExNDA1NDI0MFoXDTIxMTAxMDA1NDI0MFowRTELMAkG\n" +
            "A1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoMGEludGVybmV0\n" +
            "IFdpZGdpdHMgUHR5IEx0ZDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB\n" +
            "AOVHP4mXGPpEgbPw1EUdRZ3qiyu1FQyK7vJg6D/vZKGiUt/sw1eEUay/rZ168cXT\n" +
            "7nKT3/4G5IyeJ3elwjNeGxmU3jeG0dYexn44ryyi7ujXTjb2s0kbHKSa5f9bwzo5\n" +
            "ka3UHmX/cZwUe9AgGjmHcj6qYlUhOQKCllV5TyuzkkuxBgndiuOUZE7SHdtICMCT\n" +
            "/OOjxBVk/ooeeAi9kL0eROExFN30YG+3JjfcH3jt4jqoGKgw69vnLJVNWg6rlGxa\n" +
            "DnVVoWPe6C9q/vlGe7GpbFjYthoFFYBfcRLEHDrQRR4/ZYaWCyf6m1QriS5EE7xk\n" +
            "6VWM0qaCapqZtRPIwR7HB+8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEABunHHtlx\n" +
            "Zm0bpYzCA4njE4CdIRR9jvz7RxvJE9IMpdr4dTBPbY7JLDNUALIA7EYzwbSZyjpK\n" +
            "esG/DCNAymzVoa98Y6ldjl0ftCRNMF8cG1hqNFMk8NTq852jQkBEFGEGon/cXJom\n" +
            "hoSeWuvqbEYyAmvt3sd7+fNh+/gZiQacRYNohw10qYz4s4AAhAJbHtd4nCi25e9d\n" +
            "+vNrIyXzIfX94pmNnnMXt3KmkMotxAhmfOlZcMtu7/sSdLg0nZQOyZu9MoKhUDUg\n" +
            "DH9rbaQeLpYJ5Knq0PZ7GBoljr3Pkosj2LDk9YomWsK2KCnErRw2QmGyOUMWMdHY\n" +
            "xTajk6l3fymisA==\n" +
            "-----END CERTIFICATE-----\n";

    @Test
    public void testSmoke() {
        ConnectorImpl connector = new ConnectorImpl(new Config.Builder().useDemoMetricaKey().build());

        assertNotNull(connector);
    }

    @Test
    public void connectTest() throws GlagolException, IOException {
        DiscoveryResultItem item = new DiscoveryResultItemDummy("foo", "foo",
                "yandexmodule", "ws://echo.websocket.org", true, testCertificate);

        MockWebServer mockWebServer = new MockWebServer();
        mockWebServer.start();

        Devices devices = new Devices();
        List<Device> devicesList = new ArrayList<>();
        Device device = new Device();
        device.setPlatform("yandexmodule");
        device.setPromocodeActivated(true);
        device.setActivationCode("HUZZAH!");
        devicesList.add(device);
        device = new Device();
        device.setPlatform("b");
        devicesList.add(device);
        devices.setDevices(devicesList);

        String jsonStubResponse = gson.toJson(devices);
        assertEquals(jsonStubResponse.contains("promocode_activated"), true);
        assertEquals(jsonStubResponse.contains("activation_code"), true);
        mockWebServer.enqueue(new MockResponse().setBody(jsonStubResponse));

        String mockBackendUrl = "http://" + InetAddress.getByName(mockWebServer.getHostName()).getCanonicalHostName() + ":" + mockWebServer.getPort();

        Config config = new Config.Builder().backendUrl(mockBackendUrl).useDemoMetricaKey().build();

        Connector connector = new ConnectorImpl(config);

        Conversation conversation = connector.connect(item, "foo", message -> System.out.print("Message"), null, null);

        Payload payload = connector.getPayloadFactory().getPingPayload();

        conversation.send(payload);
    }

    // TODO: add more tests
}
