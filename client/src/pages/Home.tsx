import { MESSAGES } from "@/constants/app";
import { LogContainerSkeleton } from "@/components/Skeletons";
import { ContactFooter } from "@/components/ContactFooter";
import { ErrorState } from "@/components/ErrorState";
import { HistoryView } from "@/components/HistoryView";
import { LogContainer } from "@/components/LogContainer";
import { useLogMonitor } from "@/hooks/useLogMonitor";

export default function Home() {
  const { info, warning, error, history, isLoading, monitorError } =
    useLogMonitor();

  if (monitorError) {
    return <ErrorState onRefresh={() => window.location.reload()} />;
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container py-6">
          <h1
            className="text-3xl font-bold text-foreground"
            style={{ fontFamily: "'Poppins', sans-serif" }}
          >
            {MESSAGES.APP_TITLE}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {MESSAGES.APP_SUBTITLE}
          </p>
        </div>
      </header>

      <main className="container py-8">
        <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="h-96">
            {isLoading ? (
              <LogContainerSkeleton />
            ) : (
              <LogContainer title="Informações" entries={info} />
            )}
          </div>

          <div className="h-96">
            {isLoading ? (
              <LogContainerSkeleton />
            ) : (
              <LogContainer title="Avisos" entries={warning} />
            )}
          </div>

          <div className="h-96">
            {isLoading ? (
              <LogContainerSkeleton />
            ) : (
              <LogContainer title="Erros" entries={error} />
            )}
          </div>
        </div>

        {history.length > 0 && <HistoryView historyLogs={history} />}
      </main>

      <ContactFooter />
    </div>
  );
}
