import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { KanbanBoard } from "@/components/KanbanBoard";
import * as api from '@/lib/api';

vi.mock('@/lib/api');

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

const mockBoardData = {
  id: 1,
  columns: [
    {
      id: 1,
      title: 'To Do',
      position: 0,
      cards: [
        { id: 1, title: 'Task 1', details: 'Details 1', column_id: 1, position: 0 }
      ]
    },
    {
      id: 2,
      title: 'In Progress',
      position: 1,
      cards: []
    },
    {
      id: 3,
      title: 'Review',
      position: 2,
      cards: []
    },
    {
      id: 4,
      title: 'Testing',
      position: 3,
      cards: []
    },
    {
      id: 5,
      title: 'Done',
      position: 4,
      cards: []
    }
  ]
};

describe("KanbanBoard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (api.fetchBoard as any).mockResolvedValue(mockBoardData);
  });

  it("loads board from API on mount", async () => {
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(api.fetchBoard).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });
  });

  it("displays loading state", () => {
    render(<KanbanBoard />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("displays error state when API fails", async () => {
    (api.fetchBoard as any).mockRejectedValue(new Error('API Error'));
    
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to load board/i)).toBeInTheDocument();
    });
  });

  it("renders five columns after loading", async () => {
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("renames a column and calls API", async () => {
    (api.renameColumn as any).mockResolvedValue({ id: 1, title: 'New Name', position: 0 });
    
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getByText('To Do')).toBeInTheDocument();
    });

    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    
    await waitFor(() => {
      expect(api.renameColumn).toHaveBeenCalledWith(1, 'New Name');
    });
  });

  it("adds a card and calls API", async () => {
    const newCard = { id: 2, title: 'New card', details: 'Notes', column_id: 1, position: 1 };
    (api.createCard as any).mockResolvedValue(newCard);
    
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    await waitFor(() => {
      expect(api.createCard).toHaveBeenCalledWith(1, 'New card', 'Notes');
    });

    await waitFor(() => {
      expect(within(column).getByText("New card")).toBeInTheDocument();
    });
  });

  it("deletes a card and calls API", async () => {
    (api.deleteCard as any).mockResolvedValue(undefined);
    
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    const column = getFirstColumn();
    const deleteButton = within(column).getByRole("button", {
      name: /delete task 1/i,
    });
    await userEvent.click(deleteButton);

    await waitFor(() => {
      expect(api.deleteCard).toHaveBeenCalledWith(1);
    });

    await waitFor(() => {
      expect(within(column).queryByText("Task 1")).not.toBeInTheDocument();
    });
  });

  it("rolls back optimistic update on API error", async () => {
    (api.deleteCard as any).mockRejectedValue(new Error('API Error'));
    
    render(<KanbanBoard />);
    
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    const column = getFirstColumn();
    const deleteButton = within(column).getByRole("button", {
      name: /delete task 1/i,
    });
    await userEvent.click(deleteButton);

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/failed to delete card/i)).toBeInTheDocument();
    }, { timeout: 3000 });

    // Card should be restored after error
    await waitFor(() => {
      expect(within(column).getByText("Task 1")).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
