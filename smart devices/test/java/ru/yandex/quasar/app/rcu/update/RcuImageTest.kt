package ru.yandex.quasar.app.rcu.update

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class RcuImageTest {

    @Test(expected = RcuImage.InvalidImageException::class)
    fun when_inputStreamIsLessThan16Bytes_then_throwException() {
        val inputStream = ByteArray(10).inputStream()
        RcuImage(inputStream)
    }

    @Test
    fun when_imageInfoIsNotEmpty_then_imageInfoParsedCorrectly() {
        val bytes = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size */ 4, 5, 6,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0
        )
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)

        assertEquals(2 * 256 + 3, rcuImage.version)
        assertEquals(6 * 256 * 256 + 5 * 256 + 4, rcuImage.fileSize)
        assertEquals(7 * 256 + 8, rcuImage.id)
        assertEquals((rcuImage.fileSize + 15) / 16, rcuImage.totalBlocks)
        assert(bytes.contentEquals(rcuImage.imageInfo))
    }

    @Test(expected = RcuImage.InvalidImageException::class)
    fun given_inputStreamIsShorterThanExpectedSize_when_loadImage_then_throwException() {
        val bytes = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 15 */ 0x0F, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0,
            *ByteArray(10)
        )
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)
        rcuImage.loadImage()
    }

    @Test(expected = RcuImage.InvalidImageException::class)
    fun given_inputStreamIsGreaterThanExpectedSize_when_loadImage_then_throwException() {
        val bytes = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 15 */ 0x0F, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0,
            *ByteArray(20)
        )
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)
        rcuImage.loadImage()
    }

    @Test
    fun given_inputStreamIsEqualToExpectedSize_when_loadImage_then_noException() {
        val bytes = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 15 */ 0x0F, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0,
            *ByteArray(15)
        )
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)
        rcuImage.loadImage()
    }

    @Test
    fun when_requestImageBlockWhichLargerThanTotalBlocks_then_returnNull() {
        val bytes = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 48 */ 0x30, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0,
            *ByteArray(48)
        )
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)

        val block = rcuImage.getImageBlock(5)
        assertNull(block)
    }

    @Test
    fun when_requestZeroImageBlock_then_returnImageInfo() {
        val imageInfo = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 48 */ 0x30, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0
        )
        val bytes = byteArrayOf(*imageInfo, *ByteArray(48))
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)

        val block = rcuImage.getImageBlock(0)
        assert(imageInfo.contentEquals(block!!))
    }

    @Test
    fun when_requestImageBlock_then_returnImageBlock() {
        val imageInfo = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 48 */ 0x30, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0
        )
        val blocks = ByteArray(48)
        for (i in 0 until 48) {
            blocks[i] = i.toByte()
        }
        val bytes = byteArrayOf(*imageInfo, *blocks)
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)

        val block1 = rcuImage.getImageBlock(1)
        val block2 = rcuImage.getImageBlock(2)
        val block3 = rcuImage.getImageBlock(3)
        assert(blocks.copyOfRange(0, 16).contentEquals(block1!!))
        assert(blocks.copyOfRange(16, 32).contentEquals(block2!!))
        assert(blocks.copyOfRange(32, 48).contentEquals(block3!!))
    }

    @Test
    fun when_lastBlockIsLessThan16Bytes_then_returnSmallBlock() {
        val imageInfo = byteArrayOf(
            /* reserved */ 0, 0,
            /* version */ 2, 3,
            /* size 10 */ 0x0A, 0, 0,
            /* reserved */ 0, 0, 0, 0, 0,
            /* ID */ 7, 8,
            /* reserved */ 0, 0
        )
        val blocks = ByteArray(10)
        for (i in 0 until 10) {
            blocks[i] = i.toByte()
        }
        val bytes = byteArrayOf(*imageInfo, *blocks)
        val inputStream = bytes.inputStream()

        val rcuImage = RcuImage(inputStream)

        val block1 = rcuImage.getImageBlock(1)
        assert(blocks.contentEquals(block1!!))
    }
}
