package ru.yandex.quasar.common.ble.main

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.common.ble.CharacteristicWriteStatus
import ru.yandex.quasar.common.ble.GattWriteSession

@RunWith(RobolectricTestRunner::class)
class GattWriteSessionTest {
    @Test
    fun test_writeSinglePacket() {
        // Arrange
        val bytes = byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        val session = GattWriteSession()

        // Act
        session.write(bytes)

        // Assert
        Assert.assertTrue(session.ready())
        Assert.assertEquals(byteArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9).toList(), session.getWrittenValue().toList())
    }

    @Test
    fun test_writeSeveralPackets() {
        // Arrange
        val session = GattWriteSession()

        // Act
        session.write(byteArrayOf(1, 0, 0, 0, 10, 0, 1))
        Assert.assertFalse(session.ready())
        session.write(byteArrayOf(2, 3, 4, 5, 6, 7, 8))
        Assert.assertFalse(session.ready())
        session.write(byteArrayOf(9))
        Assert.assertTrue(session.ready())

        // Assert
        Assert.assertEquals(byteArrayOf(0, 1, 2, 3, 4, 5, 6, 7, 8, 9).toList(), session.getWrittenValue().toList())
    }

    @Test
    fun test_whenWritesAreOverflowing_then_excessiveBytesAreIgnored() {
        // Arrange
        val session = GattWriteSession()

        // Act
        session.write(byteArrayOf(1, 0, 0, 0, 4, 0, 1))
        session.write(byteArrayOf(2, 3, 4, 5, 6, 7, 8))

        // Assert
        Assert.assertTrue(session.ready())
        Assert.assertEquals(byteArrayOf(0, 1, 2, 3).toList(), session.getWrittenValue().toList())
    }

    @Test
    fun given_sessionIsFinished_when_writtenAgain_then_writeIsIgnored() {
        // Arrange
        val session = GattWriteSession()

        session.write(byteArrayOf(1, 0, 0, 0, 4, 0, 1))
        session.write(byteArrayOf(2, 3, 4, 5, 6, 7, 8))

        //session is ready here

        // Act
        session.write(byteArrayOf(9, 10, 11, 12, 13, 14, 15))


        // Assert
        Assert.assertTrue(session.ready())
        Assert.assertEquals(byteArrayOf(0, 1, 2, 3).toList(), session.getWrittenValue().toList())
    }

    @Test
    fun given_protocolVersionIsTooHigh_when_write_then_errorIsReturned() {
        // Arrange
        val bytes = byteArrayOf(2, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        val session = GattWriteSession()

        // Act
        val sessionResult = session.write(bytes)

        // Assert
        Assert.assertFalse(sessionResult.ok)
        Assert.assertEquals(sessionResult.status, CharacteristicWriteStatus.UNSUPPORTED_PROTOCOL)
    }
}
