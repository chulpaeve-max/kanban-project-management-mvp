const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('kanban_auth_token');
}

function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

export async function fetchBoard() {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  const response = await fetch(`${API_BASE}/api/board`, {
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch board');
  }
  
  return response.json();
}

export async function renameColumn(columnId: number, title: string) {
  const response = await fetch(`${API_BASE}/api/columns/${columnId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ title }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to rename column');
  }
  
  return response.json();
}

export async function createCard(columnId: number, title: string, details: string) {
  const response = await fetch(`${API_BASE}/api/cards`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ column_id: columnId, title, details }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to create card');
  }
  
  return response.json();
}

export async function updateCard(cardId: number, title?: string, details?: string) {
  const response = await fetch(`${API_BASE}/api/cards/${cardId}`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ title, details }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update card');
  }
  
  return response.json();
}

export async function deleteCard(cardId: number) {
  const response = await fetch(`${API_BASE}/api/cards/${cardId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to delete card');
  }
}

export async function moveCard(cardId: number, targetColumnId: number, position: number) {
  const response = await fetch(`${API_BASE}/api/cards/${cardId}/move`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({ target_column_id: targetColumnId, position }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to move card');
  }
  
  return response.json();
}
