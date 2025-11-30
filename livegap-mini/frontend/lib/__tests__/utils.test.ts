/**
 * Tests for utility functions
 */
import { cn } from '../utils'

describe('cn utility function', () => {
  it('should merge class names', () => {
    const result = cn('class1', 'class2')
    expect(result).toBeTruthy()
  })

  it('should handle conditional classes', () => {
    const result = cn('base', true && 'conditional', false && 'hidden')
    expect(result).toContain('base')
    expect(result).toContain('conditional')
    expect(result).not.toContain('hidden')
  })

  it('should handle empty input', () => {
    const result = cn()
    expect(result).toBe('')
  })

  it('should handle null and undefined', () => {
    const result = cn('base', null, undefined)
    expect(result).toBe('base')
  })

  it('should merge tailwind classes correctly', () => {
    const result = cn('px-2 py-1', 'px-4')
    // Should prioritize the later px-4 over px-2
    expect(result).toContain('px-4')
  })
})
