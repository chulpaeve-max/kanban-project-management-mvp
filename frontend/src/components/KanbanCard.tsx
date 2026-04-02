import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import clsx from "clsx";
import type { Card } from "@/lib/kanban";

type KanbanCardProps = {
  card: Card;
  onDelete: (cardId: string) => void;
};

export const KanbanCard = ({ card, onDelete }: KanbanCardProps) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: card.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <article
      ref={setNodeRef}
      style={style}
      className={clsx(
        "rounded-xl border border-transparent bg-white px-3 py-2.5 shadow-[0_8px_16px_rgba(3,33,71,0.06)] max-w-full",
        "transition-all duration-150 cursor-grab active:cursor-grabbing",
        isDragging && "opacity-60 shadow-[0_12px_20px_rgba(3,33,71,0.12)]"
      )}
      {...attributes}
      {...listeners}
      data-testid={`card-${card.id}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h4 className="font-display text-sm font-semibold text-[var(--navy-dark)] break-words">
            {card.title}
          </h4>
          {card.details && (
            <p className="mt-1 text-xs leading-5 text-[var(--gray-text)] line-clamp-2">
              {card.details}
            </p>
          )}
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(card.id);
          }}
          className="flex-shrink-0 rounded-full border border-transparent px-1.5 py-0.5 text-xs font-semibold text-[var(--gray-text)] transition hover:border-[var(--stroke)] hover:text-[var(--navy-dark)]"
          aria-label={`Delete ${card.title}`}
        >
          ×
        </button>
      </div>
    </article>
  );
};
