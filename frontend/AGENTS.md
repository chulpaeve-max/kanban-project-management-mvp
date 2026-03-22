# Frontend - Kanban Studio

## Overview

A NextJS 16 frontend application implementing a drag-and-drop Kanban board. Currently a standalone demo with no backend integration.

## Tech Stack

- NextJS 16.1.6 (App Router)
- React 19.2.3
- TypeScript 5
- Tailwind CSS 4
- @dnd-kit (drag and drop)
- Vitest (unit tests)
- Playwright (e2e tests)

## Architecture

### Entry Point
- `src/app/page.tsx` - Root page that renders KanbanBoard component

### Core Components

**KanbanBoard** (`src/components/KanbanBoard.tsx`)
- Main container component managing board state
- Handles DnD context with @dnd-kit
- Manages columns, cards, and all CRUD operations
- State stored in React useState (no persistence)
- Callbacks: handleDragStart, handleDragEnd, handleRenameColumn, handleAddCard, handleDeleteCard

**KanbanColumn** (`src/components/KanbanColumn.tsx`)
- Renders a single column with droppable area
- Editable column title (inline input)
- Shows card count
- Contains SortableContext for cards
- Includes NewCardForm at bottom

**KanbanCard** (`src/components/KanbanCard.tsx`)
- Individual draggable card with useSortable hook
- Displays title and details
- Delete button with onDelete callback
- Visual feedback during drag (opacity change)

**KanbanCardPreview** (`src/components/KanbanCardPreview.tsx`)
- Simplified card view shown in DragOverlay during drag operations

**NewCardForm** (`src/components/NewCardForm.tsx`)
- Toggleable form (button -> form -> button)
- Inputs: title (required), details (optional)
- Submit creates new card via onAdd callback

### Data Layer

**kanban.ts** (`src/lib/kanban.ts`)
- Type definitions: Card, Column, BoardData
- initialData: 5 columns with 8 sample cards
- moveCard(): Pure function handling all drag-and-drop logic (same column reorder, cross-column moves)
- createId(): Generates unique IDs with prefix + random + timestamp

### Styling

- Custom CSS variables in `src/app/globals.css`
- Color scheme matches project requirements (yellow accent, blue primary, purple secondary, navy dark, gray text)
- Tailwind utility classes throughout
- Radial gradient background effects

### Testing

**Unit Tests**
- `src/lib/kanban.test.ts` - Tests for moveCard logic
- `src/components/KanbanBoard.test.tsx` - Component behavior tests
- Test setup in `src/test/setup.ts`

**E2E Tests**
- `tests/kanban.spec.ts` - Playwright tests for drag-and-drop flows

## Current Limitations

- No backend integration (all state in memory)
- No persistence (refresh loses changes)
- No authentication
- No API calls
- Single board only (hardcoded initialData)

## Build Commands

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run test:unit` - Run Vitest tests
- `npm run test:e2e` - Run Playwright tests
- `npm run test:all` - Run all tests
