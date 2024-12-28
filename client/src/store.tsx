import { configureStore } from "@reduxjs/toolkit";
import usersReducer from "./components/User/state/userSlice";
import leaguesReducer from "./components/Leagues/state/leagueSlice";
import golfersReducer from "./components/Golfers/state/golferSlice";
import teamsReducer from "./components/Teams/state/teamsSlice"
import tournamentsReducer from "./components/Tournaments/state/tournamentsSlice";
import periodsReducer from "./components/Periods/state/periodSlice";

const store = configureStore({
    reducer:{
        users: usersReducer,
        leagues: leaguesReducer,
        golfers: golfersReducer,
        teams: teamsReducer,
        tournaments: tournamentsReducer,
        periods: periodsReducer
    },
});

// Infer the `RootState` type from the store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Export the store
export default store;
