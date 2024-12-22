import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios, { AxiosResponse } from "axios";
import { League } from "../../../types/leagues";
import { setLeagueTeams } from "../../Teams/state/teamsSlice"
import { LeagueSettings } from "../../../types/leagueSettings";

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

interface LeagueState {
    status: string;
    leagues: League[];
    selectedLeague: League | null
    leagueError: string | null
    leagueSettingsError: string | null
}

const initialState: LeagueState = {
    status: "idle",
    leagues: [],
    selectedLeague: null,
    leagueError: null,
    leagueSettingsError: null
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
    }
});

export const { setLeagues } = leagueSlice.actions;

export default leagueSlice.reducer;