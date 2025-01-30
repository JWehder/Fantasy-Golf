import { TournamentHoles } from "./tournamentHoles"

export interface Tournament {
    id: string
    EndDate: string
    StartDate: string
    CurrentRoundNum: string
    Name: string
    Venue: string[]
    City: string
    State: string
    Links: string[]
    Purse: number | null
    PreviousWinner: string | null
    Par: string
    Yardage: string | null
    IsCompleted: boolean
    InProgress: boolean
    ProSeasonId: string
    created_at: string
    updated_at: string
    PreviousWinnerScore: number | null
    Holes: TournamentHoles[]
}