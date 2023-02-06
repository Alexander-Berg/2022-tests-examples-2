import React from 'react';

import { Story } from '@storybook/react';

import { Button } from '../../index';

export const Interactive: Story = () => {
  return (
    <div data-testid="container" style={{ padding: 8, display: 'inline-flex' }}>
      <Button data-testid="button">Button</Button>
    </div>
  );
};
