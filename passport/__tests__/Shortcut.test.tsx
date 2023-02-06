import React from 'react';

import { createClientRender, installPointerEvent, screen } from '../../../libs/testing';
import { Shortcut } from '../index';

describe('Shortcut', () => {
  installPointerEvent();

  const render = createClientRender();

  test('should pass className', () => {
    render(<Shortcut className="my-shortcut" data-testid="shortcut" />);

    expect(screen.getByTestId('shortcut').className).toMatch(/my-shortcut/);
  });
});
