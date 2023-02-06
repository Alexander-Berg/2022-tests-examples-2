package ru.yandex.quasar.glagol.reporter

import com.google.gson.JsonParser
import okhttp3.Protocol
import okhttp3.Request
import okhttp3.Response
import org.hamcrest.Matchers.*
import org.hamcrest.MatcherAssert.assertThat
import org.junit.Before
import org.junit.Test
import ru.yandex.quasar.glagol.DiscoveryResultItemDummy
import ru.yandex.quasar.glagol.backend.model.Device
import ru.yandex.quasar.glagol.backend.model.Devices
import ru.yandex.quasar.glagol.conversation.model.Command

class MetricaEventsTest {

    lateinit var reporter: MetricaReporter
    lateinit var client: SingleEventMetricaReporter

    @Test
    fun testDiscoveryDeviceFound()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")

        reporter.onDeviceDiscovered(DiscoveryResultItemDummy("name-value", "id-value", "platform-value"), 2000000, 2000200)
        val jsonRes = client.getParamsJson()
        assertThat(client.currentEvent, `is`(equalTo("gsdkDiscoveryMdnsSuccess")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("200")))
        assertThat(jsonRes.get("startTime").asString, `is`("2000000"))
        assertThat(jsonRes.get("endTime").asString, `is`("2000200"))
    }

    @Test
    fun testDiscoveryDeviceFoundAndChecked()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")

        reporter.onDeviceDiscoveredAccountChecked(DiscoveryResultItemDummy("name-value", "id-value", "platform-value"), 0, 200)
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkDiscoveryAccountCheckSuccess")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("200")))
        assertThat(jsonRes.get("startTime").asString, `is`("0"))
        assertThat(jsonRes.get("endTime").asString, `is`("200"))
    }

    @Test
    fun testDiscoveryLostDevice() {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")

        reporter.onDeviceLost(1600, 1900, DiscoveryResultItemDummy("name-value", "id-value", "platform-value"))
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkDiscoveryMdnsDisappear")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("300")))
        assertThat(jsonRes.get("startTime").asString, `is`("1600"))
        assertThat(jsonRes.get("endTime").asString, `is`("1900"))
    }

    @Test
    fun testDiscoveryStopScan() {
        val jsonDevice1 = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")
        val jsonDevice2 = JsonParser.parseString("{\"id\":\"id-value2\",\"platform\":\"platform-value2\",\"host\":\"192.1.2.4\",\"port\":124}")

        val device1 = DiscoveryResultItemDummy("name-value", "id-value", "platform-value")
        val device2 = DiscoveryResultItemDummy("name-value", "id-value2", "platform-value2", "wss://192.1.2.4:124")

        reporter.onDiscoveryScanStopped(listOf(device1, device2), 100, 2100)
        val res = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkDiscoveryStopSearching")))
        val deviceArray = res.getAsJsonArray("devices")
        assertThat(deviceArray.size(), `is`(equalTo(2)))
        assertThat(deviceArray.get(0), `is`(equalTo(jsonDevice1)))
        assertThat(deviceArray.get(1), `is`(equalTo(jsonDevice2)))
        assertThat(res.get("durationMS").asString, `is`("2000"))
        assertThat(res.get("startTime").asString, `is`("100"))
        assertThat(res.get("endTime").asString, `is`("2100"))
    }

    @Test
    fun testDiscoverySearchFailure() {
        reporter.onDeviceDiscoverFailed("ololo-tcp.123.ololo", 1000, 2000, java.lang.Exception("ololo"))
        val res = client.getParamsJson()
        assertThat(client.currentEvent, `is`(equalTo("gsdkDiscoveryMdnsSearchFailure")))
        assertThat(res.get("serviceName").asString, `is`(equalTo("ololo-tcp.123.ololo")))
        assertThat(res.get("errorDomain").asString, `is`(notNullValue()))
        assertThat(res.get("durationMS").asString, `is`("1000"))
        assertThat(res.get("startTime").asString, `is`("1000"))
        assertThat(res.get("endTime").asString, `is`("2000"))
    }

    @Test
    fun testBackendListRequested() {

        val device1 = Device().apply {
            id = "id1"
            name = "name1"
            platform = "platform1"
        }

        val device2 = Device().apply {
            id = "id2"
            name = "name2"
            platform = "platform2"
        }

        val res = Devices()
        res.devices = listOf(device1, device2)
        reporter.onQuasarDevicesReceived(100, 200, res)

        assertThat(client.currentEvent, `is`(equalTo("gsdkBackendDeviceListRequested")))
        val jsonRes = client.getParamsJson()
        assertThat(jsonRes.get("source").asString, `is`(equalTo("quasar")))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("100")))
        assertThat(jsonRes.get("startTime").asString, `is`("100"))
        assertThat(jsonRes.get("endTime").asString, `is`("200"))

        val devicesArray = jsonRes.getAsJsonArray("devices")
        assertThat(devicesArray.size(), `is`(equalTo(2)))
        assertThat(devicesArray[0], `is`(equalTo(JsonParser.parseString("{\"id\":\"id1\",\"platform\":\"platform1\"}"))))
        assertThat(devicesArray[1], `is`(equalTo(JsonParser.parseString("{\"id\":\"id2\",\"platform\":\"platform2\"}"))))
    }

    @Test
    fun testBackendListFailure() {
        val request = Request.Builder().url("https://ya.ru/").build()
        val response = Response.Builder().code(403).message("ololo")
            .request(request).protocol(Protocol.HTTP_2).build()
        reporter.onBackendRequestFailure("Error", "iot", 200, 2200, response)

        assertThat(client.currentEvent, `is`(equalTo("gsdkError")))
        val jsonRes = client.getParamsJson()
        assertThat(jsonRes.get("source").asString, `is`(equalTo("iot")))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("2000")))
        assertThat(jsonRes.get("startTime").asString, `is`("200"))
        assertThat(jsonRes.get("endTime").asString, `is`("2200"))
        assertThat(jsonRes.get("errorCode").asString, `is`(equalTo("403")))
        assertThat(jsonRes.get("url").asString, `is`(equalTo("https://ya.ru/")))
    }

    @Test
    fun testBackendListError() {
        val request = Request.Builder().url("https://ya.ru/").build()
        reporter.onBackendRequestException("Fail", "quasar", 200, 2200, request, Exception("ololo"))

        assertThat(client.currentEvent, `is`(equalTo("gsdkFail")))
        val jsonRes = client.getParamsJson()
        assertThat(jsonRes.get("source").asString, `is`(equalTo("quasar")))
        assertThat(jsonRes.get("durationMS").asString, `is`(equalTo("2000")))
        assertThat(jsonRes.get("startTime").asString, `is`("200"))
        assertThat(jsonRes.get("endTime").asString, `is`("2200"))
        assertThat(jsonRes.get("errorCode").asString, `is`(equalTo("666")))
        assertThat(jsonRes.get("url").asString, `is`(equalTo("https://ya.ru/")))
    }

    @Test
    fun testConversationOpen()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")
        val device = DiscoveryResultItemDummy("name-value", "id-value", "platform-value")
        reporter.setDeviceInfo(device)
        reporter.onConversationCreate(device)
        reporter.onSimpleEvent(GlagolMetrics.CONNECT_WS_OPEN)
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkConnectWsOpen")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
    }

    @Test
    fun testConversationClose()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")
        val device = DiscoveryResultItemDummy("name-value", "id-value", "platform-value")
        reporter.setDeviceInfo(device)
        reporter.onConversationCreate(device)
        reporter.onWebsocketClose("websocket-close-code")
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkConnectWsClose")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("wsCloseCode").asString, `is`(equalTo("websocket-close-code")))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
    }

    @Test
    fun testConversationError()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")
        val device = DiscoveryResultItemDummy("name-value", "id-value", "platform-value")
        reporter.setDeviceInfo(device)
        reporter.onConversationCreate(device)
        reporter.onConversationError(device, java.lang.Exception("ololo"))
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkConnectWsError")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
        assertThat(jsonRes.get("errorDomain").asString, `is`(notNullValue()))
    }

    @Test
    fun testConversationCommand()  {
        val jsonExp = JsonParser.parseString("{\"id\":\"id-value\",\"platform\":\"platform-value\",\"host\":\"192.1.2.3\",\"port\":123}")
        val device = DiscoveryResultItemDummy("name-value", "id-value", "platform-value")
        reporter.setDeviceInfo(device)
        reporter.onMessageSentToDevice("123", Command("play"))
        val jsonRes = client.getParamsJson()

        assertThat(client.currentEvent, `is`(equalTo("gsdkConnectWsCommand")))
        assertThat(jsonRes.get("device"), `is`(equalTo(jsonExp)))
        assertThat(jsonRes.get("port").asString, `is`(equalTo("123")))
        assertThat(jsonRes.get("host").asString, `is`(equalTo("192.1.2.3")))
        assertThat(jsonRes.get("command").asString, `is`(equalTo("play")))
        assertThat(jsonRes.get("requestID").asString, `is`(equalTo("123")))
    }

    @Before
    fun createReporter() {
        client = SingleEventMetricaReporter()
        reporter = MetricaReporter(null, MetricaClientImpl("gsdk", client))
    }

}

