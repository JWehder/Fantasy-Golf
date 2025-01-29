import { createSlice } from "@reduxjs/toolkit";
import { Tournament } from "../../../types/tournaments";
import { createAsyncThunk } from "@reduxjs/toolkit";
import { AxiosResponse } from "axios";
import axios from "axios";
import { PayloadAction } from "@reduxjs/toolkit";
import { setActiveComponent } from "../../Leagues/state/leagueSlice";
import { FantasyLeagueTournamentsResponse } from "../../../types/fantasyLeagueTournamentsResponse";

interface TournamentResponse {
    tournament: Tournament
}

interface changeTournamentArgs {
    selectedTournaments: Array<string>;
    fantasyLeagueSeasonId: string;
}

export const getTournament = createAsyncThunk<Tournament, string>(
    "tournaments/fetchTournamentById",
    async (tournament_id, thunkAPI) => {
        if (!tournament_id) {
            return thunkAPI.rejectWithValue("Tournament ID is undefined");
        }
        try {
            const response: AxiosResponse<TournamentResponse> = await axios.get(`/api/tournaments/${tournament_id}`);
            const data = response.data.tournament;

            // First, update the selected tournament
            thunkAPI.dispatch(setSelectedTournament(data));

            // Then, change the active component
            thunkAPI.dispatch(setActiveComponent("Tournaments"));

            return data;
        } catch (error: any) {
            return thunkAPI.rejectWithValue(error.message || "An unexpected error occurred.");
        }
    }
);

export const fetchTournaments = createAsyncThunk(
    "tournaments/fetchTournaments",
    async (
      { isEditMode, currentFantasyLeagueSeasonId, proSeasonId }: { isEditMode: boolean; currentFantasyLeagueSeasonId?: string; proSeasonId?: string },
      { rejectWithValue }
    ) => {
      try {
        const url = isEditMode
          ? `/api/fantasy_league_seasons/${currentFantasyLeagueSeasonId}/pro_season/competition_schedule`
          : `/api/pro_seasons/${proSeasonId}/competition_schedule`;
  
        const response = await axios.get(url);

        // Add a flag to indicate the format
        return { data: response.data, isEditMode };
      } catch (error: any) {
        console.error("Error fetching tournaments:", error);
        return rejectWithValue(error.message || "Failed to fetch tournaments");
      }
    }
  );

export const addTournament = createAsyncThunk<Array<Tournament>, changeTournamentArgs>(
    'tournaments/addTournament',
    async (
      { selectedTournaments, fantasyLeagueSeasonId }: { selectedTournaments: Array<string>; fantasyLeagueSeasonId: string },
      { rejectWithValue }
    ) => {
      if (!selectedTournaments || selectedTournaments.length === 0) {
        return rejectWithValue('No tournaments selected for addition.');
      }
  
      try {
        const addedTournaments = await Promise.all(
          Array.from(selectedTournaments).map(async (tournamentId) => {
            const response = await axios.post(
              `/api/fantasy_league_seasons/${fantasyLeagueSeasonId}/tournaments`,
              { tournamentId }
            );
            return response.data;
          })
        );
        return addedTournaments;
      } catch (error: any) {
        console.error('Error adding tournaments:', error);
        return rejectWithValue('Failed to add one or more tournaments.');
      }
    }
  );
  

export const deleteTournament = createAsyncThunk<Array<Tournament>, changeTournamentArgs>(
    'tournaments/deleteTournament',
    async ({ selectedTournaments, fantasyLeagueSeasonId }: { selectedTournaments: Array<string>; fantasyLeagueSeasonId: string }, thunkAPI) => {
    if (!selectedTournaments || selectedTournaments.length === 0) {
      return thunkAPI.rejectWithValue('No tournaments selected for deletion.');
    }

    try {
      const deletionResults = await Promise.all(
        Array.from(selectedTournaments).map(async (tournamentId) => {
          try {
            const response = await axios.delete(`/api/fantasy_league_seasons/${fantasyLeagueSeasonId}/tournaments/${tournamentId}`);
            return response.data; 
          } catch (error) {
            console.error(`Error deleting tournament with ID ${tournamentId}:`, error);
            throw new Error(`Failed to delete tournament with ID ${tournamentId}`);
          }
        })
      );
      return deletionResults;
    } catch (error: any) {
      console.error('Error deleting tournaments:', error);
      return thunkAPI.rejectWithValue('Failed to delete one or more tournaments.');
    }
  }
);

interface TournamentState {
    status: string;
    selectedTournament: Tournament | null;
    selectedTournaments: Array<string>
    error: string | undefined;
    tournaments: FantasyLeagueTournamentsResponse | null;
}

const initialState: TournamentState = {
    status: "idle",
    selectedTournament: null,
    error: undefined,
    selectedTournaments: [],
    tournaments: null
};

const tournamentsSlice = createSlice({
    name: "tournaments",
    initialState,
    reducers: {
        setSelectedTournament(state, action: PayloadAction<Tournament | null>) {
            state.selectedTournament = action.payload;
        },
        setSelectedTournaments(state, action: PayloadAction<string>) {
            const tournamentId = action.payload;
      
            // Work with a Set for internal logic
            const updatedSet = new Set(state.selectedTournaments);
      
            if (updatedSet.has(tournamentId)) {
              updatedSet.delete(tournamentId); // Unselect
            } else {
              updatedSet.add(tournamentId); // Select
            }
      
            // Store the updated Set as an array in state
            state.selectedTournaments = Array.from(updatedSet);
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(getTournament.pending, (state) => {
                state.status = "pending";
                state.error = undefined; // Clear previous errors when a new request is made
            })
            .addCase(getTournament.fulfilled, (state, action: PayloadAction<Tournament>) => {
                state.status = "idle";
            })
            .addCase(getTournament.rejected, (state, action) => {
                state.status = "idle";
                state.error = typeof action.payload === "string" ? action.payload : "An unexpected error occurred.";
            })
            .addCase(fetchTournaments.pending, (state) => {
                state.status = "loading";
                state.error = undefined;
            })
            .addCase(fetchTournaments.fulfilled, (state, action) => {
                state.status = "succeeded";
                
                const { data, isEditMode } = action.payload;
                
                if (isEditMode) {
                    // If `isEditMode`, data is an object with three keys
                    state.tournaments = {
                    currentProSeasonTournaments: data.currentProSeasonTournaments || [],
                    pastFantasyLeagueTournaments: data.completedFantasyLeagueTournaments || [],
                    upcomingFantasyLeagueTournaments: data.upcomingFantasyLeagueTournaments || [],
                    upcomingProSeasonTournaments: data.upcomingProSeasonTournaments || []
                    };
                } else {
                    // Otherwise, data is a flat array
                    state.tournaments = { 
                        allTournaments: data || [] };
                }
            })
            .addCase(fetchTournaments.rejected, (state, action) => {
                state.status = "failed";
                state.error = action.payload as string;
            })
            // Handle addTournament
            .addCase(addTournament.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(addTournament.fulfilled, (state, action) => {
                state.status = 'succeeded';
                const addedTournaments = action.payload;
            
                const addedIds = new Set(addedTournaments.map((tournament: any) => tournament.id));
            
                if (state.tournaments) {
                    // Add to `upcomingFantasyLeagueTournaments`
                    if (!state.tournaments.upcomingFantasyLeagueTournaments) {
                        state.tournaments.upcomingFantasyLeagueTournaments = [];
                    }
                    state.tournaments.upcomingFantasyLeagueTournaments.push(...addedTournaments);
            
                    // Sort `upcomingFantasyLeagueTournaments` by start date
                    state.tournaments.upcomingFantasyLeagueTournaments.sort((a, b) =>
                        new Date(a.StartDate).getTime() - new Date(b.StartDate).getTime()
                    );
            
                    // Remove from `upcomingProSeasonTournaments`
                    if (state.tournaments.upcomingProSeasonTournaments) {
                        state.tournaments.upcomingProSeasonTournaments = state.tournaments.upcomingProSeasonTournaments.filter(
                            (tournament) => !addedIds.has(tournament.id)
                        );
            
                        // Sort `upcomingProSeasonTournaments` by start date
                        state.tournaments.upcomingProSeasonTournaments.sort((a, b) =>
                            new Date(a.StartDate).getTime() - new Date(b.StartDate).getTime()
                        );
                    }
            
                    // Clear selected tournaments
                    state.selectedTournaments = [];
                }
            })
            .addCase(addTournament.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload as string;
            })
            // Handle deleteTournament
            .addCase(deleteTournament.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(deleteTournament.fulfilled, (state, action) => {
                state.status = 'succeeded';
                const deletedTournaments = action.payload;
            
                const deletedIds = new Set(deletedTournaments.map((tournament: any) => tournament.id));
            
                if (state.tournaments) {
                    // Remove from `upcomingFantasyLeagueTournaments`
                    if (state.tournaments.upcomingFantasyLeagueTournaments) {
                        state.tournaments.upcomingFantasyLeagueTournaments = state.tournaments.upcomingFantasyLeagueTournaments.filter(
                            (tournament) => !deletedIds.has(tournament.id)
                        );
            
                        // Sort `upcomingFantasyLeagueTournaments` by start date
                        state.tournaments.upcomingFantasyLeagueTournaments.sort((a, b) =>
                            new Date(a.StartDate).getTime() - new Date(b.StartDate).getTime()
                        );
                    }
            
                    // Add back to `upcomingProSeasonTournaments`
                    if (!state.tournaments.upcomingProSeasonTournaments) {
                        state.tournaments.upcomingProSeasonTournaments = [];
                    }
                    state.tournaments.upcomingProSeasonTournaments.push(...deletedTournaments);
            
                    // Sort `upcomingProSeasonTournaments` by start date
                    state.tournaments.upcomingProSeasonTournaments.sort((a, b) =>
                        new Date(a.StartDate).getTime() - new Date(b.StartDate).getTime()
                    );
            
                    // Clear selected tournaments
                    state.selectedTournaments = [];
                }
            })
            .addCase(deleteTournament.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload as string;
            })

    },
});


export default tournamentsSlice.reducer;
export const { setSelectedTournament, setSelectedTournaments } = tournamentsSlice.actions;

