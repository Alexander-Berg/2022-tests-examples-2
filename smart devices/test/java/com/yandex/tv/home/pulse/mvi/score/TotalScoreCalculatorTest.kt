package com.yandex.tv.home.pulse.mvi.score

import android.os.Looper
import com.yandex.tv.home.EmptyTestApp
import com.yandex.tv.home.pulse.mvi.MobileVelocityIndexEvent
import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.closeTo
import org.hamcrest.Matchers.equalTo
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.shadow.api.Shadow
import org.robolectric.shadows.ShadowLooper
import java.util.concurrent.TimeUnit
import kotlin.random.Random
import kotlin.test.assertFalse
import kotlin.test.assertTrue

@RunWith(RobolectricTestRunner::class)
@Config(application = EmptyTestApp::class)
class TotalScoreCalculatorTest {
    private fun createTotalScoreCalculator(
        metricsWeights: Map<MobileVelocityIndexEvent, Double>,
        callback: (Double) -> Unit
    ) = TotalScoreCalculator(callback, metricsWeights, WAIT_OPTIONAL_METRICS_TIMEOUT_MS, Looper.myLooper()!!)

    @Test
    fun `calculate total score when all metrics are present`() {
        val scores = mapOf(
            MobileVelocityIndexEvent.COLD_BOOT to 10.0,
            MobileVelocityIndexEvent.FIRST_FRAME_DRAWN to 20.0,
            MobileVelocityIndexEvent.FIRST_CONTENT_SHOWN to 50.0,
            MobileVelocityIndexEvent.FIRST_INPUT_DELAY to 100.0,
            MobileVelocityIndexEvent.TIME_TO_INTERACTIVE to 80.0,
        )
        val expectedScore = 41.0

        var totalScore = Double.MIN_VALUE
        val calculator = createTotalScoreCalculator(METRIC_WEIGHTS) { score -> totalScore = score }

        calculator.setMetricsScores(scores)
        assertThat(totalScore, closeTo(expectedScore, EPS))
    }

    @Test
    fun `invalid total score when all weights are zero`() {
        val zeroWeights = MobileVelocityIndexEvent.values()
            .associateWith { 0.0 }
        val scores = MobileVelocityIndexEvent.values()
            .associateWith { Random.nextDouble(100.0) }

        var totalScore = Double.MIN_VALUE
        val calculator = createTotalScoreCalculator(zeroWeights) { score -> totalScore = score }

        calculator.setMetricsScores(scores)
        assertThat(totalScore, equalTo(ScoreComputeUtils.INVALID_SCORE))
    }

    @Test
    fun `invalid total score when all weights are negative`() {
        val negativeWeights = MobileVelocityIndexEvent.values()
            .associateWith { -0.1 }
        val scores = MobileVelocityIndexEvent.values()
            .associateWith { Random.nextDouble(100.0) }

        var totalScore = Double.MIN_VALUE
        val calculator = createTotalScoreCalculator(negativeWeights) { score -> totalScore = score }

        calculator.setMetricsScores(scores)
        assertThat(totalScore, equalTo(ScoreComputeUtils.INVALID_SCORE))
    }

    @Test
    fun `don't calculate total score while not all required metrics are present`() {
        val scores = MobileVelocityIndexEvent.values()
            .drop(2)
            .associateWith { Random.nextDouble(100.0) }

        var scoreCalculated = false
        val calculator = createTotalScoreCalculator(METRIC_WEIGHTS) { scoreCalculated = true }

        calculator.setMetricsScores(scores)
        assertFalse(scoreCalculated)
    }

    @Test
    fun `calculate metrics after timeout when optional metrics aren't present`() {
        val requiredScores = MobileVelocityIndexEvent.values()
            .filter { it.isRequired }
            .associateWith { Random.nextDouble(100.0) }

        var scoreCalculated = false
        val calculator = createTotalScoreCalculator(METRIC_WEIGHTS) { scoreCalculated = true }

        calculator.setMetricsScores(requiredScores)
        assertFalse(scoreCalculated)
        idleFor(WAIT_OPTIONAL_METRICS_TIMEOUT_MS)
        assertTrue(scoreCalculated)
    }

    @Test
    fun `when optional metrics received after timeout score doesn't recalculate`() {
        val requiredScores = MobileVelocityIndexEvent.values()
            .filter { it.isRequired }
            .associateWith { Random.nextDouble(100.0) }
        val optionalScores = MobileVelocityIndexEvent.values()
            .filter { !it.isRequired }
            .associateWith { Random.nextDouble(100.0) }

        var scoreCalculated = false
        val calculator = createTotalScoreCalculator(METRIC_WEIGHTS) { scoreCalculated = true }

        calculator.setMetricsScores(requiredScores)
        idleFor(WAIT_OPTIONAL_METRICS_TIMEOUT_MS)
        assertTrue(scoreCalculated)
        scoreCalculated = false

        calculator.setMetricsScores(optionalScores)
        assertFalse(scoreCalculated)
    }

    @Test
    fun `when optional metrics received before timeout score calculates`() {
        val requiredScores = MobileVelocityIndexEvent.values()
            .filter { it.isRequired }
            .associateWith { Random.nextDouble(100.0) }
        val optionalScores = MobileVelocityIndexEvent.values()
            .filter { !it.isRequired }
            .associateWith { Random.nextDouble(100.0) }

        var scoreCalculated = false
        val calculator = createTotalScoreCalculator(METRIC_WEIGHTS) { scoreCalculated = true }

        calculator.setMetricsScores(requiredScores)
        idleFor(WAIT_OPTIONAL_METRICS_TIMEOUT_MS / 2)
        assertFalse(scoreCalculated)

        calculator.setMetricsScores(optionalScores)
        assertTrue(scoreCalculated)
    }

    private fun TotalScoreCalculator.setMetricsScores(metricScores: Map<MobileVelocityIndexEvent, Double>) {
        metricScores.forEach(this::setMetricScore)
    }

    private fun idleFor(durationMs: Long) {
        val shadowLooper = Shadow.extract<ShadowLooper>(Looper.myLooper())
        shadowLooper.idleFor(durationMs, TimeUnit.MILLISECONDS)
    }

    companion object {
        private val METRIC_WEIGHTS = mapOf(
            MobileVelocityIndexEvent.COLD_BOOT to 0.2,
            MobileVelocityIndexEvent.FIRST_FRAME_DRAWN to 0.3,
            MobileVelocityIndexEvent.FIRST_CONTENT_SHOWN to 0.3,
            MobileVelocityIndexEvent.FIRST_INPUT_DELAY to 0.1,
            MobileVelocityIndexEvent.TIME_TO_INTERACTIVE to 0.1,
        )
        private const val WAIT_OPTIONAL_METRICS_TIMEOUT_MS = 30000L
        private const val EPS = 1e-6
    }
}
