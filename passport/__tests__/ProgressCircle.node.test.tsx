/**
 * @jest-environment node
 */
import React from 'react';

import { ProgressCircle } from '..';
import { createServerRender } from '../../../libs/testing';

describe('ProgressCircle (ssr)', () => {
  const render = createServerRender();

  test('should render without errors', () => {
    expect(() => {
      render(<ProgressCircle variant="default" size={36} value={50} />);
    }).not.toThrowError();
  });
});
