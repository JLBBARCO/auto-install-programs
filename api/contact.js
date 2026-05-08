/**
 * GET /api/contact
 *
 * Lê o contact.json do repositório de portfólio e devolve para o front-end.
 * A Vercel faz cache por 1 hora (s-maxage=3600), evitando muitas requisições
 * ao GitHub.
 */

const CONTACT_URL =
  "https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json";

export const config = { runtime: "edge" };

export default async function handler() {
  try {
    const res = await fetch(CONTACT_URL, {
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      throw new Error(`GitHub respondeu ${res.status}`);
    }

    const data = await res.json();

    return new Response(JSON.stringify(data), {
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "s-maxage=3600, stale-while-revalidate=300",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Erro desconhecido";

    return new Response(
      JSON.stringify({
        error: "Não foi possível carregar os dados de contato.",
        detail: message,
      }),
      {
        status: 502,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Access-Control-Allow-Origin": "*",
        },
      },
    );
  }
}