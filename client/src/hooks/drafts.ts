import axios from "axios";
import { useQuery } from "@tanstack/react-query";
import { Draft } from "../types/draft";

export interface DraftDetailsResponse {
    draft: Draft;
}

const fetchDraftData = async (draftId: string) => {
    const response = await axios.get(`/api/drafts/${draftId}`);
    return response.data;
};

export const useFetchDraftData = (draftId?: string) => {
    return useQuery<DraftDetailsResponse>({
        queryKey: ['drafts', draftId],
        queryFn: () => fetchDraftData(draftId!),
        enabled: !!draftId 
    });
};