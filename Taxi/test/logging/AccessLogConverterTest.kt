package logging

import ch.qos.logback.classic.spi.ILoggingEvent
import io.grpc.Status
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.UserCredentials
import ru.yandex.taxi.crm.masshire.search.logging.AccessLogConverter
import ru.yandex.taxi.crm.masshire.search.logging.AccessLogInterceptor
import ru.yandex.taxi.crm.masshire.search.logging.GrpcMDC
import ru.yandex.taxi.crm.masshire.search.logging.getOrNull
import ru.yandex.taxi.proto.crm.masshire.AccessLogMessage

private const val CONTEXT_UTILS = "ru.yandex.taxi.crm.masshire.search.logging.ContextUtilsKt"

internal class AccessLogConverterTest {
    private val event = mockk<ILoggingEvent>(relaxed = true)
    private val converter = AccessLogConverter()

    private fun convert(): AccessLogMessage = AccessLogMessage.parseFrom(converter.convert(event))

    @BeforeEach fun setup() = mockkStatic(CONTEXT_UTILS)
    @AfterEach fun teardown() = unmockkAll()

    @Test
    fun `given no GrpcMDC won't set method`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals("", convert().method)
    }

    @Test
    fun `given GrpcMDC without method won't set method`() {
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals("", convert().method)
    }

    @Test
    fun `given GrpcMDC with method will set method`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.METHOD_NAME_KEY, "method")
        assertEquals("method", convert().method)
    }

    @Test
    fun `given no GrpcMDC won't set status`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals("", convert().status)
    }

    @Test
    fun `given GrpcMDC without status code won't set status`() {
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals("", convert().status)
    }

    @Test
    fun `given GrpcMDC with status code sets status`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.STATUS_CODE_KEY, Status.Code.OK)
        assertEquals("OK", convert().status)
    }

    @Test
    fun `given no GrpcMDC won't set timestamp`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals(0, convert().timestamp)
    }

    @Test
    fun `given GrpcMDC without timestamp start won't set timestamp`() {
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals(0, convert().timestamp)
    }

    @Test
    fun `given GrpcMDC with timestamp start sets timestamp`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.TIMESTAMP_START_KEY, 42)
        assertEquals(42, convert().timestamp)
    }

    @Test
    fun `given no GrpcMDC won't set duration`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals(0, convert().duration)
    }

    @Test
    fun `given GrpcMDC without timestamp start won't set duration`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.TIMESTAMP_FINISH_KEY, 142)
        assertEquals(0, convert().duration)
    }

    @Test
    fun `given GrpcMDC without timestamp finish won't set duration`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.TIMESTAMP_START_KEY, 100)
        assertEquals(0, convert().duration)
    }

    @Test
    fun `given GrpcMDC with timestamp start and end sets duration`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC()
                .set(AccessLogInterceptor.TIMESTAMP_START_KEY, 100)
                .set(AccessLogInterceptor.TIMESTAMP_FINISH_KEY, 142)
        assertEquals(42, convert().duration)
    }

    @Test
    fun `given no GrpcMDC won't set request`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals("", convert().request)
    }

    @Test
    fun `given GrpcMDC without request won't set request`() {
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals("", convert().request)
    }

    @Test
    fun `given GrpcMDC with request sets request`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.REQUEST_KEY, "serialized request")
        assertEquals("serialized request", convert().request)
    }

    @Test
    fun `given GrpcMDC with request with cursor masks cursor`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.REQUEST_KEY, """{"cursor":"long_cursor_here"}""")
        assertEquals("""{"cursor":"<masked>"}""", convert().request)
    }

    @Test
    fun `given no GrpcMDC won't set requestId`() {
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals("", convert().requestId)
    }

    @Test
    fun `given GrpcMDC without request id won't set requestId`() {
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals("", convert().requestId)
    }

    @Test
    fun `given GrpcMDC with request id sets requestId`() {
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.REQUEST_ID_KEY, "42")
        assertEquals("42", convert().requestId)
    }

    @Test
    fun `given no UserCredentials won't set puid`() {
        every { UserCredentials.KEY.getOrNull() } returns null
        assertEquals(0, convert().puid)
    }

    @Test
    fun `given UserCredentials with broken userUid won't set puid`() {
        every { UserCredentials.KEY.getOrNull() } returns
            UserCredentials("", userUid = "not a long")
        assertEquals(0, convert().puid)
    }

    @Test
    fun `given UserCredentials with valid userUid sets puid`() {
        every { UserCredentials.KEY.getOrNull() } returns UserCredentials("", userUid = "42424242")
        assertEquals(42424242, convert().puid)
    }
}
