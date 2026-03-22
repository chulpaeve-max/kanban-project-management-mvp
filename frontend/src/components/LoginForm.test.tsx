import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from './LoginForm';
import * as auth from '@/lib/auth';

vi.mock('@/lib/auth');

describe('LoginForm', () => {
  it('renders form', () => {
    render(<LoginForm onLoginSuccess={() => {}} />);
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('submit with valid credentials', async () => {
    const onLoginSuccess = vi.fn();
    vi.mocked(auth.login).mockResolvedValueOnce({
      token: 'test-token',
      username: 'user',
    });

    render(<LoginForm onLoginSuccess={onLoginSuccess} />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(onLoginSuccess).toHaveBeenCalled();
    });
  });

  it('submit with invalid credentials', async () => {
    vi.mocked(auth.login).mockRejectedValueOnce(new Error('Invalid credentials'));

    render(<LoginForm onLoginSuccess={() => {}} />);

    fireEvent.change(screen.getByLabelText(/username/i), {
      target: { value: 'user' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    });
  });
});
