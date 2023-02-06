import React, { createRef } from 'react';

import { createClientRender, fireEvent, installPointerEvent, screen } from '../../../libs/testing';
import { Button } from '../Button';

describe('Button', () => {
  installPointerEvent();

  const render = createClientRender();

  test('should get correct ref', () => {
    const ref = createRef<HTMLButtonElement>();

    render(<Button ref={ref} data-testid="button" />);

    expect(ref.current).toBe(screen.getByTestId('button'));
  });

  test('should pass className', () => {
    render(<Button className="my-button" data-testid="button" />);

    expect(screen.getByTestId('button').className).toMatch(/my-button/);
  });

  test('should call onPress after mouse down', () => {
    const onPress = jest.fn();

    render(<Button onPress={onPress} data-testid="button" />);
    const button = screen.getByTestId('button');

    fireEvent.pointerDown(button);
    fireEvent.pointerUp(button);

    expect(onPress).toBeCalled();
  });

  test('should not call onPress when disabled', () => {
    const onPress = jest.fn();

    render(<Button onPress={onPress} data-testid="button" disabled />);
    const button = screen.getByTestId('button');

    fireEvent.pointerDown(button);
    fireEvent.pointerUp(button);

    expect(onPress).not.toBeCalled();
  });
});
