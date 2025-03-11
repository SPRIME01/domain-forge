import type { Meta, StoryObj } from '@storybook/react';
import DomainModelVisualizer from './DomainModelVisualizer';

/**
 * The DomainModelVisualizer component provides a visual representation of the domain model,
 * showing entities, their relationships, and other domain elements in an interactive diagram.
 */
const meta = {
  title: 'Core/DomainModelVisualizer',
  component: DomainModelVisualizer,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Interactive visualization of domain models with entities and relationships.'
      }
    }
  }
} satisfies Meta<typeof DomainModelVisualizer>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default state of the visualizer with no data
 */
export const Empty: Story = {
  args: {}
};

/**
 * Visualizer with sample domain model data
 */
export const WithSampleData: Story = {
  args: {
    model: {
      entities: [
        { name: 'User', properties: ['id', 'username', 'email'] },
        { name: 'Order', properties: ['id', 'orderDate', 'status'] }
      ],
      relationships: [
        { source: 'User', target: 'Order', type: 'OneToMany' }
      ]
    }
  }
};
