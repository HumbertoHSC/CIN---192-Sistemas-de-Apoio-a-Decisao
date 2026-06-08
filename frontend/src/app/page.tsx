"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, Crown, Download, Plus, X } from "lucide-react";
import {
  CriterionInput,
  PreferenceType,
  PREFERENCE_LABELS,
  PREFERENCE_PARAMS,
  SolveRequest,
  SolveResponse,
  exportFile,
  solve,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { RankingChart } from "./components/RankingChart";
import { GaiaPlane } from "./components/GaiaPlane";

// Exemplo pré-carregado: escolha de um carro (custo, conforto, consumo).
const EXAMPLE: {
  alternatives: string[];
  criteria: CriterionInput[];
  matrix: number[][];
} = {
  alternatives: ["Carro A", "Carro B", "Carro C", "Carro D"],
  criteria: [
    { name: "Preço (R$ mil)", weight: 0.35, maximize: false, preference: "linear", q: 5, p: 20 },
    { name: "Conforto (1-10)", weight: 0.25, maximize: true, preference: "v_shape", p: 3 },
    { name: "Consumo (km/l)", weight: 0.25, maximize: true, preference: "usual" },
    { name: "Potência (cv)", weight: 0.15, maximize: true, preference: "gaussian", s: 20 },
  ],
  matrix: [
    [80, 7, 12, 110],
    [65, 5, 15, 90],
    [95, 9, 10, 140],
    [72, 6, 14, 100],
  ],
};

const PREFERENCE_TYPES = Object.keys(PREFERENCE_LABELS) as PreferenceType[];
const PARAM_KEYS = ["q", "p", "s"] as const;

export default function Home() {
  const [alternatives, setAlternatives] = useState<string[]>(EXAMPLE.alternatives);
  const [criteria, setCriteria] = useState<CriterionInput[]>(EXAMPLE.criteria);
  const [matrix, setMatrix] = useState<number[][]>(EXAMPLE.matrix);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const weightSum = useMemo(
    () => criteria.reduce((acc, c) => acc + (Number(c.weight) || 0), 0),
    [criteria],
  );

  function buildRequest(): SolveRequest {
    return { alternatives, criteria, matrix };
  }

  async function handleSolve() {
    setLoading(true);
    setError(null);
    try {
      setResult(await solve(buildRequest()));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro desconhecido");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  // --- mutações de estado -------------------------------------------------
  function updateCriterion(i: number, patch: Partial<CriterionInput>) {
    setCriteria((cs) => cs.map((c, k) => (k === i ? { ...c, ...patch } : c)));
  }
  function addCriterion() {
    setCriteria((cs) => [
      ...cs,
      { name: `Critério ${cs.length + 1}`, weight: 1, maximize: true, preference: "usual" },
    ]);
    setMatrix((m) => m.map((row) => [...row, 0]));
  }
  function removeCriterion(i: number) {
    if (criteria.length <= 1) return;
    setCriteria((cs) => cs.filter((_, k) => k !== i));
    setMatrix((m) => m.map((row) => row.filter((_, k) => k !== i)));
  }
  function addAlternative() {
    setAlternatives((a) => [...a, `Alternativa ${a.length + 1}`]);
    setMatrix((m) => [...m, criteria.map(() => 0)]);
  }
  function removeAlternative(i: number) {
    if (alternatives.length <= 2) return;
    setAlternatives((a) => a.filter((_, k) => k !== i));
    setMatrix((m) => m.filter((_, k) => k !== i));
  }
  function updateCell(i: number, j: number, value: number) {
    setMatrix((m) => m.map((row, ri) => (ri === i ? row.map((c, ci) => (ci === j ? value : c)) : row)));
  }

  return (
    <div className="min-h-[100dvh]">
      <main className="mx-auto max-w-6xl px-4 py-10 sm:py-14">
        <header className="mb-10">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              PROMETHEE II
            </h1>
            <Badge variant="secondary" className="font-normal">
              MCDM · GAIA
            </Badge>
          </div>
          <p className="mt-2 max-w-[60ch] text-muted-foreground">
            Apoio à decisão multicritério com ranking completo e plano GAIA.
            Defina os critérios e a matriz de avaliação para calcular os fluxos
            φ⁺, φ⁻ e φ líquido.
          </p>
        </header>

        {/* ---------------- 1. Critérios ---------------- */}
        <Card className="mb-6 [--card-spacing:--spacing(5)]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2.5">
              <StepMarker n={1} />
              Critérios
              <span className="tnum text-xs font-normal text-muted-foreground">
                Σ pesos {weightSum.toFixed(2)}
              </span>
            </CardTitle>
            <CardAction>
              <Button variant="outline" size="sm" onClick={addCriterion}>
                <Plus /> Critério
              </Button>
            </CardAction>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Nome</TableHead>
                    <TableHead>Peso</TableHead>
                    <TableHead>Objetivo</TableHead>
                    <TableHead>Função de preferência</TableHead>
                    <TableHead className="text-center">q</TableHead>
                    <TableHead className="text-center">p</TableHead>
                    <TableHead className="text-center">s</TableHead>
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {criteria.map((c, i) => {
                    const params = PREFERENCE_PARAMS[c.preference];
                    return (
                      <TableRow key={i}>
                        <TableCell>
                          <Input
                            className="w-44"
                            value={c.name}
                            onChange={(e) => updateCriterion(i, { name: e.target.value })}
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            step="0.05"
                            className="tnum w-20"
                            value={c.weight}
                            onChange={(e) => updateCriterion(i, { weight: Number(e.target.value) })}
                          />
                        </TableCell>
                        <TableCell>
                          <Select
                            value={c.maximize ? "max" : "min"}
                            onValueChange={(v) => updateCriterion(i, { maximize: v === "max" })}
                          >
                            <SelectTrigger className="w-[140px]" size="sm">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="max">
                                <ArrowUp className="text-muted-foreground" /> Maximizar
                              </SelectItem>
                              <SelectItem value="min">
                                <ArrowDown className="text-muted-foreground" /> Minimizar
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Select
                            value={c.preference}
                            onValueChange={(v) => updateCriterion(i, { preference: v as PreferenceType })}
                          >
                            <SelectTrigger className="w-[230px]" size="sm">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {PREFERENCE_TYPES.map((t) => (
                                <SelectItem key={t} value={t}>
                                  {PREFERENCE_LABELS[t]}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </TableCell>
                        {PARAM_KEYS.map((param) => (
                          <TableCell key={param}>
                            <Input
                              type="number"
                              step="0.5"
                              disabled={!params.includes(param)}
                              className="tnum mx-auto w-16 text-center"
                              value={(c[param] as number | null | undefined) ?? ""}
                              onChange={(e) =>
                                updateCriterion(i, {
                                  [param]: e.target.value === "" ? null : Number(e.target.value),
                                })
                              }
                            />
                          </TableCell>
                        ))}
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon-sm"
                            className="text-muted-foreground hover:text-destructive"
                            onClick={() => removeCriterion(i)}
                            aria-label={`Remover ${c.name}`}
                            disabled={criteria.length <= 1}
                          >
                            <X />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* ---------------- 2. Matriz de avaliação ---------------- */}
        <Card className="mb-6 [--card-spacing:--spacing(5)]">
          <CardHeader>
            <CardTitle className="flex items-center gap-2.5">
              <StepMarker n={2} />
              Alternativas e avaliações
            </CardTitle>
            <CardAction>
              <Button variant="outline" size="sm" onClick={addAlternative}>
                <Plus /> Alternativa
              </Button>
            </CardAction>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Alternativa</TableHead>
                    {criteria.map((c, j) => (
                      <TableHead key={j} className="whitespace-nowrap">
                        {c.name}
                      </TableHead>
                    ))}
                    <TableHead />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {alternatives.map((name, i) => (
                    <TableRow key={i}>
                      <TableCell>
                        <Input
                          className="w-44"
                          value={name}
                          onChange={(e) =>
                            setAlternatives((a) => a.map((n, k) => (k === i ? e.target.value : n)))
                          }
                        />
                      </TableCell>
                      {criteria.map((_, j) => (
                        <TableCell key={j}>
                          <Input
                            type="number"
                            step="any"
                            className="tnum w-24"
                            value={matrix[i]?.[j] ?? 0}
                            onChange={(e) => updateCell(i, j, Number(e.target.value))}
                          />
                        </TableCell>
                      ))}
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          className="text-muted-foreground hover:text-destructive"
                          onClick={() => removeAlternative(i)}
                          aria-label={`Remover ${name}`}
                          disabled={alternatives.length <= 2}
                        >
                          <X />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <div className="mb-10 flex flex-wrap items-center gap-4">
          <Button size="lg" onClick={handleSolve} disabled={loading} className="px-6">
            {loading ? "Calculando…" : "Calcular ranking"}
          </Button>
          {error && (
            <p role="alert" className="text-sm font-medium text-destructive">
              {error}
            </p>
          )}
        </div>

        {/* ---------------- Resultados ---------------- */}
        {result && (
          <section key={result.scores.map((s) => s.name + s.phi_net).join()} className="ph-rise space-y-6">
            <Card className="[--card-spacing:--spacing(5)]">
              <CardHeader>
                <CardTitle>Ranking · PROMETHEE II</CardTitle>
                <CardAction className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => exportFile("csv", buildRequest())}>
                    <Download /> CSV
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => exportFile("pdf", buildRequest())}>
                    <Download /> PDF
                  </Button>
                </CardAction>
              </CardHeader>
              <CardContent className="space-y-6">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Alternativa</TableHead>
                      <TableHead className="text-right">φ⁺</TableHead>
                      <TableHead className="text-right">φ⁻</TableHead>
                      <TableHead className="text-right">φ líquido</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {[...result.scores]
                      .sort((a, b) => a.rank - b.rank)
                      .map((s) => (
                        <TableRow
                          key={s.name}
                          className={s.rank === 1 ? "bg-accent/40" : undefined}
                        >
                          <TableCell>
                            <Badge
                              variant={s.rank === 1 ? "default" : "secondary"}
                              className="tnum h-6 w-6 justify-center rounded-md p-0"
                            >
                              {s.rank}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-medium">
                            <span className="inline-flex items-center gap-1.5">
                              {s.name}
                              {s.rank === 1 && (
                                <Crown className="size-3.5 text-chart-3" aria-label="Melhor alternativa" />
                              )}
                            </span>
                          </TableCell>
                          <TableCell className="tnum text-right text-muted-foreground">
                            {s.phi_plus.toFixed(4)}
                          </TableCell>
                          <TableCell className="tnum text-right text-muted-foreground">
                            {s.phi_minus.toFixed(4)}
                          </TableCell>
                          <TableCell
                            className={`tnum text-right font-medium ${
                              s.phi_net >= 0 ? "text-primary" : "text-destructive"
                            }`}
                          >
                            {s.phi_net >= 0 ? "+" : ""}
                            {s.phi_net.toFixed(4)}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>

                <Separator />
                <RankingChart scores={result.scores} />
              </CardContent>
            </Card>

            {result.gaia && (
              <Card className="[--card-spacing:--spacing(5)]">
                <CardHeader>
                  <CardTitle>Plano GAIA</CardTitle>
                </CardHeader>
                <CardContent>
                  <GaiaPlane gaia={result.gaia} />
                </CardContent>
              </Card>
            )}
          </section>
        )}

        <footer className="mt-14 border-t pt-5 text-xs text-muted-foreground">
          Baseado em Brans &amp; Vincke (1986) e Behzadian et al. (2010).
        </footer>
      </main>
    </div>
  );
}

function StepMarker({ n }: { n: number }) {
  return (
    <span className="tnum inline-flex size-5 items-center justify-center rounded-md bg-secondary text-xs font-medium text-secondary-foreground">
      {n}
    </span>
  );
}
