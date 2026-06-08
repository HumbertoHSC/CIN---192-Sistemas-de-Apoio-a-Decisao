"use client";

import {
  CartesianGrid,
  Label,
  LabelList,
  ReferenceLine,
  Scatter,
  ScatterChart,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import type { GaiaOutput } from "@/lib/api";
import { ChartContainer, type ChartConfig } from "@/components/ui/chart";

const config = {
  alt: { label: "Alternativas" },
} satisfies ChartConfig;

// The GAIA plane shows alternatives (points), criteria (vectors from the
// origin) and the decision axis π. Criterion vectors are scaled so they read
// comparably to the alternative points. Colours come from --chart-* tokens:
// alternatives = blue, criteria = emerald, decision axis π = amber.
export function GaiaPlane({ gaia }: { gaia: GaiaOutput }) {
  const altPoints = gaia.alternatives.map((a) => ({ ...a }));

  const maxAlt = Math.max(
    1e-6,
    ...altPoints.flatMap((a) => [Math.abs(a.x), Math.abs(a.y)]),
  );
  const maxCrit = Math.max(
    1e-6,
    ...gaia.criteria.flatMap((c) => [Math.abs(c.x), Math.abs(c.y)]),
  );
  // Scale the criterion / decision vectors so they read comparably to the
  // alternative cloud without dominating it.
  const scale = (maxAlt / maxCrit) * 0.85;

  const criteriaScaled = gaia.criteria.map((c) => ({
    ...c,
    x: c.x * scale,
    y: c.y * scale,
  }));
  const pi = {
    x: gaia.decision_axis.x * scale,
    y: gaia.decision_axis.y * scale,
  };

  // Symmetric square domain covering every drawn element. Without an explicit
  // domain, recharts auto-fits only the Scatter points and silently drops any
  // ReferenceLine segment (criterion vectors, π) whose endpoint falls outside
  // that range. Including all geometry guarantees every vector renders.
  const extent =
    Math.max(
      ...altPoints.flatMap((a) => [Math.abs(a.x), Math.abs(a.y)]),
      ...criteriaScaled.flatMap((c) => [Math.abs(c.x), Math.abs(c.y)]),
      Math.abs(pi.x),
      Math.abs(pi.y),
      1e-6,
    ) * 1.12;
  const domain: [number, number] = [-extent, extent];

  return (
    <div>
      <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
        Qualidade do plano (δ)
        <span className="tnum font-medium text-foreground">
          {(gaia.quality * 100).toFixed(1)}%
        </span>
      </div>

      <ChartContainer config={config} className="h-96 w-full">
        <ScatterChart margin={{ top: 16, right: 28, bottom: 8, left: -8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <ReferenceLine x={0} stroke="var(--border)" />
          <ReferenceLine y={0} stroke="var(--border)" />
          {/* PCA coordinates carry no meaningful unit; the biplot is read by
              relative position, so the numeric ticks are hidden to cut noise. */}
          <XAxis
            type="number"
            dataKey="x"
            domain={domain}
            allowDataOverflow
            tickLine={false}
            axisLine={false}
            tick={false}
            height={8}
          />
          <YAxis
            type="number"
            dataKey="y"
            domain={domain}
            allowDataOverflow
            tickLine={false}
            axisLine={false}
            tick={false}
            width={8}
          />
          <ZAxis range={[130, 130]} />

          {/* criterion vectors */}
          {criteriaScaled.map((c) => (
            <ReferenceLine
              key={c.name}
              segment={[
                { x: 0, y: 0 },
                { x: c.x, y: c.y },
              ]}
              stroke="var(--chart-2)"
              strokeWidth={1.5}
            >
              <Label
                value={c.name}
                position="insideEnd"
                fontSize={11}
                fill="var(--chart-2)"
              />
            </ReferenceLine>
          ))}

          {/* decision axis π */}
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: pi.x, y: pi.y },
            ]}
            stroke="var(--chart-3)"
            strokeWidth={2.5}
          >
            <Label
              value="π"
              position="insideEnd"
              fontSize={14}
              fontWeight={600}
              fill="var(--chart-3)"
            />
          </ReferenceLine>

          {/* alternatives */}
          <Scatter data={altPoints} fill="var(--chart-1)">
            <LabelList
              dataKey="name"
              position="top"
              offset={8}
              fontSize={11}
              className="fill-foreground"
            />
          </Scatter>
        </ScatterChart>
      </ChartContainer>

      <dl className="mt-4 flex flex-wrap gap-x-6 gap-y-1.5 text-xs text-muted-foreground">
        <Legend swatch="var(--chart-1)" shape="dot">
          Alternativas
        </Legend>
        <Legend swatch="var(--chart-2)" shape="line">
          Vetores de critério
        </Legend>
        <Legend swatch="var(--chart-3)" shape="line">
          Eixo de decisão π (melhor compromisso)
        </Legend>
      </dl>
    </div>
  );
}

function Legend({
  swatch,
  shape,
  children,
}: {
  swatch: string;
  shape: "dot" | "line";
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span
        aria-hidden
        className={shape === "dot" ? "size-2 rounded-full" : "h-0.5 w-4"}
        style={{ backgroundColor: swatch }}
      />
      {children}
    </div>
  );
}
