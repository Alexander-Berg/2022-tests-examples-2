package ru.yandex.quasar.app.services.bluetooth

import android.bluetooth.BluetoothA2dp
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothDevice.EXTRA_DEVICE
import android.bluetooth.BluetoothProfile
import android.content.Context
import android.content.Intent
import android.media.MediaMetadata
import android.media.session.PlaybackState
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.ArgumentMatchers
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.reset
import org.mockito.kotlin.spy
import org.mockito.kotlin.times
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadow.api.Shadow
import ru.yandex.quasar.app.services.AliceAudioFocusHandler
import ru.yandex.quasar.fakes.FakeConfiguration
import ru.yandex.quasar.fakes.FakeExecutorService
import ru.yandex.quasar.fakes.FakeQuasarConnector
import ru.yandex.quasar.protobuf.ModelObjects
import ru.yandex.quasar.protobuf.QuasarProto
import ru.yandex.quasar.protobuf.YandexIO
import ru.yandex.quasar.shadows.ShadowMediaBrowser
import ru.yandex.quasar.shadows.ShadowMediaController
import ru.yandex.quasar.transport.QuasarConnector
import ru.yandex.quasar.transport.QuasarServer
import java.lang.reflect.Method

@RunWith(RobolectricTestRunner::class)
@Config(shadows = [ShadowMediaBrowser::class, ShadowMediaController::class])
class BluetoothCustomServiceTest {
    private lateinit var bluetoothCustomService: BluetoothCustomService
    private var context: Context = mock()
    private var bluetoothAdapterMock: BluetoothAdapter = mock()
    private val bluetoothProfileMock: BluetoothProfile = mock()
    private val bluetoothServerMock: QuasarServer = mock()
    private val brickdConnectorMock: QuasarConnector = FakeQuasarConnector()
    private val aliceAudioFocusHandlerMock: AliceAudioFocusHandler = mock()
    private val disconnector: Disconnector = mock()
    private val scheduledExecutorService = FakeExecutorService()

    private fun <T> anyObject(): T = ArgumentMatchers.any<T>()

    @Before
    fun setUp() {
        whenever(bluetoothAdapterMock.state).thenReturn(BluetoothAdapter.STATE_ON)
        whenever(bluetoothAdapterMock.isEnabled).thenReturn(true)
        whenever(bluetoothProfileMock.connectedDevices).thenReturn(listOf())

        val config = FakeConfiguration()
        config.initialize("{'bluetoothd': {'player': {'a2dpNeedsConfirmation': true, 'enabled': true }}}")

        bluetoothCustomService = BluetoothCustomService(
                context,
                config,
                mock(),
                bluetoothServerMock,
                brickdConnectorMock,
                bluetoothAdapterMock,
                aliceAudioFocusHandlerMock,
                disconnector,
                scheduledExecutorService
        )
        bluetoothCustomService.start()

        val (listenerCaptor, profileCaptor) = argumentCaptor<BluetoothProfile.ServiceListener, Int>()
        verify(bluetoothAdapterMock, times(2)).getProfileProxy(any(), listenerCaptor.capture(), profileCaptor.capture())
        listenerCaptor.firstValue.onServiceConnected(profileCaptor.firstValue, bluetoothProfileMock)
        listenerCaptor.secondValue.onServiceConnected(profileCaptor.secondValue, bluetoothProfileMock)

        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING
                        )
                ).build()
        )
    }

    private fun unbrick() {
        brickdConnectorMock.receiveValue(QuasarProto.QuasarMessage.newBuilder().setBrickStatus(ModelObjects.BrickStatus.NOT_BRICK).build())
    }

    private fun shortUnbrick() {
        bluetoothCustomService.handleQuasarMessage(QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setUnlockBrickedBt(
                        ModelObjects.EmptyMessage.getDefaultInstance()
                )
        ).build(), mock())
    }

    private fun brick() {
        brickdConnectorMock.receiveValue(QuasarProto.QuasarMessage.newBuilder().setBrickStatus(ModelObjects.BrickStatus.BRICK).build())
    }

    private fun connectToDevice() {
        val connectionIntent = Intent(BluetoothConstants.CONNECTION_STATE_CHANGE_ACTION)
        connectionIntent.putExtra(BluetoothProfile.EXTRA_STATE, BluetoothConstants.STATE_CONNECTED)
        connectionIntent.putExtra(BluetoothProfile.EXTRA_PREVIOUS_STATE, BluetoothConstants.STATE_DISCONNECTED)
        connectionIntent.putExtra(EXTRA_DEVICE, mock() as BluetoothDevice)
        bluetoothCustomService.bluetoothStateReceiver.onReceive(context, connectionIntent)
    }

    private fun startPlaybackViaAvrcp() {
        val playingPlaybackStateMock: PlaybackState = mock()
        whenever(playingPlaybackStateMock.state).thenReturn(PlaybackState.STATE_PLAYING)
        bluetoothCustomService.controllerCallback.onPlaybackStateChanged(playingPlaybackStateMock)
    }

    private fun pausePlaybackViaAvrcp() {
        val pausedPlaybackStateMock: PlaybackState = mock()
        whenever(pausedPlaybackStateMock.state).thenReturn(PlaybackState.STATE_PAUSED)
        bluetoothCustomService.controllerCallback.onPlaybackStateChanged(pausedPlaybackStateMock)
    }

    private fun pausePlaybackViaA2dp() {
        val playbackIntent = Intent(BluetoothConstants.AUDIO_STATE_CHANGE_ACTION)
        playbackIntent.putExtra(BluetoothProfile.EXTRA_STATE, BluetoothConstants.AUDIO_NOT_PLAYING)
        playbackIntent.putExtra(BluetoothProfile.EXTRA_PREVIOUS_STATE, BluetoothConstants.AUDIO_PLAYING)
        playbackIntent.putExtra(EXTRA_DEVICE, mock() as BluetoothDevice)
        bluetoothCustomService.bluetoothStateReceiver.onReceive(context, playbackIntent)
    }

    private fun startPlaybackViaA2dp() {
        val playbackIntent = Intent(BluetoothConstants.AUDIO_STATE_CHANGE_ACTION)
        playbackIntent.putExtra(BluetoothProfile.EXTRA_STATE, BluetoothConstants.AUDIO_PLAYING)
        playbackIntent.putExtra(BluetoothProfile.EXTRA_PREVIOUS_STATE, BluetoothConstants.AUDIO_NOT_PLAYING)
        playbackIntent.putExtra(EXTRA_DEVICE, mock() as BluetoothDevice)
        bluetoothCustomService.bluetoothStateReceiver.onReceive(context, playbackIntent)
    }

    @Test
    fun test_disconnectMethodExists_and_canBeInvoked() {
        // Arrange
        val device = Shadow.newInstanceOf(BluetoothDevice::class.java)
        val profile = Shadow.newInstanceOf(BluetoothA2dp::class.java)

        // Act
        val method: Method = profile.javaClass.getMethod("disconnect", device.javaClass)
        method.invoke(profile, device)
    }

    @Test
    fun when_deviceIsConnected_then_sinkEventIsSent() {
        // Act
        unbrick()
        connectToDevice()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setConnectionEvent(
                                ModelObjects.BtConnectionEvent.newBuilder().setConnectionEvent(
                                        ModelObjects.BtConnection.CONNECTED
                                )
                        )
                ).build()
        )
    }

    @Test
    fun when_deviceIsDisconnected_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()

        // Act
        val connectionIntent = Intent(BluetoothConstants.CONNECTION_STATE_CHANGE_ACTION)
        connectionIntent.putExtra(BluetoothProfile.EXTRA_STATE, BluetoothConstants.STATE_DISCONNECTED)
        connectionIntent.putExtra(BluetoothProfile.EXTRA_PREVIOUS_STATE, BluetoothConstants.STATE_CONNECTED)
        connectionIntent.putExtra(EXTRA_DEVICE, mock() as BluetoothDevice)
        bluetoothCustomService.bluetoothStateReceiver.onReceive(context, connectionIntent)

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setConnectionEvent(
                                ModelObjects.BtConnectionEvent.newBuilder().setConnectionEvent(
                                        ModelObjects.BtConnection.DISCONNECTED
                                )
                        ).setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING
                        )
                ).build()
        )
    }


    @Test
    fun when_playbackIsStartedViaAvrcp_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        // Act
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun when_playbackIsPausedViaAvrcp_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()

        reset(bluetoothServerMock)

        // Act
        pausePlaybackViaAvrcp()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING)
                ).build()
        )
    }

    @Test
    fun when_playbackIsStartedViaA2dp_then_sinkEventIsNotSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        // Act
        startPlaybackViaA2dp()

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun given_playbackIsStartedViaA2dp_when_playbackIsConfirmedViaAvrcp_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        startPlaybackViaA2dp()

        // Act
        val playbackStateMock: PlaybackState = mock()
        whenever(playbackStateMock.state).thenReturn(PlaybackState.STATE_PLAYING)
        bluetoothCustomService.controllerCallback.onPlaybackStateChanged(playbackStateMock)

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun given_playbackIsStartedViaA2dp_when_severalSecondsPass_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        startPlaybackViaA2dp()

        // Act
        scheduledExecutorService.runAllJobs()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun given_playbackIsStartedViaA2dp_when_playbackIsPausedViaA2dp_and_severalSecondsPass_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        startPlaybackViaA2dp()

        // Act
        pausePlaybackViaA2dp()

        scheduledExecutorService.runAllJobs()

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun when_playbackIsPausedViaA2dp_then_sinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(bluetoothServerMock)

        startPlaybackViaA2dp()

        scheduledExecutorService.runAllJobs() // wait 5 seconds for confirmation

        // Act
        pausePlaybackViaA2dp()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING
                        )
                ).build()
        )
    }

    @Test
    fun when_playbackPositionIsSetViaAvrcp_then_sinkEventWithMetainfoIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val playingPlaybackStateMock: PlaybackState = mock()
        whenever(playingPlaybackStateMock.state).thenReturn(PlaybackState.STATE_PLAYING)
        whenever(playingPlaybackStateMock.position).thenReturn(424242)
        bluetoothCustomService.controllerCallback.onPlaybackStateChanged(playingPlaybackStateMock)

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setBluetoothTrackMetaInfo(
                                ModelObjects.BluetoothTrackMetaInfo.newBuilder().setCurrPosMs(424242)
                        )
                ).build()
        )
    }

    @Test
    fun when_artistAndTitleAreSetViaAvrcp_then_sinkEventWithMetainfoIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val mediaMetadataMock: MediaMetadata = mock()
        whenever(mediaMetadataMock.containsKey(any())).thenAnswer { answer ->
            val key = answer.arguments[0] as String?
            return@thenAnswer key == MediaMetadata.METADATA_KEY_ARTIST || key == MediaMetadata.METADATA_KEY_TITLE
        }
        whenever(mediaMetadataMock.getString(any())).thenAnswer { answer ->
            val key = answer.arguments[0] as String?
            if (key == MediaMetadata.METADATA_KEY_ARTIST) {
                return@thenAnswer "Some Artist"
            } else if (key == MediaMetadata.METADATA_KEY_TITLE) {
                return@thenAnswer "Some Song"
            }

            throw IllegalArgumentException()
        }
        bluetoothCustomService.controllerCallback.onMetadataChanged(mediaMetadataMock)

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setBluetoothTrackMetaInfo(
                                ModelObjects.BluetoothTrackMetaInfo.newBuilder()
                                        .setArtist("Some Artist")
                                        .setTitle("Some Song")
                                        .setCurrPosMs(0)
                        )
                ).build()
        )
    }

    @Test
    fun when_visibilityStartRequestIsReceived_then_visibilityIsSet() {
        // Act
        val setVisibilityMsg = QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setSinkRequest(
                        ModelObjects.BluetoothSinkRequest.newBuilder().setSetVisibility(
                                ModelObjects.BluetoothSinkRequest.VisibilityRequest.newBuilder()
                                        .setVisibility(ModelObjects.BluetoothVisibility.CONNECTABLE_DISCOVERABLE)
                                        .setTimeout(300)
                        )
                )
        ).build()

        bluetoothCustomService.handleQuasarMessage(setVisibilityMsg, mock())

        // Assert
        val discoverableIntentStation1 = Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE)
        discoverableIntentStation1.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300)
        discoverableIntentStation1.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        argumentCaptor<Intent> {
            verify(context).startActivity(capture())
            assertTrue(firstValue.filterEquals(discoverableIntentStation1))
        }

        val discoverableIntentStation2 = Intent(BluetoothConstants.DISCOVERABLE_ON_ACTION)
        discoverableIntentStation2.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300)
        argumentCaptor<Intent> {
            verify(context).sendBroadcast(capture())
            assertTrue(firstValue.filterEquals(discoverableIntentStation2))
        }
    }

    @Test
    fun when_playCommandsIsReceived_then_mediaControllerIsInvoked() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setSinkRequest(
                        ModelObjects.BluetoothSinkRequest.newBuilder().setPlay(
                                ModelObjects.EmptyMessage.getDefaultInstance()
                        )
                )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(bluetoothCustomService.controller.transportControls).play()
    }

    @Test
    fun when_pauseCommandsIsReceived_then_mediaControllerIsInvoked() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setSinkRequest(
                        ModelObjects.BluetoothSinkRequest.newBuilder().setPause(
                                ModelObjects.EmptyMessage.getDefaultInstance()
                        )
                )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(bluetoothCustomService.controller.transportControls).pause()
    }

    @Test
    fun when_nextCommandsIsReceived_then_mediaControllerIsInvoked() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setSinkRequest(
                        ModelObjects.BluetoothSinkRequest.newBuilder().setNext(
                                ModelObjects.EmptyMessage.getDefaultInstance()
                        )
                )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(bluetoothCustomService.controller.transportControls).skipToNext()
    }

    @Test
    fun when_previousCommandsIsReceived_then_mediaControllerIsInvoked() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setBluetoothRequest(
                ModelObjects.BluetoothRequest.newBuilder().setSinkRequest(
                        ModelObjects.BluetoothSinkRequest.newBuilder().setPrev(
                                ModelObjects.BluetoothPrevRequest.getDefaultInstance()
                        )
                )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(bluetoothCustomService.controller.transportControls).skipToPrevious()
    }

    @Test
    fun when_freeFocusCommandsIsReceived_then_audioManagerIsUsed() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setMediaRequest(
                ModelObjects.MediaRequest.newBuilder()
                        .setFreeAudioFocus(
                                ModelObjects.EmptyMessage.getDefaultInstance()
                        )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(aliceAudioFocusHandlerMock).requestAudioFocus()
    }

    @Test
    fun when_takeFocusCommandsIsReceived_then_audioManagerIsUsed() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        val msg = QuasarProto.QuasarMessage.newBuilder().setMediaRequest(
                ModelObjects.MediaRequest.newBuilder()
                        .setTakeAudioFocus(
                                ModelObjects.EmptyMessage.getDefaultInstance()
                        )
        ).build()

        bluetoothCustomService.handleQuasarMessage(msg, mock())

        // Assert
        verify(aliceAudioFocusHandlerMock).abandonAudioFocus()
    }

    @Test
    fun given_deviceIsBricked_when_phoneConnects_then_a2dpDisconnects() {
        // Arrange
        /* Device is bricked on start */
        reset(disconnector)

        // Act
        connectToDevice()

        // Assert
        verify(disconnector).disconnectFromA2dpSinkProfile(anyObject())
    }

    @Test
    fun given_deviceIsNotBrickedAndPhoneIsConnected_when_deviceIsBricked_then_a2dpDisconnects() {
        // Arrange
        unbrick()
        connectToDevice()
        reset(disconnector)

        // Act
        brick()

        // Assert
        verify(disconnector).disconnectFromA2dpSinkProfile(anyObject())
    }

    @Test
    fun given_deviceIsBricked_when_musicIsStarted_then_sinkEventsAreNotSent() {
        // Arrange
        unbrick()
        connectToDevice()
        brick()

        // Act
        startPlaybackViaAvrcp()

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
    }

    @Test
    fun given_musicIsPlaying_when_deviceIsBricked_then_pauseSinkEventIsSent() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()
        reset(bluetoothServerMock)

        // Act
        brick()


        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING
                        )
                ).build())
    }

    @Test
    fun given_musicIsPlaying_when_deviceIsBricked_then_a2dpIsDisconnected() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        reset(disconnector)

        // Act
        brick()


        // Assert
        verify(disconnector).disconnectFromA2dpSinkProfile(anyObject())
    }

    @Test
    fun given_deviceIsBricked_when_shortUnbrickMessageArrives_then_deviceUnbricks() {
        // Arrange
        connectToDevice()
        shortUnbrick()

        // Act
        startPlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
    }

    @Test
    fun given_deviceIsShortUnbricked_when_shortBrickPeriodTimeouts_then_deviceBricksAgain() {
        // Arrange
        shortUnbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()
        reset(bluetoothServerMock)
        reset(disconnector)

        // Act
        scheduledExecutorService.runAllJobs()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.NOT_PLAYING
                        )
                ).build())
        verify(disconnector).disconnectFromA2dpSinkProfile(anyObject())
    }

    @Test
    fun given_shortUnbrickTimedOut_when_shortUnbrickSecondTime_then_deviceIsNotUnbricked() {
        // Arrange
        shortUnbrick()
        scheduledExecutorService.runAllJobs()
        reset(disconnector)
        reset(bluetoothServerMock)

        // Act
        shortUnbrick()
        connectToDevice()
        startPlaybackViaAvrcp()

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
        verify(disconnector).disconnectFromA2dpSinkProfile(anyObject())
    }

    @Test
    fun given_deviceIsPlaying_and_pausedByAvrcp_when_startedAgain_then_bluetoothStateIsPlaying() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()
        pausePlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        startPlaybackViaAvrcp()
        scheduledExecutorService.runAllJobs()

        // Assert
        verify(bluetoothServerMock).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
    }

    @Test
    fun given_deviceIsPlaying_and_pausedByAvrcp_when_wait5Seconds_then_bluetoothStateIsStillNotPlaying() {
        // Arrange
        unbrick()
        connectToDevice()
        startPlaybackViaAvrcp()
        startPlaybackViaA2dp()
        pausePlaybackViaAvrcp()
        reset(bluetoothServerMock)

        // Act
        scheduledExecutorService.runAllJobs()

        // Assert
        verify(bluetoothServerMock, never()).sendToAll(
                QuasarProto.QuasarMessage.newBuilder().setBluetoothSinkEvent(
                        ModelObjects.BluetoothSinkEvent.newBuilder().setAudioEvent(
                                ModelObjects.BluetoothSinkEvent.BtSinkAudioEvent.PLAYING
                        )
                ).build())
    }
}
