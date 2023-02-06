package ru.yandex.quasar.app.rcu.update

import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGattCharacteristic
import android.os.Handler
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.argumentCaptor
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock
import org.mockito.kotlin.never
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import ru.yandex.quasar.app.rcu.sender.RcuCommandSender
import ru.yandex.quasar.app.rcu.sender.RcuManager
import ru.yandex.quasar.app.rcu.update.RcuUpdater.SendingState
import ru.yandex.quasar.app.rcu.utils.toByteArray
import ru.yandex.quasar.fakes.FakeMetricaReporter
import java.nio.ByteOrder

class RcuUpdaterTest {
    private val mockDevice: BluetoothDevice = mock()
    private val mockRcuInfo: RcuInfo = mock()
    private val mockRcuImage: RcuImage = mock()
    private val mockRcuManager: RcuManager = mock()
    private val mockCommandSender: RcuCommandSender = mock()
    private val mockUpdateListener: RcuUpdateListener = mock()
    private val fakeMetricaReporter = FakeMetricaReporter()
    private val mockHandler: Handler = mock()
    private val inProgressStates = listOf(
        SendingState.SENDING_START_TRANSFER,
        SendingState.SENDING_IMAGE_INFO,
        SendingState.SENDING_IMAGE_BLOCKS
    )
    private val pausedStates = listOf(
        SendingState.WAITING_FOR_RECONNECT,
        SendingState.PAUSED,
        SendingState.STOPPED
    )

    private fun getAllStatesBut(vararg states: SendingState): List<SendingState> {
        val allStates = SendingState.values().toMutableList()
        allStates.removeAll(states)
        return allStates
    }

    @Before
    fun setUp() {
        whenever(mockRcuManager.getCommandSender(any())).thenReturn(mockCommandSender)
    }

    @Test
    fun when_rcuUpdaterCreated_then_updateStarted() {
        val rcuUpdater = createRcuUpdater(false)

        checkResume(rcuUpdater)
        assertEquals(1, fakeMetricaReporter.latencyPoints.size)
        assertEquals(RcuUpdater.TAG, fakeMetricaReporter.latencyPoints.first())
    }

    @Test
    fun given_updateInProgress_when_pauseUpdate_then_updatePaused() {
        val rcuUpdater = createRcuUpdater()

        for (state in inProgressStates) {
            rcuUpdater.sendingState = state

            rcuUpdater.pause()

            assertEquals(SendingState.PAUSED, rcuUpdater.sendingState)
            checkPause(true)
            clearInvocations()
        }
    }

    @Test
    fun given_updateInProgress_when_onRcuDisconnected_then_updateStopped() {
        val rcuUpdater = createRcuUpdater()

        for (state in inProgressStates) {
            rcuUpdater.sendingState = state

            rcuUpdater.onRcuDisconnected()

            assertEquals(SendingState.WAITING_FOR_RECONNECT, rcuUpdater.sendingState)
            checkPause(false)
            clearInvocations()
        }
    }

    @Test
    fun given_updateIsNotInProgress_when_pauseUpdate_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()
        for (state in pausedStates) {
            clearInvocations()
            rcuUpdater.sendingState = state

            rcuUpdater.pause()

            checkNothingHappens(rcuUpdater, state)
        }
    }

    @Test
    fun given_updateIsNotPaused_when_resumeUpdate_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()

        for (state in getAllStatesBut(SendingState.PAUSED)) {
            rcuUpdater.sendingState = state

            rcuUpdater.resume()

            checkNothingHappens(rcuUpdater, state)
            clearInvocations()
        }
    }

    @Test
    fun given_updatePaused_when_resumeUpdate_then_updateResumed() {
        val rcuUpdater = createRcuUpdater()
        rcuUpdater.sendingState = SendingState.PAUSED

        rcuUpdater.resume()

        checkResume(rcuUpdater)
    }

    @Test
    fun given_updateInNotInProgress_when_onRcuDisconnected_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()
        for (state in listOf(SendingState.WAITING_FOR_RECONNECT, SendingState.STOPPED)) {
            clearInvocations()
            rcuUpdater.sendingState = state

            rcuUpdater.onRcuDisconnected()

            checkNothingHappens(rcuUpdater, state)
        }
    }

    @Test
    fun given_updatePaused_when_onRcuDisconnected_then_waitForReconnect() {
        val rcuUpdater = createRcuUpdater()
        clearInvocations()
        rcuUpdater.sendingState = SendingState.PAUSED

        rcuUpdater.onRcuDisconnected()

        assertEquals(SendingState.WAITING_FOR_RECONNECT, rcuUpdater.sendingState)
        checkPause(false)
    }

    @Test
    fun given_anyState_when_destroy_then_updaterDestroyed() {
        val rcuUpdater = createRcuUpdater()
        for (state in SendingState.values()) {
            clearInvocations()
            rcuUpdater.sendingState = state

            rcuUpdater.destroy()

            checkDestroy(rcuUpdater)
        }
    }

    @Test
    fun given_anyStateButWaitingForReconnect_when_onRcuConnected_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()

        for (state in getAllStatesBut(SendingState.WAITING_FOR_RECONNECT)) {
            rcuUpdater.sendingState = state

            rcuUpdater.onRcuConnected()

            checkNothingHappens(rcuUpdater, state)
            clearInvocations()
        }
    }

    @Test
    fun given_updateWaitingForReconnect_when_onRcuConnected_then_updateResumed() {
        val rcuUpdater = createRcuUpdater()
        rcuUpdater.sendingState = SendingState.WAITING_FOR_RECONNECT

        rcuUpdater.onRcuConnected()

        checkResume(rcuUpdater)
    }

    @Test
    fun given_updateWaitingForReconnect_when_destroy_then_updaterDestroyed() {
        val rcuUpdater = createRcuUpdater()
        rcuUpdater.sendingState = SendingState.WAITING_FOR_RECONNECT

        rcuUpdater.destroy()

        checkDestroy(rcuUpdater)
    }

    @Test
    fun given_anyState_when_onUpdateResult_then_updateStopped() {
        val rcuUpdater = createRcuUpdater()

        for (state in SendingState.values()) {
            clearInvocations()
            rcuUpdater.sendingState = state

            sendUpdateResult(rcuUpdater, RcuUpdateState.OTA_COMPLETED_SUCCESSFULLY)

            assertEquals(SendingState.STOPPED, rcuUpdater.sendingState)
            verify(mockUpdateListener).onUpdateStateChanged(
                mockDevice, RcuUpdateState.OTA_COMPLETED_SUCCESSFULLY
            )
        }
    }

    @Test
    fun given_sendingStartTransfer_when_getImageInfoRequest_then_imageInfoSent() {
        val rcuUpdater = createRcuUpdater()
        rcuUpdater.sendingState = SendingState.SENDING_START_TRANSFER

        sendImageInfoRequest(rcuUpdater)

        assertEquals(SendingState.SENDING_IMAGE_INFO, rcuUpdater.sendingState)
        val expectedCommand = RcuOtaCommands.returnImageInfoCommand
        expectedCommand.payload = byteArrayOf(1)
        verify(mockCommandSender).send(expectedCommand)
    }

    @Test
    fun given_updaterDoesNotSendingBlocksOrImageInfo_when_getImageBlockRequest_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()
        for (state in getAllStatesBut(
            SendingState.SENDING_IMAGE_INFO,
            SendingState.SENDING_IMAGE_BLOCKS
        )) {
            rcuUpdater.sendingState = state

            sendImageBlockRequest(rcuUpdater, 0, 1)

            checkNothingHappens(rcuUpdater, state)
        }
    }

    @Test
    fun given_updaterDoesNotSendingBlocks_when_imageBlockWrote_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()
        for (state in getAllStatesBut(
            SendingState.SENDING_IMAGE_BLOCKS
        )) {
            rcuUpdater.sendingState = state

            onImageBlockWrote(rcuUpdater)

            checkNothingHappens(rcuUpdater, state)
        }
    }

    @Test
    fun given_updaterDoesNotSendingStartTransfer_when_getImageInfoRequest_then_nothingHappens() {
        val rcuUpdater = createRcuUpdater()
        for (state in getAllStatesBut(SendingState.SENDING_START_TRANSFER)) {
            clearInvocations()
            rcuUpdater.sendingState = state

            sendImageInfoRequest(rcuUpdater)

            checkNothingHappens(rcuUpdater, state)
        }
    }

    @Test
    fun given_sendingImageInfoOrImageBlocks_when_getImageBlockRequest_then_imageBlockSent() {
        val rcuUpdater = createRcuUpdater()

        for (state in listOf(SendingState.SENDING_IMAGE_INFO, SendingState.SENDING_IMAGE_BLOCKS)) {
            clearInvocations()
            rcuUpdater.sendingState = state

            whenever(mockRcuImage.getImageBlock(1)).thenReturn(byteArrayOf(1))
            whenever(mockRcuImage.totalBlocks).thenReturn(100)
            sendImageBlockRequest(rcuUpdater, 1, 1)

            val expectedCommand = RcuOtaCommands.sendImageBlock
            expectedCommand.payload = byteArrayOf(/* block number */ 1, 0, 0, /* block bytes */ 1)
            verify(mockCommandSender).send(expectedCommand)
            assertEquals(SendingState.SENDING_IMAGE_BLOCKS, rcuUpdater.sendingState)
        }
    }

    @Test
    fun given_sendingImageBlock_when_imageBlockWrote_then_sendNextImageBlock() {
        val rcuUpdater = createRcuUpdater()
        rcuUpdater.sendingState = SendingState.SENDING_IMAGE_BLOCKS

        // Send block request to update sending block number
        whenever(mockRcuImage.getImageBlock(1)).thenReturn(byteArrayOf(1))
        whenever(mockRcuImage.totalBlocks).thenReturn(100)
        sendImageBlockRequest(rcuUpdater, 1, 2)

        clearInvocations()
        whenever(mockRcuImage.getImageBlock(2)).thenReturn(byteArrayOf(2))
        onImageBlockWrote(rcuUpdater)

        val expectedCommand = RcuOtaCommands.sendImageBlock
        expectedCommand.payload = byteArrayOf(/* block number */ 2, 0, 0, /* block bytes */ 2)
        verify(mockCommandSender).send(expectedCommand)
        assertEquals(SendingState.SENDING_IMAGE_BLOCKS, rcuUpdater.sendingState)
    }

    @Test
    fun when_gotBadUpdateResult_then_sendError() {
        val rcuUpdater = createRcuUpdater()
        sendUpdateResult(rcuUpdater, RcuUpdateState.INVALID_IMAGE)
        verify(mockUpdateListener).onUpdateStateChanged(mockDevice, RcuUpdateState.INVALID_IMAGE)
        assertEquals(1, fakeMetricaReporter.errors.size)
        assertEquals(RcuUpdater.UPDATE_ERROR_EVENT, fakeMetricaReporter.errors.first().name)
    }

    @Test
    fun when_gotSuccessUpdateResult_then_sendSuccessEvent() {
        val rcuUpdater = createRcuUpdater()
        sendUpdateResult(rcuUpdater, RcuUpdateState.OTA_COMPLETED_SUCCESSFULLY)
        verify(mockUpdateListener).onUpdateStateChanged(
            mockDevice,
            RcuUpdateState.OTA_COMPLETED_SUCCESSFULLY
        )
        assertEquals(1, fakeMetricaReporter.events.size)
        assertEquals(RcuUpdater.UPDATE_SUCCESS_EVENT, fakeMetricaReporter.events.first().name)
    }

    @Test
    fun when_gotOtaAborted_then_retryUpdate() {
        val rcuUpdater = createRcuUpdater()
        sendUpdateResult(rcuUpdater, RcuUpdateState.RCU_ABORTED_OTA)
        assertEquals(1, fakeMetricaReporter.errors.size)
        assertEquals(RcuUpdater.UPDATE_ERROR_EVENT, fakeMetricaReporter.errors.first().name)
        checkResume(rcuUpdater)
    }

    @Test
    fun given_retriedUpdate_when_gotOtaAborted_then_doNotRetryUpdate() {
        val rcuUpdater = createRcuUpdater()
        // retry update
        for (i in 1..RcuUpdater.MAX_RETRIES) {
            sendUpdateResult(rcuUpdater, RcuUpdateState.RCU_ABORTED_OTA)
        }
        clearInvocations()

        sendUpdateResult(rcuUpdater, RcuUpdateState.RCU_ABORTED_OTA)
        assertEquals(1, fakeMetricaReporter.errors.size)
        assertEquals(RcuUpdater.UPDATE_ERROR_EVENT, fakeMetricaReporter.errors.first().name)
        checkNothingHappens(rcuUpdater, SendingState.STOPPED)
    }

    @Test
    fun when_sendTransferStart_then_postDelayedTimeout() {
        createRcuUpdater(false)
        verify(mockHandler).postDelayed(any(), eq(RcuUpdater.TIMEOUT_MS))
    }

    @Test
    fun when_sendImageInfo_then_postDelayedTimeout() {
        val rcuUpdater = createRcuUpdater()
        sendImageInfoRequest(rcuUpdater)
        verify(mockHandler).postDelayed(any(), eq(RcuUpdater.TIMEOUT_MS))
    }

    @Test
    fun when_timeout_then_updateStopped() {
        val rcuUpdater = createRcuUpdater(false)
        argumentCaptor<Runnable> {
            verify(mockHandler).postDelayed(capture(), eq(RcuUpdater.TIMEOUT_MS))
            val runnable = firstValue
            runnable.run()
        }
        assertEquals(rcuUpdater.sendingState, SendingState.STOPPED)
        verify(mockUpdateListener).onUpdateStateChanged(mockDevice, RcuUpdateState.TIMEOUT)
    }

    @Test
    fun when_imageBlockSent_then_updateProgress() {
        val rcuUpdater = createRcuUpdater(false)
        rcuUpdater.sendingState = SendingState.SENDING_IMAGE_BLOCKS

        whenever(mockRcuImage.getImageBlock(any())).thenReturn(byteArrayOf(1))
        whenever(mockRcuImage.totalBlocks).thenReturn(100)
        sendImageBlockRequest(rcuUpdater, 1, 10)

        for (i in 1..10) {
            verify(mockUpdateListener).onUpdateProgress(mockDevice, i)
            onImageBlockWrote(rcuUpdater)
        }
    }

    private fun createRcuUpdater(clear: Boolean = true): RcuUpdater {
        val updater = RcuUpdater(
            mockDevice,
            mockRcuInfo,
            mockRcuImage,
            mockRcuManager,
            mockUpdateListener,
            fakeMetricaReporter,
            mockHandler
        )
        if (clear) {
            clearInvocations()
        }
        return updater
    }

    private fun clearInvocations() {
        org.mockito.kotlin.clearInvocations(mockCommandSender, mockUpdateListener, mockHandler)
        fakeMetricaReporter.latencyPoints.clear()
        fakeMetricaReporter.latencies.clear()
        fakeMetricaReporter.events.clear()
        fakeMetricaReporter.errors.clear()
    }

    private fun checkNothingHappens(rcuUpdater: RcuUpdater, previousState: SendingState) {
        assertEquals(previousState, rcuUpdater.sendingState)
        assertEquals(0, fakeMetricaReporter.latencyPoints.size)
        assertEquals(0, fakeMetricaReporter.latencies.size)
        verify(mockCommandSender, never()).send(RcuOtaCommands.stopUpdateCommand)
        verify(mockUpdateListener, never()).onUpdateStateChanged(mockDevice, RcuUpdateState.PAUSED)
    }

    private fun checkResume(rcuUpdater: RcuUpdater) {
        assertEquals(SendingState.SENDING_START_TRANSFER, rcuUpdater.sendingState)

        verify(mockCommandSender).send(RcuOtaCommands.startImageTransferCommand)
        verify(mockUpdateListener).onUpdateStateChanged(mockDevice, RcuUpdateState.IN_PROGRESS)

        assertEquals(1, fakeMetricaReporter.latencies.size)
        assertEquals(RcuUpdater.TAG, fakeMetricaReporter.latencies.first().pointName)
        assertEquals(
            RcuUpdater.UPDATE_STARTED_EVENT,
            fakeMetricaReporter.latencies.first().eventName
        )
        assertFalse(fakeMetricaReporter.latencies.first().removePoint)
    }

    private fun checkPause(shouldSendStopUpdate: Boolean) {
        if (shouldSendStopUpdate) {
            verify(mockCommandSender).send(RcuOtaCommands.stopUpdateCommand)
        } else {
            verify(mockCommandSender, never()).send(any())
        }
        verify(mockUpdateListener).onUpdateStateChanged(mockDevice, RcuUpdateState.PAUSED)

        assertEquals(1, fakeMetricaReporter.latencies.size)
        assertEquals(RcuUpdater.TAG, fakeMetricaReporter.latencies.first().pointName)
        assertEquals(
            RcuUpdater.UPDATE_PAUSED_EVENT,
            fakeMetricaReporter.latencies.first().eventName
        )
        assertFalse(fakeMetricaReporter.latencies.first().removePoint)
    }

    private fun checkDestroy(rcuUpdater: RcuUpdater) {
        assertEquals(SendingState.STOPPED, rcuUpdater.sendingState)

        verify(mockCommandSender, never()).send(any())
        verify(mockUpdateListener, never()).onUpdateStateChanged(mockDevice, RcuUpdateState.PAUSED)

        assertEquals(1, fakeMetricaReporter.latencies.size)
        assertEquals(RcuUpdater.TAG, fakeMetricaReporter.latencies.first().pointName)
        assertEquals(
            RcuUpdater.UPDATE_ENDED_EVENT,
            fakeMetricaReporter.latencies.first().eventName
        )
        assertTrue(fakeMetricaReporter.latencies.first().removePoint)
    }

    private fun sendImageInfoRequest(rcuUpdater: RcuUpdater) {
        val characteristic: BluetoothGattCharacteristic = mock()
        whenever(characteristic.uuid).thenReturn(RcuOtaCommands.OTA_COMMANDS_CHARACTERISTIC_UUID)
        whenever(characteristic.value).thenReturn(
            byteArrayOf(
                RcuOtaCommands.COMMAND_HEADER,
                RcuOtaCommands.GET_IMAGE_INFO
            )
        )
        whenever(mockRcuImage.imageInfo).thenReturn(byteArrayOf(1))
        rcuUpdater.onCharacteristicChanged(mockDevice, characteristic)
    }

    private fun sendImageBlockRequest(rcuUpdater: RcuUpdater, blockNumber: Int, blockCount: Int) {
        val blockNumberArr =
            blockNumber.toByteArray(ByteOrder.LITTLE_ENDIAN).copyOfRange(0, 3)
        val blockSizeArr =
            (blockCount * RcuImage.IMAGE_BLOCK_SIZE).toByteArray(ByteOrder.LITTLE_ENDIAN)
                .copyOfRange(0, 2)
        val characteristic: BluetoothGattCharacteristic = mock()
        whenever(characteristic.uuid).thenReturn(RcuOtaCommands.OTA_IMAGE_TRANSFER_CHARACTERISTIC_UUID)
        whenever(characteristic.value).thenReturn(
            byteArrayOf(
                RcuOtaCommands.COMMAND_HEADER,
                *blockNumberArr,
                /* reserved */ 0,
                *blockSizeArr
            )
        )
        rcuUpdater.onCharacteristicChanged(mockDevice, characteristic)
    }

    private fun onImageBlockWrote(rcuUpdater: RcuUpdater) {
        val characteristic: BluetoothGattCharacteristic = mock()
        whenever(characteristic.uuid).thenReturn(RcuOtaCommands.OTA_IMAGE_TRANSFER_CHARACTERISTIC_UUID)
        rcuUpdater.onCharacteristicWrite(mockDevice, characteristic)
    }

    private fun sendUpdateResult(rcuUpdater: RcuUpdater, result: RcuUpdateState) {
        val characteristic: BluetoothGattCharacteristic = mock()
        whenever(characteristic.uuid).thenReturn(RcuOtaCommands.OTA_COMMANDS_CHARACTERISTIC_UUID)
        whenever(characteristic.value).thenReturn(
            byteArrayOf(
                RcuOtaCommands.COMMAND_HEADER,
                RcuOtaCommands.RETURN_UPGRADE_RESULT,
                result.code
            )
        )
        whenever(mockRcuImage.imageInfo).thenReturn(byteArrayOf(1))
        rcuUpdater.onCharacteristicChanged(mockDevice, characteristic)
    }
}
