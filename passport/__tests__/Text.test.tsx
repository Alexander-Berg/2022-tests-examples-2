import React, { createRef } from 'react';

import { Text } from '..';
import { createClientRender, screen } from '../../../libs/testing';

describe('Text', () => {
  const render = createClientRender();

  test('should render custom element', () => {
    render(
      <Text as="h1" data-testid="text">
        Text
      </Text>,
    );

    expect(screen.getByTestId('text')).toHaveProperty('tagName', 'H1');
  });

  test('should correct set data-variant attribute', () => {
    const { setProps } = render(<Text data-testid="text">Text</Text>);

    expect(screen.getByTestId('text')).not.toHaveAttribute('data-variant');

    setProps({ variant: 'heading-m' });

    expect(screen.getByTestId('text')).toHaveAttribute('data-variant', 'heading-m');
  });

  test('should correct set data-color attribute', () => {
    const { setProps } = render(<Text data-testid="text">Text</Text>);

    expect(screen.getByTestId('text')).toHaveAttribute('data-color', 'primary');

    setProps({ color: 'secondary' });

    expect(screen.getByTestId('text')).toHaveAttribute('data-color', 'secondary');
  });

  test('should correct set data-weight attribute', () => {
    const { setProps } = render(<Text data-testid="text">Text</Text>);

    expect(screen.getByTestId('text')).not.toHaveAttribute('data-weight');

    setProps({ weight: 'medium' });

    expect(screen.getByTestId('text')).toHaveAttribute('data-weight', 'medium');
  });

  test('should correct set data-overflow attribute', () => {
    const { setProps } = render(<Text data-testid="text">Text</Text>);

    expect(screen.getByTestId('text')).not.toHaveAttribute('data-overflow');

    setProps({ overflow: 'ellipsis' });

    expect(screen.getByTestId('text')).toHaveAttribute('data-overflow', 'ellipsis');
  });

  test('should set custom class name', () => {
    render(
      <Text className="custom-text" data-testid="text">
        Text
      </Text>,
    );

    expect(screen.getByTestId('text')).toHaveClass('custom-text');
  });

  test('should set ref for element', () => {
    const ref = createRef<HTMLSpanElement>();

    render(
      <Text ref={ref} data-testid="text">
        Text
      </Text>,
    );

    expect(screen.getByTestId('text')).toBe(ref.current);
  });
});
