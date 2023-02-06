package ru.yandex.quasar.app.rcu.utils

import org.junit.Assert.assertEquals
import org.junit.Test
import java.nio.ByteOrder

class RcuUtilsTest {
    @Test
    fun given_littleEndian_when_toByteArray_then_convertCorrectly() {
        val int = 42
        val expectedArr = byteArrayOf(0x2A, 0, 0, 0)
        val byteArray = int.toByteArray(ByteOrder.LITTLE_ENDIAN)
        assert(byteArray.contentEquals(expectedArr))
    }

    @Test
    fun given_bigEndian_when_toByteArray_then_convertCorrectly() {
        val int = 42
        val expectedArr = byteArrayOf(0, 0, 0, 0x2A)
        val byteArray = int.toByteArray(ByteOrder.BIG_ENDIAN)
        assert(byteArray.contentEquals(expectedArr))
    }

    @Test
    fun given_littleEndian_when_toInt_then_convertCorrectly() {
        val arr = byteArrayOf(0x2A, 0, 0, 0)
        val expectedInt = 42
        val int = arr.toInt(ByteOrder.LITTLE_ENDIAN)
        assertEquals(expectedInt, int)
    }

    @Test
    fun given_bigEndian_when_toInt_then_convertCorrectly() {
        val arr = byteArrayOf(0, 0, 0, 0x2A)
        val expectedInt = 42
        val int = arr.toInt(ByteOrder.BIG_ENDIAN)
        assertEquals(expectedInt, int)
    }

    @Test
    fun given_byte_when_toHex_then_convertCorrectly() {
        val bytes =
            mapOf(
                0.toByte() to "0x0",
                5.toByte() to "0x5",
                42.toByte() to "0x2a",
                (-5).toByte() to "0xfb",
                255.toByte() to "0xff"
            )
        for (byte in bytes) {
            assertEquals(byte.value, byte.key.toHex())
        }
    }

    @Test
    fun given_byteArray_when_toHex_then_convertCorrectly() {
        val bytes = byteArrayOf(0, 5, 42, -5, 255.toByte())
        val expectedHex = "[0x0, 0x5, 0x2a, 0xfb, 0xff]"
        assertEquals(expectedHex, bytes.toHex())
    }
}
