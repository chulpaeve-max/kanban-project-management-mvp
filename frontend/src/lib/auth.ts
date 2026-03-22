const TOKEN_KEY = 'kanban_auth_token';

export type LoginResponse = {
  token: string;
  username: string;
};

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  const data = await response.json();
  localStorage.setItem(TOKEN_KEY, data.token);
  return data;
}

export async function logout(): Promise<void> {
  const token = getToken();
  if (token) {
    await fetch('/api/auth/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }
  localStorage.removeItem(TOKEN_KEY);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export async function getCurrentUser(): Promise<{ username: string } | null> {
  const token = getToken();
  if (!token) {
    return null;
  }

  const response = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    localStorage.removeItem(TOKEN_KEY);
    return null;
  }

  return response.json();
}
