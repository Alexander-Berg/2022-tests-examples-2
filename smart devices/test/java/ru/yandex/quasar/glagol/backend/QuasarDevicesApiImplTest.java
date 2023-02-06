package ru.yandex.quasar.glagol.backend;

import com.google.gson.Gson;
import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;
import okhttp3.mockwebserver.MockResponse;
import okhttp3.mockwebserver.MockWebServer;
import org.junit.Test;
import ru.yandex.quasar.glagol.backend.impl.QuasarDevicesApiImpl;
import ru.yandex.quasar.glagol.backend.impl.BackendOkHttpClient;
import ru.yandex.quasar.glagol.backend.model.Device;
import ru.yandex.quasar.glagol.backend.model.Devices;
import ru.yandex.quasar.glagol.reporter.MockMetricaClient;
import ru.yandex.quasar.glagol.reporter.MetricaReporter;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public class QuasarDevicesApiImplTest {

    private final Gson gson = new Gson();
    private MockMetricaClient metricaClient;

    private QuasarDevicesApiImpl backendForResponse(String response) throws Exception {
        MockWebServer mockWebServer = new MockWebServer();
        mockWebServer.start();

        mockWebServer.enqueue(new MockResponse().setBody(response));

        metricaClient = new MockMetricaClient();
        return new QuasarDevicesApiImpl(new BackendOkHttpClient(
                "http://" + InetAddress.getByName(mockWebServer.getHostName()).getCanonicalHostName()
                        + ":" + mockWebServer.getPort()), new MetricaReporter(null, metricaClient));
    }

    @Test
    public void discoveredDeviceNameInConfig() throws Exception {
        // a sample device response
        QuasarDevicesApiImpl backendDevicesApi = backendForResponse("{\n" +
                "  \"devices\": [\n" +
                "    {\n" +
                "      \"activation_code\": 123,\n" +
                "      \"config\": {\n" +
                "        \"name\": \"NameInConfig\"\n" +
                "      },\n" +
                "      \"glagol\": {\n" +
                "        \"security\": {\n" +
                "          \"server_certificate\": \"cert\",\n" +
                "          \"server_private_key\": \"key\"\n" +
                "        }\n" +
                "      },\n" +
                "      \"id\": \"9400503441102c2b090b\",\n" +
                "      \"name\": \"NameInBackend\",\n" +
                "      \"platform\": \"yandexstation\"\n" +
                "    }]" +
                "}");

        Devices result = backendDevicesApi.getConnectedDevicesList("blah");
        assertEquals(1, result.getDevices().size());
        assertEquals("NameInConfig", result.getDevices().get(0).getConfig().get("name"));
        assertEquals("NameInBackend", result.getDevices().get(0).getName());
        assertEquals(1, metricaClient.getEventLog().size());
    }

    @Test
    public void discoveredDeviceNoConfig() throws Exception {
        // a sample device response
        QuasarDevicesApiImpl backendDevicesApi = backendForResponse("{\n" +
                "  \"devices\": [\n" +
                "    {\n" +
                "      \"activation_code\": 123,\n" +
                "      \"glagol\": {\n" +
                "        \"security\": {\n" +
                "          \"server_certificate\": \"cert\",\n" +
                "          \"server_private_key\": \"key\"\n" +
                "        }\n" +
                "      },\n" +
                "      \"id\": \"9400503441102c2b090b\",\n" +
                "      \"name\": \"NameInBackend\",\n" +
                "      \"platform\": \"yandexstation\"\n" +
                "    }]" +
                "}");

        Devices result = backendDevicesApi.getConnectedDevicesList("blah");
        assertEquals(1, result.getDevices().size());
        assertEquals(null, result.getDevices().get(0).getConfig());
        assertEquals("NameInBackend", result.getDevices().get(0).getName());
        assertEquals("cert", result.getDevices().get(0).getGlagol().getSecurity().getServerCertificate());
        assertEquals("key", result.getDevices().get(0).getGlagol().getSecurity().getServerPrivateKey());
    }

    @Test
    public void getConnectedDevicesShouldFilterBy() throws Exception {
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

        QuasarDevicesApiImpl quasarDevicesApiImplImpl = backendForResponse(jsonStubResponse);

        Devices result = quasarDevicesApiImplImpl.getConnectedDevicesList("blah");
        assertEquals(2, result.getDevices().size());
        assertEquals("yandexmodule", result.getDevices().get(0).getPlatform());
        assertEquals(true, result.getDevices().get(0).getPromocodeActivated());
        assertEquals("HUZZAH!", result.getDevices().get(0).getActivationCode());
        assertEquals(1, metricaClient.getEventLog().size());
    }

    private static class TimeoutServerThread implements Runnable {

        ServerSocket serverSocket;
        private Socket clientSocket;
        private CountDownLatch countDownLatch = new CountDownLatch(1);
        private AtomicInteger successFlag;

        TimeoutServerThread(AtomicInteger successFlag) {
            this.successFlag = successFlag;
        }

        @Override
        public void run() {
            try {
                serverSocket = new ServerSocket(0, 0, InetAddress.getLocalHost());
                countDownLatch.countDown();
                System.out.println(serverSocket.getLocalPort());
                System.out.println(serverSocket.getInetAddress());
                clientSocket = serverSocket.accept();
                System.out.println("throwing out first connection attempt");
                clientSocket = serverSocket.accept();
                successFlag.incrementAndGet();
            } catch (IOException e) {
                e.printStackTrace();
            }
            try {
                Thread.sleep(10000000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        void waitForStart() throws InterruptedException {
            countDownLatch.await();
        }
    }

    @Test
    public void getRetryOnTimeout() throws Exception {
        AtomicInteger successFlag = new AtomicInteger();
        TimeoutServerThread timeoutServer = new TimeoutServerThread(successFlag);
        new Thread(timeoutServer).start();
        timeoutServer.waitForStart();

        String hostAddress = timeoutServer.serverSocket.getInetAddress().getCanonicalHostName();
        int localPort = timeoutServer.serverSocket.getLocalPort();
        String backendUrl = "https://" + hostAddress + ":" + localPort;
        QuasarDevicesApiImpl quasarDevicesApiImplImpl = null;
        metricaClient = new MockMetricaClient();
        quasarDevicesApiImplImpl = new QuasarDevicesApiImpl(new BackendOkHttpClient(backendUrl), new MetricaReporter(null, metricaClient));
        Devices result;
        try {
            result = quasarDevicesApiImplImpl.getConnectedDevicesList("blah");
        } catch (Exception e) {
            if ((e instanceof SocketTimeoutException || e.getCause() instanceof SocketTimeoutException)
                    && successFlag.get() != 1) {
                fail("did not retry!");
            }
        }

        assertEquals(metricaClient.getEventLog().size(), 1);
    }

    @Test
    public void getRetryOn503() throws Exception {
        MockWebServer mockWebServer = new MockWebServer();
        mockWebServer.start();

        mockWebServer.enqueue(new MockResponse().setResponseCode(503));

        Devices devices = new Devices();
        List<Device> devicesList = new ArrayList<>();
        Device device = new Device();
        device.setId("id1");
        device.setPlatform("yandexmodule");
        devicesList.add(device);
        device = new Device();
        device.setId("id2");
        device.setPlatform("b");
        devicesList.add(device);
        devices.setDevices(devicesList);

        String jsonStubResponse = gson.toJson(devices);
        mockWebServer.enqueue(new MockResponse().setBody(jsonStubResponse));


        metricaClient = new MockMetricaClient();
        QuasarDevicesApiImpl quasarDevicesApiImplImpl = new QuasarDevicesApiImpl(new BackendOkHttpClient(
                "http://" + InetAddress.getByName(mockWebServer.getHostName()).getCanonicalHostName()
                        + ":" + mockWebServer.getPort()), new MetricaReporter(null, metricaClient));

        Devices result = quasarDevicesApiImplImpl.getConnectedDevicesList("blah");
        assertEquals(2, result.getDevices().size());
        assertEquals(1, metricaClient.getEventLog().size());
    }

    @Test
    public void getErrorOn504() throws Exception {
        MockWebServer mockWebServer = new MockWebServer();
        mockWebServer.start();

        mockWebServer.enqueue(new MockResponse().setResponseCode(504));

        metricaClient = new MockMetricaClient();
        QuasarDevicesApiImpl quasarDevicesApiImplImpl = new QuasarDevicesApiImpl(new BackendOkHttpClient(
                "http://" + InetAddress.getByName(mockWebServer.getHostName()).getCanonicalHostName()
                        + ":" + mockWebServer.getPort()), new MetricaReporter(null, metricaClient));

        boolean exception = false;
        try {
            Devices result = quasarDevicesApiImplImpl.getConnectedDevicesList("blah");
        } catch (IOException e) {
            exception = true;
        }
        assertTrue(exception);
        final MockMetricaClient.Event actual = metricaClient.getEventLog().get(0);
        assertEquals(actual.getName(), "gsdkBackendDeviceListFailure");
        assertEquals("504", actual.getParam("errorCode").toString());
    }
}
