import React from 'react';

import { Story } from '@storybook/react';

import { Button, variants } from '../../index';

export const Common: Story = (args) => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      {variants.map((variant) => (
        <Button {...args} variant={variant} key={variant}>
          Button variant {variant}
        </Button>
      ))}
    </div>
  );
};

Common.args = {
  size: 'm',
  disabled: false,
};
