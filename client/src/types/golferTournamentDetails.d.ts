import { Round } from "./rounds"
import { TournamentHoles } from "./tournamentHoles"

export interface GolferTournamentDetails {
    id: string
    GolferId: string
    Position: string
    Name: string
    Score: string
    R1: string
    R2: string
    R3: string
    R4: string 
    TotalStrokes: string
    Earnings: string
    FedexPts: string
    TournamentId: string
    Rounds: Round[]
    created_at: Date
    updated_at: Date
    TournamentName: string
    WinningScore: string
    StartDate: string
    HoleData: TournamentHoles[]
    TeeTimes: { [key: string]: string }
    Today?: string
    Thru?: string
}