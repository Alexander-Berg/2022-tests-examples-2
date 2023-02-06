/**
 * @jest-environment node
 */
import React from 'react';

import { createServerRender } from '../../../libs/testing';
import { Shortcut } from '../index';

describe('Shortcut (ssr)', () => {
  const render = createServerRender();

  test('should render without errors', () => {
    expect(() => {
      render(<Shortcut />);
    }).not.toThrowError();
  });
});
