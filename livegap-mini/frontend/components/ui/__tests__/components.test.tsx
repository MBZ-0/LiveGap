/**
 * Tests for UI components
 */
import { render } from '@testing-library/react'
import { Button } from '../button'
import { Card, CardHeader, CardTitle, CardContent } from '../card'
import { Badge } from '../badge'

describe('Button Component', () => {
  it('should render button with text', () => {
    const { getByText } = render(<Button>Click me</Button>)
    expect(getByText('Click me')).toBeInTheDocument()
  })

  it('should handle click events', () => {
    const handleClick = jest.fn()
    const { getByText } = render(<Button onClick={handleClick}>Click me</Button>)
    getByText('Click me').click()
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('should be disabled when disabled prop is true', () => {
    const { getByText } = render(<Button disabled>Disabled</Button>)
    expect(getByText('Disabled')).toBeDisabled()
  })
})

describe('Card Component', () => {
  it('should render card with content', () => {
    const { getByText } = render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
        </CardHeader>
        <CardContent>
          Test Content
        </CardContent>
      </Card>
    )
    expect(getByText('Test Title')).toBeInTheDocument()
    expect(getByText('Test Content')).toBeInTheDocument()
  })
})

describe('Badge Component', () => {
  it('should render badge with text', () => {
    const { getByText } = render(<Badge>New</Badge>)
    expect(getByText('New')).toBeInTheDocument()
  })

  it('should apply variant classes', () => {
    const { getByText } = render(<Badge variant="destructive">Error</Badge>)
    expect(getByText('Error')).toBeInTheDocument()
  })
})
