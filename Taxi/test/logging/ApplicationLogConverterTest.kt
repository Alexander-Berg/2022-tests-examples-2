package logging

import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.classic.spi.ThrowableProxyUtil
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import ru.yandex.taxi.crm.masshire.search.logging.AccessLogInterceptor
import ru.yandex.taxi.crm.masshire.search.logging.ApplicationLogConverter
import ru.yandex.taxi.crm.masshire.search.logging.GrpcMDC
import ru.yandex.taxi.crm.masshire.search.logging.getOrNull
import ru.yandex.taxi.proto.crm.masshire.ApplicationLogMessage

private const val CONTEXT_UTILS = "ru.yandex.taxi.crm.masshire.search.logging.ContextUtilsKt"
private const val THROWABLE_PROXY_UTIL = "ch.qos.logback.classic.spi.ThrowableProxyUtil"

internal class ApplicationLogConverterTest {
    private val event = mockk<ILoggingEvent>(relaxed = true)
    private val converter = ApplicationLogConverter()

    private fun convert(): ApplicationLogMessage =
        ApplicationLogMessage.parseFrom(converter.convert(event))

    @BeforeEach
    fun setup() {
        every { event.throwableProxy } returns null
    }

    @AfterEach fun teardown() = unmockkAll()

    @Test
    fun `given no threadName won't set thread`() {
        every { event.threadName } returns null
        assertEquals("", convert().thread)
    }

    @Test
    fun `given threadName sets thread`() {
        every { event.threadName } returns "ThreadName"
        assertEquals("ThreadName", convert().thread)
    }

    @Test
    fun `given no level won't set level`() {
        every { event.level } returns null
        assertEquals("", convert().level)
    }

    @Test
    fun `given level sets level`() {
        every { event.level.toString() } returns "LogLevel"
        assertEquals("LogLevel", convert().level)
    }

    @Test
    fun `given no loggerName won't set logger`() {
        every { event.loggerName } returns null
        assertEquals("", convert().logger)
    }

    @Test
    fun `given loggerName sets logger`() {
        every { event.loggerName } returns "LoggerName"
        assertEquals("LoggerName", convert().logger)
    }

    @Test
    fun `given no formattedMessage won't set message`() {
        every { event.formattedMessage } returns null
        assertEquals("", convert().message)
    }

    @Test
    fun `given formattedMessage sets message`() {
        every { event.formattedMessage } returns "Message"
        assertEquals("Message", convert().message)
    }

    @Test
    fun `given formattedMessage with client_secret masks secret`() {
        every { event.formattedMessage } returns "https://hh.ru?client_secret=SOME_SECRET"
        assertEquals("https://hh.ru?client_secret=<masked>", convert().message)
    }

    @Test
    fun `given formattedMessage with cursor masks cursor`() {
        every { event.formattedMessage } returns """{"cursor":"123454321"}"""
        assertEquals("""{"cursor":"<masked>"}""", convert().message)
    }

    @Test
    fun `given no GrpcMDC won't set requestId`() {
        mockkStatic(CONTEXT_UTILS)
        every { GrpcMDC.KEY.getOrNull() } returns null
        assertEquals("", convert().requestId)
    }

    @Test
    fun `given GrpcMDC without request id won't set requestId`() {
        mockkStatic(CONTEXT_UTILS)
        every { GrpcMDC.KEY.getOrNull() } returns GrpcMDC()
        assertEquals("", convert().requestId)
    }

    @Test
    fun `given GrpcMDC with request id sets requestId`() {
        mockkStatic(CONTEXT_UTILS)
        every { GrpcMDC.KEY.getOrNull() } returns
            GrpcMDC().set(AccessLogInterceptor.REQUEST_ID_KEY, "42")
        assertEquals("42", convert().requestId)
    }

    @Test
    fun `given no mdcPropertyMap won't fill mdc`() {
        every { event.mdcPropertyMap } returns null
        assertTrue(convert().mdcMap.isEmpty())
    }

    @Test
    fun `given mdcPropertyMap fills mdc`() {
        every { event.mdcPropertyMap } returns mapOf("something" to "42")
        assertEquals(1, convert().mdcMap.size)
        assertEquals("42", convert().mdcMap["something"])
    }

    @Test
    fun `given no throwableProxy won't set stacktrace`() {
        every { event.throwableProxy } returns null
        assertEquals("", convert().stacktrace)
    }

    @Test
    fun `given throwableProxy sets stacktrace`() {
        mockkStatic(THROWABLE_PROXY_UTIL)
        every { event.throwableProxy } returns mockk()
        every { ThrowableProxyUtil.asString(any()) } returns "stacktrace"
        assertEquals("stacktrace", convert().stacktrace)
    }

    @Test
    fun `given throwableProxy with client_secret masks secret`() {
        mockkStatic(THROWABLE_PROXY_UTIL)
        every { event.throwableProxy } returns mockk()
        every { ThrowableProxyUtil.asString(any()) } returns "\n\tError: client_secret=SECRET\n\t"
        assertEquals("\n\tError: client_secret=<masked>\n\t", convert().stacktrace)
    }
}
