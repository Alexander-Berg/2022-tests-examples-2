package ru.yandex.quasar.app.video.mediaInfo

import org.junit.Assert
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import ru.yandex.quasar.shadows.ShadowThreadUtil

@RunWith(RobolectricTestRunner::class)
@Config(
        shadows = [ShadowThreadUtil::class],
        instrumentedPackages = ["ru.yandex.quasar.concurrency"]
)
class DynamicRangesObservableTest {

    private val dynamicRangesInfoPath = ""
    private val dynamicRangesStateObservable = DynamicRangesObservable(dynamicRangesInfoPath)

    @Test
    fun when_fullHdrData_then_getFullDynamicRanges() {
        val data = "HDR10Plus Supported: 1\n" +
                "HDR Static Metadata:\n" +
                "    Supported EOTF:\n" +
                "        Traditional SDR: 1\n" +
                "        Traditional HDR: 1\n" +
                "        SMPTE ST 2084: 1\n" +
                "        Hybrid Log-Gamma: 1\n" +
                "    Supported SMD type1: 1\n" +
                "    Luminance Data\n" +
                "        Max: 0\n" +
                "        Avg: 0\n" +
                "        Min: 0\n" +
                "\n" +
                "HDR Dynamic Metadata:\n" +
                "\n" +
                "colorimetry_data: ff"
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(data)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_HDR_PLUS,
                MediaInfoUtil.DYNAMIC_RANGE_HDR, MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }

    @Test
    fun when_hdrDataContains_then_getHdr() {
        val data = "HDR Static Metadata:\n" +
                "    Supported EOTF:\n" +
                "        Traditional SDR: 1\n" +
                "        Traditional HDR: 1\n" +
                "        SMPTE ST 2084: 1\n" +
                "        Hybrid Log-Gamma: 1\n" +
                "    Supported SMD type1: 1\n" +
                "    Luminance Data\n" +
                "        Max: 0\n" +
                "        Avg: 0\n" +
                "        Min: 0\n" +
                "\n" +
                "HDR Dynamic Metadata:\n" +
                "\n" +
                "colorimetry_data: ff"
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(data)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_HDR,
                MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }

    @Test
    fun when_sdrDataContains_then_getSdr() {
        val data = "HDR Static Metadata:\n" +
                "    Supported EOTF:\n" +
                "        Traditional SDR: 1\n" +
                "        Traditional HDR: 0\n" +
                "        SMPTE ST 2084: 1\n" +
                "        Hybrid Log-Gamma: 1\n" +
                "    Supported SMD type1: 1\n" +
                "    Luminance Data\n" +
                "        Max: 0\n" +
                "        Avg: 0\n" +
                "        Min: 0\n" +
                "\n" +
                "HDR Dynamic Metadata:\n" +
                "\n" +
                "colorimetry_data: ff"
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(data)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }

    @Test
    fun when_emptyData_then_getEmptyDynamicRanges() {
        val data = "HDR Static Metadata:\n" +
                "    Supported EOTF:\n" +
                "        Traditional SDR: 0\n" +
                "        Traditional HDR: 0\n" +
                "        SMPTE ST 2084: 1\n" +
                "        Hybrid Log-Gamma: 1\n" +
                "    Supported SMD type1: 1\n" +
                "    Luminance Data\n" +
                "        Max: 0\n" +
                "        Avg: 0\n" +
                "        Min: 0\n" +
                "\n" +
                "HDR Dynamic Metadata:\n" +
                "\n" +
                "colorimetry_data: ff"
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(data)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }

    @Test
    fun when_incorrectFormat_then_getEmptyDynamicRanges() {
        val data = "HDR fsdfsdfsfsdf"
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(data)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }

    @Test
    fun when_null_then_getEmptyDynamicRanges() {
        val result = dynamicRangesStateObservable.getDynamicRangesInfo(null)
        val expected = listOf(MediaInfoUtil.DYNAMIC_RANGE_SDR)

        Assert.assertTrue(result!!.containsAll(expected))
    }
}