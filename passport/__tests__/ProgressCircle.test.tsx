import React, { createRef } from 'react';

import { ProgressCircle } from '..';
import { createClientRender, screen } from '../../../libs/testing';

describe('ProgressCircle', () => {
  const render = createClientRender();

  test('should set ref for element', () => {
    const ref = createRef<HTMLSpanElement>();

    render(<ProgressCircle ref={ref} data-testid="element" />);

    expect(screen.getByTestId('element')).toBe(ref.current);
  });

  test('should set custom class name', () => {
    render(<ProgressCircle className="custom-class" data-testid="element" />);

    expect(screen.getByTestId('element')).toHaveClass('custom-class');
  });

  test('should set aria attributes', () => {
    render(<ProgressCircle data-testid="element" value={30} />);

    const element = screen.getByTestId('element');

    expect(element).toHaveAttribute('role', 'progressbar');
    expect(element).toHaveAttribute('aria-valuemin', '0');
    expect(element).toHaveAttribute('aria-valuemax', '100');
    expect(element).toHaveAttribute('aria-valuenow', '30');
  });

  test('should display formatted text', () => {
    const { setProps } = render(
      <ProgressCircle value={35} min={0} max={100} data-testid="element" />,
    );

    expect(screen.getByTestId('element')).not.toHaveTextContent(/35/);

    setProps({ formatStyle: 'decimal' });

    expect(screen.getByTestId('element')).toHaveTextContent(/35\/100/);

    setProps({ formatStyle: 'percent' });

    expect(screen.getByTestId('element')).toHaveTextContent(/35%/);
  });
});
