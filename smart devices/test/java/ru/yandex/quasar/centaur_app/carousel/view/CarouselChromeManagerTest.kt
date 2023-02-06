package ru.yandex.quasar.centaur_app.carousel.view

import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.mockito.AdditionalMatchers
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever
import org.robolectric.RobolectricTestRunner
import ru.yandex.quasar.centaur_app.BaseTest
import ru.yandex.quasar.div.container.contracts.DivInfo

@RunWith(RobolectricTestRunner::class)
class CarouselChromeManagerTest: BaseTest() {

    private var carouselChromeView: CarouselChromeView = mock()

    @Before
    fun setUp() {
        whenever(carouselChromeView.width).thenReturn(2000)
    }

    @Test
    fun `when all teasers are empty then scroll empty cards`() {
        val emptyList = listOf<DivInfo?>(null, null, null)
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(emptyList))

        chromeManager.onPageScrolled(0, 0.1f, 100)
        chromeManager.onPageScrolled(1, 0.4f, 400)
        chromeManager.onPageScrolled(1, 0.1f, 100)

        checkEmptySetData(3)
    }

    @Test
    fun `when all teasers are alternate then scroll always`() {
        val alternateList = listOf<DivInfo?>(null, mock(), null, mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(alternateList))

        chromeManager.onPageScrolled(0, 0.05f, 100)
        checkOffset(0.95f)

        chromeManager.onPageScrolled(1, 0.2f, 400)
        checkOffset(-0.2f)

        chromeManager.onPageScrolled(1, 0.05f, 100)
        checkOffset(0.95f)
    }

    @Test
    fun `when spinning inside one chrome card then scrolling should not be called`() {
        val chromeList = listOf<DivInfo?>(mock(), mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(chromeList))

        chromeManager.onPageScrolled(0, 0.4f, 800)
        chromeManager.onPageScrolled(0, 0.2f, 400)
        chromeManager.onPageScrolled(0, 0.4f, 800)

        checkOffset(offset = 0f, count = 3)
        checkNotEmptySetData(3)
    }

    @Test
    fun `when scroll backward only on chromes then set correct chrome position`() {
        val chromeList = listOf<DivInfo?>(mock(), mock(), mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(chromeList))

        chromeManager.onPageScrolled(0, 0.9f, 1900)
        chromeManager.onPageScrolled(0, 0f, 0)

        checkOffset(offset = 0f, count = 2)
    }

    @Test
    fun `when scrolling forward and backward then chrome position set correctly`() {
        val chromeList = listOf<DivInfo?>(mock(), mock(), mock(), mock(), mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(chromeList))

        chromeManager.onPageScrolled(1, 0.9f, 1900)
        chromeManager.onPageScrolled(1, 0.1f, 100)
        chromeManager.onPageScrolled(0, 0.9f, 1500)

        checkOffset(offset = 0f, count = 3)
        checkNotEmptySetData(3)
    }

    @Test
    fun `when scrolling only forward on chromes then chrome position set correctly`() {
        val chromeList = listOf<DivInfo?>(mock(), mock(), mock(), mock(), mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(chromeList))

        chromeManager.onPageScrolled(1, 0.1f, 100)
        chromeManager.onPageScrolled(2, 0.1f, 100)
        chromeManager.onPageScrolled(2, 0.3f, 300)
        chromeManager.onPageScrolled(3, 0.2f, 200)


        checkOffset(offset = 0f, count = 4)
        checkNotEmptySetData(4)
    }

    @Test
    fun `when scrolling only chromes and empty cards then scrolling is correctly`() {
        val alternateList = listOf<DivInfo?>(null, mock(), mock(), null, mock())
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(alternateList))

        chromeManager.onPageScrolled(0, 0.7f, 1400)
        checkOffset(0.3f)

        chromeManager.onPageScrolled(1, 0.2f, 400)
        chromeManager.onPageScrolled(2, 0f, 0)
        checkOffset(offset = 0f, count = 2)

        chromeManager.onPageScrolled(2, 0.4f, 800)
        checkOffset(-0.4f)

        chromeManager.onPageScrolled(3, 0.8f, 1800)
        checkOffset(0.2f)

        checkNotEmptySetData(5)
    }

    @Test
    fun `when scrolling from empty to chrome sequence then scrolling and set chrome are correctly`() {
        val alternateList = listOf<DivInfo?>(mock(), mock(), null)
        val chromeManager = CarouselChromeManager(carouselChromeView, mock(), mock(), getCardByPositionFunc(alternateList))

        chromeManager.onPageScrolled(1, 0.9f, 1800)
        checkOffset(-0.9f)

        chromeManager.onPageScrolled(0, 0.9f, 1600)
        checkOffset(0f)
    }

    private fun checkOffset(offset: Float, count: Int = 1) {
        verify(carouselChromeView, Mockito.times(count)).offset =
            AdditionalMatchers.eq(offset, 0.0001f)
    }

    private fun checkNotEmptySetData(count: Int = 1) {
        verify(carouselChromeView, Mockito.times(count)).setChromeData(ArgumentMatchers.any(DivInfo::class.java), any(), any())
    }

    private fun checkEmptySetData(count: Int = 1) {
        verify(carouselChromeView, Mockito.times(count)).setChromeData(ArgumentMatchers.isNull(), any(), any())
    }

    private fun getCardByPositionFunc(
        carouselChromeList: List<DivInfo?>
    ): (position: Int) -> DivInfo? {
        return { pos ->
            val correctPosition = pos % carouselChromeList.size
            carouselChromeList[correctPosition]
        }
    }
}
