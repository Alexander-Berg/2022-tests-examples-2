package ru.yandextaxi.argument;

import org.junit.Test;

import java.util.Map;

import static org.junit.Assert.*;

public class CommandParserTest {

    private final ArgumentsParser parser = new ArgumentsParser();

    @Test(expected = NullPointerException.class)
    public void emptyArgs() {
        String[] args = {};

        parser.parse(args);
    }

    @Test(expected = IllegalArgumentException.class)
    public void incorrectCommandName() {
        String[] args = new String[]{"-testCommand"};

        parser.parse(args);
    }

    @Test
    public void onlyCommandName() {
        String testCommand = "testCommand";
        String[] args = {testCommand};

        Command command = parser.parse(args);

        String actual = command.getName();
        Map<String, String> parameters = command.getParameters();

        assertEquals(testCommand, actual);
        assertTrue(parameters.isEmpty());
    }

    @Test(expected = IllegalArgumentException.class)
    public void incorrectArgsSize() {
        String[] args = {"testCommand", "-key"};

        parser.parse(args);
    }

    @Test(expected = IllegalArgumentException.class)
    public void shortKey() {
        String[] args = {"testCommand", "-", "value"};

        parser.parse(args);
    }

    @Test(expected = IllegalArgumentException.class)
    public void incorrectKey() {
        String[] args = {"testCommand", "key", "value"};

        parser.parse(args);
    }

    @Test(expected = IllegalArgumentException.class)
    public void incorrectValue() {
        String[] args = {"testCommand", "-key", "-value"};

        parser.parse(args);
    }

    @Test
    public void oneKeyValue() {
        String testCommand = "testCommand";
        String key = "-key1";
        String value = "value1";
        String[] args = {testCommand, key, value};

        Command arguments = parser.parse(args);

        String command = arguments.getName();
        Map<String, String> parameters = arguments.getParameters();

        assertEquals(testCommand, command);
        assertFalse(parameters.isEmpty());
        assertEquals(1, parameters.size());

        String restoredValue = parameters.get("key1");

        assertEquals(value, restoredValue);
    }

    @Test
    public void twoKeyValues() {
        String testCommand = "testCommand";
        String key1 = "-key1";
        String value1 = "value1";
        String key2 = "-key2";
        String value2 = "value2";
        String[] args = {testCommand, key1, value1, key2, value2};

        Command arguments = parser.parse(args);

        String command = arguments.getName();
        Map<String, String> parameters = arguments.getParameters();

        assertEquals(testCommand, command);
        assertFalse(parameters.isEmpty());
        assertEquals(2, parameters.size());

        String restoredValue1 = parameters.get("key1");
        String restoredValue2 = parameters.get("key2");

        assertEquals(value1, restoredValue1);
        assertEquals(value2, restoredValue2);
    }
}