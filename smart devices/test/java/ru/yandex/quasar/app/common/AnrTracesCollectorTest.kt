package ru.yandex.quasar.app.common

import android.util.Base64
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.app.configs.ExternalConfigObservable
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.app.configs.SystemConfig
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.fakes.FakeMetricaReporter
import ru.yandex.quasar.core.utils.Observable
import java.io.BufferedReader
import java.io.ByteArrayInputStream
import java.io.File
import java.io.InputStreamReader
import java.nio.file.Files
import java.util.zip.GZIPInputStream

@RunWith(RobolectricTestRunner::class)
class AnrTracesCollectorTest {
    private lateinit var anrDirectory: String
    private val fakeConfiguration = FakeConfiguration()
    private val fakeExecutor = FakeExecutorService()
    private val mockConfigObservable: ExternalConfigObservable = mock()
    private val fakeMetricaReporter = FakeMetricaReporter()
    private var anrTracesEnabled = false
    private lateinit var anrTracesCollector: AnrTracesCollector

    @Before
    fun setup() {
        val directory = Files.createTempDirectory("anr").toFile()
        directory.deleteOnExit()
        directory.setWritable(true)
        directory.setReadable(true)
        anrDirectory = directory.path

        val systemConfig: SystemConfig = mock()
        val stationConfig: StationConfig = mock()
        whenever(systemConfig.sendAnrTracesToMetrica()).thenAnswer { anrTracesEnabled }
        whenever(stationConfig.systemConfig).thenReturn(systemConfig)
        whenever(mockConfigObservable.current).thenReturn(stationConfig)

        val config = "{'common':{'anrTracesDirectory':'$anrDirectory'}}"
        fakeConfiguration.initialize(config)

        anrTracesCollector = AnrTracesCollector(
            fakeExecutor,
            mockConfigObservable,
            fakeMetricaReporter,
            fakeConfiguration
        )
        anrTracesCollector.start()
    }

    @After
    fun clearDirectory() {
        File(anrDirectory).delete()
    }

    private fun setAnrTraceEnabled(enabled: Boolean) {
        anrTracesEnabled = enabled
        updateConfig()
    }

    private fun updateConfig() {
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(mockConfigObservable).addObserver(capture())
            firstValue.update(mockConfigObservable.current)
        }
    }

    @Test
    fun when_anrDisabled_then_doNotSendEvents() {
        setAnrTraceEnabled(false)

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_anrEnabled_then_sendEvents() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        fakeExecutor.runAllJobs()
        assertEquals(1, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_disableAnr_then_stopSendingEvents() {
        setAnrTraceEnabled(true)
        setAnrTraceEnabled(false)

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_readEmptyFile_then_doNotSendEvent() {
        setAnrTraceEnabled(true)
        val filenames = listOf("anr_123.txt, trace_123, traces.txt")

        for (filename in filenames) {
            // create empty file
            File(anrDirectory, filename).createNewFile()
        }
        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_unknownPattern_then_doNotSendEvent() {
        setAnrTraceEnabled(true)

        val filenames = listOf("123.txt", "abc.txt", "not_a_trace", "trace.txt")
        for (filename in filenames) {
            val file = File(anrDirectory, filename)
            file.createNewFile()
            file.writeText("some text")
        }

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_knownPattern_then_sendEvent() {
        setAnrTraceEnabled(true)

        val filenames = listOf(
            "anr_123",
            "anr_2020-12-04-04-49-03-532",
            "trace_00",
            "trace_12.txt",
            "traces.txt"
        )
        for (filename in filenames) {
            val file = File(anrDirectory, filename)
            file.createNewFile()
            file.writeText("some text")
        }

        fakeExecutor.runAllJobs()
        assertEquals(filenames.size, fakeMetricaReporter.events.size)
    }


    @Test
    fun when_traceSent_then_traceCanBeDecoded() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val text = "trace\ntrace 1\n   abc  \n\n some trace \n"
        val file = File(anrDirectory, filename)
        file.createNewFile()
        file.writeText(text)

        fakeExecutor.runAllJobs()
        assertEquals(1, fakeMetricaReporter.events.size)
        val event = fakeMetricaReporter.events.first()
        assertEquals(file.path, event.mapData1!!["path"])
        val base64Trace = event.mapData1["trace"] as String
        val trace = Base64.decode(base64Trace, Base64.DEFAULT)

        ByteArrayInputStream(trace).use { bais ->
            GZIPInputStream(bais).use { gzis ->
                InputStreamReader(gzis).use { isReader ->
                    BufferedReader(isReader).use { reader ->
                        assertEquals(text, reader.readText())
                    }
                }

            }
        }
    }

    @Test
    fun when_largeFile_then_sendPart() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        val bytes = ByteArray(200 * 1024) { it.toByte() }
        for (i in 1..1000) {
            file.appendBytes(bytes)
        }
        fakeExecutor.runAllJobs()
        assertEquals(1, fakeMetricaReporter.events.size)
        val event = fakeMetricaReporter.events.first()
        val base64Trace = event.mapData1!!["trace"] as String
        val maxMetricaMessageSize = 175 * 1024
        assert(base64Trace.length < maxMetricaMessageSize)
    }

    @Test
    fun when_fileSent_then_deleteFile() {
        setAnrTraceEnabled(true)
        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        fakeExecutor.runAllJobs()
        assertFalse(file.exists())
    }

    @Test
    fun when_cannotDeleteFile_then_clearFile() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val directory = File(anrDirectory)
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        directory.setReadOnly()

        fakeExecutor.runAllJobs()
        assert(file.exists())
        assertEquals(0, file.length())
    }

    @Test
    fun when_cannotReadFile_then_deleteFile() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        file.setReadable(false)

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
        assertFalse(file.exists())
    }

    @Test
    fun when_newTraceAvailable_then_collectTrace() {
        setAnrTraceEnabled(true)
        // collect traces for the first time
        fakeExecutor.runAllJobs()
        fakeMetricaReporter.events.clear()

        val filename = "anr_123"
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        // collect traces again in 60 minutes
        fakeExecutor.runAllJobs()
        assertEquals(1, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_directoryIsNotExist_then_doNotSendTraces() {
        setAnrTraceEnabled(true)

        val directory = File(anrDirectory)
        directory.delete()

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }

    @Test
    fun when_cannotDeleteFile_then_doNotSendTraces() {
        setAnrTraceEnabled(true)

        val filename = "anr_123"
        val directory = File(anrDirectory)
        val file = File(anrDirectory, filename)
        file.writeText("some text")

        directory.setReadOnly()
        file.setReadOnly()

        fakeExecutor.runAllJobs()
        assertEquals(0, fakeMetricaReporter.events.size)
    }
}
