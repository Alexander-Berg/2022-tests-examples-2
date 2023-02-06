import React, { RefObject, VFC, createRef, useContext, useImperativeHandle } from 'react';

import { ThemeProvider, ThemeValue } from '@yandex-id/design-system';
import { ThemeContext } from '@yandex-id/design-system/ThemeContext';

import { Snackbar } from '.';
import { createClientRender, screen } from '../../libs/testing';

const ThemeFixture: VFC<{ contextRef: RefObject<ThemeValue> }> = (props) => {
  const context = useContext(ThemeContext);

  useImperativeHandle(props.contextRef, () => context);

  return null;
};

describe('Snackbar', () => {
  const render = createClientRender();

  it('should have custom class name', () => {
    render(<Snackbar data-testid="snackbar" className="test-class" />);

    expect(screen.getByTestId('snackbar')).toHaveClass('test-class');
  });

  it('should passed html attributes', () => {
    render(<Snackbar data-testid="snackbar" title="tooltip" style={{ zIndex: 1000 }} />);

    expect(screen.getByTestId('snackbar')).toHaveStyle({ zIndex: 1000 });
    expect(screen.getByTestId('snackbar')).toHaveAttribute('title', 'tooltip');
  });

  it('should contain content slot', () => {
    render(
      <Snackbar data-testid="snackbar">
        <Snackbar.Content data-testid="slot">slot content</Snackbar.Content>
      </Snackbar>,
    );

    expect(screen.getByTestId('slot')).toBeInTheDocument();
  });

  it('should contain before slot', () => {
    render(
      <Snackbar data-testid="snackbar">
        <Snackbar.Before data-testid="slot">slot content</Snackbar.Before>
      </Snackbar>,
    );

    expect(screen.getByTestId('slot')).toBeInTheDocument();
  });

  it('should contain after slot', () => {
    render(
      <Snackbar data-testid="snackbar">
        <Snackbar.After data-testid="slot">slot content</Snackbar.After>
      </Snackbar>,
    );

    expect(screen.getByTestId('slot')).toBeInTheDocument();
  });

  it('should use children by default for content', () => {
    render(
      <Snackbar data-testid="snackbar">
        <span data-testid="content">children</span>
      </Snackbar>,
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  it('should set ref', () => {
    const ref = createRef<HTMLDivElement>();

    render(
      <Snackbar ref={ref} data-testid="snackbar">
        children
      </Snackbar>,
    );

    expect(screen.getByTestId('snackbar')).toBe(ref.current);
  });

  it('should contain progress if duration passed', () => {
    const { setProps } = render(
      <Snackbar data-testid="snackbar">
        <Snackbar.Progress data-testid="progress" />
      </Snackbar>,
    );

    expect(screen.queryByTestId('progress')).not.toBeInTheDocument();

    setProps({ duration: 5000 });

    expect(screen.getByTestId('progress')).toBeInTheDocument();
  });

  it('should set animation duration on progress', () => {
    render(
      <Snackbar duration={1234} data-testid="snackbar">
        <Snackbar.Progress data-testid="progress" />
      </Snackbar>,
    );

    expect(screen.getByTestId('progress')).toHaveStyle({ animationDuration: '1234ms' });
  });

  it('should override color schema to dark by default', () => {
    const ref = createRef<ThemeValue>();

    render(
      <ThemeProvider colorScheme="light">
        <Snackbar>
          <ThemeFixture contextRef={ref} />
        </Snackbar>
      </ThemeProvider>,
    );

    expect(ref.current?.colorScheme).toBe('dark');
  });

  it('should override color schema to light', () => {
    const ref = createRef<ThemeValue>();

    render(
      <ThemeProvider colorScheme="dark">
        <Snackbar colorScheme="light">
          <ThemeFixture contextRef={ref} />
        </Snackbar>
      </ThemeProvider>,
    );

    expect(ref.current?.colorScheme).toBe('light');
  });
});
