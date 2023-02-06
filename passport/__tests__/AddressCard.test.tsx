import React from 'react';

import { AddressCard } from '..';
import { createClientRender, screen } from '../../../libs/testing';
import { AddressType } from '../constants';

describe('AddressCard', () => {
  const render = createClientRender();

  test('should set custom class name', () => {
    render(
      <AddressCard className="custom-class" addressType={AddressType.Home} data-testid="element" />,
    );

    expect(screen.getByTestId('element')).toHaveClass('custom-class');
  });
});
