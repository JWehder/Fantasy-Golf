import React, { useEffect, useState } from "react";
import DraftResults from "./DraftResults";
import DraftingConsole from "./DraftingConsole";
import { useParams } from "react-router-dom";
import LoadingScreen from "../Utils/components/LoadingScreen";
import ErrorPage from "../Utils/components/ErrorPage";
import { useFetchDraftData } from "../../hooks/drafts";
import { useDispatch } from "react-redux";
import { useSelector } from "react-redux";
import { getLeague } from "../Leagues/state/leagueSlice";
import { AppDispatch, RootState } from "../../store";

const DraftPage = () => {
    const { leagueId, draftId } = useParams<{ leagueId: string; draftId: string }>();
    const dispatch = useDispatch<AppDispatch>();
    const [isLoading, setIsLoading] = useState(true);

    const league = useSelector((state: RootState) => state.leagues.selectedLeague);
  
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
    } = useFetchDraftData(draftId!)
    
    if (!data || isLoading || !league) {
        return <LoadingScreen />
    };

    return (
        <div>
        {data.draft.IsComplete ? (
            <DraftResults
            draftPicks={data.draft.DraftPicks}
            draftOrder={data.draft.DraftOrder}
            leagueSettings={league!.LeagueSettings}
            rounds={data.draft.Rounds}
            />
        ) : (
            // <DraftingConsole
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