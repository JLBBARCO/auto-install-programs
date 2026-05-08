/**
 * Skeleton loader para containers de log
 * Melhora a percepção de performance enquanto aguarda conexão
 */
export function LogContainerSkeleton() {
  return (
    <div className="flex flex-col h-full gap-4">
      <div className="h-6 bg-muted rounded-md w-20 animate-pulse" />
      <div className="flex-1 border border-border rounded-lg bg-card p-3 space-y-2">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="h-4 bg-muted rounded w-full animate-pulse"
            style={{ animationDelay: `${i * 50}ms` }}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Skeleton loader para contatos no rodapé
 */
export function ContactSkeleton() {
  return (
    <div className="flex flex-row flex-wrap items-center justify-center gap-3">
      {[...Array(3)].map((_, i) => (
        <div
          key={i}
          className="h-12 w-48 bg-muted rounded-2xl animate-pulse"
          style={{ animationDelay: `${i * 100}ms` }}
        />
      ))}
    </div>
  );
}
