/**
 * Tests for UI components
 */
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Button } from '../button'
import { Card, CardHeader, CardTitle, CardContent, CardDescription, CardFooter } from '../card'
import { Badge } from '../badge'
import { Input } from '../input'
import { Label } from '../label'
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '../dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../select'

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

  it('should render with different variants', () => {
    render(<Button variant="destructive">Delete</Button>)
    expect(screen.getByText('Delete')).toBeInTheDocument()
  })

  it('should render with different sizes', () => {
    render(<Button size="sm">Small</Button>)
    expect(screen.getByText('Small')).toBeInTheDocument()
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

  it('should render card with description and footer', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Title</CardTitle>
          <CardDescription>Description</CardDescription>
        </CardHeader>
        <CardContent>Content</CardContent>
        <CardFooter>Footer</CardFooter>
      </Card>
    )
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Footer')).toBeInTheDocument()
  })

  it('should apply custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>)
    expect(container.firstChild).toHaveClass('custom-class')
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

  it('should render outline variant', () => {
    render(<Badge variant="outline">Outline</Badge>)
    expect(screen.getByText('Outline')).toBeInTheDocument()
  })

  it('should render secondary variant', () => {
    render(<Badge variant="secondary">Secondary</Badge>)
    expect(screen.getByText('Secondary')).toBeInTheDocument()
  })
})

describe('Input Component', () => {
  it('should render with placeholder', () => {
    render(<Input placeholder="Enter text" />)
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument()
  })

  it('should accept user input', () => {
    render(<Input data-testid="input" />)
    const input = screen.getByTestId('input') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'test value' } })
    expect(input.value).toBe('test value')
  })

  it('should be disabled when disabled prop is true', () => {
    render(<Input disabled data-testid="input" />)
    expect(screen.getByTestId('input')).toBeDisabled()
  })

  it('should support different input types', () => {
    const { rerender } = render(<Input type="email" data-testid="input" />)
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'email')
    
    rerender(<Input type="password" data-testid="input" />)
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'password')
  })
})

describe('Label Component', () => {
  it('should render with text', () => {
    render(<Label>Field Label</Label>)
    expect(screen.getByText('Field Label')).toBeInTheDocument()
  })

  it('should associate with input via htmlFor', () => {
    render(
      <div>
        <Label htmlFor="test-input">Username</Label>
        <Input id="test-input" />
      </div>
    )
    const label = screen.getByText('Username')
    expect(label).toHaveAttribute('for', 'test-input')
  })
})

describe('Dialog Component', () => {
  it('should open dialog when trigger is clicked', () => {
    render(
      <Dialog>
        <DialogTrigger asChild>
          <Button>Open</Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dialog Title</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )

    expect(screen.queryByText('Dialog Title')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Open'))
    expect(screen.getByText('Dialog Title')).toBeInTheDocument()
  })

  it('should render dialog with description and footer', () => {
    render(
      <Dialog open>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Title</DialogTitle>
            <DialogDescription>Description</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button>Action</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    )

    expect(screen.getByText('Title')).toBeInTheDocument()
    expect(screen.getByText('Description')).toBeInTheDocument()
    expect(screen.getByText('Action')).toBeInTheDocument()
  })
})

describe('Select Component', () => {
  it('should render select with placeholder', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Choose option" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="opt1">Option 1</SelectItem>
        </SelectContent>
      </Select>
    )

    expect(screen.getByText('Choose option')).toBeInTheDocument()
  })

  it('should show options when clicked', () => {
    render(
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Select" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="opt1">First</SelectItem>
          <SelectItem value="opt2">Second</SelectItem>
        </SelectContent>
      </Select>
    )

    expect(screen.queryByText('First')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Select'))
    expect(screen.getByText('First')).toBeInTheDocument()
    expect(screen.getByText('Second')).toBeInTheDocument()
  })
})

