import React, { useEffect, useState } from "react";
import DraftResults from "./DraftResults";
import { useParams } from "react-router-dom";
import LoadingScreen from "../Utils/components/LoadingScreen";
import ErrorPage from "../Utils/components/ErrorPage"; 
import { useFetchDraftData } from "../../hooks/drafts";
import { useDispatch } from "react-redux";
import { useSelector } from "react-redux";
import { getLeague, setSelectedLeague } from "../Leagues/state/leagueSlice";
import { AppDispatch, RootState } from "../../store";
import { DraftPick } from "../../types/draftPicks";
import { useQueryClient, useMutation } from "@tanstack/react-query";

const DraftPage = () => {
    const { leagueId, draftId } = useParams<{ leagueId: string; draftId: string }>();
    const queryClient = useQueryClient();
    const dispatch = useDispatch<AppDispatch>();
    const [isLoading, setIsLoading] = useState(true);

    const league = useSelector((state: RootState) => state.leagues.selectedLeague);
    const leagues = useSelector((state: RootState) => state.leagues.leagues);

    useEffect(() => {
        if (!league) {
            const selectedLeague = leagues.filter((league) => league.id === leagueId);
            dispatch(setSelectedLeague(selectedLeague));
        };
    }, [leagueId]);
  
    useEffect(() => {
      const loadData = async () => {
        if (!league || league.id !== leagueId) {
            dispatch(getLeague(leagueId!)); // Ensure league data is fetched
        }
        setIsLoading(false);
      };
  
      loadData();
    }, [leagueId, draftId, league, dispatch]);

    if (!draftId || !leagueId) {
        return <ErrorPage message="We do not recognize the draft or league you are looking for." />
    };

    const {
        data,
        isError, 
        error,
        isFetching
    } = useFetchDraftData(draftId!)

    // Mutation for adding a draft pick
    // Handle draft pick submission by directly modifying the local data
    const onDraft = (draftPick: DraftPick) => {
        // Directly update the draft picks in the local cache
        queryClient.setQueryData(['drafts', draftId], (oldData: any) => {
            return {
                ...oldData,
                draft: {
                    ...oldData.draft,
                    DraftPicks: [...oldData.draft.DraftPicks, draftPick],
                },
            };
        });
    };
    
    if (!data || isLoading || !league || isFetching) {
        return <LoadingScreen />
    };

    return (
        <div className="bg-dark overflow-auto p-2">
        {data.draft.IsComplete ? (
            <DraftResults
            draftPicks={data.draft.DraftPicks}
            draftOrder={data.draft.DraftOrder}
            leagueSettings={league!.LeagueSettings}
            rounds={data.draft.Rounds}
            />
        ) : (
            // <DraftingConsole
            // draftId={data.draft.id} 
            // leagueId={leagueId}
            // tournamentId={data.TournamentId}
            // currentTeam={}
            // draftOrder={}
            // draftPicks={}
            // onDraft={}
            // leagueSettings={league!.LeagueSettings}
            // />
            <>
            </>
        )}
        <>
           {isError && <ErrorPage message={error.message} />}
        </>
        </div>
        
    );
};
  
export default DraftPage;