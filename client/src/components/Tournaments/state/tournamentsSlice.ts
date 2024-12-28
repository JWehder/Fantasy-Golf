import { createSlice } from "@reduxjs/toolkit";
import { Tournament } from "../../../types/tournaments";
import { createAsyncThunk } from "@reduxjs/toolkit";
import { AxiosResponse } from "axios";
import axios from "axios";
import { PayloadAction } from "@reduxjs/toolkit";
import { setActiveComponent } from "../../Leagues/state/leagueSlice";

interface TournamentResponse {
    tournament: Tournament
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


interface TournamentState {
    status: string;
    selectedTournament: Tournament | null;
    error: string | undefined;
}

const initialState: TournamentState = {
    status: "idle",
    selectedTournament: null,
    error: undefined,
};

const tournamentsSlice = createSlice({
    name: "tournaments",
    initialState,
    reducers: {
        setSelectedTournament(state, action: PayloadAction<Tournament | null>) {
            state.selectedTournament = action.payload;
        },
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
            });
    },
});


export default tournamentsSlice.reducer;
export const { setSelectedTournament } = tournamentsSlice.actions;

