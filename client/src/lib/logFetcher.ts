import { getLogServerDisplay, getLogServerPortFromUrl } from "@/constants/app";

interface FetchLogStreamOptions {
  signal?: AbortSignal;
}

export async function* fetchLogStream(
  url: string,
  options: FetchLogStreamOptions = {}
) {
  const portDisplay = getLogServerDisplay(getLogServerPortFromUrl(url));
  const res = await fetch(url, {
    headers: { Accept: "text/plain" },
    signal: options.signal,
  });

  if (!res.ok) {
    throw new Error(
      `Servidor na porta ${portDisplay.port} respondeu ${res.status}`
    );
  }

  if (!res.body) {
    throw new Error(
      "Resposta sem body - verifique se o servidor expõe o arquivo."
    );
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      buffer += decoder.decode();
      const finalLines = buffer.split(/\r?\n/).filter(line => line.trim());

      for (const line of finalLines) {
        yield line;
      }
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split(/\r?\n/);
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.trim()) {
        yield line;
      }
    }
  }
}

/**
 * Fetcha o arquivo de log completo (sem streaming)
 * Útil para polling periódico após a conexão inicial terminar
 */
export async function fetchLogOnce(
  url: string,
  signal?: AbortSignal
): Promise<string[]> {
  const portDisplay = getLogServerDisplay(getLogServerPortFromUrl(url));
  const res = await fetch(url, {
    headers: { Accept: "text/plain" },
    signal,
  });

  if (!res.ok) {
    throw new Error(
      `Servidor na porta ${portDisplay.port} respondeu ${res.status}`
    );
  }

  const text = await res.text();
  return text.split(/\r?\n/).filter(line => line.trim());
}
