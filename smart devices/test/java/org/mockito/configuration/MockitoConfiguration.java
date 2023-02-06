package org.mockito.configuration;

/**
 * This is a workaround to prevent ClassCastException occurred while creating the mockito proxy
 */
@SuppressWarnings("unused")
public class MockitoConfiguration extends DefaultMockitoConfiguration {

    @Override
    public boolean enableClassCache() {
        return false;
    }
}
