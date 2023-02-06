import React from 'react';

import { Story } from '@storybook/react';

import { Card } from '../../Card';

import './base-story-styles.css';

const listItems = new Array(10).fill(null).map((_, index) => `Item ${index + 1}`);

export const HermioneDefault: Story = () => {
  return (
    <div data-testid="story">
      <Card>
        {listItems.map((item) => (
          <div key={item}>{item}</div>
        ))}
      </Card>
      <Card>
        {listItems.map((item) => (
          <div key={item}>{item}</div>
        ))}
      </Card>
    </div>
  );
};
