import React, { createRef } from 'react';

import { ListItemView } from '..';
import { createClientRender, fireEvent, installPointerEvent, screen } from '../../../libs/testing';

describe('ListItemView', () => {
  installPointerEvent();

  const render = createClientRender();

  test('should render custom element', () => {
    render(
      <ListItemView as="a" data-testid="element">
        Content
      </ListItemView>,
    );

    expect(screen.getByTestId('element')).toHaveProperty('tagName', 'A');
  });

  test('should render children to ContentSlot', () => {
    render(
      <ListItemView>
        <div data-testid="content">Content</div>
      </ListItemView>,
    );

    expect(screen.getByTestId('content')).toBeInTheDocument();
  });

  test('should render content from slots', () => {
    render(
      <ListItemView>
        <ListItemView.Before data-testid="before">Before</ListItemView.Before>
        <ListItemView.Content data-testid="content">Content</ListItemView.Content>
        <ListItemView.After data-testid="after">After</ListItemView.After>
      </ListItemView>,
    );

    expect(screen.getByTestId('before')).toHaveTextContent('Before');
    expect(screen.getByTestId('content')).toHaveTextContent('Content');
    expect(screen.getByTestId('after')).toHaveTextContent('After');
  });

  test('should be interactive by default', () => {
    render(<ListItemView data-testid="element">Content</ListItemView>);

    expect(screen.getByTestId('element')).toHaveAttribute('data-interactive', 'true');
  });

  test('should disable interactive', () => {
    render(
      <ListItemView interactive={false} data-testid="element">
        Content
      </ListItemView>,
    );

    expect(screen.getByTestId('element')).not.toHaveAttribute('data-interactive');
  });

  test('should set data-hovered on hover', () => {
    render(<ListItemView data-testid="element">Content</ListItemView>);

    const element = screen.getByTestId('element');

    expect(element).not.toHaveAttribute('data-hovered');

    fireEvent.hover(element);

    expect(element).toHaveAttribute('data-hovered', 'true');
  });

  test('should set ref for element', () => {
    const ref = createRef<HTMLDivElement>();

    render(
      <ListItemView ref={ref} data-testid="element">
        Content
      </ListItemView>,
    );

    expect(screen.getByTestId('element')).toBe(ref.current);
  });

  test('should call onPress', () => {
    const onPress = jest.fn();

    render(
      <ListItemView data-testid="element" onPress={onPress}>
        Content
      </ListItemView>,
    );

    fireEvent.click(screen.getByTestId('element'));

    expect(onPress).toBeCalled();
  });
});
