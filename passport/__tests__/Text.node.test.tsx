/**
 * @jest-environment node
 */
import React from 'react';

import { createServerRender } from '../../../libs/testing';
import { Text } from '../Text';

describe('Text (ssr)', () => {
  const render = createServerRender();

  test('should render without errors', () => {
    expect(() => {
      render(<Text>Some text</Text>);
    }).not.toThrowError();
  });
});
