package ru.yandex.quasar.common.ble.main

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.common.ble.GattReadSession

@RunWith(RobolectricTestRunner::class)
class GattReadSessionTest {
    @Test
    fun test_readSinglePacket() {
        // Arrange
        val bytes = ByteArray(10) { i -> i.toByte() }
        val session = GattReadSession(bytes, 20, 512, true)

        // Act
        val chunk = session.read()

        // Assert
        Assert.assertEquals(byteArrayOf(1, 0, 0, 0, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9).toList(), chunk.toList())
    }

    @Test
    fun test_severalPackets() {
        // Arrange
        val bytes = ByteArray(10) { i -> i.toByte() }
        val session = GattReadSession(bytes, 7, 512, true)

        // Act
        val chunk1 = session.read()
        val chunk2 = session.read()
        val chunk3 = session.read()

        // Assert
        Assert.assertEquals(byteArrayOf(1, 0, 0, 0, 10, 0, 1).toList(), chunk1.toList())
        Assert.assertEquals(byteArrayOf(2, 3, 4, 5, 6, 7, 8).toList(), chunk2.toList())
        Assert.assertEquals(byteArrayOf(9).toList(), chunk3.toList())
    }

    @Test
    fun test_severalPackets_withMessageLongerThanMaxCharacteristicLength() {
        // Arrange
        val bytes = ByteArray(10) { i -> i.toByte() }
        val session = GattReadSession(bytes, 7, 10, true)

        // Act
        val chunk1 = session.read()
        val chunk2 = session.read()
        val chunk3 = session.read()

        // Assert
        Assert.assertEquals(byteArrayOf(1, 0, 0, 0, 10, 0, 1).toList(), chunk1.toList())
        Assert.assertEquals(byteArrayOf(2, 3, 4).toList(), chunk2.toList())
        Assert.assertEquals(byteArrayOf(5, 6, 7, 8, 9).toList(), chunk3.toList())
    }

    @Test
    fun test_emptyContent_shouldNotThrow() {
        // Arrange
        val bytes = ByteArray(0)
        val session = GattReadSession(bytes, 7, 10, true)

        // Act
        val chunk = session.read()

        // Assert
        Assert.assertEquals(byteArrayOf(1, 0, 0, 0, 0).toList(), chunk.toList())
    }

    @Test
    fun when_allChunksWereRead_then_sessionIsFinished() {
        // Arrange
        val bytes = ByteArray(10) { i -> i.toByte() }
        val session = GattReadSession(bytes, 7, 10, true)

        // Act / Assert
        session.read()
        Assert.assertFalse(session.finished())
        session.read()
        Assert.assertFalse(session.finished())
        session.read()
        Assert.assertTrue(session.finished())
    }

    @Test(expected = Exception::class)
    fun given_sessionIsFinished_when_readAgain_then_ExceptionIsThrown() {
        // Arrange
        val bytes = ByteArray(10) { i -> i.toByte() }
        val session = GattReadSession(bytes, 7, 10, true)

        session.read()
        session.read()
        session.read()

        // session is finished here

        // Act
        session.read()
    }
}
