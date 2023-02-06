package ru.yandex.quasar.app.rcu.update

import org.junit.Assert.assertEquals
import org.junit.Test

class RcuInfoTest {

    @Test(expected = IllegalArgumentException::class)
    fun when_firstByteIsNotHeader_then_throwException() {
        val bytes = ByteArray(8)
        RcuInfo(bytes)
    }

    @Test(expected = IllegalArgumentException::class)
    fun when_secondByteIsNotRcuInfoCommand_then_throwException() {
        val bytes = byteArrayOf(RcuOtaCommands.COMMAND_HEADER, *ByteArray(7))
        RcuInfo(bytes)
    }

    @Test
    fun when_firstTwoBytesIsOk_then_noException() {
        val bytes = byteArrayOf(
            RcuOtaCommands.COMMAND_HEADER,
            RcuOtaCommands.RETURN_REMOTE_INFO,
            *ByteArray(6)
        )
        RcuInfo(bytes)
    }

    @Test
    fun when_versionIsNotZero_then_versionParsedCorrectly() {
        val bytes = byteArrayOf(
            RcuOtaCommands.COMMAND_HEADER,
            RcuOtaCommands.RETURN_REMOTE_INFO,
            /* version */ 2, 3,
            *ByteArray(4)
        )
        val rcuInfo = RcuInfo(bytes)
        assertEquals(2 * 256 + 3, rcuInfo.imageVersion)
    }

    @Test
    fun when_idIsNotZero_then_idParsedCorrectly() {
        val bytes = byteArrayOf(
            RcuOtaCommands.COMMAND_HEADER,
            RcuOtaCommands.RETURN_REMOTE_INFO,
            /* version */ 0, 0,
            /* id */ 2, 3,
            *ByteArray(2)
        )
        val rcuInfo = RcuInfo(bytes)
        assertEquals(2 * 256 + 3, rcuInfo.id)
    }
}
