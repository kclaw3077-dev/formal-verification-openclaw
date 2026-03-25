import type { Scenario, ScenarioSummary } from "./types";

const BASE = "/api";

export async function fetchScenarios(lang: string): Promise<ScenarioSummary[]> {
  const res = await fetch(`${BASE}/scenarios?lang=${lang}`);
  return res.json();
}

export async function fetchScenario(id: string, lang: string): Promise<Scenario> {
  const res = await fetch(`${BASE}/scenarios/${id}?lang=${lang}`);
  return res.json();
}

export async function fetchTlaSpec(
  filename: string
): Promise<{ filename: string; content: string }> {
  const res = await fetch(`${BASE}/tla/${filename}`);
  return res.json();
}
