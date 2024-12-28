import { createSlice } from "@reduxjs/toolkit";
import { Period } from "../../../types/periods";

interface PeriodState {
    status: string;
    periods: Period[];
}

const initialState: PeriodState = {
    status: "idle",
    periods: [],
};

const periodSlice = createSlice({
    name: "periods",
    initialState,
    reducers: {
        setPeriods(state, action) {
            state.periods = action.payload;
        },
    },
    extraReducers: builder => {
        builder
    }
});

export const { setPeriods } = periodSlice.actions;

export default periodSlice.reducer;