import { useInfiniteQuery } from "@tanstack/react-query";
import { Golfer } from "../types/golfers"
import axios from "axios";

export interface GolfersResponse {
    golfers: Golfer[];
    nextPage?: number | null; // Handle the optional nextPage
}

// Fetch golfers with pagination
const fetchAvailableGolfers = async ({ pageParam = 0, leagueId }: { pageParam?: number; leagueId: string }): Promise<GolfersResponse> => {
    const response = await axios.get<GolfersResponse>(`/api/golfers/available_golfers/leagues/${leagueId}?page=${pageParam}`);
    return response.data;
};

// Custom hook for fetching golfers with infinite pagination
export const useFetchAvailableGolfers = (leagueId: string ) => {
    return useInfiniteQuery<GolfersResponse>({
        queryKey: ['golfers', leagueId],
        queryFn: ({ pageParam }) => fetchAvailableGolfers({ pageParam: pageParam as number, leagueId }),
        initialPageParam: 0,
        getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
    });
};


// Fetch golfers with pagination
const fetchAvailableTourneyGolfers = async ({ 
    pageParam = 0, 
    leagueId, 
    tournamentId 
    }: 
    { 
    pageParam?: number; 
    leagueId: string, 
    tournamentId: string 
}): Promise<GolfersResponse> => {
    const response = await axios.get<GolfersResponse>(`/api/golfers/available_golfers/leagues/${leagueId}/tournaments/${tournamentId}?page=${pageParam}`);
    return response.data;
};

// Custom hook for fetching golfers with infinite pagination
export const useFetchAvailableTourneyGolfers = (leagueId: string, tournamentId: string ) => {
    return useInfiniteQuery<GolfersResponse>({
        queryKey: ['golfers', leagueId],
        queryFn: ({ pageParam }) => fetchAvailableTourneyGolfers({ pageParam: pageParam as number, leagueId, tournamentId }),
        initialPageParam: 0,
        getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
    });
};
