package com.yandex.tv.common.utility

import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import org.hamcrest.Matchers.greaterThan
import org.hamcrest.Matchers.lessThan
import org.junit.Before
import org.junit.Test

class BackoffRetryPolicyTest {
    private lateinit var policy: BackoffRetryPolicy
    private lateinit var policyWithJitter: BackoffRetryPolicy

    @Before
    fun runBeforeAnyTest() {
        policy = BackoffRetryPolicy(INITIAL_DELAY, MAX_DELAY, jitterPercent = NO_JITTER)
        policyWithJitter = BackoffRetryPolicy(INITIAL_DELAY, MAX_DELAY, jitterPercent = JITTER)
    }

    @Test
    fun given_noJitter_when_getDelayIsCalled_then_initialDelayIsReturned() {
        assertThat(policy.getDelay(), equalTo(INITIAL_DELAY))
    }

    @Test
    fun given_noJitter_when_increaseDelayIsCalled_then_doubledDelayIsReturned() {
        policy.increaseDelay()
        assertThat(policy.getDelay(), equalTo(2 * INITIAL_DELAY))
    }

    @Test
    fun given_noJitter_when_resetIsCalled_then_delayIsResetToInitial() {
        policy.increaseDelay()
        policy.reset()
        assertThat(policy.getDelay(), equalTo(INITIAL_DELAY))
    }

    @Test
    fun given_noJitter_when_increaseDelayIsCalledManyTimes_then_maxDelayIsReturned() {
        for (i in 0..100) {
            policy.increaseDelay()
        }
        assertThat(policy.getDelay(), equalTo(MAX_DELAY))
    }

    @Test
    fun given_noJitter_when_getDelayCalledTwice_then_theSameDelayIsReturned() {
        assertThat(policy.getDelay(), equalTo(policy.getDelay()))
    }

    @Test
    fun given_jitter_when_getDelayCalledTwice_then_differentDelaysAreReturned() {
        val delays = LongArray(100) { policyWithJitter.getDelay() }

        // Delays with jitter should not be all equal
        assertThat(delays.distinct().size, greaterThan(1))

        // All delays should be inside of expected interval
        assertThat(delays.minOrNull()!!.toDouble(), greaterThan(INITIAL_DELAY * (1 - JITTER)))
        assertThat(delays.maxOrNull()!!.toDouble(), lessThan(INITIAL_DELAY * (1 + JITTER)))
    }

    private companion object {
        const val INITIAL_DELAY = 10L
        const val MAX_DELAY = 100L
        const val NO_JITTER = 0.0
        const val JITTER = 0.25
    }
}
