import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import HomePage from '../page';

// Mock ReactMarkdown
jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }: { children: string }) => <div>{children}</div>,
}));

// Mock fetch globally
global.fetch = jest.fn();

// Mock crypto.randomUUID
const mockUUID = jest.fn(() => 'mock-uuid-123');
Object.defineProperty(global, 'crypto', {
  value: {
    randomUUID: mockUUID,
  },
  writable: true,
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('HomePage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.clear();
    jest.useFakeTimers();
    
    // Default mock for fetch - returns a "done" status for any polling requests
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      // Default response for polling requests
      return Promise.resolve({
        ok: true,
        json: async () => ({
          status: 'done',
          results: [],
        }),
      });
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Initial Render', () => {
    it('renders the header with branding', () => {
      render(<HomePage />);
      expect(screen.getByText('another.ai')).toBeInTheDocument();
      expect(screen.getByText('A')).toBeInTheDocument();
      expect(screen.getByRole('link', { name: /about/i })).toBeInTheDocument();
    });

    it('renders sidebar with Test Runs heading and New button', () => {
      render(<HomePage />);
      expect(screen.getByText(/test runs/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /new/i })).toBeInTheDocument();
    });

    it('shows empty state when no test runs exist', () => {
      render(<HomePage />);
      expect(screen.getByText('Run your first agent test')).toBeInTheDocument();
      expect(screen.getByText(/We run your reference agent against 10 SaaS websites/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create your first test/i })).toBeInTheDocument();
    });

    it('renders search input', () => {
      render(<HomePage />);
      expect(screen.getByPlaceholderText('Search runs…')).toBeInTheDocument();
    });
  });

  describe('LocalStorage Integration', () => {
    it('loads persisted runs from localStorage on mount', async () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Test Run 1',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 75,
          results: [],
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Test Run 1')[0]).toBeInTheDocument();
      });
      expect(screen.getByText(/Success:.*75/)).toBeInTheDocument();
    });

    it('persists runs to localStorage when they change', async () => {
      render(<HomePage />);
      
      // Open modal and create test
      fireEvent.click(screen.getByRole('button', { name: /create your first test/i }));
      
      const testNameInput = screen.getByPlaceholderText(/Slack onboarding/i);
      fireEvent.change(testNameInput, { target: { value: 'New Test' } });

      // Mock fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ run_id: 'backend-run-123', status: 'pending', created_at: new Date().toISOString() }),
      });

      fireEvent.click(screen.getByRole('button', { name: /run test on 10 saas sites/i }));

      await waitFor(() => {
        const stored = localStorageMock.getItem('lg_runs');
        expect(stored).toBeTruthy();
        const parsed = JSON.parse(stored!);
        expect(parsed).toHaveLength(1);
        expect(parsed[0].name).toBe('New Test');
      });
    });

    it('handles localStorage errors gracefully', () => {
      // Mock localStorage.getItem to throw
      jest.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new Error('localStorage error');
      });

      // Should not crash
      expect(() => render(<HomePage />)).not.toThrow();
    });
  });

  describe('Create Test Modal', () => {
    it('opens modal when New button is clicked', () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('New Agent Test')).toBeInTheDocument();
    });

    it('closes modal when Close button is clicked', () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      fireEvent.click(screen.getByRole('button', { name: /close/i }));
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('validates test name is required', async () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      
      fireEvent.click(screen.getByRole('button', { name: /run test on 10 saas sites/i }));
      
      await waitFor(() => {
        expect(screen.getByText('Test name required')).toBeInTheDocument();
      });
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('creates test run with valid data', async () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      
      const testNameInput = screen.getByPlaceholderText(/Slack onboarding/i);
      fireEvent.change(testNameInput, { target: { value: 'Integration Test' } });

      const goalSelect = screen.getByDisplayValue(/Can you show me the pricing/i);
      fireEvent.change(goalSelect, { target: { value: "How do I create an account or get started?" } });

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ run_id: 'run-456', status: 'pending', created_at: new Date().toISOString() }),
      });

      fireEvent.click(screen.getByRole('button', { name: /run test on 10 saas sites/i }));

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/run-reality-check'),
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: "How do I create an account or get started?" }),
          })
        );
      });

      // Modal should close
      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      // Test run should appear in sidebar
      await waitFor(() => {
        expect(screen.getAllByText('Integration Test')[0]).toBeInTheDocument();
      });
    });

    it('displays error when API call fails', async () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      
      const testNameInput = screen.getByPlaceholderText(/Slack onboarding/i);
      fireEvent.change(testNameInput, { target: { value: 'Failing Test' } });

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: async () => 'Server error',
      });

      fireEvent.click(screen.getByRole('button', { name: /run test on 10 saas sites/i }));

      await waitFor(() => {
        expect(screen.getByText('Server error')).toBeInTheDocument();
      });
    });

    it('disables buttons while loading', async () => {
      render(<HomePage />);
      fireEvent.click(screen.getByRole('button', { name: /new/i }));
      
      const testNameInput = screen.getByPlaceholderText(/Slack onboarding/i);
      fireEvent.change(testNameInput, { target: { value: 'Loading Test' } });

      (global.fetch as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

      fireEvent.click(screen.getByRole('button', { name: /run test on 10 saas sites/i }));

      // Button should show loading state
      expect(screen.getByRole('button', { name: /running test/i })).toBeDisabled();
    });
  });

  describe('Search Functionality', () => {
    beforeEach(() => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Slack Sales Test',
          goal: "I'm trying to talk to sales — can you help me reach the sales team?" as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 80,
          results: [],
        },
        {
          id: 'run-2',
          name: 'HubSpot Pricing',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 65,
          results: [],
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));
    });

    it('filters runs by name', async () => {
      render(<HomePage />);
      
      // Wait for runs to load
      await waitFor(() => {
        expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search runs…');
      fireEvent.change(searchInput, { target: { value: 'Slack' } });
      
      expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
      expect(screen.queryByText('HubSpot Pricing')).toBeNull();
    });

    it('filters runs by goal', async () => {
      render(<HomePage />);
      
      // Wait for runs to load
      await waitFor(() => {
        expect(screen.getByText('HubSpot Pricing')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search runs…');
      fireEvent.change(searchInput, { target: { value: 'pricing' } });
      
      // Should show HubSpot Pricing in sidebar, Slack Sales Test should be filtered out from sidebar
      await waitFor(() => {
        expect(screen.getByText('HubSpot Pricing')).toBeInTheDocument();
      });
      
      // Check that sidebar only has one run button visible (HubSpot Pricing)
      const sidebar = document.querySelector('aside');
      expect(sidebar).toBeInTheDocument();
      const runButtons = sidebar?.querySelectorAll('button[class*="rounded-lg"]');
      expect(runButtons).toHaveLength(1);
    });

    it('shows all runs when search is cleared', async () => {
      render(<HomePage />);
      
      // Wait for runs to load
      await waitFor(() => {
        expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search runs…');
      fireEvent.change(searchInput, { target: { value: 'Slack' } });
      fireEvent.change(searchInput, { target: { value: '' } });
      
      expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
      expect(screen.getByText('HubSpot Pricing')).toBeInTheDocument();
    });

    it('is case-insensitive', async () => {
      render(<HomePage />);
      
      // Wait for runs to load
      await waitFor(() => {
        expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search runs…');
      fireEvent.change(searchInput, { target: { value: 'SLACK' } });
      
      expect(screen.getAllByText('Slack Sales Test')[0]).toBeInTheDocument();
    });
  });

  describe('Run Selection and Display', () => {
    beforeEach(() => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Test Run 1',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: '2025-11-30T10:00:00Z',
          overallSuccessRate: 75,
          results: [
            {
              site_id: 'site-1',
              site_name: 'Slack',
              url: 'https://slack.com',
              success: true,
              reason: 'Successfully found pricing',
              video_url: 'https://example.com/video.mp4',
              steps: [],
              report: '# Test Report\n\nSuccess!',
            },
            {
              site_id: 'site-2',
              site_name: 'HubSpot',
              url: 'https://hubspot.com',
              success: false,
              reason: 'Could not locate pricing page',
              video_url: null,
              steps: null,
              report: null,
            },
          ],
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));
    });

    it('auto-selects first run on mount', async () => {
      render(<HomePage />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Test Run 1')[0]).toBeInTheDocument();
      });
      expect(screen.getByText('Sites Evaluated')).toBeInTheDocument();
    });

    it('displays run details when selected', async () => {
      render(<HomePage />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Test Run 1')[0]).toBeInTheDocument();
      });
      expect(screen.getByText('Can you show me the pricing or plans for this company?')).toBeInTheDocument();
      expect(screen.getByText(/^75$/)).toBeInTheDocument();
      expect(screen.getByText('Total: 2')).toBeInTheDocument();
    });

    it('displays site results in table', () => {
      render(<HomePage />);
      expect(screen.getByText('Slack')).toBeInTheDocument();
      expect(screen.getByText('HubSpot')).toBeInTheDocument();
      expect(screen.getByText('Successfully found pricing')).toBeInTheDocument();
      expect(screen.getByText('Could not locate pricing page')).toBeInTheDocument();
    });

    it('shows success badge for successful sites', () => {
      render(<HomePage />);
      const successBadges = screen.getAllByText('Success');
      expect(successBadges).toHaveLength(1);
    });

    it('shows failed badge for failed sites', () => {
      render(<HomePage />);
      const failedBadges = screen.getAllByText('Failed');
      expect(failedBadges).toHaveLength(1);
    });

    it('renders clickable URLs', () => {
      render(<HomePage />);
      const slackLink = screen.getByRole('link', { name: /slack.com/i });
      expect(slackLink).toHaveAttribute('href', 'https://slack.com');
      expect(slackLink).toHaveAttribute('target', '_blank');
    });
  });

  describe('Video Modal', () => {
    beforeEach(() => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Video Test',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 100,
          results: [
            {
              site_id: 'site-1',
              site_name: 'TestSite',
              url: 'https://test.com',
              success: true,
              reason: 'Success',
              video_url: 'https://example.com/test-video.mp4',
              steps: [],
              report: null,
            },
          ],
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));
    });

    it('opens video modal when Video button is clicked', async () => {
      render(<HomePage />);
      
      await waitFor(() => {
        const videoButtons = screen.getAllByRole('button');
        expect(videoButtons.some(btn => btn.textContent === 'Video')).toBe(true);
      });
      
      const videoButtons = screen.getAllByRole('button');
      const artifactVideoButton = videoButtons.find(btn => 
        btn.textContent === 'Video' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactVideoButton!);
      
      expect(screen.getByText('Recorded Session')).toBeInTheDocument();
      const video = document.querySelector('video');
      expect(video).toBeInTheDocument();
    });

    it('closes video modal when Close button is clicked', () => {
      render(<HomePage />);
      const videoButtons = screen.getAllByRole('button');
      const artifactVideoButton = videoButtons.find(btn => 
        btn.textContent === 'Video' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactVideoButton!);
      fireEvent.click(screen.getAllByRole('button', { name: /close/i })[0]);
      
      expect(screen.queryByText('Recorded Session')).not.toBeInTheDocument();
    });

    it('displays video with correct src', () => {
      render(<HomePage />);
      const videoButtons = screen.getAllByRole('button');
      const artifactVideoButton = videoButtons.find(btn => 
        btn.textContent === 'Video' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactVideoButton!);
      
      const video = document.querySelector('video');
      expect(video).toHaveAttribute('src', 'https://example.com/test-video.mp4');
      expect(video).toHaveAttribute('controls');
      expect(video).toHaveAttribute('autoPlay');
    });
  });

  describe('Report Modal', () => {
    beforeEach(() => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Test with Report',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 100,
          results: [
            {
              site_id: 'site-1',
              site_name: 'TestSite',
              url: 'https://test.com',
              success: true,
              reason: 'Success',
              video_url: null,
              steps: [],
              report: '# Test Report\n\nThis is a **bold** test.',
            },
          ],
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));
    });

    it('opens report modal when Report button is clicked', () => {
      render(<HomePage />);
      const reportButtons = screen.getAllByRole('button');
      const artifactReportButton = reportButtons.find(btn => 
        btn.textContent === 'Report' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactReportButton!);
      
      expect(screen.getByText('Report – TestSite')).toBeInTheDocument();
    });

    it('closes report modal when Close button is clicked', () => {
      render(<HomePage />);
      const reportButtons = screen.getAllByRole('button');
      const artifactReportButton = reportButtons.find(btn => 
        btn.textContent === 'Report' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactReportButton!);
      fireEvent.click(screen.getAllByRole('button', { name: /close/i })[0]);
      
      expect(screen.queryByText('Report – TestSite')).not.toBeInTheDocument();
    });

    it('renders markdown content in report', () => {
      render(<HomePage />);
      const reportButtons = screen.getAllByRole('button');
      const artifactReportButton = reportButtons.find(btn => 
        btn.textContent === 'Report' && btn.classList.contains('rounded-md')
      );
      fireEvent.click(artifactReportButton!);
      
      // The mock renders markdown as plain text, so look for the raw content
      expect(screen.getByText(/Test Report/i)).toBeInTheDocument();
      expect(screen.getByText(/This is a/i)).toBeInTheDocument();
      expect(screen.getByText(/bold/i)).toBeInTheDocument();
    });
  });

  describe('Polling for Run Status', () => {
    it('polls for pending runs and updates status', async () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Polling Test',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 0,
          results: [],
          runId: 'backend-run-123',
          status: 'pending' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          status: 'done',
          result: {
            goal: 'Can you show me the pricing or plans for this company?',
            overall_success_rate: 80,
            total_sites: 10,
            successful_sites: 8,
            failed_sites: 2,
            results: [
              {
                site_id: 'site-1',
                site_name: 'Slack',
                url: 'https://slack.com',
                success: true,
                reason: 'Found pricing',
                video_url: null,
                steps: null,
                report: null,
              },
            ],
          },
        }),
      });

      render(<HomePage />);

      // Should show pending status
      expect(screen.getByText('Queued...')).toBeInTheDocument();

      // Advance timers to trigger polling
      jest.advanceTimersByTime(3000);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/run/backend-run-123')
        );
      });

      // Status should update to done - use regex to find text with % in separate span
      await waitFor(() => {
        expect(screen.getByText(/^80$/)).toBeInTheDocument();
      });
    });

    it('displays loading state for running tests', () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Running Test',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 0,
          results: [],
          runId: 'backend-run-456',
          status: 'running' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      expect(screen.getByText('Running test...')).toBeInTheDocument();
      expect(screen.getByText('Processing sites...')).toBeInTheDocument();
    });

    it('displays error state for failed tests', () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Failed Test',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 0,
          results: [],
          runId: 'backend-run-789',
          status: 'error' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      expect(screen.getByText('Test failed')).toBeInTheDocument();
    });
  });

  describe('Success Rate Display', () => {
    it('shows green color for high success rate (>=70%)', () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'High Success',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 85,
          results: [],
          status: 'done' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      const successDiv = screen.getByText(/^85$/).closest('div');
      expect(successDiv).toHaveClass('text-emerald-300');
    });

    it('shows yellow color for medium success rate (40-69%)', () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Medium Success',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 55,
          results: [],
          status: 'done' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      const successDiv = screen.getByText(/^55$/).closest('div');
      expect(successDiv).toHaveClass('text-yellow-300');
    });

    it('shows red color for low success rate (<40%)', () => {
      const mockRuns = [
        {
          id: 'run-1',
          name: 'Low Success',
          goal: 'Can you show me the pricing or plans for this company?' as const,
          createdAt: new Date().toISOString(),
          overallSuccessRate: 25,
          results: [],
          status: 'done' as const,
        },
      ];
      localStorageMock.setItem('lg_runs', JSON.stringify(mockRuns));

      render(<HomePage />);
      const successDiv = screen.getByText(/^25$/).closest('div');
      expect(successDiv).toHaveClass('text-red-300');
    });
  });
});
