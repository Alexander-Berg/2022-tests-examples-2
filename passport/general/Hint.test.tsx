import React, { AnchorHTMLAttributes, FC } from 'react';

import { PressProps, UseHoverProps, UseHoverResult, useHover } from '@use-platform/react';

import { createClientRender, fireEvent, installPointerEvent } from '../../libs/testing';
import { Hint } from './Hint';

const useHoverMocked = useHover as jest.Mock<UseHoverResult, [UseHoverProps]>;

jest.mock('@use-platform/react', () => {
  const source = jest.requireActual('@use-platform/react');

  return {
    ...source,
    __esModule: true,
    useHover: jest.fn<UseHoverResult, [UseHoverProps]>(() => ({
      isHovered: false,
      hoverProps: {},
    })),
  };
});

describe('Hint', () => {
  installPointerEvent();

  const render = createClientRender();

  test('should fire onClick event on click', () => {
    const renderFn = () => <></>;
    const onClickSpy = jest.fn();

    const { container } = render(<Hint before={renderFn} text="Some text" onPress={onClickSpy} />);

    fireEvent.pointerDown(container.firstElementChild as Element);
    fireEvent.pointerUp(container.firstElementChild as Element);
    expect(onClickSpy).toHaveBeenCalled();
  });

  // TODO: убрать тайпкаст когда срастется PASSP-36029
  (test as unknown as jest.It).concurrent.each`
    event
    ${'onPress'}
    ${'onPressEnd'}
    ${'onPressStart'}
    ${'onPressUp'}
    `('should have clickable mod if component has $event handler', ({ event }) => {
    const renderFn = () => <></>;
    const pressProps: PressProps = {
      [event]: jest.fn(),
    };
    const { container } = render(<Hint before={renderFn} text="Some text" {...pressProps} />);

    expect(container.firstElementChild).toHaveAttribute('data-pressable', 'true');
  });

  test('hint as link should be clickable', () => {
    const renderFn = () => <></>;

    const { container } = render(
      <Hint before={renderFn} text="Some text" href="https://example.com" tabIndex={42} />,
    );

    expect(container.firstElementChild).toHaveAttribute('data-pressable', 'true');
  });

  test('should set hover event handlers', () => {
    const renderFn = () => <></>;
    const pointerEnterSpy = jest.fn();
    const pointerLeaveSpy = jest.fn();

    useHoverMocked.mockReturnValue({
      isHovered: false,
      hoverProps: { onPointerEnter: pointerEnterSpy, onPointerLeave: pointerLeaveSpy },
    });

    const { container } = render(<Hint before={renderFn} text="Some text" />);

    fireEvent.pointerEnter(container.firstElementChild as Element);
    expect(pointerEnterSpy).toHaveBeenCalled();

    fireEvent.pointerLeave(container.firstElementChild as Element);
    expect(pointerLeaveSpy).toHaveBeenCalled();
  });

  test('should set hover mod if component is hovered', () => {
    const renderFn = () => <></>;

    useHoverMocked.mockReturnValue({ isHovered: true, hoverProps: {} });

    const { container } = render(<Hint before={renderFn} text="Some text" />);

    expect(container.firstElementChild).toHaveAttribute('data-hovered');
  });

  test("should disable hover if component doesn't have any press handlers", () => {
    const renderFn = () => <></>;

    render(<Hint before={renderFn} text="Some text" />);

    expect(useHoverMocked).toHaveBeenCalledWith(expect.objectContaining({ disabled: true }));
  });

  (test as unknown as jest.It).concurrent.each`
    event
    ${'onPress'}
    ${'onPressEnd'}
    ${'onPressStart'}
    ${'onPressUp'}
    `('should not disable hover if component has $event handler', ({ event }) => {
    const pressProps: PressProps = {
      [event]: jest.fn(),
    };
    const renderFn = () => <></>;

    useHoverMocked.mockClear();

    render(<Hint before={renderFn} text="Some text" {...pressProps} />);

    expect(useHoverMocked.mock.calls[0][0].disabled).toBeFalsy();
  });

  (test as unknown as jest.It).concurrent.each`
    event
    ${'onPress'}
    ${'onPressEnd'}
    ${'onPressStart'}
    ${'onPressUp'}
    `('should set tabindex automatically, if component has $event handler', ({ event }) => {
    const pressProps: PressProps = {
      [event]: jest.fn(),
    };
    const renderFn = () => <></>;

    useHoverMocked.mockClear();

    const { container } = render(<Hint before={renderFn} text="Some text" {...pressProps} />);

    expect(container.firstElementChild).toHaveAttribute('tabindex', '0');
  });

  test('should set custom tabindex', () => {
    const renderFn = () => <></>;

    const { container } = render(
      <Hint before={renderFn} text="Some text" onPress={jest.fn()} tabIndex={42} />,
    );

    expect(container.firstElementChild).toHaveAttribute('tabindex', '42');
  });

  test('wrapper element should be link with correct attrs', () => {
    const renderFn = () => <></>;

    const { container } = render(
      <Hint
        before={renderFn}
        text="Some text"
        href="https://example.com"
        target="_blank"
        rel="nofollow"
        title="Test link"
        tabIndex={42}
      />,
    );

    const root = container.firstElementChild;

    expect(root?.tagName.toLowerCase()).toBe('a');
    expect(root).toHaveAttribute('href', 'https://example.com');
    expect(root).toHaveAttribute('target', '_blank');
    expect(root).toHaveAttribute('title', 'Test link');
  });

  test('wrapper element should be custom link component', () => {
    type TestComponentProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & {
      to: string;
    };
    const TestComponent: FC<TestComponentProps> = (props) => (
      <a data-testid="test-component" {...props}>
        {props.children}
      </a>
    );

    const renderFn = () => <></>;

    const { container } = render(
      <Hint
        before={renderFn}
        text="Some text"
        as={TestComponent}
        to="https://example.com"
        target="_blank"
        rel="nofollow"
        title="Test link"
        tabIndex={42}
      />,
    );

    expect(container.firstElementChild).toHaveAttribute('data-testid', 'test-component');
  });
});
