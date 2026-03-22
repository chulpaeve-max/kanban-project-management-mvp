import { describe, it, expect, beforeEach, vi } from 'vitest';
import { login, logout, getToken, isAuthenticated } from './auth';

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

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
});

// Mock fetch
global.fetch = vi.fn();

describe('auth', () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('login stores token', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: 'test-token', username: 'user' }),
    });

    await login('user', 'password');
    expect(getToken()).toBe('test-token');
  });

  it('logout clears token', async () => {
    localStorageMock.setItem('kanban_auth_token', 'test-token');
    (global.fetch as any).mockResolvedValueOnce({ ok: true });

    await logout();
    expect(getToken()).toBeNull();
  });

  it('isAuthenticated returns true when token exists', () => {
    localStorageMock.setItem('kanban_auth_token', 'test-token');
    expect(isAuthenticated()).toBe(true);
  });

  it('isAuthenticated returns false when no token', () => {
    expect(isAuthenticated()).toBe(false);
  });
});
