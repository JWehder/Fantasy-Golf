import axios from "axios";
import { useQuery } from "@tanstack/react-query";
import { Round } from "../types/rounds";

interface RoundsResponse {
    rounds: Round[]
}

const fetchGolferTournamentRounds = async (golferTournamentDetailId: string) => {
    const response = await axios.get(`/api/rounds/${golferTournamentDetailId}`);
    return response.data;
};

export const useFetchGolferTournamentRounds = (golferTournamentDetailId?: string) => {
    return useQuery<RoundsResponse>({
        queryKey: ['golferTournamentDetails', golferTournamentDetailId],
        queryFn: () => fetchGolferTournamentRounds(golferTournamentDetailId!),
        enabled: !!golferTournamentDetailId // Only enable query if golferId is valid
    });
};