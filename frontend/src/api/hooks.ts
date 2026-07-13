import { useQuery } from "@tanstack/react-query";
import { getGoal, getRecommend, getSnapshot } from "./client";

export function useSnapshot() {
  return useQuery({
    queryKey: ["snapshot"],
    queryFn: getSnapshot,
  });
}

export function useRecommend(weights?: Record<string, number>) {
  return useQuery({
    queryKey: ["recommend", weights ?? null],
    queryFn: () => getRecommend(weights),
    placeholderData: (prev) => prev, // keep last plan while sliders re-query
  });
}

export function useGoal(agentName: string | null, weights?: Record<string, number>) {
  return useQuery({
    queryKey: ["goal", agentName, weights ?? null],
    queryFn: () => getGoal(agentName as string, weights),
    enabled: !!agentName,
    placeholderData: (prev) => prev,
  });
}
