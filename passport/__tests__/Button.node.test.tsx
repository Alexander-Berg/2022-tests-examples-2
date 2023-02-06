/**
 * @jest-environment node
 */
import React from 'react';

import { createServerRender } from '../../../libs/testing';
import { Button } from '../Button';

describe('Button (ssr)', () => {
  const render = createServerRender();

  test('should render without errors', () => {
    expect(() => {
      render(<Button>Button</Button>);
    }).not.toThrowError();
  });
});
