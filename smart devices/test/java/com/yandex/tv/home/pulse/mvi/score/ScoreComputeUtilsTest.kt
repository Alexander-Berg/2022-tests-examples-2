package com.yandex.tv.home.pulse.mvi.score

import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.closeTo
import org.hamcrest.Matchers.equalTo
import org.junit.Test

class ScoreComputeUtilsTest {
    @Test
    fun `evaluate score for control points`() {
        for (point in CONTROL_SCORE_POINTS) {
            val score = ScoreComputeUtils.evaluateScore(point.value, VALID_SCORE_INTERVALS)
            assertThat(score, closeTo(point.score, EPS))
        }
    }

    @Test
    fun `get max score if value is less than left border`() {
        val millis = Long.MIN_VALUE
        val expectedScore = VALID_SCORE_INTERVALS.first().score
        val actualScore = ScoreComputeUtils.evaluateScore(millis, VALID_SCORE_INTERVALS)
        assertThat(actualScore, equalTo(expectedScore))
    }

    @Test
    fun `get min score if value is greater than right border`() {
        val millis = Long.MAX_VALUE
        val expectedScore = VALID_SCORE_INTERVALS.last().score
        val actualScore = ScoreComputeUtils.evaluateScore(millis, VALID_SCORE_INTERVALS)
        assertThat(actualScore, equalTo(expectedScore))
    }

    @Test
    fun `get invalid score on empty intervals`() {
        val millis = 25L
        val score = ScoreComputeUtils.evaluateScore(millis, emptyList())
        assertThat(score, equalTo(ScoreComputeUtils.INVALID_SCORE))
    }

    @Test
    fun `get invalid score on invalid intervals`() {
        val invalidOrderIntervals = listOf(
            ScorePoint(40, 80.0),
            ScorePoint(10, 75.0),
            ScorePoint(20, 95.0),
            ScorePoint(0, 90.0),
            ScorePoint(50, 50.0)
        )

        val millis = 25L
        val score = ScoreComputeUtils.evaluateScore(millis, invalidOrderIntervals)
        assertThat(score, equalTo(ScoreComputeUtils.INVALID_SCORE))
    }

    @Test
    fun `get invalid score on matching borders intervals`() {
        val matchingBordersIntervals = listOf(
            ScorePoint(0, 100.0),
            ScorePoint(250, 95.0),
            ScorePoint(250, 90.0),
            ScorePoint(350, 85.0),
            ScorePoint(351, 85.0),
            ScorePoint(500, 50.0),
            ScorePoint(502, 50.0),
            ScorePoint(1000, 0.0)
        )

        val millis = 25L
        val score = ScoreComputeUtils.evaluateScore(millis, matchingBordersIntervals)
        assertThat(score, equalTo(ScoreComputeUtils.INVALID_SCORE))
    }

    companion object {
        private val VALID_SCORE_INTERVALS: List<ScorePoint> = listOf(
            ScorePoint(0, 100.0),
            ScorePoint(10, 75.0),
            ScorePoint(20, 50.0),
            ScorePoint(30, 25.0),
            ScorePoint(40, 0.0)
        )

        private val CONTROL_SCORE_POINTS: List<ScorePoint> = listOf(
            ScorePoint(0, 100.0),
            ScorePoint(10, 75.0),
            ScorePoint(20, 50.0),
            ScorePoint(30, 25.0),
            ScorePoint(40, 0.0),
            // See https://www.desmos.com/calculator/wkzcelbn4g
            ScorePoint(21, 47.5),
            ScorePoint(22, 45.0),
            ScorePoint(23, 42.5),
            ScorePoint(24, 40.0),
            ScorePoint(25, 37.5),
            ScorePoint(26, 35.0),
            ScorePoint(27, 32.5),
            ScorePoint(28, 30.0),
            ScorePoint(29, 27.5)
        )
        private const val EPS = 1e-6
    }
}
