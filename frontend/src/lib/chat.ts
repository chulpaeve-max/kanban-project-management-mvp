const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
};

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

export async function sendMessage(
  message: string,
  conversationHistory: Message[]
): Promise<{ response: string; boardUpdate: boolean }> {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No authentication token found');
  }
  
  const history = conversationHistory.map(msg => ({
    role: msg.role,
    content: msg.content
  }));
  
  const response = await fetch(`${API_BASE}/api/ai/chat`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      message,
      conversation_history: history
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to send message');
  }
  
  const data = await response.json();
  return {
    response: data.response,
    boardUpdate: !!data.board_update
  };
}

export function getConversationHistory(): Message[] {
  if (typeof window === 'undefined') return [];
  
  const stored = sessionStorage.getItem('chat_history');
  if (!stored) return [];
  
  try {
    const parsed = JSON.parse(stored);
    return parsed.map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));
  } catch {
    return [];
  }
}

export function saveConversationHistory(history: Message[]): void {
  if (typeof window === 'undefined') return;
  sessionStorage.setItem('chat_history', JSON.stringify(history));
}

export function clearConversationHistory(): void {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem('chat_history');
}
