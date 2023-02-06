package ru.yandex.pricecalc;

import java.util.HashMap;
import java.util.Map;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * Instrumented test, which will execute on an Android device.
 */
@RunWith(JUnit4.class)
public class PriceCalcTests {
    static {
        System.loadLibrary("price-calc");
    }

    private static void assertEqual(CompositePrice actual, CompositePrice expected) {
        assertEquals(actual.getBoarding(), expected.getBoarding(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getDistance(), expected.getDistance(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getTime(), expected.getTime(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getWaiting(), expected.getWaiting(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getRequirements(), expected.getRequirements(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getTransitWaiting(), expected.getTransitWaiting(), TestData.DOUBLE_EPSILON);
        assertEquals(actual.getDestinationWaiting(), expected.getDestinationWaiting(), TestData.DOUBLE_EPSILON);
    }

    @Test
    public void calculateBaseTest() {
        final CompositePrice result1 = PriceCalc.calculateBase(
                TestData.ROUTE, TestData.POLYGONS, TestData.PRICES_1);
        assertEqual(result1, TestData.PRICE_1);

        final CompositePrice result2 = PriceCalc.calculateBase(
                TestData.ROUTE, TestData.POLYGONS, TestData.PRICES_2);
        assertEqual(result2, TestData.PRICE_2);

        final CompositePrice resultH = PriceCalc.calculateBase(
                TestData.ROUTE_HELSINKI, TestData.POLYGONS_HELSINKI,
                TestData.PRICES_HELSINKI);
        assertEqual(resultH, TestData.PRICE_HELSINKI);
    }

    @Test
    public void runInterpreterTest() {
        HashMap<String, Integer> metadataMapping = new HashMap<String, Integer>();

        final InterpreterInput userInput1 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_RETURN_PRICE_X_0_9);
        final InterpreterInput driverInput1 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_IF_PAID_OPTION_IN_USER_OPTIONS);

        metadataMapping.put(new String("paid_option"), 1);

        final InterpreterResults result1 = PriceCalc.runInterpreter(
                userInput1, driverInput1, metadataMapping, 1.0);
        assertEquals(result1.getUser().getRoundedPrice(),
                     Math.ceil(TestData.PRICE_SUM * 0.9), TestData.DOUBLE_EPSILON);
        assertEqual(result1.getUser().getPrice(), TestData.PRICE_X_0_9);
        assertEquals(result1.getDriver().getRoundedPrice(),
                     Math.ceil(TestData.PRICE_SUM + 3 * 42), TestData.DOUBLE_EPSILON);
        assertEqual(result1.getDriver().getPrice(), TestData.PRICE_REQ_PLUS_3X42);

        final InterpreterInput userInput2 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_WITH_EMIT);
        final InterpreterInput driverInput2 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_WITH_EMIT);

        final InterpreterResults result2 = PriceCalc.runInterpreter(
                userInput2, driverInput2, metadataMapping, 1.0);
        assertEquals(result2.getUser().getRoundedPrice(), Math.ceil(TestData.PRICE_SUM), TestData.DOUBLE_EPSILON);
        assertEqual(result2.getUser().getPrice(), TestData.PRICE);
        assertEquals(result2.getDriver().getRoundedPrice(), Math.ceil(TestData.PRICE_SUM), TestData.DOUBLE_EPSILON);
        assertEqual(result2.getDriver().getPrice(), TestData.PRICE);

        final Map<Integer, Double> userMetadata2 = result2.getUser().getMetadata();
        assertTrue(userMetadata2.size() == 1 && userMetadata2.containsKey(1));
        assertEquals(userMetadata2.get(1), TestData.PRICE_SUM, TestData.DOUBLE_EPSILON);
        final Map<Integer, Double> driverMetadata2 = result2.getDriver().getMetadata();
        assertTrue(driverMetadata2.size() == 1 && driverMetadata2.containsKey(1));
        assertEquals(driverMetadata2.get(1), TestData.PRICE_SUM, TestData.DOUBLE_EPSILON);

        final InterpreterInput userInput3 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_IF_PAID_OPTION_IN_USER_OPTIONS);
        final InterpreterInput driverInput3 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_IF_PAID_OPTION_IN_USER_OPTIONS);

        final InterpreterResults result3 = PriceCalc.runInterpreter(
                userInput3, driverInput3, metadataMapping, 1.0);
        assertEquals(result3.getUser().getRoundedPrice(),
                Math.ceil(TestData.PRICE_SUM + 3 * 42), TestData.DOUBLE_EPSILON);
        assertEqual(result3.getUser().getPrice(), TestData.PRICE_REQ_PLUS_3X42);
        assertEquals(result3.getDriver().getRoundedPrice(),
                Math.ceil(TestData.PRICE_SUM + 3 * 42), TestData.DOUBLE_EPSILON);
        assertEqual(result3.getDriver().getPrice(), TestData.PRICE_REQ_PLUS_3X42);

        final InterpreterInput userInput4 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_CHECK_USER_META);
        final InterpreterInput driverInput4 = new InterpreterInput(
                TestData.PRICE, TestData.TRIP_DETAILS, TestData.BYTECODE_CHECK_USER_META);

        metadataMapping.put(new String("foo"), 2);

        final InterpreterResults result4 = PriceCalc.runInterpreter(
                userInput4, driverInput4, metadataMapping, 1.0);
        assertEquals(result4.getUser().getRoundedPrice(),
                Math.ceil(TestData.PRICE_SUM), TestData.DOUBLE_EPSILON);
        assertEquals(result4.getDriver().getRoundedPrice(),
                Math.ceil(TestData.PRICE_SUM + TestData.PRICE.getBoarding() * 0.2), TestData.DOUBLE_EPSILON);

        final Map<Integer, Double> userMetadata4 = result4.getUser().getMetadata();
        assertTrue(userMetadata4.size() == 1 && userMetadata4.containsKey(2));
        assertEquals(userMetadata4.get(2), 1.2, TestData.DOUBLE_EPSILON);
        final Map<Integer, Double> driverMetadata4 = result4.getDriver().getMetadata();
        assertTrue(driverMetadata4.size() == 1 && driverMetadata4.containsKey(2));
        assertEquals(driverMetadata4.get(2), 2.0, TestData.DOUBLE_EPSILON);
    }
}
