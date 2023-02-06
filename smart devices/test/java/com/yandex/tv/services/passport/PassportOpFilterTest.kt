package com.yandex.tv.services.passport

import android.os.Build
import com.yandex.passport.api.PassportUid
import com.yandex.tv.services.passport.PassportOpFilter.Op
import org.junit.Assert.assertSame
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [Build.VERSION_CODES.P], manifest = Config.NONE)
class PassportOpFilterTest {

    /**
     * .-----------------------------------+---------------------.
     * |              before               |        after        |
     * |-----------------------------------+---------------------|
     * | current  next  new                |  current    next    |
     * |-----------------------------------+---------------------|
     * | any?     any?  SET                |  new        -       |
     * '-----------------------------------+---------------------'
     */
    @Test
    fun `submitOp, pass different SET, emit new, cancel current and next`() {

        val newSet = Op.set(PassportUid.Factory.from(2))

        for (initialOps in getValidOpsCombinations(includeNullCurrent = true)) {
            val opFilter = createOpFilter(initialOps[0], initialOps[1])
            val testObserver = opFilter.filteredOps.test()

            opFilter.submitOp(newSet)
            testObserver.assertValues(newSet)
            assertSame(newSet, opFilter.currentOp)
            assertSame(null, opFilter.nextOp)
        }
    }

    /**
     * .-----------------------------------+---------------------.
     * |              before               |        after        |
     * |-----------------------------------+---------------------|
     * | current  next  new                |  current    next    |
     * |-----------------------------------+---------------------|
     * | SET(1)   any?  SET(1)             |  old       -        |
     * '-----------------------------------+---------------------'
     */
    @Test
    fun `submitOp, pass identical SET, don't emit new, don't cancel current`() {

        val oldSet = Op.set(PassportUid.Factory.from(1))
        val newSet = Op.set(PassportUid.Factory.from(1))

        val opFilter = createOpFilter(oldSet, null)
        val testObserver = opFilter.filteredOps.test()

        opFilter.submitOp(newSet)
        assertSame(oldSet, opFilter.currentOp)
        testObserver.assertNoValues()
    }

    /**
     * .-----------------------------------+---------------------.
     * |              before               |        after        |
     * |-----------------------------------+---------------------|
     * | current  next  new                |  current    next    |
     * |-----------------------------------+---------------------|
     * | -        -     REFRESH, PICK_ANY  |  new        -       |
     * '-----------------------------------+---------------------'
     */
    @Test
    fun `submitOp, null current, pass REFRESH|PICK_ANY, emit new`() {

        val opsToTest = arrayOf(
                Op.refresh(),
                Op.pickAny()
        )

        for (newOp in opsToTest) {
            val opFilter = createOpFilter(null, null)
            val testObserver = opFilter.filteredOps.test()

            opFilter.submitOp(newOp)
            testObserver.assertValues(newOp)
            assertSame(newOp, opFilter.currentOp)
            assertSame(null, opFilter.nextOp)
        }
    }

    /**
     * .-----------------------------------+---------------------.
     * |              before               |        after        |
     * |-----------------------------------+---------------------|
     * | current  next  new                |  current    next    |
     * |-----------------------------------+---------------------|
     * | any      any?  REFRESH, PICK_ANY  |  unchanged  new     |
     * '-----------------------------------+---------------------'
     */
    @Test
    fun `submitOp, nonnull current, pass REFRESH|PICK_ANY, enqueue new`() {

        val opsToTest = arrayOf(
                Op.refresh(),
                Op.pickAny()
        )

        for (opToTest in opsToTest) {
            for (initialOps in getValidOpsCombinations(includeNullCurrent = false)) {
                val opFilter = createOpFilter(initialOps[0], initialOps[1])
                val testObserver = opFilter.filteredOps.test()

                opFilter.submitOp(opToTest)
                testObserver.assertValues()
                assertSame(initialOps[0], opFilter.currentOp)
                assertSame(opToTest, opFilter.nextOp)
            }
        }
    }

    /**
     * .---------------------------------+-----------------------.
     * |              before             |         after         |
     * |---------------------------------+-----------------------|
     * | current  next  completed        |  current    next      |
     * |---------------------------------+-----------------------|
     * | any?     any?  non-current      |  unchanged  unchanged |
     * '---------------------------------+-----------------------'
     */
    @Test
    fun `onOpComplete, pass non-current, do nothing`() {

        val illegalSet = Op.set(PassportUid.Factory.from(1))
        val illegalRefresh = Op.refresh()
        val illegalPickAny = Op.pickAny()

        for (initialOps in getValidOpsCombinations(includeNullCurrent = true)) {
            val opFilter = createOpFilter(initialOps[0], initialOps[1])
            val testObserver = opFilter.filteredOps.test()

            opFilter.onOpComplete(illegalSet)
            opFilter.onOpComplete(illegalRefresh)
            opFilter.onOpComplete(illegalPickAny)
            testObserver.assertValues()
            assertSame(initialOps[0], opFilter.currentOp)
            assertSame(initialOps[1], opFilter.nextOp)
        }
    }

    /**
     * .---------------------------------+-----------------------.
     * |              before             |         after         |
     * |---------------------------------+-----------------------|
     * | current  next  completed        |  current    next      |
     * |---------------------------------+-----------------------|
     * | any      any?  current          |  next       -         |
     * '---------------------------------+-----------------------'
     */
    @Test
    fun `onOpComplete, pass current, emit next`() {

        for (initialOps in getValidOpsCombinations(includeNullCurrent = false)) {
            val opFilter = createOpFilter(initialOps[0], initialOps[1])
            val testObserver = opFilter.filteredOps.test()

            opFilter.onOpComplete(initialOps[0]!!)
            if (initialOps[1] != null) {
                testObserver.assertValues(initialOps[1])
                assertSame(initialOps[1], opFilter.currentOp)
                assertSame(null, opFilter.nextOp)
            } else {
                testObserver.assertValues()
                assertSame(null, opFilter.currentOp)
                assertSame(null, opFilter.nextOp)
            }
        }
    }

    private fun createOpFilter(current: Op?, next: Op?): PassportOpFilter {
        val opFilter = PassportOpFilter()
        if (current != null) {
            opFilter.submitOp(current)
        }
        if (next != null) {
            opFilter.submitOp(next)
        }
        return opFilter
    }

    private fun getValidOpsCombinations(includeNullCurrent: Boolean): Array<Array<Op?>> {
        val set = Op.set(PassportUid.Factory.from(1))
        val refresh = Op.refresh()
        val pickAny = Op.pickAny()
        val opsCombinations = arrayOf<Array<Op?>>(
                arrayOf(set, refresh),
                arrayOf(set, pickAny),
                arrayOf(set, null),

                arrayOf(refresh, refresh),
                arrayOf(refresh, pickAny),
                arrayOf(refresh, null),

                arrayOf(pickAny, refresh),
                arrayOf(pickAny, pickAny),
                arrayOf(pickAny, null)
        )

        if (includeNullCurrent) {
            return opsCombinations + arrayOf<Op?>(null, null)
        }
        return opsCombinations
    }

}
