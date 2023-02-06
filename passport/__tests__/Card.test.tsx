import React from 'react';

import { createClientRender, screen } from '../../../libs/testing';
import { Card } from '../Card';

const render = createClientRender();

describe('card', () => {
  it('should have wrapper', () => {
    render(<Card data-testid="card">Hello, world!</Card>);

    const wrapper = screen.getByTestId('card');

    expect(wrapper).toBeTruthy();
    expect(wrapper.textContent).toBe('Hello, world!');
  });
});
