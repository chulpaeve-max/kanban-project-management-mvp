"use client";

import { useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { moveCard as moveCardLocal, type BoardData, type Card, type Column } from "@/lib/kanban";
import * as api from "@/lib/api";

type KanbanBoardProps = {
  onBoardLoaded?: () => void;
  refreshTrigger?: number;
};

export const KanbanBoard = ({ onBoardLoaded, refreshTrigger }: KanbanBoardProps) => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  // Load board from API
  useEffect(() => {
    loadBoard();
  }, []);

  // Refresh when trigger changes
  useEffect(() => {
    if (refreshTrigger !== undefined && refreshTrigger > 0) {
      loadBoard();
    }
  }, [refreshTrigger]);

  async function loadBoard() {
    try {
      setLoading(true);
      setError(null);
      const data = await api.fetchBoard();
      
      // Transform API data to BoardData format
      const columns: Column[] = data.columns.map((col: any) => ({
        id: String(col.id),
        title: col.title,
        cardIds: col.cards.map((card: any) => String(card.id)),
      }));
      
      const cards: Record<string, Card> = {};
      data.columns.forEach((col: any) => {
        col.cards.forEach((card: any) => {
          cards[String(card.id)] = {
            id: String(card.id),
            title: card.title,
            details: card.details || "",
          };
        });
      });
      
      setBoard({ columns, cards });
    } catch (err) {
      setError("Failed to load board");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const cardsById = useMemo(() => board?.cards || {}, [board?.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    console.log("🎯 [DragEnd] Started", { activeId: active.id, overId: over?.id });

    if (!over || active.id === over.id || !board) {
      console.log("❌ [DragEnd] Cancelled - no valid drop target");
      return;
    }

    const cardId = active.id as string;
    const overId = over.id as string;

    // Find target column BEFORE optimistic update
    const isOverColumn = board.columns.some(col => col.id === overId);
    let targetColumnId: string;
    
    if (isOverColumn) {
      targetColumnId = overId;
      console.log("📍 [DragEnd] Dropped on column", { columnId: targetColumnId });
    } else {
      // overId is a card, find which column it's in
      const targetCol = board.columns.find(col => col.cardIds.includes(overId));
      if (!targetCol) {
        console.log("❌ [DragEnd] Could not find target column");
        return;
      }
      targetColumnId = targetCol.id;
      console.log("📍 [DragEnd] Dropped on card in column", { columnId: targetColumnId, overCardId: overId });
    }

    // Optimistic update - create completely new object to trigger re-render
    const oldBoard = { ...board, columns: [...board.columns] };
    const newColumns = moveCardLocal(board.columns, cardId, overId);
    
    console.log("🔄 [DragEnd] Applying optimistic update");
    setBoard({
      columns: newColumns,
      cards: board.cards,
    });

    try {
      // Find position in target column after move
      const targetColumn = newColumns.find(col => col.id === targetColumnId);
      if (targetColumn) {
        const position = targetColumn.cardIds.indexOf(cardId);
        const cardIdNum = Number(cardId);
        const columnIdNum = Number(targetColumnId);
        
        console.log("📤 [DragEnd] Sending API request", { 
          cardId: cardIdNum, 
          targetColumnId: columnIdNum, 
          position 
        });
        
        if (!isNaN(cardIdNum) && !isNaN(columnIdNum) && position !== -1) {
          await api.moveCard(cardIdNum, columnIdNum, position);
          console.log("✅ [DragEnd] API request successful");
        } else {
          console.log("⚠️ [DragEnd] Invalid parameters", { cardIdNum, columnIdNum, position });
        }
      }
    } catch (err) {
      // Rollback on error
      console.error("❌ [DragEnd] API request failed, rolling back", err);
      setBoard(oldBoard);
      setError("Failed to move card");
    }
  };

  const handleRenameColumn = async (columnId: string, title: string) => {
    if (!board) return;
    
    // Optimistic update
    const oldBoard = board;
    setBoard({
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    });

    try {
      await api.renameColumn(Number(columnId), title);
    } catch (err) {
      // Rollback on error
      setBoard(oldBoard);
      setError("Failed to rename column");
      console.error(err);
    }
  };

  const handleAddCard = async (columnId: string, title: string, details: string) => {
    if (!board) return;

    try {
      const newCard = await api.createCard(Number(columnId), title, details);
      
      // Update board with new card
      setBoard({
        ...board,
        cards: {
          ...board.cards,
          [String(newCard.id)]: {
            id: String(newCard.id),
            title: newCard.title,
            details: newCard.details || "",
          },
        },
        columns: board.columns.map((column) =>
          column.id === columnId
            ? { ...column, cardIds: [...column.cardIds, String(newCard.id)] }
            : column
        ),
      });
    } catch (err) {
      setError("Failed to create card");
      console.error(err);
    }
  };

  const handleDeleteCard = async (columnId: string, cardId: string) => {
    if (!board) return;
    
    // Optimistic update
    const oldBoard = board;
    setBoard({
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    });

    try {
      await api.deleteCard(Number(cardId));
    } catch (err) {
      // Rollback on error
      setBoard(oldBoard);
      setError("Failed to delete card");
      console.error(err);
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-lg text-[var(--gray-text)]">Loading board...</p>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-lg text-red-600">Failed to load board</p>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      {error && (
        <div className="fixed top-4 right-4 z-50 rounded-lg bg-red-100 border border-red-400 px-4 py-3 text-red-700">
          {error}
          <button onClick={() => setError(null)} className="ml-4 font-bold">×</button>
        </div>
      )}
      
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
            </div>
            <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                Focus
              </p>
              <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                One board. Five columns. Zero clutter.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                cards={column.cardIds.map((cardId) => board.cards[cardId]).filter(Boolean)}
                onRename={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>
    </div>
  );
};
