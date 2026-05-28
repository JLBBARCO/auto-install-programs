import { AlertCircle, Github, RotateCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { MESSAGES, getLogServerDisplay } from "@/constants/app";

interface ErrorStateProps {
  onRefresh: () => void;
}

export function ErrorState({ onRefresh }: ErrorStateProps) {
  const logServerDisplay = getLogServerDisplay();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="max-w-md w-full text-center">
        <div className="mb-6 flex justify-center">
          <div className="p-4 bg-destructive/10 rounded-full">
            <AlertCircle
              className="w-8 h-8 text-destructive/80"
              aria-hidden="true"
            />
          </div>
        </div>

        <h1 className="text-2xl font-display font-bold text-foreground mb-2">
          {MESSAGES.CONNECTION_ERROR}
        </h1>

        <p className="text-foreground/70 mb-2">{logServerDisplay.portError}</p>

        <p className="text-sm text-muted-foreground mb-6">
          {MESSAGES.PORT_ERROR_HINT} {logServerDisplay.troubleshootingHint}
        </p>

        <div className="flex flex-col gap-3">
          <Button
            onClick={onRefresh}
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground gap-2"
          >
            <RotateCw className="w-4 h-4" />
            {MESSAGES.RETRY_BUTTON}
          </Button>

          <a
            href="https://github.com/JLBBARCO/programs-manager"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="outline" className="w-full">
              <Github className="w-4 h-4 mr-2" />
              Ver repositório
            </Button>
          </a>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          {logServerDisplay.timeout}
        </p>
      </div>
    </div>
  );
}
