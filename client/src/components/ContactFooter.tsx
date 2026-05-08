import { Github, Linkedin, Mail } from "lucide-react";
import { useEffect, useState } from "react";
import {
  CONTACT_API_ENDPOINTS,
  CONTACT_FETCH_TIMEOUT_MS,
  ICON_NAMES,
  MESSAGES,
} from "@/constants/app";
import { ContactSkeleton } from "@/components/Skeletons";

interface ContactCard {
  name: string;
  iconName: string;
  url: string;
}

const ICON_COMPONENTS = {
  [ICON_NAMES.EMAIL]: Mail,
  [ICON_NAMES.GITHUB]: Github,
  [ICON_NAMES.LINKEDIN]: Linkedin,
} as const;

export function ContactFooter() {
  const [contacts, setContacts] = useState<ContactCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchContacts = async () => {
      try {
        for (const endpoint of CONTACT_API_ENDPOINTS) {
          try {
            const controller = new AbortController();
            const timeoutId = window.setTimeout(
              () => controller.abort(),
              CONTACT_FETCH_TIMEOUT_MS
            );

            const response = await fetch(endpoint, {
              headers: { Accept: "application/json" },
              signal: controller.signal,
            });

            window.clearTimeout(timeoutId);

            if (!response.ok) {
              continue;
            }

            const data = await response.json();
            const cards = Array.isArray(data?.cards) ? data.cards : [];

            if (cards.length > 0) {
              setContacts(cards);
              setError(false);
              return;
            }
          } catch {
            continue;
          }
        }
        setError(true);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    void fetchContacts();
  }, []);

  const getIcon = (iconName: string) => {
    const IconComponent =
      ICON_COMPONENTS[iconName as keyof typeof ICON_COMPONENTS];
    return IconComponent ? <IconComponent className="w-5 h-5" /> : null;
  };

  return (
    <footer className="border-t border-border bg-card mt-8 py-6">
      <div className="container">
        <div className="flex flex-row flex-wrap items-center justify-center gap-3">
          {loading ? (
            <ContactSkeleton />
          ) : error ? (
            <p className="text-sm text-muted-foreground">
              {MESSAGES.CONTACT_ERROR}
            </p>
          ) : contacts.length > 0 ? (
            contacts.map(contact => (
              <a
                key={contact.url}
                href={contact.url}
                title={contact.name}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-3 rounded-2xl border border-border bg-background px-4 py-3 text-foreground shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/40 hover:bg-primary/5"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-foreground transition-colors group-hover:bg-primary/10 group-hover:text-primary">
                  {getIcon(contact.iconName)}
                </span>
                <span className="text-sm font-medium leading-none">
                  {contact.name}
                </span>
              </a>
            ))
          ) : null}
        </div>
        <p className="text-xs text-muted-foreground text-center mt-4">
          Programs Manager - Monitoramento em Tempo Real
        </p>
      </div>
    </footer>
  );
}
