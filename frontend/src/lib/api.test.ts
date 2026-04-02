import { describe, it, expect, beforeEach, vi } from 'vitest';
import { fetchBoard, renameColumn, createCard, updateCard, deleteCard, moveCard } from './api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.setItem('kanban_auth_token', 'test-token');
  });

  describe('fetchBoard', () => {
    it('should fetch board data with auth token', async () => {
      const mockBoard = {
        id: 1,
        columns: [
          { id: 1, title: 'To Do', position: 0, cards: [] }
        ]
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockBoard
      });

      const result = await fetchBoard();

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/board', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
      expect(result).toEqual(mockBoard);
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401
      });

      await expect(fetchBoard()).rejects.toThrow('Failed to fetch board');
    });
  });

  describe('renameColumn', () => {
    it('should rename column with auth token', async () => {
      const mockColumn = { id: 1, title: 'New Title', position: 0 };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockColumn
      });

      const result = await renameColumn(1, 'New Title');

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/columns/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify({ title: 'New Title' })
      });
      expect(result).toEqual(mockColumn);
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      await expect(renameColumn(1, 'New Title')).rejects.toThrow('Failed to rename column');
    });
  });

  describe('createCard', () => {
    it('should create card with auth token', async () => {
      const mockCard = { id: 1, title: 'New Card', details: 'Details', column_id: 1, position: 0 };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCard
      });

      const result = await createCard(1, 'New Card', 'Details');

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/cards', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify({ column_id: 1, title: 'New Card', details: 'Details' })
      });
      expect(result).toEqual(mockCard);
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 422
      });

      await expect(createCard(1, 'New Card', 'Details')).rejects.toThrow('Failed to create card');
    });
  });

  describe('updateCard', () => {
    it('should update card with auth token', async () => {
      const mockCard = { id: 1, title: 'Updated', details: 'Updated details', column_id: 1, position: 0 };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCard
      });

      const result = await updateCard(1, 'Updated', 'Updated details');

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/cards/1', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify({ title: 'Updated', details: 'Updated details' })
      });
      expect(result).toEqual(mockCard);
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      await expect(updateCard(1, 'Updated', 'Details')).rejects.toThrow('Failed to update card');
    });
  });

  describe('deleteCard', () => {
    it('should delete card with auth token', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true
      });

      await deleteCard(1);

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/cards/1', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      await expect(deleteCard(1)).rejects.toThrow('Failed to delete card');
    });
  });

  describe('moveCard', () => {
    it('should move card with auth token', async () => {
      const mockCard = { id: 1, title: 'Card', details: '', column_id: 2, position: 1 };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockCard
      });

      const result = await moveCard(1, 2, 1);

      expect(global.fetch).toHaveBeenCalledWith('http://localhost:8000/api/cards/1/move', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        },
        body: JSON.stringify({ target_column_id: 2, position: 1 })
      });
      expect(result).toEqual(mockCard);
    });

    it('should throw error when response is not ok', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      await expect(moveCard(1, 2, 1)).rejects.toThrow('Failed to move card');
    });
  });

  describe('auth token handling', () => {
    it('should throw error when no auth token is present', async () => {
      localStorage.clear();

      await expect(fetchBoard()).rejects.toThrow('No authentication token found');
    });
  });
});
