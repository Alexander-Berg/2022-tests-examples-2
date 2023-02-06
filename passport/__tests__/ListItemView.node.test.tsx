/**
 * @jest-environment node
 */
import React from 'react';

import { createServerRender } from '../../../libs/testing';
import { ListItemView } from '../ListItemView';

describe('ListItemView (ssr)', () => {
  const render = createServerRender();

  test('should render without errors', () => {
    expect(() => {
      render(
        <ListItemView>
          <ListItemView.Before>Before</ListItemView.Before>
          <ListItemView.Content>Content</ListItemView.Content>
          <ListItemView.After>After</ListItemView.After>
        </ListItemView>,
      );
    }).not.toThrowError();
  });
});
