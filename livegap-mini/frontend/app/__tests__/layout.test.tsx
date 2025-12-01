import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import RootLayout, { metadata } from '../layout';

describe('RootLayout Component', () => {
  it('renders children correctly', () => {
    const { container } = render(
      <RootLayout>
        <div data-testid="test-child">Test Content</div>
      </RootLayout>
    );
    
    const child = container.querySelector('[data-testid="test-child"]');
    expect(child).toBeInTheDocument();
    expect(child).toHaveTextContent('Test Content');
  });

  it('renders html tag with lang and dark class', () => {
    const { container } = render(
      <RootLayout>
        <div>Content</div>
      </RootLayout>
    );
    
    const html = container.querySelector('html');
    expect(html).toHaveAttribute('lang', 'en');
    expect(html).toHaveClass('dark');
  });

  it('renders body with correct classes', () => {
    const { container } = render(
      <RootLayout>
        <div>Content</div>
      </RootLayout>
    );
    
    const body = container.querySelector('body');
    expect(body).toHaveClass('bg-slate-950');
    expect(body).toHaveClass('text-slate-50');
  });

  it('includes Tailwind CDN script in head', () => {
    const { container } = render(
      <RootLayout>
        <div>Content</div>
      </RootLayout>
    );
    
    const script = container.querySelector('script[src="https://cdn.tailwindcss.com"]');
    expect(script).toBeInTheDocument();
  });

  it('exports correct metadata', () => {
    expect(metadata).toBeDefined();
    expect(metadata.title).toBe('another.ai');
    expect(metadata.description).toBe('Reality check for browser agents');
  });

  it('renders multiple children', () => {
    const { container } = render(
      <RootLayout>
        <div data-testid="child-1">First</div>
        <div data-testid="child-2">Second</div>
      </RootLayout>
    );
    
    expect(container.querySelector('[data-testid="child-1"]')).toBeInTheDocument();
    expect(container.querySelector('[data-testid="child-2"]')).toBeInTheDocument();
  });
});
