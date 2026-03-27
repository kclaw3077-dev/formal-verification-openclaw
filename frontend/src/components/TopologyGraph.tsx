import { useEffect, useRef } from "react";
import * as d3 from "d3";
import type { InfrastructureState, ServiceState } from "../types";
import { useLang } from "../i18n/context";

const STATE_COLORS: Record<ServiceState, string> = {
  running: "#10b981",
  deploying: "#f59e0b",
  degraded: "#f97316",
  down: "#ef4444",
};

const CRITICAL_STROKE = "#6366f1";

interface Node extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  state: ServiceState;
  replicas: string;
  isCritical: boolean;
  stateLabel: string;
  cacheHitRate?: number;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string;
  target: string;
}

export function TopologyGraph({ state }: { state: InfrastructureState }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const { t } = useLang();

  useEffect(() => {
    if (!svgRef.current) return;

    const width = svgRef.current.clientWidth || 560;
    const height = 360;

    const nodes: Node[] = Object.values(state.services).map((svc) => {
      const region = state.active_region;
      const replicaStr = Object.entries(svc.replicas)
        .map(([r, n]) => `${r}:${n}`)
        .join(" ");
      const rawState = (svc.state[region] ?? "running") as ServiceState;
      const metrics = (svc as any).metrics;
      const cacheHitRate = metrics?.cache_hit_rate != null ? metrics.cache_hit_rate : undefined;
      return {
        id: svc.name,
        label: svc.name,
        state: rawState,
        replicas: replicaStr,
        isCritical: svc.is_critical,
        stateLabel: t(`state.${rawState}`),
        cacheHitRate,
      };
    });

    const links: Link[] = [];
    for (const svc of Object.values(state.services)) {
      for (const dep of svc.dependencies) {
        links.push({ source: svc.name, target: dep });
      }
    }

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    svg.attr("viewBox", `0 0 ${width} ${height}`);

    svg
      .append("defs")
      .append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 28)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#64748b");

    const simulation = d3
      .forceSimulation<Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<Node, Link>(links)
          .id((d) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(40));

    const linkGroup = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#64748b")
      .attr("stroke-width", 1.5)
      .attr("marker-end", "url(#arrowhead)");

    const nodeGroup = svg
      .append("g")
      .selectAll<SVGGElement, Node>("g")
      .data(nodes)
      .join("g")
      .call(
        d3
          .drag<SVGGElement, Node>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    nodeGroup
      .append("circle")
      .attr("r", 22)
      .attr("fill", (d) => STATE_COLORS[d.state])
      .attr("stroke", (d) => (d.isCritical ? CRITICAL_STROKE : "transparent"))
      .attr("stroke-width", 3)
      .attr("opacity", 0.9);

    nodeGroup
      .filter((d) => d.state !== "running")
      .append("circle")
      .attr("r", 22)
      .attr("fill", "none")
      .attr("stroke", (d) => STATE_COLORS[d.state])
      .attr("stroke-width", 2)
      .attr("opacity", 0)
      .append("animate")
      .attr("attributeName", "r")
      .attr("from", "22")
      .attr("to", "35")
      .attr("dur", "1.5s")
      .attr("repeatCount", "indefinite")
      .select(function () {
        return this.parentElement;
      })
      .append("animate")
      .attr("attributeName", "opacity")
      .attr("from", "0.6")
      .attr("to", "0")
      .attr("dur", "1.5s")
      .attr("repeatCount", "indefinite");

    nodeGroup
      .append("text")
      .text((d) => d.label.replace("-svc", "").replace("inventory", "inv"))
      .attr("text-anchor", "middle")
      .attr("dy", -30)
      .attr("fill", "#e2e8f0")
      .attr("font-size", "11px")
      .attr("font-weight", "600");

    nodeGroup
      .append("text")
      .text((d) => d.replicas)
      .attr("text-anchor", "middle")
      .attr("dy", 4)
      .attr("fill", "#fff")
      .attr("font-size", "8px")
      .attr("font-family", "JetBrains Mono, monospace");

    nodeGroup
      .append("text")
      .text((d) => d.stateLabel)
      .attr("text-anchor", "middle")
      .attr("dy", 38)
      .attr("fill", (d) => STATE_COLORS[d.state])
      .attr("font-size", "9px")
      .attr("font-weight", "500");

    // Cache hit rate label for nodes with metrics
    nodeGroup
      .filter((d) => d.cacheHitRate != null)
      .append("text")
      .text((d) => `cache: ${Math.round((d.cacheHitRate ?? 0) * 100)}%`)
      .attr("text-anchor", "middle")
      .attr("dy", 50)
      .attr("class", (d) =>
        `metrics-label${(d.cacheHitRate ?? 0) < 0.5 ? " metrics-warning" : ""}`
      )
      .attr("fill", (d) => (d.cacheHitRate ?? 0) >= 0.5 ? "#10b981" : "#c62828");

    simulation.on("tick", () => {
      linkGroup
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      nodeGroup.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
    };
  }, [state, t]);

  return <svg ref={svgRef} className="topology-svg" />;
}
