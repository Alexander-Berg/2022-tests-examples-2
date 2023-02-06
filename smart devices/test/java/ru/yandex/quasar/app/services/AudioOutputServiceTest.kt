package ru.yandex.quasar.app.services

import org.junit.Assert.*
import com.fasterxml.jackson.databind.ObjectMapper
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.inOrder
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.core.MetricaReporter
import ru.yandex.quasar.TestUtils.toJsonQuotes
import ru.yandex.quasar.app.alice.AliceStateObservable
import ru.yandex.quasar.app.common.AlarmPlayingObservable
import ru.yandex.quasar.app.common.AudioOutputObservable
import ru.yandex.quasar.app.common.ScreenStateObservable
import ru.yandex.quasar.app.common.SimplePlayerStateObservable
import ru.yandex.quasar.app.configs.ExternalConfigObservable
import ru.yandex.quasar.app.configs.StationConfig
import ru.yandex.quasar.app.video.hdmi.HdmiObservable
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.fakes.FakeOutputDeviceSwitcher
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.ModelObjects.UserConfig
import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.core.utils.Observable


@RunWith(RobolectricTestRunner::class)
class AudioOutputServiceTest {

    private lateinit var aliceStateObservable: AliceStateObservable
    private lateinit var audioOutputObservable: AudioOutputObservable
    private lateinit var hdmiObservable: HdmiObservable
    private lateinit var alarmPlayingObservable: AlarmPlayingObservable
    private lateinit var screenStateObservable: ScreenStateObservable
    private lateinit var simplePlayerStateObservable: SimplePlayerStateObservable
    private lateinit var userConfigObservable: ExternalConfigObservable
    private lateinit var audioDeviceSwitcher: OutputDeviceSwitcher
    private lateinit var service: AudioOutputService
    private lateinit var metricaReporter: MetricaReporter
    private lateinit var stationConfigObserver: Observable.Observer<StationConfig>
    private lateinit var aliceStateObserver: Observable.Observer<ModelObjects.AliceState>

    private val objectMapper = ObjectMapper()

    @Before
    fun setUp() {
        aliceStateObservable = mock()
        audioOutputObservable = AudioOutputObservable()
        hdmiObservable = HdmiObservable()
        alarmPlayingObservable = mock()
        screenStateObservable = ScreenStateObservable()
        simplePlayerStateObservable = SimplePlayerStateObservable()
        userConfigObservable = mock()
        audioDeviceSwitcher = FakeOutputDeviceSwitcher(audioOutputObservable)
        metricaReporter = mock()

        service = AudioOutputService(
            aliceStateObservable,
            audioOutputObservable,
            hdmiObservable,
            userConfigObservable,
            simplePlayerStateObservable,
            screenStateObservable,
            alarmPlayingObservable,
            audioDeviceSwitcher,
            metricaReporter
        )

        service.onCreate()
        argumentCaptor<Observable.Observer<StationConfig>> {
            verify(userConfigObservable).addObserver(capture())
            stationConfigObserver = firstValue
        }
        argumentCaptor<Observable.Observer<ModelObjects.AliceState>> {
            verify(aliceStateObservable).addObserver(capture())
            aliceStateObserver = firstValue
        }

    }

    private fun setHdmiConnected(connected: Boolean) {
        hdmiObservable.receiveValue(connected)
    }

    private fun setVideoScreen() {
        val screenState = ModelObjects.AppState.ScreenState.newBuilder().setScreenType(ModelObjects.AppState.ScreenType.VIDEO_PLAYER).build()
        screenStateObservable.receiveValue(screenState)
    }

    private fun setVideoPlaying(value: Boolean) {
        val simplePlayerState = QuasarProto.SimplePlayerState.newBuilder().setHasPause(value).build()
        simplePlayerStateObservable.receiveValue(simplePlayerState)
    }

    private fun setConfig(config: TestConfig) {
        setHdmiConnected(config.hdmiConnected)
        setVideoScreen()
        setUserConfig(config)
        setAliceState()
        setVideoPlaying(config.videoPlaying)
    }

    private fun setUserConfig(config: TestConfig) {
        val configuration = FakeConfiguration()
        configuration.initialize(toJsonQuotes("{'common': {'deviceType': 'yandexstation'}, 'aliced':{'experiments':[]}, 'metricad':{'port': 9887}}"));
        val configStr = "{'account_config': {'contentAccess': 'foo', 'spotter': 'yandex'}, 'device_config': {'hdmiAudio': ${config.hdmiAudioPP}}, 'system_config': {'logHttpTraffic': true, 'turnTvOnOffEnabled': true, 'hdmiAudioForVideoOnly': ${config.hdmiAudioForVideoOnly}, 'hdmiAudioEnabled': ${config.hdmiAudioEnabled}, 'forceHdmiAudio': ${config.hdmiAudioQuasmodrom}}}"
        val userConfig = UserConfig
            .newBuilder()
            .setConfig(toJsonQuotes(configStr))
            .setGroupConfig("{}")
            .setPassportUid("123")
            .build()

        val stationConfig = StationConfig.fromUserConfigUpdate(userConfig, objectMapper, configuration)
        stationConfigObserver.update(stationConfig)
    }

    private fun setAliceState() {
        val aliceState = ModelObjects.AliceState.newBuilder().setState(ModelObjects.AliceState.State.IDLE).build()
        aliceStateObserver.update(aliceState)
    }

    @Test
    fun testHdmiAudioEnabledFlag() {
        setConfig(TestConfig(videoPlaying = true, hdmiAudioPP = true))
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.currentDevice)

        setConfig(TestConfig(videoPlaying = true, hdmiAudioPP = true, hdmiAudioEnabled = false))
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.currentDevice)

        inOrder(metricaReporter) {
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "1")
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
        }
    }

    @Test
    fun testHdmiReturnsBackAfterVideoPlayerStop() {
        setConfig(TestConfig(videoPlaying = true, hdmiAudioPP = true))
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.currentDevice)

        setConfig(TestConfig(videoPlaying = false, hdmiAudioPP = true))
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.currentDevice)

        inOrder(metricaReporter) {
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "1")
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
        }
    }

    @Test
    fun testSpeakerAudioWhenBasicSettings() {
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.SPEAKER, audioOutputObservable.current!!.currentDevice)
        inOrder(metricaReporter) {
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
        }
    }

    @Test
    fun testAudioOutputSwitched() {
        setConfig(TestConfig(hdmiAudioPP = true))

        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.switchingTo)
        assertEquals(ModelObjects.AudioOutputDeviceState.AudioOutputDeviceType.HDMI, audioOutputObservable.current!!.currentDevice)
        inOrder(metricaReporter) {
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "0")
            metricaReporter.putAppEnvironmentValue("is_hdmi_audio_route", "1")
        }
    }

    data class TestConfig(
        val hdmiAudioPP: Boolean = false,
        val hdmiAudioQuasmodrom: Boolean = false,
        val hdmiAudioForVideoOnly: Boolean = true,
        val hdmiAudioEnabled: Boolean = true,
        val videoPlaying: Boolean = true,
        val hdmiConnected: Boolean = true)
}
