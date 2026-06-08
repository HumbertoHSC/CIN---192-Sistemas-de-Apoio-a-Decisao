"use client";

import {
  Bar,
  BarChart,
  Cell,
  CartesianGrid,
  LabelList,
  XAxis,
  YAxis,
} from "recharts";
import type { ScoreOutput } from "@/lib/api";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

// Positive net flow reads in the accent (blue); negative in rose. These are
// data encodings driven by the --chart-* tokens, so they track light/dark.
const config = {
  phi: { label: "φ líquido" },
} satisfies ChartConfig;

export function RankingChart({ scores }: { scores: ScoreOutput[] }) {
  const data = [...scores]
    .sort((a, b) => a.rank - b.rank)
    .map((s) => ({ name: s.name, phi: Number(s.phi_net.toFixed(4)) }));

  return (
    <ChartContainer config={config} className="h-72 w-full">
      <BarChart data={data} margin={{ top: 16, right: 12, bottom: 4, left: -8 }}>
        <CartesianGrid vertical={false} strokeDasharray="3 3" />
        <XAxis
          dataKey="name"
          tickLine={false}
          axisLine={false}
          tickMargin={10}
          tick={{ fontSize: 12 }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          width={48}
          tick={{ fontSize: 11 }}
          className="tnum"
        />
        <ChartTooltip
          cursor={{ fill: "var(--muted)", opacity: 0.4 }}
          content={
            <ChartTooltipContent
              formatter={(v) => (v as number).toFixed(4)}
            />
          }
        />
        <Bar dataKey="phi" radius={[6, 6, 0, 0]} maxBarSize={72}>
          {data.map((d) => (
            <Cell
              key={d.name}
              fill={d.phi >= 0 ? "var(--chart-1)" : "var(--chart-4)"}
            />
          ))}
          <LabelList
            dataKey="phi"
            position="top"
            offset={8}
            className="fill-muted-foreground tnum"
            fontSize={11}
            formatter={(v) => (typeof v === "number" ? v.toFixed(3) : v)}
          />
        </Bar>
      </BarChart>
    </ChartContainer>
  );
}
