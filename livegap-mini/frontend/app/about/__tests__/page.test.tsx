/**
 * Tests for the About page
 */
import { render, screen } from '@testing-library/react'
import AboutPage from '../page'

describe('About Page', () => {
  it('should render about page', () => {
    render(<AboutPage />)
    // Basic smoke test - check if page renders
    expect(document.body).toBeTruthy()
  })
})
