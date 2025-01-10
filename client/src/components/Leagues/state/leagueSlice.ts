import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios, { AxiosResponse } from "axios";
import { League } from "../../../types/leagues";
import { setLeagueTeams } from "../../Teams/state/teamsSlice"
import { LeagueSettings } from "../../../types/leagueSettings";

interface proSeasonChangeResponse {
    newProSeasonId: string,
    newSeasonId: string
}

export const getLeague = createAsyncThunk<League, string>(
    "leagues/fetchLeagueById",
    async (league_id, thunkAPI) => {
        if (!league_id) {
            return thunkAPI.rejectWithValue("League ID is undefined");
        }
        try {
            const response: AxiosResponse<League> = await axios.get(`/api/leagues/${league_id!}`);
            const data = response.data

            // Destructure the data to pull out `Teams` and the rest of the league data
            const { Teams, ...leagueWithoutTeams } = data;

            // Dispatch teams to the teams slice
            thunkAPI.dispatch(setLeagueTeams(Teams));

            // Return the rest of the league data (without Teams) for the league slice
            return leagueWithoutTeams;

        } catch (error) {
            return thunkAPI.rejectWithValue(error);
        }
    }
);

export const updateLeagueSettings = createAsyncThunk<
  LeagueSettings, // Return type of the thunk
  { leagueSettings: LeagueSettings }, // Payload type (single object with both arguments)
  {
    rejectValue: string; // Type of the value returned by `rejectWithValue`
  }
>(
  "leagues/updateLeagueSettings",
  async ({ leagueSettings }, thunkAPI) => {
    if (!leagueSettings.id) {
      return thunkAPI.rejectWithValue("League settings ID is undefined");
    }
    try {
      const response: AxiosResponse<LeagueSettings> = await axios.patch(
        `/api/league_settings/${leagueSettings.id}`,
        leagueSettings
      );
      return response.data; // Return the updated LeagueSettings
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error instanceof Error ? error.message : "An unknown error occurred"
      );
    }
  }
);

export const createLeague = createAsyncThunk<
  LeagueSettings, // Return type of the thunk
  { league: League }, // Payload type (single object with both arguments)
  {
    rejectValue: string; // Type of the value returned by `rejectWithValue`
  }
>(
  "leagues/createLeague",
  async ({ league }, thunkAPI) => {
    if (!league) {
      return thunkAPI.rejectWithValue("No league was received");
    }
    try {
      const response: AxiosResponse<LeagueSettings> = await axios.post(
        '/api/leagues',
        league
      );
      return response.data; // Return the updated LeagueSettings
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error instanceof Error ? error.message : "An unknown error occurred"
      );
    }
  }
);

export const goToNextSeason = createAsyncThunk<
  proSeasonChangeResponse, // Return type of the thunk
  string, // Payload type (single object with both arguments)
  {
    rejectValue: string; // Type of the value returned by `rejectWithValue`
  }
>(
  "leagues/goToNextSeason",
  async (leagueId, thunkAPI) => {
    if (!leagueId) {
      return thunkAPI.rejectWithValue("No league ID was received");
    }
    try {
      const response: AxiosResponse<proSeasonChangeResponse> = await axios.post(
        `/api/leagues/${leagueId}/fantasy_league_seasons/create_new_season`,
      );
      return response.data; // Return the updated LeagueSettings
    } catch (error) {
        // Extract error details from the backend response
        if (axios.isAxiosError(error) && error.response) {
          const backendError = error.response.data.error || "An error occurred";
          return thunkAPI.rejectWithValue(backendError);
        }
        return thunkAPI.rejectWithValue(
          error instanceof Error ? error.message : "An unknown error occurred"
        );
    }
  }
);

interface LeagueState {
    status: string;
    leagues: League[];
    selectedLeague: League | null;
    leagueError: string | null;
    leagueSettingsError: string | null;
    activeComponent: string;
    goToNextSeasonError: string | null;
    goToNextSeasonSuccessBanner: boolean;
}

const initialState: LeagueState = {
    status: "idle",
    leagues: [],
    selectedLeague: null,
    leagueError: null,
    leagueSettingsError: null,
    activeComponent: "Schedule",
    goToNextSeasonError: null,
    goToNextSeasonSuccessBanner: false
};

const leagueSlice = createSlice({
    name: "leagues",
    initialState,
    reducers: {
        setLeagues(state, action) {
            state.leagues = action.payload;
        },
        clearSelectedLeague(state) {
            state.selectedLeague = null;
        },
        setActiveComponent(state, action) {
            state.activeComponent = action.payload;
        }, 
        setSelectedLeague(state, action) {
            state.selectedLeague = action.payload;
        }
    },
    extraReducers: builder => {
        builder
        .addCase(getLeague.pending, (state) => {
            state.status = "loading";
            state.leagueError = null;
        })
        .addCase(getLeague.fulfilled, (state, action) => {
            state.status = "succeeded";
            state.selectedLeague = action.payload; // assuming 'data' is the key for your league data
            console.log(state.selectedLeague)
            state.leagueError = null;
        })
        .addCase(getLeague.rejected, (state, action) => {
            state.status = "failed";
            state.leagueError = action.error.message || "Failed to fetch league data";
        })
        .addCase(updateLeagueSettings.pending, (state) => {
            state.status = "loading";
            state.leagueSettingsError = null;
        })
        .addCase(updateLeagueSettings.fulfilled, (state, action) => {
            state.status = "succeeded";

            if (!state.selectedLeague || !state.selectedLeague.id) {
                throw new Error("selectedLeague.id is unexpectedly undefined");
            }

            state.selectedLeague! = {
              ...state.selectedLeague,
              LeagueSettings: action.payload,
            };
            state.leagueSettingsError = null;
          })
        .addCase(updateLeagueSettings.rejected, (state, action) => {
            state.status = "failed";
            state.leagueError = action.error.message || "Failed to fetch league data";
        })
        .addCase(goToNextSeason.pending, (state) => {
            state.status = "loading";
            state.goToNextSeasonError = null;
        })
        .addCase(goToNextSeason.fulfilled, (state, action) => {
            state.status = "succeeded";
            if (!state.selectedLeague || !state.selectedLeague.id) {
                state.goToNextSeasonError = "selectedLeague.id is unexpectedly undefined"
                throw new Error("selectedLeague.id is unexpectedly undefined");
            }
            state.selectedLeague! = {
                ...state.selectedLeague,
                LeagueSettings: {
                    ...state.selectedLeague.LeagueSettings,
                    ProSeasonId: action.payload.newProSeasonId
                },
                CurrentFantasyLeagueSeasonId: action.payload.newSeasonId,
                id: state.selectedLeague.id // Ensure `id` is preserved
            };
            state.goToNextSeasonSuccessBanner = true;
            state.goToNextSeasonError = null;
        })
        .addCase(goToNextSeason.rejected, (state, action) => {
            state.status = "failed";
            console.log(action)
            state.goToNextSeasonError = action.payload || "Failed to transition to next season.";
        })
    }
});

export const { 
    setLeagues, 
    setActiveComponent, 
    setSelectedLeague } = leagueSlice.actions;

export default leagueSlice.reducer;