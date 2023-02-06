package ru.yandex.taxi.conversation.common.yav;

import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringJUnitConfig(classes = YavConfiguration.class)
@TestPropertySource("classpath:/application.properties")
@Tag("Integration")
public class YavClientTest {

    @Autowired
    private YavClient yavClient;

    @Test
    public void test() {
        // arrange
        var expectedValue = "test_value";
        var secretResolver = new YavSecretResolver(yavClient);

        // act
        var result = secretResolver.getKey("sec-01fr2nejpg7tyxqqhk1texc5a9", "test_key");

        // assert
        assertEquals(result, expectedValue);
    }
}
